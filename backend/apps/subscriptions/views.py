from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied
from rest_framework.decorators import action

from apps.subscriptions.helpers import (
    get_active_subscription,
    get_pending_subscription,
    has_active_subscription,
)
from core import serializers
from .serializers import PaymentMethodSerializer, PlanSerializer
from .permissions import (
    IsSubscribed,
    IsNotSubscribed,
    IsSubscriptionOwner,
)
from .models import PaymentMethod, Subscription, SubscriptionMember, Plan
from apps.accounts.models import User
from rest_framework.exceptions import ValidationError

from dateutil.relativedelta import relativedelta


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class MySubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        subscription = get_active_subscription(user) or get_pending_subscription(user)
        if subscription:
            plan = subscription.plan
            serializer = PlanSerializer(plan)
            members = subscription.members.count()
            is_owner = subscription.owner == user
            return Response(
                {
                    "plan": serializer.data,
                    "status": subscription.status,
                    "is_owner": is_owner,
                    "members": members,
                    "start_date": subscription.start_date,
                    "end_date": subscription.end_date,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"plan": None}, status=status.HTTP_200_OK)


class SubscribeView(APIView):
    permission_classes = [IsNotSubscribed]

    def post(self, request):
        plan_id = request.data.get("plan_id")
        user = request.user
        if get_pending_subscription(user):
            return Response(
                {"error": "You already have a pending subscription."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response(
                {"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND
            )

        subscription = Subscription.objects.create(
            plan=plan, owner=user, status="pending"
        )
        SubscriptionMember.objects.create(subscription=subscription, user=user)

        return Response(
            {
                "message": "Subscription created",
                "subscription_id": subscription.id,
                "plan": plan.name,
            },
            status=status.HTTP_201_CREATED,
        )


class CancelPendingSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        subscription = get_pending_subscription(user)

        if not subscription:
            return Response(
                {"error": "No pending subscription found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        subscription.members.all().delete()
        subscription.status = "canceled"
        subscription.save()

        return Response(
            {"message": "Pending subscription cancelled."},
            status=status.HTTP_200_OK,
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

        if get_pending_subscription(user):
            return Response(
                {"error": "User already has a pending subscription"},
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


class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.payment_methods.count() >= 3:
            raise ValidationError({"error": "You can have at most 3 payment methods."})

        serializer.save(user=self.request.user)


class PayPendingSubscriptionView(APIView):
    permission_classes = [IsNotSubscribed]

    def post(self, request):
        user = request.user

        payment_method_id = request.data.get("payment_method_id")
        cvv = request.data.get("cvv")

        if not payment_method_id or not cvv:
            return Response(
                {"error": "payment_method_id and cvv are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment_method = PaymentMethod.objects.get(
                id=payment_method_id,
                user=user,
            )
        except PaymentMethod.DoesNotExist:
            return Response(
                {"error": "Payment method not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        subscription = get_pending_subscription(user)

        if not subscription:
            return Response(
                {"error": "No pending subscription found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ---- FAKE PAYMENT LOGIC (TEST ONLY) ----
        cvv = request.data.get("cvv")

        if cvv == "100":
            subscription.status = "active"
            subscription.start_date = timezone.now()
            subscription.end_date = subscription.start_date + relativedelta(
                months=subscription.plan.duration_months
            )
            subscription.save()

            return Response(
                {"message": "Payment successful"},
                status=status.HTTP_200_OK,
            )

        elif cvv == "200":
            return Response(
                {"error": "Insufficient funds"},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        else:
            return Response(
                {"error": "Invalid CVV"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class IsSubscribedView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        has_subscription = has_active_subscription(request.user)
        return Response(
            {
                "subscribed": has_subscription,
            },
            status=status.HTTP_200_OK,
        )
