"""Budget management service."""

from datetime import datetime
from src.storage import JSONStorage
from src.utils import VALID_CATEGORIES, validate_budget_amount


class BudgetService:
    """Manages budget limits and tracking."""

    def __init__(self, data_dir="data"):
        """Initialize budget service.

        Args:
            data_dir (str): Directory for storing data files
        """
        self.storage = JSONStorage(data_dir)
        self.budgets = self.storage.load_budgets()

    def set_budget(self, category, amount):
        """Set budget limit for a category.

        Args:
            category (str): Category name
            amount (float): Budget amount

        Returns:
            str: Success or error message
        """
        category_lower = category.lower().strip()
        if category_lower not in VALID_CATEGORIES:
            return f"✗ Invalid category: {category}"

        try:
            amount_float = validate_budget_amount(amount)
            self.budgets[category_lower] = amount_float
            self.storage.save_budgets(self.budgets)
            return f"✓ Budget set for {category_lower}: ${amount_float:.2f}"
        except ValueError as e:
            return f"✗ {e}"

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
            today = datetime.now().date()
            year, month = today.year, today.month

        status = {}

        for category in VALID_CATEGORIES:
            spent = monthly_summary.get(category, 0.0)
            budget = self.budgets.get(category)

            if budget is None:
                continue

            percentage = (spent / budget) * 100 if budget > 0 else 0
            remaining = budget - spent

            warning = 80 <= percentage < 100
            over_budget = percentage > 100
            limit = percentage == 100

            if over_budget:
                status_text = "❌  OVER BUDGET"
            elif warning:
                status_text = "⚠️  Near Budget Limit"
            elif limit:
                status_text = "❗  At Budget Limit"
            else:
                status_text = "✅  Within Budget"

            status[category] = {
                "spent": spent,
                "budget": budget,
                "remaining": remaining,
                "percentage": percentage,
                "warning": warning,
                "over_budget": over_budget,
                "limit": limit,
                "status": status_text,
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

        del self.budgets[category]
        self.storage.save_budgets(self.budgets)

        return True

    def clear_all_budgets(self):
        """
        Remove all budgets.

        Returns:
            bool: True when completed successfully.
        """

        self.budgets.clear()
        self.storage.save_budgets(self.budgets)

        return True