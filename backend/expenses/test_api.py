
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserSettings
from expenses.models import Expense


User = get_user_model()


class ExpenseAPITests(APITestCase):
    url = "/api/v1/expenses/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="expenseapiuser",
            password="Strong-Password-928!",
        )
        UserSettings.objects.create(
            user=self.user,
            currency="USD",
        )

        self.client.force_authenticate(user=self.user)

    def make_expense(self, user=None, **overrides):
        values = {
            "user": user or self.user,
            "occurred_on": date(2026, 10, 23),
            "amount": Decimal("12.30"),
            "currency": "USD",
            "category": "food",
            "description": "Lunch",
        }
        values.update(overrides)

        return Expense.objects.create(**values)

    def test_create_expense(self):
        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "12.30",
                "category": "food",
                "description": "Lunch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["amount"], "12.30")
        self.assertEqual(response.data["currency"], "USD")
        self.assertEqual(response.data["user"], self.user.pk)
        self.assertEqual(Expense.objects.count(), 1)

    def test_expense_uses_users_configured_currency(self):
        settings = self.user.settings
        settings.currency = "MYR"
        settings.save()

        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "12.30",
                "category": "food",
                "description": "Lunch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["currency"], "MYR")

    def test_client_cannot_choose_owner_or_currency(self):
        other_user = User.objects.create_user(
            username="otherexpenseuser",
            password="Strong-Password-928!",
        )
        UserSettings.objects.create(user=other_user, currency="MYR")

        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "12.30",
                "category": "food",
                "description": "Lunch",
                "user": other_user.pk,
                "currency": "MYR",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Expense.objects.count(), 0)

    def test_list_contains_only_current_users_expenses(self):
        own_expense = self.make_expense()

        other_user = User.objects.create_user(
            username="anotheruser",
            password="Strong-Password-928!",
        )
        UserSettings.objects.create(user=other_user, currency="USD")

        self.make_expense(
            user=other_user,
            description="Private expense",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {
            item["id"] for item in response.data["results"]
        }

        self.assertEqual(returned_ids, {str(own_expense.id)})

    def test_cannot_retrieve_another_users_expense(self):
        other_user = User.objects.create_user(
            username="privateuser",
            password="Strong-Password-928!",
        )
        UserSettings.objects.create(user=other_user, currency="USD")

        other_expense = self.make_expense(user=other_user)

        response = self.client.get(
            f"{self.url}{other_expense.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_own_expense(self):
        expense = self.make_expense()

        response = self.client.patch(
            f"{self.url}{expense.id}/",
            {"description": "Updated lunch"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expense.refresh_from_db()
        self.assertEqual(expense.description, "Updated lunch")

    def test_delete_own_expense(self):
        expense = self.make_expense()

        response = self.client.delete(
            f"{self.url}{expense.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())

    def test_zero_amount_is_rejected_by_api(self):
        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "0.00",
                "category": "food",
                "description": "Lunch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_category_is_rejected_by_api(self):
        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "12.30",
                "category": "invalid",
                "description": "Lunch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_category(self):
        self.make_expense(category="food")
        self.make_expense(
            category="transport",
            description="Bus ticket",
        )

        response = self.client.get(
            self.url,
            {"category": "food"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["category"], "food")

    def test_expense_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
