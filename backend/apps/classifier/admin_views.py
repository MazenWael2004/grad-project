import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    ClassifierClassForm,
    ClassifierClassUpdateForm,
    ConfirmActionForm,
    PromoteModelVersionForm,
    TrainingImageUploadForm,
    TrainingRunStartForm,
)
from .models import ClassifierClass, ClassifierModelVersion, TrainingImage, TrainingRun


def _model_server_url(path):
    base_url = getattr(settings, "MODEL_SERVER_URL", "http://127.0.0.1:8001").rstrip("/")
    return f"{base_url}{path}"


def _internal_headers():
    return {
        "X-Internal-API-Key": getattr(
            settings,
            "CLASSIFIER_INTERNAL_API_KEY",
            "",
        )
    }


def _dashboard_context(training_form=None):
    classes = ClassifierClass.objects.prefetch_related("images").all()
    return {
        "title": "Classifier Dashboard",
        "active_model": ClassifierModelVersion.objects.filter(is_active=True).first(),
        "classes": classes,
        "class_count": classes.count(),
        "image_count": TrainingImage.objects.count(),
        "min_images": getattr(settings, "CLASSIFIER_MIN_IMAGES_PER_CLASS", 15),
        "latest_runs": TrainingRun.objects.prefetch_related("requested_classes").select_related(
            "base_model_version",
        )[:10],
        "ready_versions": ClassifierModelVersion.objects.filter(
            is_active=False,
            status=ClassifierModelVersion.Status.READY,
        ).select_related("training_run")[:10],
        "training_form": training_form or TrainingRunStartForm(),
        "confirm_form": ConfirmActionForm(),
    }


@staff_member_required
def dashboard(request):
    if request.method == "POST":
        return _start_training_from_request(request)
    return render(
        request,
        "classifier_admin/dashboard.html",
        _dashboard_context(),
    )


@staff_member_required
def class_create(request):
    if request.method == "POST":
        form = ClassifierClassForm(request.POST)
        if form.is_valid():
            artifact_class = form.save(commit=False)
            artifact_class.created_by = request.user
            artifact_class.save()
            messages.success(request, f"Class '{artifact_class.name}' created.")
            return redirect("classifier_admin:class_detail", pk=artifact_class.pk)
    else:
        form = ClassifierClassForm()

    return render(
        request,
        "classifier_admin/class_form.html",
        {
            "title": "New Class",
            "form": form,
        },
    )


@staff_member_required
def class_edit(request, pk):
    artifact_class = get_object_or_404(ClassifierClass, pk=pk)
    if request.method == "POST":
        form = ClassifierClassUpdateForm(request.POST, instance=artifact_class)
        if form.is_valid():
            form.save()
            messages.success(request, f"Class '{artifact_class.name}' updated.")
            return redirect("classifier_admin:class_detail", pk=artifact_class.pk)
    else:
        form = ClassifierClassUpdateForm(instance=artifact_class)

    return render(
        request,
        "classifier_admin/class_form.html",
        {
            "title": f"Edit {artifact_class.name}",
            "form": form,
            "artifact_class": artifact_class,
        },
    )


@staff_member_required
def class_delete(request, pk):
    artifact_class = get_object_or_404(ClassifierClass, pk=pk)
    if request.method != "POST":
        return redirect("classifier_admin:class_detail", pk=artifact_class.pk)

    form = ConfirmActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Class deletion was not confirmed.")
        return redirect("classifier_admin:class_detail", pk=artifact_class.pk)

    class_name = artifact_class.name
    artifact_class.delete()
    messages.success(request, f"Class '{class_name}' deleted.")
    return redirect("classifier_admin:dashboard")


@staff_member_required
def class_detail(request, pk):
    artifact_class = get_object_or_404(
        ClassifierClass.objects.prefetch_related("images"),
        pk=pk,
    )
    if request.method == "POST":
        upload_form = TrainingImageUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            uploaded_images = upload_form.cleaned_data["images"]
            for image in uploaded_images:
                TrainingImage.objects.create(
                    artifact_class=artifact_class,
                    image=image,
                    original_filename=image.name,
                    uploaded_by=request.user,
                )
            messages.success(
                request,
                f"Uploaded {len(uploaded_images)} image(s) for '{artifact_class.name}'.",
            )
            return redirect("classifier_admin:class_detail", pk=artifact_class.pk)
    else:
        upload_form = TrainingImageUploadForm()

    return render(
        request,
        "classifier_admin/class_detail.html",
        {
            "title": artifact_class.name,
            "artifact_class": artifact_class,
            "upload_form": upload_form,
            "min_images": getattr(settings, "CLASSIFIER_MIN_IMAGES_PER_CLASS", 15),
            "recent_images": artifact_class.images.all()[:24],
            "confirm_form": ConfirmActionForm(),
        },
    )


@staff_member_required
def image_delete(request, pk):
    image = get_object_or_404(TrainingImage.objects.select_related("artifact_class"), pk=pk)
    class_pk = image.artifact_class_id
    if request.method != "POST":
        return redirect("classifier_admin:class_detail", pk=class_pk)

    form = ConfirmActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Image deletion was not confirmed.")
        return redirect("classifier_admin:class_detail", pk=class_pk)

    image.delete()
    messages.success(request, "Training image deleted.")
    return redirect("classifier_admin:class_detail", pk=class_pk)


@staff_member_required
def start_training(request):
    if request.method != "POST":
        return redirect("classifier_admin:dashboard")
    return _start_training_from_request(request)


def _start_training_from_request(request):
    form = TrainingRunStartForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Training run was not started.")
        return render(
            request,
            "classifier_admin/dashboard.html",
            _dashboard_context(training_form=form),
            status=400,
        )

    training_run = TrainingRun.objects.create(
        base_model_version=ClassifierModelVersion.objects.filter(is_active=True).first(),
        config=form.training_config(),
        created_by=request.user,
    )
    training_run.requested_classes.set(form.cleaned_data["classes"])

    try:
        response_data = _start_model_server_training(training_run)
    except requests.RequestException as exc:
        training_run.status = TrainingRun.Status.FAILED
        training_run.error_message = str(exc)
        training_run.finished_at = timezone.now()
        training_run.save(update_fields=["status", "error_message", "finished_at", "updated_at"])
        messages.error(request, "Unable to reach classifier model server.")
        return redirect("classifier_admin:training_run_detail", pk=training_run.pk)

    training_run.status = response_data.get("status", TrainingRun.Status.QUEUED)
    training_run.model_server_job_id = response_data.get("job_id", "")
    training_run.save(update_fields=["status", "model_server_job_id", "updated_at"])
    messages.success(request, f"Training run #{training_run.pk} started.")
    return redirect("classifier_admin:training_run_detail", pk=training_run.pk)


def _start_model_server_training(training_run):
    payload = {
        "run_id": training_run.id,
        "base_model_version_id": training_run.base_model_version_id,
        "base_checkpoint_path": (
            training_run.base_model_version.checkpoint_path
            if training_run.base_model_version
            else None
        ),
        "config": training_run.config,
        "classes": [
            {
                "id": artifact_class.id,
                "name": artifact_class.name,
                "image_paths": [
                    image.image.path
                    for image in artifact_class.images.all()
                    if image.image
                ],
            }
            for artifact_class in training_run.requested_classes.prefetch_related("images")
        ],
    }
    response = requests.post(
        _model_server_url("/api/internal/classifier/training-runs/start"),
        json=payload,
        headers=_internal_headers(),
        timeout=getattr(settings, "MODEL_SERVER_TIMEOUT_SECONDS", 10),
    )
    if response.status_code == 409:
        training_run.status = TrainingRun.Status.FAILED
        training_run.error_message = response.text
        training_run.finished_at = timezone.now()
        training_run.save(update_fields=["status", "error_message", "finished_at", "updated_at"])
    response.raise_for_status()
    return response.json()


@staff_member_required
def training_run_detail(request, pk):
    training_run = get_object_or_404(
        TrainingRun.objects.prefetch_related("requested_classes", "model_versions"),
        pk=pk,
    )
    return render(
        request,
        "classifier_admin/training_run_detail.html",
        {
            "title": f"Training Run #{training_run.pk}",
            "training_run": training_run,
            "model_version": training_run.model_versions.first(),
            "promote_form": PromoteModelVersionForm(),
            "confirm_form": ConfirmActionForm(),
        },
    )


@staff_member_required
def training_status_fragment(request, pk):
    training_run = get_object_or_404(
        TrainingRun.objects.prefetch_related("model_versions"),
        pk=pk,
    )
    return render(
        request,
        "classifier_admin/_training_status.html",
        {
            "training_run": training_run,
            "model_version": training_run.model_versions.first(),
            "promote_form": PromoteModelVersionForm(),
            "confirm_form": ConfirmActionForm(),
        },
    )


@staff_member_required
def training_run_delete(request, pk):
    training_run = get_object_or_404(
        TrainingRun.objects.prefetch_related("model_versions"),
        pk=pk,
    )
    if request.method != "POST":
        return redirect("classifier_admin:training_run_detail", pk=training_run.pk)

    form = ConfirmActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Training run deletion was not confirmed.")
        return redirect("classifier_admin:training_run_detail", pk=training_run.pk)

    if training_run.model_versions.filter(is_active=True).exists():
        messages.error(request, "Cannot delete a training run linked to the active model.")
        return redirect("classifier_admin:training_run_detail", pk=training_run.pk)

    run_id = training_run.pk
    training_run.delete()
    messages.success(request, f"Training run #{run_id} deleted.")
    return redirect("classifier_admin:dashboard")


@staff_member_required
def promote_model_version(request, pk):
    model_version = get_object_or_404(ClassifierModelVersion, pk=pk)
    redirect_url = _model_version_redirect_url(model_version)
    if request.method != "POST":
        return redirect(redirect_url)

    form = PromoteModelVersionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Promotion was not confirmed.")
        return redirect(redirect_url)

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
        messages.error(request, f"Model server could not load the checkpoint: {exc}")
        return redirect(redirect_url)

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

    messages.success(request, f"Model version '{model_version.version}' promoted.")
    return redirect(redirect_url)


@staff_member_required
def retire_model_version(request, pk):
    model_version = get_object_or_404(ClassifierModelVersion, pk=pk)
    redirect_url = _model_version_redirect_url(model_version)
    if request.method != "POST":
        return redirect(redirect_url)

    form = ConfirmActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Model retirement was not confirmed.")
        return redirect(redirect_url)

    if model_version.is_active:
        messages.error(request, "Cannot retire the active model. Promote another version first.")
        return redirect(redirect_url)

    model_version.status = ClassifierModelVersion.Status.RETIRED
    model_version.save(update_fields=["status"])
    messages.success(request, f"Model version '{model_version.version}' retired.")
    return redirect(redirect_url)


@staff_member_required
def delete_model_version(request, pk):
    model_version = get_object_or_404(ClassifierModelVersion, pk=pk)
    redirect_url = _model_version_redirect_url(model_version)
    if request.method != "POST":
        return redirect(redirect_url)

    form = ConfirmActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Model version deletion was not confirmed.")
        return redirect(redirect_url)

    if model_version.is_active:
        messages.error(request, "Cannot delete the active model version.")
        return redirect(redirect_url)

    version_name = model_version.version
    model_version.delete()
    messages.success(request, f"Model version '{version_name}' deleted.")
    return redirect("classifier_admin:dashboard")


def _model_version_redirect_url(model_version):
    if model_version.training_run_id:
        return reverse("classifier_admin:training_run_detail", args=[model_version.training_run_id])
    return reverse("classifier_admin:dashboard")
