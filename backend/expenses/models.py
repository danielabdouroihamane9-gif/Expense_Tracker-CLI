
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from accounts.models import UserSettings
from accounts.validators import (
    currency_code_validator,
    normalize_currency_code,
)
from .choices import ExpenseCategory


def validate_description(value):
    if not value or not value.strip():
        raise ValidationError("Description cannot be empty.")


class Expense(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    occurred_on = models.DateField()

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Positive amount, stored to two decimal places.",
    )

    currency = models.CharField(
        max_length=3,
        validators=[currency_code_validator],
    )

    category = models.CharField(
        max_length=20,
        choices=ExpenseCategory.choices,
    )

    description = models.CharField(
        max_length=500,
        validators=[validate_description],
    )

    # Unlike auto_now_add, this permits assigning a historical
    # timestamp when importing existing expense records.
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    def _normalize_values(self):
        self.currency = normalize_currency_code(self.currency)
        self.category = self.category.strip().lower()
        self.description = self.description.strip()

    def _validate_owner_currency(self):
        if not self.user_id:
            raise ValidationError({
                "user": "An expense must belong to a user."
            })

        user_currency = (
            UserSettings.objects.filter(user_id=self.user_id)
            .values_list("currency", flat=True)
            .first()
        )

        if user_currency is None:
            raise ValidationError({
                "user": "Create user settings before adding expenses."
            })

        if self.currency != user_currency:
            raise ValidationError({
                "currency": (
                    "Expense currency must match the user's "
                    "configured currency."
                )
            })

    def clean(self):
        super().clean()
        self._normalize_values()
        self._validate_owner_currency()

    def save(self, *args, **kwargs):
        self._normalize_values()
        self._validate_owner_currency()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-occurred_on", "-created_at"]

        indexes = [
            models.Index(
                fields=["user", "occurred_on"],
                name="exp_user_date_idx",
            ),
            models.Index(
                fields=["user", "category"],
                name="exp_user_cat_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="expense_amount_positive",
            ),
            models.CheckConstraint(
                condition=Q(category__in=ExpenseCategory.values),
                name="expense_category_valid",
            ),
            models.CheckConstraint(
                condition=~Q(description=""),
                name="expense_description_nonempty",
            ),
        ]

    def __str__(self):
        return (
            f"{self.occurred_on} — {self.currency} "
            f"{self.amount} ({self.category})"
        )
