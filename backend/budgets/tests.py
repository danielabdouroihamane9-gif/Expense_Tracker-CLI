
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import UserSettings
from .models import Budget


User = get_user_model()


class BudgetModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="budgetuser",
            password="test-password-123",
        )
        UserSettings.objects.create(user=self.user)

    def test_budget_is_created(self):
        budget = Budget.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("250.00"),
        )

        self.assertEqual(budget.amount, Decimal("250.00"))
        self.assertEqual(budget.category, "food")

    def test_only_one_budget_per_user_and_category(self):
        Budget.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("250.00"),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Budget.objects.create(
                    user=self.user,
                    category="food",
                    amount=Decimal("300.00"),
                )

    def test_database_rejects_nonpositive_budget(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Budget.objects.create(
                    user=self.user,
                    category="food",
                    amount=Decimal("0.00"),
                )

    def test_database_rejects_invalid_category(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Budget.objects.create(
                    user=self.user,
                    category="invalid",
                    amount=Decimal("100.00"),
                )

    def test_budget_requires_user_settings(self):
        user_without_settings = User.objects.create_user(
            username="no-budget-settings",
            password="test-password-123",
        )

        with self.assertRaises(ValidationError):
            Budget.objects.create(
                user=user_without_settings,
                category="food",
                amount=Decimal("100.00"),
            )
