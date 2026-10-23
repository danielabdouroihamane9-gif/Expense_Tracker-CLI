
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import UserSettings
from .models import Expense


User = get_user_model()


class ExpenseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="expenseuser",
            password="test-password-123",
        )
        UserSettings.objects.create(user=self.user)

    def make_expense(self, **overrides):
        values = {
            "user": self.user,
            "occurred_on": date(2026, 10, 23),
            "amount": Decimal("12.30"),
            "currency": "USD",
            "category": "food",
            "description": "Lunch",
        }
        values.update(overrides)
        return Expense.objects.create(**values)

    def test_expense_uses_uuid_and_decimal(self):
        expense = self.make_expense()

        self.assertIsInstance(expense.id, UUID)
        self.assertEqual(expense.amount, Decimal("12.30"))

    def test_text_fields_are_normalized(self):
        expense = self.make_expense(
            currency="usd",
            category=" FOOD ",
            description="  Lunch  ",
        )

        self.assertEqual(expense.currency, "USD")
        self.assertEqual(expense.category, "food")
        self.assertEqual(expense.description, "Lunch")

    def test_currency_must_match_user_settings(self):
        with self.assertRaises(ValidationError):
            self.make_expense(currency="MYR")

    def test_user_must_have_settings(self):
        user_without_settings = User.objects.create_user(
            username="no-settings",
            password="test-password-123",
        )

        with self.assertRaises(ValidationError):
            Expense.objects.create(
                user=user_without_settings,
                occurred_on=date(2026, 10, 23),
                amount=Decimal("12.30"),
                currency="USD",
                category="food",
                description="Lunch",
            )

    def test_database_rejects_nonpositive_amount(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_expense(amount=Decimal("0.00"))

    def test_database_rejects_invalid_category(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_expense(category="invalid")

    def test_database_rejects_empty_description(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_expense(description="   ")
