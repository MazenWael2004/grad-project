from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from apps.accounts.models import User
from .models import Plan, Subscription, SubscriptionMember


class BaseSubscriptionSetup(APITestCase):
    def setUp(self):
        # User
        self.user = User.objects.create_user(
            email="test@test.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

        self.token = Token.objects.create(user=self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        # Plan
        self.plan = Plan.objects.create(
            name="Premium",
            price=100,
            max_users=5,
        )


class PlanTests(BaseSubscriptionSetup):
    def test_list_plans(self):
        response = self.client.get(reverse("plan-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Premium")


class SubscribeTests(BaseSubscriptionSetup):
    def test_subscribe_success(self):
        response = self.client.post(
            reverse("subscribe"),
            {"plan_id": self.plan.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UnsubscribeTests(BaseSubscriptionSetup):
    def setUp(self):
        super().setUp()

        self.other_user = User.objects.create_user(
            email="other@test.com",
            first_name="Jane",
            last_name="Doe",
            password="password123",
        )

        now = timezone.now()

        self.subscription = Subscription.objects.create(
            owner=self.other_user,
            plan=self.plan,
            status="active",
            start_date=now,
            end_date=now + timedelta(days=30),
        )

    def test_owner_unsubscribe_cancels_subscription(self):
        # make self.user the owner
        self.subscription.owner = self.user
        self.subscription.save()

        SubscriptionMember.objects.create(
            subscription=self.subscription,
            user=self.user,
        )

        response = self.client.post(reverse("unsubscribe"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, "cancelled")


    def test_member_unsubscribe_leaves_subscription(self):
        SubscriptionMember.objects.create(
            subscription=self.subscription,
            user=self.user,
        )

        response = self.client.post(reverse("unsubscribe"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # subscription should NOT be cancelled
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, "active")

        # member should be removed
        self.assertFalse(
            SubscriptionMember.objects.filter(
                subscription=self.subscription,
                user=self.user,
            ).exists()
        )


    def test_unsubscribe_requires_authentication(self):
        self.client.credentials()

        response = self.client.post(reverse("unsubscribe"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthTests(BaseSubscriptionSetup):
    def test_subscribe_requires_authentication(self):
        self.client.credentials()

        response = self.client.post(
            reverse("subscribe"),
            {"plan_id": self.plan.id},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)