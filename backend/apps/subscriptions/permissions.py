from django.utils import timezone
from .models import Subscription
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


def get_active_subscription(user):
    """
    Returns the user's active subscription if exists, otherwise None.
    """
    now = timezone.now()
    return (
        Subscription.objects.filter(
            status="active", start_date__lte=now, end_date__gte=now
        )
        .filter(members__user=user)
        .first()
    )


class IsSubscribed(permissions.IsAuthenticated):
    """
    Allows access only to users with an active subscription.
    Attaches the subscription instance to request.active_subscription
    """

    message = "You must have an active subscription to access this endpoint."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user = request.user
        subscription = get_active_subscription(user)
        if subscription is None:
            raise PermissionDenied(self.message)
        request.active_subscription = subscription
        return True


class IsNotSubscribed(permissions.IsAuthenticated):
    """
    Allows access only to users without an active subscription.
    """

    message = "You already have an active subscription."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user = request.user
        subscription = get_active_subscription(user)
        if subscription:
            raise PermissionDenied(self.message)
        return True


class IsSubscriptionOwner(IsSubscribed):
    """
    Allows access only to users who own an active subscription.
    Attaches the subscription instance to request.active_subscription.
    """

    message = "You must own an active subscription to access this endpoint."

    def has_permission(self, request, view):
        # Ensures the user is authenticated and has an active subscription.
        if not super().has_permission(request, view):
            return False

        if request.active_subscription.owner != request.user:
            raise PermissionDenied(self.message)

        return True