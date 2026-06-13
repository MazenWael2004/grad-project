from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied
from .serializers import PlanSerializer
from .permissions import IsSubscribed, IsNotSubscribed, get_active_subscription
from .models import Subscription, SubscriptionMember, Plan
from apps.accounts.models import User

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscribeView(APIView):
    permission_classes = [IsNotSubscribed]

    def post(self, request):
        plan_id = request.data.get("plan_id")
        user = request.user

        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response(
                {"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND
            )

        now = timezone.now()
        end_date = now + timedelta(days=30)  # 1 month subscription

        subscription = Subscription.objects.create(
            plan=plan, owner=user, status="active", start_date=now, end_date=end_date
        )
        SubscriptionMember.objects.create(subscription=subscription, user=user)

        return Response(
            {
                "message": "Subscription created",
                "subscription_id": subscription.id,
                "plan": plan.name,
                "start_date": now,
                "end_date": end_date,
            },
            status=status.HTTP_201_CREATED,
        )


class UnsubscribeView(APIView):
    permission_classes = [IsSubscribed]

    def post(self, request):
        subscription = request.active_subscription
        user = request.user

        # CASE 1: OWNER cancels
        if subscription.owner == user:
            subscription.status = "cancelled"
            subscription.save()
            # Remove Members
            SubscriptionMember.objects.filter(subscription=subscription).delete()

            return Response(
                {"message": "Subscription cancelled by owner"},
                status=status.HTTP_200_OK,
            )

        # CASE 2: MEMBER leaves
        removed, _ = SubscriptionMember.objects.filter(
            subscription=subscription,
            user=user,
        ).delete()

        if removed == 0:
            return Response(
                {"error": "User is not a member"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "You left the subscription"},
            status=status.HTTP_200_OK,
        )

class AddMemberView(APIView):
    permission_classes = [IsSubscribed]

    def post(self, request):
        subscription = request.active_subscription

        # Only owner can add members
        if subscription.owner != request.user:
            raise PermissionDenied(
                "Only the subscription owner can add members."
            )

        user_email = request.data.get("user_email")

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # User already belongs to a subscription
        if get_active_subscription(user):
            return Response(
                {"error": "User already has an active subscription"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Capacity check
        current_members = subscription.members.count()

        if current_members >= subscription.plan.max_users:
            return Response(
                {"error": "Subscription has reached its member limit"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        SubscriptionMember.objects.create(
            subscription=subscription,
            user=user,
        )

        return Response(
            {"message": "Member added successfully"},
            status=status.HTTP_201_CREATED,)