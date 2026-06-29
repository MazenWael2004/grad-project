from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("register")

    def test_register_success(self):
        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_register_existing_email(self):
        User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_missing_fields(self):
        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("login")

        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

    def test_login_success(self):
        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        self.assertEqual(
            response.data["user"]["email"],
            "test@example.com",
        )

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "password": "wrong_password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("logout")

        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def test_logout_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_invalid_refresh_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(
            self.url,
            {"refresh": "invalid-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class TokenRefreshTests(APITestCase):
    def setUp(self):
        self.url = reverse("token_refresh")

        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)

    def test_refresh_token_success(self):
        response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_invalid(self):
        response = self.client.post(
            self.url,
            {"refresh": "invalid-refresh-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
