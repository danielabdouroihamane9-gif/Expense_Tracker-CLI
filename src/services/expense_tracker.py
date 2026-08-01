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

    def search_expenses(self, keyword):
        """
        Search expenses by description or category.

        Args:
            keyword (str): Search text.

        Returns:
            list: Matching expenses.
        """

        keyword = keyword.lower()

        expenses = self.get_all_expenses()

        results = []

        for expense in expenses:
            if (
                keyword in expense.description.lower()
                or keyword in expense.category.lower()
            ):
                results.append(expense)

        return results

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

    def get_spending_by_category(self):
        """
        Calculate total spending for each category.

        Returns:
            dict:
                {
                    "food": 120.50,
                    "transport": 75.00
                }
        """

        expenses = self.get_all_expenses()

        spending = {}

        for expense in expenses:

            category = expense.category

            if category not in spending:
                spending[category] = 0

            spending[category] += expense.amount

        return dict(sorted(spending.items()))

    def get_top_spending_categories(self, limit=5):
        """
        Return categories ranked by spending amount.

        Args:
            limit (int):
                Number of categories to return.

        Returns:
            list of tuples:
                [
                    ("shopping", 900),
                    ("food", 500)
                ]
        """

        spending = self.get_spending_by_category()

        if not spending:
            return []

        ranked_categories = sorted(
            spending.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return ranked_categories[:limit]

    def get_expense_statistics(self):
        """
        Calculate summary statistics for all expenses.

        Returns:
            dict:
                {
                    "count": int,
                    "total": float,
                    "highest": Expense | None,
                    "lowest": Expense | None,
                    "average": float
                }
        """

        expenses = self.get_all_expenses()

        if not expenses:
            return {
                "count": 0,
                "total": 0,
                "highest": None,
                "lowest": None,
                "average": 0,
            }

        total = sum(expense.amount for expense in expenses)

        highest = max(
            expenses,
            key=lambda expense: expense.amount
        )

        lowest = min(
            expenses,
            key=lambda expense: expense.amount
        )

        highest_index = expenses.index(highest) + 1
        lowest_index = expenses.index(lowest) + 1

        average = total / len(expenses)

        return {
            "count": len(expenses),
            "total": total,
            "highest": highest,
            "highest_index": highest_index,
            "lowest": lowest,
            "lowest_index": lowest_index,
            "average": average,
        }

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

    def get_by_date_range(self, start_date, end_date):
        """
        Return expenses between two dates.

        Args:
            start_date (date): Start date of the range
            end_date (date): End date of the range

        Returns:
            list of expenses
        """

        expenses = self.get_all_expenses()

        filtered = []

        for expense in expenses:

            if start_date <= expense.date <= end_date:
                filtered.append(expense)

        return filtered

    def get_sorted_expenses(self, sort_by, reverse=False):
        """
        Return expenses sorted by a given field.

        Args:
            sort_by (str):
                "date"
                "amount"
                "category"
                "description"

            reverse (bool):
                True for descending order.

        Returns:
            list
        """

        expenses = self.get_all_expenses()

        valid_fields = {
            "date": lambda expense: expense.date,
            "amount": lambda expense: expense.amount,
            "category": lambda expense: expense.category.lower(),
            "description": lambda expense: expense.description.lower(),
        }

        if sort_by not in valid_fields:
            return expenses

        return sorted(
            expenses,
            key=valid_fields[sort_by],
            reverse=reverse,
        )

    def duplicate_expense(self, expense, new_date):
        """
        Duplicate an existing expense using a new date.
        """

        self.add_expense(
            date=new_date,
            category=expense.category,
            amount=expense.amount,
            description=expense.description,
        )

        return (
            f"✓ Expense duplicated successfully: "
            f"${expense.amount:.2f} "
            f"({expense.category}) "
            f"on {new_date}"
        )