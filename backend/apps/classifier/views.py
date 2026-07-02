from django.conf import settings
from django.db import transaction
from django.utils import timezone

import requests
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClassifierClass, ClassifierModelVersion, TrainingImage, TrainingRun
from .serializers import (
    ClassifierClassSerializer,
    ClassifierModelVersionSerializer,
    TrainingImageSerializer,
    TrainingImageUploadSerializer,
    TrainingRunCreateSerializer,
    TrainingRunSerializer,
)


class ModelServerConflict(Exception):
    pass


def _internal_api_key():
    return getattr(settings, "CLASSIFIER_INTERNAL_API_KEY", "")


def _model_server_url(path):
    base_url = getattr(settings, "MODEL_SERVER_URL", "http://127.0.0.1:8001").rstrip("/")
    return f"{base_url}{path}"


def _internal_headers():
    return {"X-Internal-API-Key": _internal_api_key()}


class ClassifierClassViewSet(viewsets.ModelViewSet):
    queryset = ClassifierClass.objects.prefetch_related("images").all()
    serializer_class = ClassifierClassSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        url_path="images",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_images(self, request, pk=None):
        artifact_class = self.get_object()
        files = request.FILES.getlist("images") or request.FILES.getlist("image")
        if not files:
            return Response(
                {"detail": "Upload at least one file using the 'images' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_images = []
        for file_obj in files:
            serializer = TrainingImageUploadSerializer(data={"image": file_obj})
            serializer.is_valid(raise_exception=True)
            training_image = TrainingImage.objects.create(
                artifact_class=artifact_class,
                image=serializer.validated_data["image"],
                original_filename=file_obj.name,
                uploaded_by=request.user,
            )
            uploaded_images.append(training_image)

        return Response(
            TrainingImageSerializer(uploaded_images, many=True, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class TrainingRunViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        TrainingRun.objects.prefetch_related("requested_classes", "model_versions")
        .select_related("base_model_version")
        .all()
    )
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return TrainingRunCreateSerializer
        return TrainingRunSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        active_model = ClassifierModelVersion.objects.filter(is_active=True).first()
        training_run = TrainingRun.objects.create(
            base_model_version=active_model,
            config=serializer.validated_data["config"],
            created_by=request.user,
        )
        training_run.requested_classes.set(serializer.validated_data["classes"])

        try:
            response_data = self._start_model_server_training(training_run)
        except ModelServerConflict as exc:
            training_run.status = TrainingRun.Status.FAILED
            training_run.error_message = str(exc)
            training_run.finished_at = timezone.now()
            training_run.save(update_fields=["status", "error_message", "finished_at", "updated_at"])
            return Response(
                {"detail": str(exc), "training_run_id": training_run.id},
                status=status.HTTP_409_CONFLICT,
            )
        except requests.RequestException as exc:
            training_run.status = TrainingRun.Status.FAILED
            training_run.error_message = str(exc)
            training_run.finished_at = timezone.now()
            training_run.save(update_fields=["status", "error_message", "finished_at", "updated_at"])
            return Response(
                {"detail": "Unable to reach classifier model server.", "error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        training_run.status = response_data.get("status", TrainingRun.Status.QUEUED)
        training_run.model_server_job_id = response_data.get("job_id", "")
        training_run.save(update_fields=["status", "model_server_job_id", "updated_at"])

        output_serializer = TrainingRunSerializer(training_run, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def _start_model_server_training(self, training_run):
        payload = {
            "run_id": training_run.id,
            "base_model_version_id": training_run.base_model_version_id,
            "base_checkpoint_path": (
                training_run.base_model_version.checkpoint_path
                if training_run.base_model_version
                else None
            ),
            "config": training_run.config,
            "classes": [],
        }

        for artifact_class in training_run.requested_classes.prefetch_related("images"):
            payload["classes"].append(
                {
                    "id": artifact_class.id,
                    "name": artifact_class.name,
                    "image_paths": [
                        image.image.path
                        for image in artifact_class.images.all()
                        if image.image
                    ],
                }
            )

        response = requests.post(
            _model_server_url("/api/internal/classifier/training-runs/start"),
            json=payload,
            headers=_internal_headers(),
            timeout=getattr(settings, "MODEL_SERVER_TIMEOUT_SECONDS", 10),
        )
        if response.status_code == status.HTTP_409_CONFLICT:
            raise ModelServerConflict(response.text)
        response.raise_for_status()
        return response.json()


class ClassifierModelVersionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ClassifierModelVersion.objects.select_related(
        "training_run",
        "base_version",
    ).all()
    serializer_class = ClassifierModelVersionSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"], url_path="promote")
    def promote(self, request, pk=None):
        model_version = self.get_object()
        if not model_version.checkpoint_path:
            return Response(
                {"detail": "Model version has no checkpoint path."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response = requests.post(
                _model_server_url("/api/internal/classifier/model-versions/reload"),
                json={
                    "model_version_id": model_version.id,
                    "checkpoint_path": model_version.checkpoint_path,
                },
                headers=_internal_headers(),
                timeout=getattr(settings, "MODEL_SERVER_TIMEOUT_SECONDS", 10),
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            return Response(
                {"detail": "Model server could not load the checkpoint.", "error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        with transaction.atomic():
            ClassifierModelVersion.objects.filter(is_active=True).exclude(id=model_version.id).update(
                is_active=False,
                status=ClassifierModelVersion.Status.RETIRED,
            )
            model_version.is_active = True
            model_version.status = ClassifierModelVersion.Status.ACTIVE
            model_version.promoted_by = request.user
            model_version.promoted_at = timezone.now()
            model_version.save(
                update_fields=["is_active", "status", "promoted_by", "promoted_at"]
            )

        serializer = self.get_serializer(model_version)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InternalTrainingRunStatusView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        if request.headers.get("X-Internal-API-Key") != _internal_api_key():
            return Response(
                {"detail": "Invalid internal API key."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            training_run = TrainingRun.objects.get(pk=pk)
        except TrainingRun.DoesNotExist:
            return Response(
                {"detail": "Training run not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")
        valid_statuses = {choice[0] for choice in TrainingRun.Status.choices}
        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Invalid status '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        training_run.status = new_status
        training_run.metrics = request.data.get("metrics", training_run.metrics)
        training_run.error_message = request.data.get("error_message", training_run.error_message)
        training_run.model_server_job_id = request.data.get(
            "job_id",
            training_run.model_server_job_id,
        )

        if new_status == TrainingRun.Status.RUNNING and not training_run.started_at:
            training_run.started_at = now
        if new_status in {TrainingRun.Status.SUCCEEDED, TrainingRun.Status.FAILED}:
            training_run.finished_at = now

        training_run.save()

        model_version = None
        if new_status == TrainingRun.Status.SUCCEEDED:
            model_version = self._record_model_version(training_run, request.data)

        return Response(
            {
                "training_run": TrainingRunSerializer(training_run).data,
                "model_version": (
                    ClassifierModelVersionSerializer(model_version).data if model_version else None
                ),
            },
            status=status.HTTP_200_OK,
        )

    def _record_model_version(self, training_run, payload):
        checkpoint_path = payload.get("checkpoint_path")
        class_names = payload.get("class_names") or []
        version = payload.get("version") or f"classifier-run-{training_run.id}"

        if not checkpoint_path:
            return None

        model_version, _ = ClassifierModelVersion.objects.update_or_create(
            training_run=training_run,
            defaults={
                "version": version,
                "checkpoint_path": checkpoint_path,
                "class_names": class_names,
                "metrics": payload.get("metrics") or {},
                "status": ClassifierModelVersion.Status.READY,
                "is_active": False,
                "base_version": training_run.base_model_version,
            },
        )
        return model_version
