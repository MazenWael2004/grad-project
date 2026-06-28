from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    IsSubscribedView,
    MySubscriptionView,
    PayPendingSubscriptionView,
    PaymentMethodViewSet,
    PlanListView,
    SubscribeView,
    UnsubscribeView,
    MemberViewSet,
)

router = DefaultRouter()
router.register(r"members", MemberViewSet, basename="members")
router.register(
    r"payment-methods",
    PaymentMethodViewSet,
    basename="payment-methods",
)
urlpatterns = [
    path("plans/", PlanListView.as_view(), name="plan-list"),
    path("my-subscription/", MySubscriptionView.as_view(), name="my-subscription"),
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
    path(
        "pay-subscription/",
        PayPendingSubscriptionView.as_view(),
        name="pay-subscription",
    ),
    path(
        "is-subscribed/",
        IsSubscribedView.as_view(),
        name="is-subscribed",
    ),
    # ViewSet routes
    path("", include(router.urls)),
]
