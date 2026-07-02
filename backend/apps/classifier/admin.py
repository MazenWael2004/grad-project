from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    ClassifierClass,
    ClassifierModelVersion,
    TrainingImage,
    TrainingRun,
)


class TrainingImageInline(admin.TabularInline):
    model = TrainingImage
    extra = 0
    readonly_fields = ("original_filename", "uploaded_by", "created_at")


@admin.register(ClassifierClass)
class ClassifierClassAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "image_count",
        "created_by",
        "created_at",
        "dashboard_link",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    inlines = [TrainingImageInline]

    def image_count(self, obj):
        return obj.images.count()

    def dashboard_link(self, obj):
        url = reverse("classifier_admin:class_detail", args=[obj.pk])
        return format_html('<a href="{}">Open dashboard</a>', url)


@admin.register(TrainingImage)
class TrainingImageAdmin(admin.ModelAdmin):
    list_display = ("artifact_class", "original_filename", "uploaded_by", "created_at")
    list_filter = ("artifact_class", "created_at")
    search_fields = ("artifact_class__name", "original_filename")


@admin.register(TrainingRun)
class TrainingRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "model_server_job_id",
        "created_by",
        "created_at",
        "started_at",
        "finished_at",
        "dashboard_link",
    )
    list_filter = ("status", "created_at")
    search_fields = ("model_server_job_id", "error_message")
    readonly_fields = ("metrics", "error_message", "created_at", "updated_at")
    filter_horizontal = ("requested_classes",)

    def dashboard_link(self, obj):
        url = reverse("classifier_admin:training_run_detail", args=[obj.pk])
        return format_html('<a href="{}">Open dashboard</a>', url)


@admin.register(ClassifierModelVersion)
class ClassifierModelVersionAdmin(admin.ModelAdmin):
    list_display = (
        "version",
        "status",
        "is_active",
        "training_run",
        "created_at",
        "promoted_at",
        "dashboard_link",
    )
    list_filter = ("status", "is_active", "created_at")
    search_fields = ("version", "checkpoint_path")
    readonly_fields = ("class_names", "metrics", "created_at", "promoted_at")

    def dashboard_link(self, obj):
        if obj.training_run_id:
            url = reverse("classifier_admin:training_run_detail", args=[obj.training_run_id])
        else:
            url = reverse("classifier_admin:dashboard")
        return format_html('<a href="{}">Open dashboard</a>', url)
