
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from budgets.models import Budget
from expenses.models import Expense
from .models import UserSettings


User = get_user_model()


class UserSettingsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="test-password-123",
        )
        self.settings = UserSettings.objects.create(
            user=self.user
        )

    def test_default_currency_is_usd(self):
        self.assertEqual(self.settings.currency, "USD")

    def test_currency_is_normalized(self):
        self.settings.currency = "myr"
        self.settings.save()

        self.assertEqual(self.settings.currency, "MYR")

    def test_invalid_currency_is_rejected(self):
        self.settings.currency = "US1"

        with self.assertRaises(ValidationError):
            self.settings.save()

    def test_currency_can_change_without_financial_data(self):
        self.settings.currency = "MYR"
        self.settings.save()

        self.settings.refresh_from_db()
        self.assertEqual(self.settings.currency, "MYR")

    def test_currency_change_is_blocked_after_expense(self):
        Expense.objects.create(
            user=self.user,
            occurred_on=date(2026, 10, 23),
            amount=Decimal("12.30"),
            currency="USD",
            category="food",
            description="Lunch",
        )

        self.settings.currency = "MYR"

        with self.assertRaises(ValidationError):
            self.settings.save()

    def test_currency_change_is_blocked_after_budget(self):
        Budget.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("100.00"),
        )

        self.settings.currency = "MYR"

        with self.assertRaises(ValidationError):
            self.settings.save()
