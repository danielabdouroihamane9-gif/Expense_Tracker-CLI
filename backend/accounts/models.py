from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .validators import (
    currency_code_validator,
    normalize_currency_code,
)


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    currency = models.CharField(
        max_length=3,
        default="USD",
        validators=[currency_code_validator],
    )

    def _check_currency_change(self):
        """Prevent changing the currency when financial data exists."""
        if not self.pk or not self.user_id:
            return

        previous_currency = (
            type(self).objects.filter(pk=self.pk)
            .values_list("currency", flat=True)
            .first()
        )

        if previous_currency is None or previous_currency == self.currency:
            return

        has_expenses = self.user.expenses.exists()
        has_budgets = self.user.budgets.exists()

        if has_expenses or has_budgets:
            raise ValidationError({
                "currency": (
                    "Currency cannot be changed while expenses or "
                    "budgets exist for this account."
                )
            })

    def clean(self):
        super().clean()
        self.currency = normalize_currency_code(self.currency)
        self._check_currency_change()

    def save(self, *args, **kwargs):
        self.currency = normalize_currency_code(self.currency)
        self._check_currency_change()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.user.get_username()} settings "
            f"({self.currency})"
        )
