"""Core expense tracking service."""

from datetime import datetime
from src.models import Expense
from src.storage import JSONStorage
from src.utils import VALID_CATEGORIES


class ExpenseTrackerService:
    """Manages expense operations with CRUD functionality."""

    def __init__(self, data_dir="data"):
        """Initialize the expense tracker service.

        Args:
            data_dir (str): Directory for storing data files
        """
        self.storage = JSONStorage(data_dir)
        self.expenses = self.storage.load_expenses()

    def add_expense(self, date, amount, category, description):
        """Add a new expense after validation.

        Args:
            date (str): Date in YYYY-MM-DD format
            amount (float): Expense amount
            category (str): Expense category
            description (str): Expense description

        Returns:
            str: Success or error message
        """
        try:
            expense = Expense(date, amount, category, description)
            self.expenses.append(expense)
            self.storage.save_expenses(self.expenses)
            return f"✓ Expense added: ${expense.amount:.2f} ({expense.category}) on {expense.date}"
        except ValueError as e:
            return f"✗ Error: {e}"

    def get_all_expenses(self):
        """Return all expenses sorted by date (newest first).

        Returns:
            list: List of Expense objects sorted by date
        """
        return sorted(self.expenses, key=lambda e: e.date, reverse=True)

    def get_by_category(self, category):
        """Return expenses for a specific category.

        Args:
            category (str): Category name

        Returns:
            list: List of Expense objects in the category
        """
        category_lower = category.lower().strip()
        if category_lower not in VALID_CATEGORIES:
            return []
        return [e for e in self.get_all_expenses() if e.category == category_lower]

    def get_monthly_summary(self, year=None, month=None):
        """Get total spent per category for given month.

        Args:
            year (int): Year (defaults to current)
            month (int): Month (defaults to current)

        Returns:
            dict: Dictionary with categories and total amounts
        """
        if year is None or month is None:
            today = datetime.now().date()
            year = today.year if year is None else year
            month = today.month if month is None else month

        summary = {cat: 0.0 for cat in VALID_CATEGORIES}

        for expense in self.expenses:
            if expense.date.year == year and expense.date.month == month:
                summary[expense.category] += expense.amount

        return {cat: total for cat, total in summary.items() if total > 0}

    def delete_expense(self, expense):
        """
        Delete an expense object.

        Args:
            expense (Expense): Expense instance to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        if expense in self.expenses:
            self.expenses.remove(expense)
            self.storage.save_expenses(self.expenses)
            return True
        return False

    def get_expense_count(self):
        """Get total number of expenses.

        Returns:
            int: Number of expenses
        """
        return len(self.expenses)

    def clear_all_expenses(self):
        """
        Remove all expenses from the tracker.

        Returns:
            bool: True when completed successfully.
        """
        self.expenses.clear()
        self.storage.save_expenses(self.expenses)
        return True

    def update_expense(
            self,
            expense,
            amount,
            category,
            description
    ):
        """
        Update an existing expense.
        """

        expense.amount = amount
        expense.category = category
        expense.description = description

        self.storage.save_expenses(self.expenses)

        return True