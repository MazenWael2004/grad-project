from PIL import Image, UnidentifiedImageError

from django.conf import settings
from rest_framework import serializers

from .models import ClassifierClass, ClassifierModelVersion, TrainingImage, TrainingRun


class ClassifierClassSerializer(serializers.ModelSerializer):
    image_count = serializers.IntegerField(source="images.count", read_only=True)

    class Meta:
        model = ClassifierClass
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "image_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "image_count", "created_at", "updated_at"]


class TrainingImageSerializer(serializers.ModelSerializer):
    artifact_class_name = serializers.CharField(source="artifact_class.name", read_only=True)

    class Meta:
        model = TrainingImage
        fields = [
            "id",
            "artifact_class",
            "artifact_class_name",
            "image",
            "original_filename",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "artifact_class",
            "artifact_class_name",
            "original_filename",
            "created_at",
        ]


class TrainingImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, image):
        try:
            image.seek(0)
            with Image.open(image) as opened_image:
                opened_image.verify()
            image.seek(0)
        except (UnidentifiedImageError, OSError) as exc:
            raise serializers.ValidationError("Upload must be a valid image file.") from exc
        return image


class TrainingRunCreateSerializer(serializers.Serializer):
    class_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=False,
    )
    config = serializers.JSONField(required=False)

    def validate(self, attrs):
        min_images = getattr(settings, "CLASSIFIER_MIN_IMAGES_PER_CLASS", 15)
        class_ids = attrs.get("class_ids")

        queryset = ClassifierClass.objects.filter(is_active=True)
        if class_ids:
            queryset = queryset.filter(id__in=class_ids)
            found_ids = set(queryset.values_list("id", flat=True))
            missing_ids = set(class_ids) - found_ids
            if missing_ids:
                raise serializers.ValidationError(
                    {"class_ids": f"Unknown or inactive class ids: {sorted(missing_ids)}"}
                )

        classes = list(queryset)
        if not classes:
            raise serializers.ValidationError("At least one active classifier class is required.")

        underfilled = [
            artifact_class.name
            for artifact_class in classes
            if artifact_class.images.count() < min_images
        ]
        if underfilled:
            raise serializers.ValidationError(
                {
                    "class_ids": (
                        f"Each requested class needs at least {min_images} images. "
                        f"Underfilled classes: {', '.join(underfilled)}"
                    )
                }
            )

        attrs["classes"] = classes
        attrs["config"] = attrs.get("config") or {}
        return attrs


class TrainingRunSerializer(serializers.ModelSerializer):
    requested_classes = ClassifierClassSerializer(many=True, read_only=True)
    model_versions = serializers.SerializerMethodField()

    class Meta:
        model = TrainingRun
        fields = [
            "id",
            "status",
            "model_server_job_id",
            "requested_classes",
            "base_model_version",
            "config",
            "metrics",
            "error_message",
            "model_versions",
            "created_at",
            "started_at",
            "finished_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_model_versions(self, obj):
        return [
            {
                "id": version.id,
                "version": version.version,
                "is_active": version.is_active,
                "status": version.status,
                "checkpoint_path": version.checkpoint_path,
            }
            for version in obj.model_versions.all()
        ]


class ClassifierModelVersionSerializer(serializers.ModelSerializer):
    class_count = serializers.SerializerMethodField()

    class Meta:
        model = ClassifierModelVersion
        fields = [
            "id",
            "version",
            "checkpoint_path",
            "class_names",
            "class_count",
            "metrics",
            "status",
            "is_active",
            "training_run",
            "base_version",
            "created_at",
            "promoted_at",
        ]
        read_only_fields = fields

    def get_class_count(self, obj):
        return len(obj.class_names or [])
