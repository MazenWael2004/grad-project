from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def training_image_upload_to(instance, filename):
    class_slug = slugify(instance.artifact_class.name) or "class"
    return f"classifier/training-images/{class_slug}/{filename}"


class ClassifierClass(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_classifier_classes",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TrainingImage(models.Model):
    artifact_class = models.ForeignKey(
        ClassifierClass,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=training_image_upload_to)
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_classifier_images",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.artifact_class.name}: {self.original_filename or self.image.name}"


class TrainingRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    requested_classes = models.ManyToManyField(
        ClassifierClass,
        related_name="training_runs",
        blank=True,
    )
    base_model_version = models.ForeignKey(
        "ClassifierModelVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_training_runs",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    model_server_job_id = models.CharField(max_length=120, blank=True)
    config = models.JSONField(default=dict, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classifier_training_runs",
    )
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Training run #{self.pk} ({self.status})"


class ClassifierModelVersion(models.Model):
    class Status(models.TextChoices):
        READY = "ready", "Ready"
        ACTIVE = "active", "Active"
        RETIRED = "retired", "Retired"
        FAILED = "failed", "Failed"

    version = models.CharField(max_length=120, unique=True)
    checkpoint_path = models.CharField(max_length=1000)
    class_names = models.JSONField(default=list, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.READY,
    )
    is_active = models.BooleanField(default=False)
    training_run = models.ForeignKey(
        TrainingRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="model_versions",
    )
    base_version = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_versions",
    )
    created_at = models.DateTimeField(default=timezone.now)
    promoted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promoted_classifier_versions",
    )
    promoted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        active = " active" if self.is_active else ""
        return f"{self.version}{active}"
