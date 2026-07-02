from django.urls import path

from . import admin_views

app_name = "classifier_admin"

urlpatterns = [
    path("", admin_views.dashboard, name="dashboard"),
    path("classes/new/", admin_views.class_create, name="class_create"),
    path("classes/<int:pk>/", admin_views.class_detail, name="class_detail"),
    path("classes/<int:pk>/edit/", admin_views.class_edit, name="class_edit"),
    path("classes/<int:pk>/delete/", admin_views.class_delete, name="class_delete"),
    path("images/<int:pk>/delete/", admin_views.image_delete, name="image_delete"),
    path("training-runs/start/", admin_views.start_training, name="start_training"),
    path("training-runs/<int:pk>/", admin_views.training_run_detail, name="training_run_detail"),
    path(
        "training-runs/<int:pk>/delete/",
        admin_views.training_run_delete,
        name="training_run_delete",
    ),
    path(
        "training-runs/<int:pk>/status-fragment/",
        admin_views.training_status_fragment,
        name="training_status_fragment",
    ),
    path(
        "model-versions/<int:pk>/promote/",
        admin_views.promote_model_version,
        name="promote_model_version",
    ),
    path(
        "model-versions/<int:pk>/retire/",
        admin_views.retire_model_version,
        name="retire_model_version",
    ),
    path(
        "model-versions/<int:pk>/delete/",
        admin_views.delete_model_version,
        name="delete_model_version",
    ),
]
