from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MySubscriptionView,
    PlanListView,
    SubscribeView,
    UnsubscribeView,
    MemberViewSet,
)

router = DefaultRouter()
router.register(r"members", MemberViewSet, basename="members")

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="plan-list"),
    path("my-subscription/", MySubscriptionView.as_view(), name="my-subscription"),
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),

    # ViewSet routes
    path("", include(router.urls)),
]