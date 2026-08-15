"""Application settings service."""

from src.exceptions import CurrencyChangeBlockedError
from src.repositories import BudgetRepository, ExpenseRepository, SettingsRepository
from src.utils import validate_currency

from .results import CurrencyUpdateResult


class SettingsService:
    """Manages application-wide settings and their safety rules."""

    def __init__(
        self,
        settings_repository: SettingsRepository,
        expense_repository: ExpenseRepository,
        budget_repository: BudgetRepository,
    ):
        self.settings_repository = settings_repository
        self.expense_repository = expense_repository
        self.budget_repository = budget_repository
        self.currency = self.settings_repository.load_settings()["currency"]

    def get_currency(self):
        """Return the configured application currency."""
        return self.currency

    def set_currency(self, currency):
        """Change currency only when no financial data would be relabelled."""
        currency = validate_currency(currency)

        if currency == self.currency:
            return CurrencyUpdateResult(currency, changed=False)

        if (
            self.expense_repository.load_expenses()
            or self.budget_repository.load_budgets()
        ):
            raise CurrencyChangeBlockedError(
                "Currency cannot be changed while expenses or budgets exist. "
                "Export or clear the existing financial data first."
            )

        self.settings_repository.save_settings({"currency": currency})
        self.currency = currency
        return CurrencyUpdateResult(currency, changed=True)
