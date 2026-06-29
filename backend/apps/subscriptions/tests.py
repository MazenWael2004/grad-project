from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from .models import PaymentMethod, Plan, Subscription, SubscriptionMember


class BaseSubscriptionSetup(APITestCase):
    def setUp(self):
        # User
        self.user = User.objects.create_user(
            email="test@test.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

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
        self.assertEqual(subscription.status, "pending")

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

    def test_subscribe_after_cancelled_subscription(self):
        now = timezone.now()

        old_subscription = Subscription.objects.create(
            owner=self.user,
            plan=self.plan,
            status="cancelled",
            start_date=now - timedelta(days=30),
            end_date=now,
        )

        SubscriptionMember.objects.create(
            subscription=old_subscription,
            user=self.user,
        )

        response = self.client.post(
            reverse("subscribe"),
            {"plan_id": self.plan.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_subscription = Subscription.objects.exclude(id=old_subscription.id).get(
            owner=self.user
        )

        self.assertEqual(new_subscription.plan, self.plan)
        self.assertEqual(new_subscription.status, "pending")

        self.assertTrue(
            SubscriptionMember.objects.filter(
                subscription=new_subscription,
                user=self.user,
            ).exists()
        )


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


class MemberTests(BaseSubscriptionSetup):
    def setUp(self):
        super().setUp()

        self.member = User.objects.create_user(
            email="member@test.com",
            first_name="Member",
            last_name="User",
            password="password123",
        )

        now = timezone.now()

        self.subscription = Subscription.objects.create(
            owner=self.user,
            plan=self.plan,
            status="active",
            start_date=now,
            end_date=now + timedelta(days=30),
        )

        SubscriptionMember.objects.create(
            subscription=self.subscription,
            user=self.user,
        )

    def test_owner_can_add_member(self):
        response = self.client.post(
            reverse("members-list"),
            {"user_email": self.member.email},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            SubscriptionMember.objects.filter(
                subscription=self.subscription,
                user=self.member,
            ).exists()
        )

    def test_add_nonexistent_user(self):
        response = self.client.post(
            reverse("members-list"),
            {"user_email": "missing@test.com"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_non_owner_cannot_add_member(self):
        other_user = User.objects.create_user(
            email="other@test.com",
            first_name="Other",
            last_name="User",
            password="password123",
        )

        SubscriptionMember.objects.create(
            subscription=self.subscription,
            user=other_user,
        )

        refresh = RefreshToken.for_user(other_user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(
            reverse("members-list"),
            {"user_email": self.member.email},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_cannot_add_user_already_subscribed(self):

        other_subscription = Subscription.objects.create(
            owner=self.member,
            plan=self.plan,
            status="active",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
        )

        SubscriptionMember.objects.create(
            subscription=other_subscription,
            user=self.member,
        )

        response = self.client.post(
            reverse("members-list"),
            {"user_email": self.member.email},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_add_member_when_subscription_is_full(self):
        self.plan.max_users = 1
        self.plan.save()

        response = self.client.post(
            reverse("members-list"),
            {"user_email": self.member.email},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_list_members(self):
        response = self.client.get(reverse("members-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(
            self.user.email,
            response.data["members"],
        )

    def test_remove_member_success(self):

        SubscriptionMember.objects.create(
            subscription=self.subscription,
            user=self.member,
        )
        response = self.client.delete(
            reverse("members-remove") + f"?email={self.member.email}",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            SubscriptionMember.objects.filter(
                subscription=self.subscription,
                user=self.member,
            ).exists()
        )

    def test_remove_non_member(self):
        response = self.client.delete(
            reverse("members-remove") + f"?email=notfound@test.com",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_remove_owner(self):
        response = self.client.delete(
            reverse("members-remove") + f"?email={self.user.email}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class MySubscriptionTests(BaseSubscriptionSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse("my-subscription")

    def test_no_subscription(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"plan": None})

    def test_owner_subscription(self):
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

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["plan"]["id"], self.plan.id)
        self.assertEqual(response.data["plan"]["name"], self.plan.name)
        self.assertEqual(response.data["plan"]["price"], "100.00")
        self.assertEqual(response.data["plan"]["max_users"], 5)

        self.assertTrue(response.data["is_owner"])
        self.assertEqual(response.data["members"], 1)

    def test_member_subscription(self):
        owner = User.objects.create_user(
            email="owner@test.com",
            first_name="Owner",
            last_name="User",
            password="password123",
        )

        now = timezone.now()

        subscription = Subscription.objects.create(
            owner=owner,
            plan=self.plan,
            status="active",
            start_date=now,
            end_date=now + timedelta(days=30),
        )

        SubscriptionMember.objects.create(
            subscription=subscription,
            user=owner,
        )

        SubscriptionMember.objects.create(
            subscription=subscription,
            user=self.user,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["plan"]["id"], self.plan.id)
        self.assertFalse(response.data["is_owner"])

        # owner + current user
        self.assertEqual(response.data["members"], 2)


class PaymentMethodTests(BaseSubscriptionSetup):

    def test_create_payment_method(self):
        response = self.client.post(
            reverse("payment-methods-list"),
            {
                "card_holder_name": "John Doe",
                "card_number": "4111111111111111",
                "expiration_month": 12,
                "expiration_year": 2030,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            PaymentMethod.objects.filter(
                user=self.user,
                card_number="4111111111111111",
            ).exists()
        )

    def test_list_payment_methods(self):
        PaymentMethod.objects.create(
            user=self.user,
            card_holder_name="John Doe",
            card_number="4111111111111111",
            expiration_month=12,
            expiration_year=2030,
        )

        response = self.client.get(reverse("payment-methods-list"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["card_holder_name"],
            "John Doe",
        )

    def test_delete_payment_method(self):
        payment_method = PaymentMethod.objects.create(
            user=self.user,
            card_holder_name="John Doe",
            card_number="4111111111111111",
            expiration_month=12,
            expiration_year=2030,
        )

        response = self.client.delete(
            reverse(
                "payment-methods-detail",
                args=[payment_method.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(PaymentMethod.objects.filter(id=payment_method.id).exists())

    def test_cannot_create_more_than_three_payment_methods(self):
        # Create 3 existing payment methods
        for i in range(3):
            PaymentMethod.objects.create(
                user=self.user,
                card_holder_name=f"User {i}",
                card_number=f"41111111111111{i}",
                expiration_month=12,
                expiration_year=2030,
            )

        response = self.client.post(
            reverse("payment-methods-list"),
            {
                "card_holder_name": "Extra Card",
                "card_number": "4111111111119999",
                "expiration_month": 12,
                "expiration_year": 2030,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            PaymentMethod.objects.filter(user=self.user).count(),
            3,
        )

    def test_cannot_delete_other_users_payment_method(self):
        other_user = User.objects.create_user(
            email="other@test.com",
            first_name="Other",
            last_name="User",
            password="password123",
        )

        other_payment_method = PaymentMethod.objects.create(
            user=other_user,
            card_holder_name="Other User",
            card_number="4111111111111111",
            expiration_month=12,
            expiration_year=2030,
        )

        response = self.client.delete(
            reverse(
                "payment-methods-detail",
                args=[other_payment_method.id],
            )
        )

        # Because queryset is filtered by user, DRF returns 404 (not 403)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            PaymentMethod.objects.filter(id=other_payment_method.id).exists()
        )


class PaySubscriptionTests(BaseSubscriptionSetup):

    def setUp(self):
        super().setUp()

        # Create payment method for user
        self.payment_method = PaymentMethod.objects.create(
            user=self.user,
            card_holder_name="John Doe",
            card_number="4111111111111111",
            expiration_month=12,
            expiration_year=2030,
        )

    def test_no_pending_subscription(self):
        response = self.client.post(
            reverse("pay-subscription"),
            {
                "payment_method_id": self.payment_method.id,
                "cvv": "100",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_method_not_found(self):
        subscription = Subscription.objects.create(
            owner=self.user,
            plan=self.plan,
            status="pending",
        )
        SubscriptionMember.objects.create(
            subscription=subscription,
            user=self.user,
        )
        response = self.client.post(
            reverse("pay-subscription"),
            {
                "payment_method_id": 9999,
                "cvv": "100",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_failed_wrong_cvv(self):
        subscription = Subscription.objects.create(
            owner=self.user,
            plan=self.plan,
            status="pending",
        )
        SubscriptionMember.objects.create(
            subscription=subscription,
            user=self.user,
        )
        response = self.client.post(
            reverse("pay-subscription"),
            {
                "payment_method_id": self.payment_method.id,
                "cvv": "999",  # wrong CVV
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_failed_insufficient_fund(self):
        subscription = Subscription.objects.create(
            owner=self.user,
            plan=self.plan,
            status="pending",
        )
        SubscriptionMember.objects.create(
            subscription=subscription,
            user=self.user,
        )

        response = self.client.post(
            reverse("pay-subscription"),
            {
                "payment_method_id": self.payment_method.id,
                "cvv": "200",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(response.data["error"], "Insufficient funds")

    def test_payment_success(self):
        subscription = Subscription.objects.create(
            owner=self.user,
            plan=self.plan,
            status="pending",
        )
        SubscriptionMember.objects.create(
            subscription=subscription,
            user=self.user,
        )
        response = self.client.post(
            reverse("pay-subscription"),
            {
                "payment_method_id": self.payment_method.id,
                "cvv": "100",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subscription.refresh_from_db()

        self.assertEqual(subscription.status, "active")
        self.assertIsNotNone(subscription.start_date)
        self.assertIsNotNone(subscription.end_date)
