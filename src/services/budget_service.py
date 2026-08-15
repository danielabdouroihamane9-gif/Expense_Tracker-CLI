"""Budget management service."""

from decimal import Decimal

from src.providers import Clock
from src.repositories import BudgetRepository, RepositoryError, SettingsRepository
from src.utils import VALID_CATEGORIES, validate_budget_amount, validate_category

from .results import BudgetUpdateResult


class BudgetService:
    """Manages budget limits and tracking."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        settings_repository: SettingsRepository,
        *,
        clock: Clock,
    ):
        """Initialize with persistence-agnostic repository dependencies."""
        self.budget_repository = budget_repository
        self.settings_repository = settings_repository
        self.clock = clock
        self.currency = self.settings_repository.load_settings()["currency"]
        self.budgets = self.budget_repository.load_budgets()

    def set_budget(self, category, amount):
        """Set budget limit for a category.

        Args:
            category (str): Category name
            amount (str | int | float | Decimal): Budget amount

        Returns:
            BudgetUpdateResult: The normalized persisted budget.
        """
        category_lower = validate_category(category)
        amount_decimal = validate_budget_amount(amount)
        previous_amount = self.budgets.get(category_lower)
        existed = category_lower in self.budgets
        self.budgets[category_lower] = amount_decimal
        try:
            self.budget_repository.save_budgets(self.budgets)
        except RepositoryError:
            if existed:
                self.budgets[category_lower] = previous_amount
            else:
                del self.budgets[category_lower]
            raise
        return BudgetUpdateResult(category_lower, amount_decimal)

    def get_budget(self, category):
        """Get budget limit for a category.

        Args:
            category (str): Category name

        Returns:
            float: Budget amount or None if not set
        """
        category_lower = category.lower().strip()
        return self.budgets.get(category_lower)

    def get_all_budgets(self):
        """Get all budget limits.

        Returns:
            dict: Copy of budgets dictionary
        """
        return self.budgets.copy()

    def get_budget_status(self, monthly_summary, year=None, month=None):
        """Get budget status for all categories.

        Args:
            monthly_summary (dict): Monthly summary from expense tracker
            year (int): Year (defaults to current)
            month (int): Month (defaults to current)

        Returns:
            dict: Budget status with spent, budget, remaining, percentage, warning
        """
        if year is None or month is None:
            today = self.clock.now().date()
            year, month = today.year, today.month

        status = {}

        for category in VALID_CATEGORIES:
            spent = monthly_summary.get(category, Decimal("0.00"))
            budget = self.budgets.get(category)

            if budget is None:
                continue

            percentage = (spent / budget) * 100 if budget > 0 else 0
            remaining = budget - spent

            warning = 80 <= percentage < 100
            over_budget = percentage > 100
            limit = percentage == 100

            status[category] = {
                "spent": spent,
                "budget": budget,
                "remaining": remaining,
                "percentage": percentage,
                "warning": warning,
                "over_budget": over_budget,
                "limit": limit,
            }

        return status

    def delete_budget(self, category):
        """
        Delete a budget for a specific category.

        Args:
            category (str): Budget category.

        Returns:
            bool: True if the budget existed and was deleted.
        """
        category = category.lower()

        if category not in self.budgets:
            return False

        previous_amount = self.budgets.pop(category)
        try:
            self.budget_repository.save_budgets(self.budgets)
        except RepositoryError:
            self.budgets[category] = previous_amount
            raise

        return True

    def clear_all_budgets(self):
        """
        Remove all budgets.

        Returns:
            bool: True when completed successfully.
        """

        previous_budgets = self.budgets.copy()
        self.budgets.clear()
        try:
            self.budget_repository.save_budgets(self.budgets)
        except RepositoryError:
            self.budgets.update(previous_budgets)
            raise

        return True
