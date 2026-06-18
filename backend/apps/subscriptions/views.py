from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied
from rest_framework.decorators import action
from .serializers import PlanSerializer
from .permissions import (
    IsSubscribed,
    IsNotSubscribed,
    IsSubscriptionOwner,
    get_active_subscription,
)
from .models import Subscription, SubscriptionMember, Plan
from apps.accounts.models import User


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class MySubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        subscription = get_active_subscription(user)
        if subscription:
            plan = subscription.plan
            serializer = PlanSerializer(plan)
            members = subscription.members.count()
            is_owner = subscription.owner == user
            return Response(
                {"plan": serializer.data, "is_owner": is_owner, "members": members},
                status=status.HTTP_200_OK,
            )
        return Response({"plan": None}, status=status.HTTP_200_OK)


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


class MemberViewSet(viewsets.ViewSet):
    permission_classes = [IsSubscriptionOwner]

    def list(self, request):
        subscription = request.active_subscription

        members = subscription.members.values_list(
            "user__email",
            flat=True,
        )

        return Response({"members": list(members)})

    def create(self, request):
        subscription = request.active_subscription
        email = request.data.get("user_email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if get_active_subscription(user):
            return Response(
                {"error": "User already has an active subscription"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if subscription.members.count() >= subscription.plan.max_users:
            return Response(
                {"error": "Subscription limit reached"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        SubscriptionMember.objects.create(
            subscription=subscription,
            user=user,
        )

        return Response(
            {"message": "Member added"},
            status=status.HTTP_201_CREATED,
        )
    @action(detail=False, methods=["delete"])
    def remove(self, request):
        subscription = request.active_subscription
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"error": "email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if email == subscription.owner.email:
            return Response(
                {"error": "Cannot remove owner"}, status=status.HTTP_403_FORBIDDEN
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        deleted, _ = SubscriptionMember.objects.filter(
            subscription=subscription,
            user=user,
        ).delete()

        if not deleted:
            return Response(
                {"error": "User is not a member"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Member removed"},
            status=status.HTTP_200_OK,
        )
