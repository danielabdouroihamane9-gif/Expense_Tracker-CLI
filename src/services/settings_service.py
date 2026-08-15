"""Application settings service."""

from src.storage import JSONStorage
from src.utils import validate_currency


class SettingsService:
    """Manages application-wide settings and their safety rules."""

    def __init__(self, data_dir="data"):
        self.storage = JSONStorage(data_dir)
        self.currency = self.storage.load_settings()["currency"]

    def get_currency(self):
        """Return the configured application currency."""
        return self.currency

    def set_currency(self, currency):
        """Change currency only when no financial data would be relabelled."""
        try:
            currency = validate_currency(currency)
        except ValueError as error:
            return f"✗ {error}"

        if currency == self.currency:
            return f"✓ Currency is already set to {currency}"

        if self.storage.load_expenses() or self.storage.load_budgets():
            return (
                "✗ Currency cannot be changed while expenses or budgets exist. "
                "Export or clear the existing financial data first."
            )

        self.storage.save_settings({"currency": currency})
        self.currency = currency
        return f"✓ Application currency changed to {currency}"
