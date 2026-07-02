from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ClassifierClassViewSet,
    ClassifierModelVersionViewSet,
    InternalTrainingRunStatusView,
    TrainingRunViewSet,
)

router = DefaultRouter()
router.register(r"classes", ClassifierClassViewSet, basename="classifier-classes")
router.register(r"training-runs", TrainingRunViewSet, basename="classifier-training-runs")
router.register(r"model-versions", ClassifierModelVersionViewSet, basename="classifier-model-versions")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "internal/training-runs/<int:pk>/status/",
        InternalTrainingRunStatusView.as_view(),
        name="classifier-training-run-status",
    ),
]
