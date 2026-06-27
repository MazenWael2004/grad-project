from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol
from uuid import uuid4

from django.conf import settings as django_settings
from django.utils import timezone
from livekit import api as livekit_api

from .content import load_giza_tour
from .tour_state import ActiveMode, TourState
from .models import TourSession, TourStateCheckpoint, RecognitionEvent, EvalEvent


@dataclass(frozen=True)
class ApiSettings:
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    guest_token_hash_secret: str
    livekit_agent_name: str = "my-agent"
    guest_session_ttl: timedelta = timedelta(hours=4)
    livekit_token_ttl: timedelta = timedelta(minutes=15)
    cors_allow_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    )

    @classmethod
    def from_settings(cls) -> ApiSettings:
        # Load from Django settings or fallback to env variables
        return cls(
            livekit_url=getattr(django_settings, "LIVEKIT_URL", os.getenv("LIVEKIT_URL", "")),
            livekit_api_key=getattr(django_settings, "LIVEKIT_API_KEY", os.getenv("LIVEKIT_API_KEY", "")),
            livekit_api_secret=getattr(django_settings, "LIVEKIT_API_SECRET", os.getenv("LIVEKIT_API_SECRET", "")),
            livekit_agent_name=getattr(django_settings, "LIVEKIT_AGENT_NAME", os.getenv("LIVEKIT_AGENT_NAME", "my-agent")),
            guest_token_hash_secret=getattr(django_settings, "GUEST_TOKEN_HASH_SECRET", os.getenv("GUEST_TOKEN_HASH_SECRET", getattr(django_settings, "SECRET_KEY", ""))),
            guest_session_ttl=timedelta(hours=getattr(django_settings, "GUEST_SESSION_TTL_HOURS", 4)),
            livekit_token_ttl=timedelta(minutes=getattr(django_settings, "LIVEKIT_TOKEN_TTL_MINUTES", 15)),
        )


@dataclass(frozen=True)
class SessionRecord:
    id: str
    owner_subject: str
    guest_token_hash: str
    tour_slug: str
    language: str
    livekit_room: str
    participant_identity: str
    expires_at: datetime
    created_at: datetime


@dataclass(frozen=True)
class CheckpointRecord:
    id: str
    session_id: str
    event_id: str
    event_type: str
    state_version: int
    state_payload: dict[str, object]
    created_at: datetime


@dataclass(frozen=True)
class RecognitionRecord:
    id: str
    session_id: str
    request_event_id: str
    idempotency_key: str
    status: str
    file_name: str
    content_type: str | None
    confidence: float | None = None
    result_payload: dict[str, object] | None = None
    error_code: str | None = None
    retryable: bool | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass(frozen=True)
class EvalEventRecord:
    id: str
    session_id: str
    event_id: str
    event_type: str
    payload: dict[str, object]
    created_at: datetime


@dataclass(frozen=True)
class LiveKitJoinToken:
    url: str
    room_name: str
    participant_identity: str
    participant_token: str
    expires_at: datetime


class AppRepository(Protocol):
    def create_session(
        self, session: SessionRecord, checkpoint: CheckpointRecord
    ) -> None: ...

    def get_session(self, session_id: str) -> SessionRecord | None: ...

    def get_session_by_token_hash(
        self, guest_token_hash: str
    ) -> SessionRecord | None: ...

    def latest_checkpoint(self, session_id: str) -> CheckpointRecord | None: ...

    def create_pending_recognition(
        self,
        *,
        session_id: str,
        request_event_id: str,
        idempotency_key: str,
        file_name: str,
        content_type: str | None,
        created_at: datetime,
    ) -> RecognitionRecord: ...

    def get_recognition(
        self, *, session_id: str, recognition_id: str
    ) -> RecognitionRecord | None: ...

    def record_event(self, event: EvalEventRecord) -> bool: ...


class DjangoAppRepository:
    def create_session(
        self, session: SessionRecord, checkpoint: CheckpointRecord
    ) -> None:
        db_session = TourSession.objects.create(
            id=session.id,
            owner_subject=session.owner_subject,
            guest_token_hash=session.guest_token_hash,
            tour_slug=session.tour_slug,
            language=session.language,
            livekit_room=session.livekit_room,
            participant_identity=session.participant_identity,
            expires_at=session.expires_at,
            created_at=session.created_at,
        )
        TourStateCheckpoint.objects.create(
            id=checkpoint.id,
            session=db_session,
            event_id=checkpoint.event_id,
            event_type=checkpoint.event_type,
            state_version=checkpoint.state_version,
            active_mode=checkpoint.state_payload.get("active_mode"),
            current_beat_id=checkpoint.state_payload.get("current_beat_slug"),
            safe_anchor=checkpoint.state_payload.get("safe_anchor"),
            state_payload=checkpoint.state_payload,
            created_at=checkpoint.created_at,
        )

    def get_session(self, session_id: str) -> SessionRecord | None:
        try:
            s = TourSession.objects.get(id=session_id)
            return SessionRecord(
                id=s.id,
                owner_subject=s.owner_subject,
                guest_token_hash=s.guest_token_hash,
                tour_slug=s.tour_slug,
                language=s.language,
                livekit_room=s.livekit_room,
                participant_identity=s.participant_identity,
                expires_at=s.expires_at,
                created_at=s.created_at,
            )
        except TourSession.DoesNotExist:
            return None

    def get_session_by_token_hash(self, guest_token_hash: str) -> SessionRecord | None:
        try:
            s = TourSession.objects.get(guest_token_hash=guest_token_hash)
            return SessionRecord(
                id=s.id,
                owner_subject=s.owner_subject,
                guest_token_hash=s.guest_token_hash,
                tour_slug=s.tour_slug,
                language=s.language,
                livekit_room=s.livekit_room,
                participant_identity=s.participant_identity,
                expires_at=s.expires_at,
                created_at=s.created_at,
            )
        except TourSession.DoesNotExist:
            return None

    def latest_checkpoint(self, session_id: str) -> CheckpointRecord | None:
        latest = TourStateCheckpoint.objects.filter(session_id=session_id).order_by("state_version").last()
        if latest is None:
            return None
        return CheckpointRecord(
            id=latest.id,
            session_id=latest.session_id,
            event_id=latest.event_id,
            event_type=latest.event_type,
            state_version=latest.state_version,
            state_payload=latest.state_payload,
            created_at=latest.created_at,
        )

    def create_pending_recognition(
        self,
        *,
        session_id: str,
        request_event_id: str,
        idempotency_key: str,
        file_name: str,
        content_type: str | None,
        created_at: datetime,
    ) -> RecognitionRecord:
        existing = RecognitionEvent.objects.filter(
            session_id=session_id,
            request_event_id=request_event_id,
            idempotency_key=idempotency_key,
        ).first()

        if existing:
            return _recognition_record_from_model(existing)

        session = TourSession.objects.get(id=session_id)
        rec = RecognitionEvent.objects.create(
            id=_prefixed_id("rec"),
            session=session,
            request_event_id=request_event_id,
            idempotency_key=idempotency_key,
            status="pending",
            file_name=file_name,
            content_type=content_type,
            created_at=created_at,
        )
        return _recognition_record_from_model(rec)

    def get_recognition(
        self, *, session_id: str, recognition_id: str
    ) -> RecognitionRecord | None:
        rec = RecognitionEvent.objects.filter(
            id=recognition_id, session_id=session_id
        ).first()
        if rec is None:
            return None
        return _recognition_record_from_model(rec)

    def record_event(self, event: EvalEventRecord) -> bool:
        if EvalEvent.objects.filter(session_id=event.session_id, event_id=event.event_id).exists():
            return False
        
        session = TourSession.objects.get(id=event.session_id)
        EvalEvent.objects.create(
            id=event.id,
            session=session,
            event_id=event.event_id,
            event_type=event.event_type,
            payload=event.payload,
            created_at=event.created_at,
        )
        return True


def _recognition_record_from_model(rec: RecognitionEvent) -> RecognitionRecord:
    return RecognitionRecord(
        id=rec.id,
        session_id=rec.session_id,
        request_event_id=rec.request_event_id,
        idempotency_key=rec.idempotency_key,
        status=rec.status,
        file_name=rec.file_name,
        content_type=rec.content_type,
        confidence=rec.confidence,
        result_payload=rec.result_payload,
        error_code=rec.error_code,
        retryable=rec.retryable,
        created_at=rec.created_at,
        completed_at=rec.completed_at,
    )


class LiveKitTokenIssuer(Protocol):
    def issue(self, *, session: SessionRecord) -> LiveKitJoinToken: ...


class LiveKitAccessTokenIssuer:
    def __init__(self, settings: ApiSettings) -> None:
        self.settings = settings

    def issue(self, *, session: SessionRecord) -> LiveKitJoinToken:
        expires_at = datetime.now(timezone.utc) + self.settings.livekit_token_ttl
        binding = {
            "session_id": session.id,
            "owner_subject": session.owner_subject,
            "room_name": session.livekit_room,
            "participant_identity": session.participant_identity,
            "tour_slug": session.tour_slug,
        }
        metadata = json.dumps(binding, separators=(",", ":"))
        token = (
            livekit_api.AccessToken(
                self.settings.livekit_api_key,
                self.settings.livekit_api_secret,
            )
            .with_identity(session.participant_identity)
            .with_name("AI Tour Guide Guest")
            .with_metadata(metadata)
            .with_attributes(binding)
            .with_ttl(self.settings.livekit_token_ttl)
            .with_grants(
                livekit_api.VideoGrants(
                    room_join=True,
                    room=session.livekit_room,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                    can_publish_sources=["microphone"],
                )
            )
            .with_room_config(
                livekit_api.RoomConfiguration(
                    agents=[
                        livekit_api.RoomAgentDispatch(
                            agent_name=self.settings.livekit_agent_name,
                            metadata=metadata,
                        )
                    ]
                )
            )
            .to_jwt()
        )
        return LiveKitJoinToken(
            url=self.settings.livekit_url,
            room_name=session.livekit_room,
            participant_identity=session.participant_identity,
            participant_token=token,
            expires_at=expires_at,
        )


def create_session_record(
    *,
    tour_slug: str,
    language: str,
    settings: ApiSettings,
    now: datetime,
) -> tuple[SessionRecord, CheckpointRecord, str]:
    session_id = _prefixed_id("sess")
    owner_subject = _prefixed_id("owner")
    guest_token = f"gst_{secrets.token_urlsafe(32)}"
    guest_token_hash = hash_guest_token(
        guest_token, secret=settings.guest_token_hash_secret
    )
    session = SessionRecord(
        id=session_id,
        owner_subject=owner_subject,
        guest_token_hash=guest_token_hash,
        tour_slug=tour_slug,
        language=language,
        livekit_room=f"tour_{session_id}",
        participant_identity=f"guest_{owner_subject.removeprefix('owner_')[:16]}",
        expires_at=now + settings.guest_session_ttl,
        created_at=now,
    )
    checkpoint = CheckpointRecord(
        id=_prefixed_id("chk"),
        session_id=session_id,
        event_id=_prefixed_id("evt"),
        event_type="session_created",
        state_version=0,
        state_payload=initial_state_payload(tour_slug=tour_slug, language=language),
        created_at=now,
    )
    return session, checkpoint, guest_token


def initial_state_payload(*, tour_slug: str, language: str) -> dict[str, object]:
    graph = load_giza_tour()
    if tour_slug != graph.slug:
        raise ValueError(f"unknown tour slug: {tour_slug}")
    first_beat = graph.first_beat()
    return TourState(
        tour_slug=tour_slug,
        language=language,
        active_mode=ActiveMode.NOT_STARTED,
        state_version=0,
        current_stop_slug=first_beat.stop_slug,
        current_topic=first_beat.topic,
        current_beat_slug=first_beat.slug,
    ).to_dict()


def public_state(state_payload: dict[str, object]) -> dict[str, object]:
    return {
        "state_version": int(state_payload["state_version"]),
        "active_mode": str(state_payload["active_mode"]),
        "current_beat_id": state_payload.get("current_beat_slug"),
        "safe_anchor": state_payload.get("safe_anchor"),
    }


def hash_guest_token(token: str, *, secret: str) -> str:
    return hmac.new(secret.encode(), token.encode(), hashlib.sha256).hexdigest()


def verify_guest_token(token: str, token_hash: str, *, secret: str) -> bool:
    return hmac.compare_digest(hash_guest_token(token, secret=secret), token_hash)


def _prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"
