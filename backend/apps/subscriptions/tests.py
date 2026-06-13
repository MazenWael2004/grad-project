from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from apps.accounts.models import User
from .models import Plan, Subscription, SubscriptionMember

class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

        self.token = Token.objects.create(user=self.user)

        self.plan = Plan.objects.create(
            name="Premium",
            price=100,
            max_users=5,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

    # --------------------
    # Plan List
    # --------------------

    def test_list_plans(self):
        response = self.client.get(reverse("plan-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Premium")

    # --------------------
    # Subscribe
    # --------------------

    def test_subscribe_success(self):
        response = self.client.post(
            reverse("subscribe"),
            {"plan_id": self.plan.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Subscription.objects.filter(owner=self.user).exists()
        )

        subscription = Subscription.objects.get(owner=self.user)

        self.assertEqual(subscription.plan, self.plan)
        self.assertEqual(subscription.status, "active")

        self.assertTrue(
            SubscriptionMember.objects.filter(
                subscription=subscription,
                user=self.user,
            ).exists()
        )

    def test_subscribe_invalid_plan(self):
        response = self.client.post(
            reverse("subscribe"),
            {"plan_id": 9999},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_subscribe_when_already_subscribed(self):
        now = timezone.now()

        subscription = Subscription.objects.create(
            owner=self.user,
            plan=self.plan,
            status="active",
            start_date=now,
            end_date=now + timedelta(days=30),
        )

        SubscriptionMember.objects.create(
            subscription=subscription,
            user=self.user,
        )

        response = self.client.post(
            reverse("subscribe"),
            {"plan_id": self.plan.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # --------------------
    # Unsubscribe
    # --------------------

    def test_unsubscribe_success(self):
        now = timezone.now()

        subscription = Subscription.objects.create(
            owner=self.user,
            plan=self.plan,
            status="active",
            start_date=now,
            end_date=now + timedelta(days=30),
        )

        SubscriptionMember.objects.create(
            subscription=subscription,
            user=self.user,
        )

        response = self.client.post(reverse("unsubscribe"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subscription.refresh_from_db()
        self.assertEqual(subscription.status, "cancelled")

    def test_unsubscribe_without_subscription(self):
        response = self.client.post(reverse("unsubscribe"))

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # --------------------
    # Authentication
    # --------------------

    def test_subscribe_requires_authentication(self):
        self.client.credentials()

        response = self.client.post(
            reverse("subscribe"),
            {"plan_id": self.plan.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unsubscribe_requires_authentication(self):
        self.client.credentials()

        response = self.client.post(reverse("unsubscribe"))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )