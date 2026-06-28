from django.utils import timezone
from .models import Subscription

from apps.subscriptions.models import Subscription


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


def get_pending_subscription(user):
    return (
        Subscription.objects.filter(status="pending")
        .filter(members__user=user)
        .first()
    )
