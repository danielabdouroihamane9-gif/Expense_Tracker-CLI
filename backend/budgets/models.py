
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from accounts.models import UserSettings
from expenses.choices import ExpenseCategory


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
    )

    category = models.CharField(
        max_length=20,
        choices=ExpenseCategory.choices,
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    def _validate_user_settings(self):
        if not self.user_id:
            raise ValidationError({
                "user": "A budget must belong to a user."
            })

        if not UserSettings.objects.filter(
            user_id=self.user_id
        ).exists():
            raise ValidationError({
                "user": (
                    "Create user settings before adding budgets."
                )
            })

    def clean(self):
        super().clean()
        self.category = self.category.strip().lower()
        self._validate_user_settings()

    def save(self, *args, **kwargs):
        self.category = self.category.strip().lower()
        self._validate_user_settings()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["category"]

        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="budget_amount_positive",
            ),
            models.CheckConstraint(
                condition=Q(category__in=ExpenseCategory.values),
                name="budget_category_valid",
            ),
            models.UniqueConstraint(
                fields=["user", "category"],
                name="budget_unique_user_category",
            ),
        ]

    def __str__(self):
        return f"{self.category}: {self.amount}"
