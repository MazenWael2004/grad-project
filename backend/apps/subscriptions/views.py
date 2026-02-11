from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PlanSerializer
from .permissions import IsSubscribed, IsNotSubscribed
from .models import Subscription, SubscriptionMember, Plan


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
        subscription = (
            request.active_subscription
        )  # Provided by IsSubscribed permission
        subscription.status = "cancelled"
        subscription.save()

        return Response(
            {"message": "Subscription cancelled"}, status=status.HTTP_200_OK
        )
