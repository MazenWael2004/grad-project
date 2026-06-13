from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

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
        self.assertTrue(
            User.objects.filter(email="test@example.com").exists()
        )

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
        self.assertIn("token", response.data)

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

        self.token = Token.objects.create(user=self.user)

    def test_logout_success(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Token.objects.filter(key=self.token.key).exists()
        )

    def test_logout_unauthenticated(self):
        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )