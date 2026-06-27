from datetime import datetime, timezone, timedelta
import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .content import load_giza_tour
from .tour_state import (
    ActiveMode,
    IllegalTransition,
    DjangoCheckpointStore,
    RouteAction,
    RouteActionProposal,
    StaleStateVersion,
    TourController,
    TourState,
)
from .backend import (
    DjangoAppRepository,
    ApiSettings,
    SessionRecord,
    CheckpointRecord,
    RecognitionRecord,
    EvalEventRecord,
    hash_guest_token,
)
from .models import TourSession, TourStateCheckpoint, RecognitionEvent, EvalEvent


class TourStateTestCase(TestCase):
    def setUp(self):
        # Create a test session in the database first
        self.session = TourSession.objects.create(
            id="sess_test_state",
            owner_subject="owner_123",
            guest_token_hash="dummy_hash",
            tour_slug="giza-v1",
            language="en",
            livekit_room="tour_sess_test_state",
            participant_identity="guest_123",
            expires_at=django_timezone.now() + timedelta(hours=4),
            created_at=django_timezone.now(),
        )
        self.store = DjangoCheckpointStore()

    def _controller(self) -> TourController:
        return TourController.for_giza(
            session_id=self.session.id,
            store=self.store,
            language="en",
        )

    def test_giza_tour_graph_has_minimal_reviewed_beats(self) -> None:
        graph = load_giza_tour()

        self.assertEqual(
            [stop.slug for stop in graph.stops],
            ["arrival", "khufu", "khafre", "menkaure", "sphinx", "wrap_up"],
        )
        self.assertEqual(graph.first_beat().slug, "arrival_orientation")
        self.assertEqual(graph.next_beat_slug("arrival_orientation"), "khufu_overview")

        for beat in graph.beats:
            self.assertEqual(beat.review_status, "reviewed")
            self.assertTrue(30 <= beat.estimated_seconds <= 45)
            self.assertTrue(beat.source_ids)

    def test_start_and_normal_completion_advance_exactly_one_beat(self) -> None:
        controller = self._controller()

        start = controller.start_tour(event_id="evt_start")
        self.assertTrue(start.applied)
        self.assertEqual(controller.state.active_mode, ActiveMode.NARRATING)
        self.assertEqual(controller.state.state_version, 1)
        self.assertEqual(controller.state.current_beat_slug, "arrival_orientation")
        self.assertEqual(controller.state.prefetched_next_beat_slug, "khufu_overview")

        packet = controller.current_response_packet()
        self.assertEqual(packet["current_beat"]["slug"], "arrival_orientation")
        self.assertEqual(packet["safe_anchor"]["beat_slug"], "arrival_orientation")
        self.assertEqual(
            packet["allowed_actions"],
            [
                "resume",
                "skip",
                "switch_topic",
                "answer_question",
                "go_deeper",
                "simplify",
                "photo_explanation",
            ],
        )

        advance = controller.record_speech_outcome(
            event_id="evt_complete_arrival",
            expected_state_version=1,
            interrupted=False,
        )

        self.assertTrue(advance.applied)
        self.assertEqual(controller.state.state_version, 2)
        self.assertEqual(controller.state.current_beat_slug, "khufu_overview")
        self.assertEqual(controller.state.completed_beats, ("arrival_orientation",))
        self.assertEqual(controller.state.prefetched_next_beat_slug, "khafre_overview")

    def test_interruption_preserves_anchor_and_waits_for_validated_resume(self) -> None:
        controller = self._controller()
        controller.start_tour(event_id="evt_start")
        before = controller.state

        interrupted = controller.record_speech_outcome(
            event_id="evt_interrupt_arrival",
            expected_state_version=1,
            interrupted=True,
        )

        self.assertFalse(interrupted.applied)
        self.assertEqual(interrupted.reason, "interrupted")
        self.assertEqual(controller.state, before)

        resumed = controller.apply_proposal(
            RouteActionProposal(
                action=RouteAction.RESUME,
                event_id="evt_resume_arrival",
                expected_state_version=1,
            )
        )

        self.assertTrue(resumed.applied)
        self.assertEqual(controller.state.state_version, 2)
        self.assertEqual(controller.state.current_beat_slug, "arrival_orientation")
        self.assertEqual(controller.state.safe_anchor.beat_slug, "arrival_orientation")

    def test_question_deeper_simplify_and_photo_preserve_current_beat(self) -> None:
        controller = self._controller()
        controller.start_tour(event_id="evt_start")

        question = controller.apply_proposal(
            RouteActionProposal(
                action=RouteAction.ANSWER_QUESTION,
                event_id="evt_question",
                expected_state_version=1,
                prompt="Who built this?",
            )
        )
        self.assertTrue(question.applied)
        self.assertEqual(controller.state.active_mode, ActiveMode.ANSWERING)
        self.assertEqual(controller.state.current_beat_slug, "arrival_orientation")
        self.assertEqual(controller.state.last_user_question, "Who built this?")

        deeper = controller.apply_proposal(
            RouteActionProposal(
                action=RouteAction.GO_DEEPER,
                event_id="evt_deeper",
                expected_state_version=2,
                prompt="Tell me more about this stop.",
            )
        )
        self.assertTrue(deeper.applied)
        self.assertEqual(controller.state.current_beat_slug, "arrival_orientation")
        self.assertEqual(controller.state.return_later_topics, ("orientation",))

        simpler = controller.apply_proposal(
            RouteActionProposal(
                action=RouteAction.SIMPLIFY,
                event_id="evt_simplify",
                expected_state_version=3,
                prompt="Make that simpler.",
            )
        )
        self.assertTrue(simpler.applied)
        self.assertEqual(controller.state.current_beat_slug, "arrival_orientation")

        photo = controller.apply_proposal(
            RouteActionProposal(
                action=RouteAction.PHOTO_EXPLANATION,
                event_id="evt_photo_done",
                expected_state_version=4,
                recognition_id="rec_123",
            )
        )
        self.assertTrue(photo.applied)
        self.assertEqual(controller.state.current_beat_slug, "arrival_orientation")
        self.assertEqual(controller.state.recent_recognition_ids, ("rec_123",))

    def test_skip_and_switch_topic_are_validated_controller_transitions(self) -> None:
        controller = self._controller()
        controller.start_tour(event_id="evt_start")

        skipped = controller.apply_proposal(
            RouteActionProposal(
                action=RouteAction.SKIP,
                event_id="evt_skip",
                expected_state_version=1,
            )
        )
        self.assertTrue(skipped.applied)
        self.assertEqual(controller.state.current_beat_slug, "khufu_overview")
        self.assertEqual(controller.state.skipped_topics, ("orientation",))

        switched = controller.apply_proposal(
            RouteActionProposal(
                action=RouteAction.SWITCH_TOPIC,
                event_id="evt_switch_sphinx",
                expected_state_version=2,
                target_topic="sphinx",
            )
        )
        self.assertTrue(switched.applied)
        self.assertEqual(controller.state.current_beat_slug, "sphinx_overview")
        self.assertEqual(controller.state.return_later_topics, ("khufu",))

    def test_duplicate_stale_and_illegal_transitions_do_not_mutate_state(self) -> None:
        controller = self._controller()

        with self.assertRaises(IllegalTransition):
            controller.record_speech_outcome(
                event_id="evt_complete_before_start",
                expected_state_version=0,
                interrupted=False,
            )

        controller.start_tour(event_id="evt_start")
        state_after_start = controller.state

        duplicate = controller.start_tour(event_id="evt_start")
        self.assertFalse(duplicate.applied)
        self.assertEqual(duplicate.reason, "duplicate_event")
        self.assertEqual(controller.state, state_after_start)

        with self.assertRaises(StaleStateVersion):
            controller.apply_proposal(
                RouteActionProposal(
                    action=RouteAction.SKIP,
                    event_id="evt_stale_skip",
                    expected_state_version=0,
                )
            )
        self.assertEqual(controller.state, state_after_start)

        with self.assertRaises(IllegalTransition):
            controller.apply_proposal(
                RouteActionProposal(
                    action=RouteAction.SWITCH_TOPIC,
                    event_id="evt_unknown_topic",
                    expected_state_version=1,
                    target_topic="alexandria",
                )
            )
        self.assertEqual(controller.state, state_after_start)

    def test_state_serializes_and_restores_from_latest_checkpoint(self) -> None:
        controller = self._controller()
        controller.start_tour(event_id="evt_start")
        controller.record_speech_outcome(
            event_id="evt_complete_arrival",
            expected_state_version=1,
            interrupted=False,
        )

        serialized = controller.state.to_dict()
        self.assertEqual(TourState.from_dict(serialized), controller.state)

        restored = TourController.restore_giza(
            session_id=self.session.id,
            store=self.store,
        )
        self.assertEqual(restored.state, controller.state)
        self.assertEqual(
            restored.current_response_packet()["current_beat"]["slug"], "khufu_overview"
        )


class AppRepositoryTestCase(TestCase):
    def setUp(self):
        self.repo = DjangoAppRepository()

    def test_session_lifecycle_in_repo(self):
        now = django_timezone.now()
        session_rec = SessionRecord(
            id="sess_repo_test",
            owner_subject="owner_repo",
            guest_token_hash="hash_repo",
            tour_slug="giza-v1",
            language="en",
            livekit_room="tour_sess_repo_test",
            participant_identity="guest_repo",
            expires_at=now + timedelta(hours=4),
            created_at=now,
        )
        checkpoint_rec = CheckpointRecord(
            id="chk_repo_test",
            session_id="sess_repo_test",
            event_id="evt_repo_test",
            event_type="session_created",
            state_version=0,
            state_payload={"active_mode": "not_started", "state_version": 0},
            created_at=now,
        )

        self.repo.create_session(session_rec, checkpoint_rec)

        # Retrieve session
        fetched = self.repo.get_session("sess_repo_test")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.owner_subject, "owner_repo")

        # Retrieve by hash
        fetched_by_hash = self.repo.get_session_by_token_hash("hash_repo")
        self.assertIsNotNone(fetched_by_hash)
        self.assertEqual(fetched_by_hash.id, "sess_repo_test")

        # Retrieve latest checkpoint
        latest_chk = self.repo.latest_checkpoint("sess_repo_test")
        self.assertIsNotNone(latest_chk)
        self.assertEqual(latest_chk.id, "chk_repo_test")
        self.assertEqual(latest_chk.state_version, 0)

    def test_recognition_in_repo(self):
        now = django_timezone.now()
        session = TourSession.objects.create(
            id="sess_rec_test",
            owner_subject="owner_rec",
            guest_token_hash="hash_rec",
            tour_slug="giza-v1",
            language="en",
            livekit_room="tour_sess_rec_test",
            participant_identity="guest_rec",
            expires_at=now + timedelta(hours=4),
            created_at=now,
        )

        rec = self.repo.create_pending_recognition(
            session_id=session.id,
            request_event_id="evt_rec_req",
            idempotency_key="key_123",
            file_name="test.jpg",
            content_type="image/jpeg",
            created_at=now,
        )

        self.assertEqual(rec.status, "pending")
        self.assertEqual(rec.request_event_id, "evt_rec_req")

        # Duplicate check returns same record
        rec_dup = self.repo.create_pending_recognition(
            session_id=session.id,
            request_event_id="evt_rec_req",
            idempotency_key="key_123",
            file_name="test.jpg",
            content_type="image/jpeg",
            created_at=now,
        )
        self.assertEqual(rec.id, rec_dup.id)

        # Retrieve it
        fetched_rec = self.repo.get_recognition(session_id=session.id, recognition_id=rec.id)
        self.assertIsNotNone(fetched_rec)
        self.assertEqual(fetched_rec.id, rec.id)


class ToursAPITestCase(APITestCase):
    def setUp(self):
        self.guest_token = "gst_secure_token_123"
        self.token_hash = hash_guest_token(self.guest_token, secret="test_secret_hash")
        
        # Override ApiSettings defaults for testing (or we ensure setting is readable)
        from django.conf import settings
        setattr(settings, "GUEST_TOKEN_HASH_SECRET", "test_secret_hash")

        self.session = TourSession.objects.create(
            id="sess_api_test",
            owner_subject="owner_api",
            guest_token_hash=self.token_hash,
            tour_slug="giza-v1",
            language="en",
            livekit_room="tour_sess_api_test",
            participant_identity="guest_api",
            expires_at=django_timezone.now() + timedelta(hours=4),
            created_at=django_timezone.now(),
        )
        
        # Create an initial checkpoint
        TourStateCheckpoint.objects.create(
            id="chk_api_init",
            session=self.session,
            event_id="evt_init",
            event_type="session_created",
            state_version=0,
            active_mode="not_started",
            state_payload={"active_mode": "not_started", "state_version": 0},
            created_at=django_timezone.now()
        )

        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.guest_token}"}

    def test_health_check(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "ok"})

    def test_list_tours(self):
        response = self.client.get(reverse("tours_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tours", response.data)
        self.assertEqual(response.data["tours"][0]["slug"], "giza-v1")

    def test_create_session(self):
        payload = {"tour_slug": "giza-v1", "language": "en"}
        response = self.client.post(reverse("create_session"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session_id", response.data)
        self.assertIn("guest_session_token", response.data)

    def test_get_session_state_authorized(self):
        url = reverse("session_state", kwargs={"session_id": self.session.id})
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["active_mode"], "not_started")

    def test_get_session_state_unauthorized(self):
        url = reverse("session_state", kwargs={"session_id": self.session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_session_state_mismatch(self):
        url = reverse("session_state", kwargs={"session_id": "sess_wrong"})
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_photo_upload(self):
        import io
        from django.core.files.uploadedfile import SimpleUploadedFile

        file_data = io.BytesIO(b"dummy image data")
        upload_file = SimpleUploadedFile("photo.jpg", file_data.read(), content_type="image/jpeg")

        url = reverse("upload_photo", kwargs={"session_id": self.session.id})
        
        headers = {
            **self.auth_headers,
            "HTTP_IDEMPOTENCY_KEY": "idemp_key_999"
        }
        
        response = self.client.post(
            url,
            {"file": upload_file, "event_id": "evt_photo_upload"},
            format="multipart",
            **headers
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("recognition_id", response.data)
        self.assertEqual(response.data["status"], "pending")

    def test_nearby_stops(self):
        url = reverse("nearby_stops")
        query_params = {
            "session_id": self.session.id,
            "tour_slug": "giza-v1",
            "latitude": 29.9792,
            "longitude": 31.1342
        }
        response = self.client.get(url, query_params, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("suggestions", response.data)
        # Verify Khufu stop is suggestions[0] since distance is 0
        self.assertEqual(response.data["suggestions"][0]["stop_slug"], "khufu")
        self.assertEqual(response.data["suggestions"][0]["distance_meters"], 0)
