from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserSettings
from budgets.models import Budget
from expenses.models import Expense

User = get_user_model()


class RegistrationAPITests(APITestCase):
    url = "/api/v1/auth/register/"

    def test_registration_creates_user_and_settings(self):
        response = self.client.post(
            self.url,
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "Strong-Password-928!",
                "password_confirm": "Strong-Password-928!",
                "currency": "myr",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="newuser")

        self.assertTrue(
            user.check_password("Strong-Password-928!")
        )
        self.assertEqual(user.settings.currency, "MYR")
        self.assertEqual(response.data["currency"], "MYR")
        self.assertNotIn("password", response.data)

    def test_registration_defaults_to_usd(self):
        response = self.client.post(
            self.url,
            {
                "username": "defaultcurrency",
                "password": "Strong-Password-928!",
                "password_confirm": "Strong-Password-928!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["currency"], "USD")

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(
            username="existinguser",
            password="Strong-Password-928!",
        )

        response = self.client.post(
            self.url,
            {
                "username": "existinguser",
                "password": "Strong-Password-928!",
                "password_confirm": "Strong-Password-928!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "username": "mismatchuser",
                "password": "Strong-Password-928!",
                "password_confirm": "Different-Password-123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            User.objects.filter(username="mismatchuser").exists()
        )

    def test_invalid_currency_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "username": "badcurrency",
                "password": "Strong-Password-928!",
                "password_confirm": "Strong-Password-928!",
                "currency": "US1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="Strong-Password-928!",
        )

        UserSettings.objects.create(
            user=self.user,
            currency="MYR",
        )

    def test_login_returns_jwt_tokens(self):
        response = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": "loginuser",
                "password": "Strong-Password-928!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_current_user_requires_authentication(self):
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_returns_authenticated_profile(self):
        token_response = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": "loginuser",
                "password": "Strong-Password-928!",
            },
            format="json",
        )

        access_token = token_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "loginuser")
        self.assertEqual(response.data["currency"], "MYR")


class UserSettingsAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="settings_test_user",
            password="StrongPass123!",
        )

        self.settings = UserSettings.objects.create(
            user=self.user,
            currency="USD",
        )

        self.client.force_authenticate(user=self.user)

    def test_user_can_change_currency_without_financial_data(self):
        response = self.client.patch(
            "/api/v1/auth/settings/",
            {"currency": "myr"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.settings.refresh_from_db()
        self.assertEqual(self.settings.currency, "MYR")

    def test_invalid_currency_is_rejected(self):
        response = self.client.patch(
            "/api/v1/auth/settings/",
            {"currency": "US"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.settings.refresh_from_db()
        self.assertEqual(self.settings.currency, "USD")

    def test_currency_change_is_blocked_when_expenses_exist(self):
        Expense.objects.create(
            user=self.user,
            occurred_on=date(2026, 9, 1),
            amount=Decimal("12.50"),
            currency="USD",
            category="food",
            description="Lunch",
        )

        response = self.client.patch(
            "/api/v1/auth/settings/",
            {"currency": "MYR"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.settings.refresh_from_db()
        self.assertEqual(self.settings.currency, "USD")

    def test_currency_change_is_blocked_when_budgets_exist(self):
        Budget.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("100.00"),
        )

        response = self.client.patch(
            "/api/v1/auth/settings/",
            {"currency": "MYR"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.settings.refresh_from_db()
        self.assertEqual(self.settings.currency, "USD")