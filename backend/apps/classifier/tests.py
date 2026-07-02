from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from .models import ClassifierClass, ClassifierModelVersion, TrainingImage, TrainingRun


def make_test_image(name="artifact.jpg"):
    buffer = BytesIO()
    Image.new("RGB", (4, 4), color=(200, 100, 50)).save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


class ClassifierAdminAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email="admin@test.com",
            first_name="Ada",
            last_name="Admin",
            password="password123",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="user@test.com",
            first_name="Regular",
            last_name="User",
            password="password123",
        )

    def test_only_staff_can_create_classifier_class(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/classifier/classes/",
            {"name": "New Artifact"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.staff)
        response = self.client.post(
            "/api/classifier/classes/",
            {"name": "New Artifact"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ClassifierClass.objects.filter(name="New Artifact").exists())

    def test_staff_can_upload_training_image(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.client.force_authenticate(user=self.staff)
                artifact_class = ClassifierClass.objects.create(
                    name="Fresh Class",
                    created_by=self.staff,
                )

                response = self.client.post(
                    f"/api/classifier/classes/{artifact_class.id}/images/",
                    {"image": make_test_image()},
                    format="multipart",
                )

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(TrainingImage.objects.filter(artifact_class=artifact_class).count(), 1)

    @override_settings(
        CLASSIFIER_MIN_IMAGES_PER_CLASS=2,
        MODEL_SERVER_URL="http://model-server.test",
        CLASSIFIER_INTERNAL_API_KEY="test-key",
    )
    @patch("apps.classifier.views.requests.post")
    def test_training_run_starts_model_server_job(self, mock_post):
        mock_response = Mock(status_code=status.HTTP_202_ACCEPTED)
        mock_response.json.return_value = {"job_id": "job-1", "status": "queued"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.client.force_authenticate(user=self.staff)
                artifact_class = ClassifierClass.objects.create(name="New Statue")
                TrainingImage.objects.create(artifact_class=artifact_class, image=make_test_image("a.jpg"))
                TrainingImage.objects.create(artifact_class=artifact_class, image=make_test_image("b.jpg"))

                response = self.client.post(
                    "/api/classifier/training-runs/",
                    {"class_ids": [artifact_class.id], "config": {"epochs": 1}},
                    format="json",
                )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        training_run = TrainingRun.objects.get()
        self.assertEqual(training_run.status, TrainingRun.Status.QUEUED)
        self.assertEqual(training_run.model_server_job_id, "job-1")
        mock_post.assert_called_once()
        self.assertEqual(
            mock_post.call_args.args[0],
            "http://model-server.test/api/internal/classifier/training-runs/start",
        )
        self.assertEqual(mock_post.call_args.kwargs["headers"]["X-Internal-API-Key"], "test-key")

    @override_settings(CLASSIFIER_INTERNAL_API_KEY="test-key")
    def test_internal_training_callback_is_protected_and_records_model_version(self):
        training_run = TrainingRun.objects.create(created_by=self.staff)

        response = self.client.post(
            f"/api/classifier/internal/training-runs/{training_run.id}/status/",
            {"status": "running"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            f"/api/classifier/internal/training-runs/{training_run.id}/status/",
            {
                "status": "succeeded",
                "job_id": "job-1",
                "checkpoint_path": "app/AI_Models/model_versions/run.pth",
                "class_names": ["old", "new"],
                "metrics": {"best_val_accuracy": 90.0},
                "version": "run-v1",
            },
            format="json",
            HTTP_X_INTERNAL_API_KEY="test-key",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        training_run.refresh_from_db()
        self.assertEqual(training_run.status, TrainingRun.Status.SUCCEEDED)
        model_version = ClassifierModelVersion.objects.get(training_run=training_run)
        self.assertFalse(model_version.is_active)
        self.assertEqual(model_version.class_names, ["old", "new"])

    @override_settings(
        MODEL_SERVER_URL="http://model-server.test",
        CLASSIFIER_INTERNAL_API_KEY="test-key",
    )
    @patch("apps.classifier.views.requests.post")
    def test_promote_model_version_reloads_model_server_and_marks_active(self, mock_post):
        mock_response = Mock(status_code=status.HTTP_200_OK)
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.client.force_authenticate(user=self.staff)
        old_version = ClassifierModelVersion.objects.create(
            version="old",
            checkpoint_path="old.pth",
            class_names=["old"],
            is_active=True,
            status=ClassifierModelVersion.Status.ACTIVE,
        )
        new_version = ClassifierModelVersion.objects.create(
            version="new",
            checkpoint_path="new.pth",
            class_names=["old", "new"],
            status=ClassifierModelVersion.Status.READY,
        )

        response = self.client.post(
            f"/api/classifier/model-versions/{new_version.id}/promote/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        old_version.refresh_from_db()
        new_version.refresh_from_db()
        self.assertFalse(old_version.is_active)
        self.assertEqual(old_version.status, ClassifierModelVersion.Status.RETIRED)
        self.assertTrue(new_version.is_active)
        self.assertEqual(new_version.status, ClassifierModelVersion.Status.ACTIVE)
        self.assertEqual(
            mock_post.call_args.args[0],
            "http://model-server.test/api/internal/classifier/model-versions/reload",
        )


class ClassifierTemplateAdminTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email="staff-template@test.com",
            first_name="Staff",
            last_name="Template",
            password="password123",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="template-user@test.com",
            first_name="Normal",
            last_name="User",
            password="password123",
        )

    def test_non_staff_cannot_access_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get("/admin/classifier-dashboard/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_staff_can_access_dashboard_and_create_class(self):
        self.client.force_login(self.staff)

        response = self.client.get("/admin/classifier-dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            "/admin/classifier-dashboard/classes/new/",
            {
                "name": "Template Artifact",
                "description": "Recently cataloged object.",
            },
        )

        artifact_class = ClassifierClass.objects.get(name="Template Artifact")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, f"/admin/classifier-dashboard/classes/{artifact_class.pk}/")
        self.assertEqual(artifact_class.created_by, self.staff)

    def test_staff_can_upload_multiple_images_from_template_page(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.client.force_login(self.staff)
                artifact_class = ClassifierClass.objects.create(name="Upload Class")

                response = self.client.post(
                    f"/admin/classifier-dashboard/classes/{artifact_class.pk}/",
                    {
                        "images": [
                            make_test_image("one.jpg"),
                            make_test_image("two.jpg"),
                        ]
                    },
                )

                self.assertEqual(response.status_code, status.HTTP_302_FOUND)
                self.assertEqual(
                    TrainingImage.objects.filter(artifact_class=artifact_class).count(),
                    2,
                )

    def test_staff_can_edit_class_from_template_page(self):
        self.client.force_login(self.staff)
        artifact_class = ClassifierClass.objects.create(
            name="Editable Class",
            description="Before",
        )

        response = self.client.post(
            f"/admin/classifier-dashboard/classes/{artifact_class.pk}/edit/",
            {
                "name": "Edited Class",
                "description": "After",
                "is_active": "",
            },
        )

        artifact_class.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(
            response.url,
            f"/admin/classifier-dashboard/classes/{artifact_class.pk}/",
        )
        self.assertEqual(artifact_class.name, "Edited Class")
        self.assertEqual(artifact_class.description, "After")
        self.assertFalse(artifact_class.is_active)

    def test_staff_can_delete_class_from_template_page(self):
        self.client.force_login(self.staff)
        artifact_class = ClassifierClass.objects.create(name="Disposable Class")

        response = self.client.post(
            f"/admin/classifier-dashboard/classes/{artifact_class.pk}/delete/",
            {"confirm": "on"},
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, "/admin/classifier-dashboard/")
        self.assertFalse(ClassifierClass.objects.filter(pk=artifact_class.pk).exists())

    def test_staff_can_delete_training_image_from_template_page(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.client.force_login(self.staff)
                artifact_class = ClassifierClass.objects.create(name="Image Delete Class")
                training_image = TrainingImage.objects.create(
                    artifact_class=artifact_class,
                    image=make_test_image("delete-me.jpg"),
                    uploaded_by=self.staff,
                )

                response = self.client.post(
                    f"/admin/classifier-dashboard/images/{training_image.pk}/delete/",
                    {"confirm": "on"},
                )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(
            response.url,
            f"/admin/classifier-dashboard/classes/{artifact_class.pk}/",
        )
        self.assertFalse(TrainingImage.objects.filter(pk=training_image.pk).exists())

    def test_invalid_template_image_upload_is_rejected(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.client.force_login(self.staff)
                artifact_class = ClassifierClass.objects.create(name="Invalid Upload Class")

                response = self.client.post(
                    f"/admin/classifier-dashboard/classes/{artifact_class.pk}/",
                    {
                        "images": SimpleUploadedFile(
                            "not-image.txt",
                            b"not an image",
                            content_type="text/plain",
                        )
                    },
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    TrainingImage.objects.filter(artifact_class=artifact_class).count(),
                    0,
                )

    @override_settings(
        CLASSIFIER_MIN_IMAGES_PER_CLASS=2,
        MODEL_SERVER_URL="http://model-server.test",
        CLASSIFIER_INTERNAL_API_KEY="test-key",
    )
    @patch("apps.classifier.admin_views.requests.post")
    def test_template_start_training_posts_to_model_server(self, mock_post):
        mock_response = Mock(status_code=status.HTTP_202_ACCEPTED)
        mock_response.json.return_value = {"job_id": "job-template", "status": "queued"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.client.force_login(self.staff)
                artifact_class = ClassifierClass.objects.create(name="Trainable Class")
                TrainingImage.objects.create(artifact_class=artifact_class, image=make_test_image("a.jpg"))
                TrainingImage.objects.create(artifact_class=artifact_class, image=make_test_image("b.jpg"))

                response = self.client.post(
                    "/admin/classifier-dashboard/training-runs/start/",
                    {
                        "classes": [str(artifact_class.pk)],
                        "epochs": "1",
                        "batch_size": "4",
                        "learning_rate": "0.001",
                    },
                )

        training_run = TrainingRun.objects.get(model_server_job_id="job-template")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(
            response.url,
            f"/admin/classifier-dashboard/training-runs/{training_run.pk}/",
        )
        self.assertEqual(training_run.status, TrainingRun.Status.QUEUED)
        self.assertEqual(
            mock_post.call_args.args[0],
            "http://model-server.test/api/internal/classifier/training-runs/start",
        )

    @override_settings(CLASSIFIER_MIN_IMAGES_PER_CLASS=2)
    def test_template_start_training_enforces_minimum_images(self):
        self.client.force_login(self.staff)
        artifact_class = ClassifierClass.objects.create(name="Underfilled Class")

        response = self.client.post(
            "/admin/classifier-dashboard/training-runs/start/",
            {
                "classes": [str(artifact_class.pk)],
                "epochs": "1",
                "batch_size": "4",
                "learning_rate": "0.001",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(TrainingRun.objects.exists())

    def test_training_status_fragment_renders_status(self):
        self.client.force_login(self.staff)
        training_run = TrainingRun.objects.create(
            status=TrainingRun.Status.RUNNING,
            created_by=self.staff,
        )

        response = self.client.get(
            f"/admin/classifier-dashboard/training-runs/{training_run.pk}/status-fragment/",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Running")

    def test_template_delete_training_run_without_active_model_version(self):
        self.client.force_login(self.staff)
        training_run = TrainingRun.objects.create(
            status=TrainingRun.Status.FAILED,
            created_by=self.staff,
        )
        ClassifierModelVersion.objects.create(
            version="delete-run-version",
            checkpoint_path="version.pth",
            class_names=["new"],
            status=ClassifierModelVersion.Status.RETIRED,
            training_run=training_run,
        )

        response = self.client.post(
            f"/admin/classifier-dashboard/training-runs/{training_run.pk}/delete/",
            {"confirm": "on"},
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, "/admin/classifier-dashboard/")
        self.assertFalse(TrainingRun.objects.filter(pk=training_run.pk).exists())
        self.assertTrue(
            ClassifierModelVersion.objects.filter(version="delete-run-version").exists()
        )

    def test_template_delete_training_run_blocks_active_model_version(self):
        self.client.force_login(self.staff)
        training_run = TrainingRun.objects.create(
            status=TrainingRun.Status.SUCCEEDED,
            created_by=self.staff,
        )
        ClassifierModelVersion.objects.create(
            version="active-run-version",
            checkpoint_path="active.pth",
            class_names=["new"],
            status=ClassifierModelVersion.Status.ACTIVE,
            is_active=True,
            training_run=training_run,
        )

        response = self.client.post(
            f"/admin/classifier-dashboard/training-runs/{training_run.pk}/delete/",
            {"confirm": "on"},
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(
            response.url,
            f"/admin/classifier-dashboard/training-runs/{training_run.pk}/",
        )
        self.assertTrue(TrainingRun.objects.filter(pk=training_run.pk).exists())

    @override_settings(
        MODEL_SERVER_URL="http://model-server.test",
        CLASSIFIER_INTERNAL_API_KEY="test-key",
    )
    @patch("apps.classifier.admin_views.requests.post")
    def test_template_promote_model_version(self, mock_post):
        mock_response = Mock(status_code=status.HTTP_200_OK)
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.client.force_login(self.staff)
        old_version = ClassifierModelVersion.objects.create(
            version="template-old",
            checkpoint_path="old.pth",
            class_names=["old"],
            is_active=True,
            status=ClassifierModelVersion.Status.ACTIVE,
        )
        training_run = TrainingRun.objects.create(
            status=TrainingRun.Status.SUCCEEDED,
            created_by=self.staff,
        )
        new_version = ClassifierModelVersion.objects.create(
            version="template-new",
            checkpoint_path="new.pth",
            class_names=["old", "new"],
            status=ClassifierModelVersion.Status.READY,
            training_run=training_run,
        )

        response = self.client.post(
            f"/admin/classifier-dashboard/model-versions/{new_version.pk}/promote/",
            {"confirm": "on"},
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        old_version.refresh_from_db()
        new_version.refresh_from_db()
        self.assertFalse(old_version.is_active)
        self.assertTrue(new_version.is_active)
        self.assertEqual(new_version.promoted_by, self.staff)

    def test_template_can_retire_and_delete_non_active_model_version(self):
        self.client.force_login(self.staff)
        model_version = ClassifierModelVersion.objects.create(
            version="retirable-version",
            checkpoint_path="ready.pth",
            class_names=["new"],
            status=ClassifierModelVersion.Status.READY,
        )

        response = self.client.post(
            f"/admin/classifier-dashboard/model-versions/{model_version.pk}/retire/",
            {"confirm": "on"},
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        model_version.refresh_from_db()
        self.assertEqual(model_version.status, ClassifierModelVersion.Status.RETIRED)

        response = self.client.post(
            f"/admin/classifier-dashboard/model-versions/{model_version.pk}/delete/",
            {"confirm": "on"},
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(
            ClassifierModelVersion.objects.filter(pk=model_version.pk).exists()
        )

    def test_template_delete_active_model_version_is_blocked(self):
        self.client.force_login(self.staff)
        model_version = ClassifierModelVersion.objects.create(
            version="active-delete-blocked",
            checkpoint_path="active.pth",
            class_names=["old"],
            status=ClassifierModelVersion.Status.ACTIVE,
            is_active=True,
        )

        response = self.client.post(
            f"/admin/classifier-dashboard/model-versions/{model_version.pk}/delete/",
            {"confirm": "on"},
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(
            ClassifierModelVersion.objects.filter(pk=model_version.pk).exists()
        )
