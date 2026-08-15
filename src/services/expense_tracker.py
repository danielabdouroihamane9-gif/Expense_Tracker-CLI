"""Core expense tracking service."""

from decimal import Decimal

from src.exceptions import CurrencyMismatchError, DomainValidationError
from src.models import Expense
from src.providers import Clock, UUIDGenerator
from src.repositories import ExpenseRepository, RepositoryError, SettingsRepository
from src.utils import VALID_CATEGORIES

from .results import ExpenseImportError, ExpenseImportResult


class ExpenseTrackerService:
    """Manages expense operations with CRUD functionality."""

    def __init__(
        self,
        expense_repository: ExpenseRepository,
        settings_repository: SettingsRepository,
        *,
        clock: Clock,
        uuid_generator: UUIDGenerator,
    ):
        """Initialize with persistence-agnostic repository dependencies."""
        self.expense_repository = expense_repository
        self.settings_repository = settings_repository
        self.clock = clock
        self.uuid_generator = uuid_generator
        self.currency = self.settings_repository.load_settings()["currency"]
        self.expenses = self.expense_repository.load_expenses()
        if any(expense.currency != self.currency for expense in self.expenses):
            raise CurrencyMismatchError(
                f"Stored expenses must use configured currency {self.currency}"
            )

    def add_expense(self, date, amount, category, description, currency=None):
        """Add a new expense after validation.

        Args:
            date (str): Date in YYYY-MM-DD format
            amount (str | int | float | Decimal): Expense amount
            category (str): Expense category
            description (str): Expense description
            currency (str | None): Optional currency that must match settings

        Returns:
            Expense: The persisted expense.
        """
        currency = currency or self.currency
        expense = Expense(
            date,
            amount,
            category,
            description,
            expense_id=self.uuid_generator.new_uuid(),
            currency=currency,
            created_at=self.clock.now(),
        )
        if expense.currency != self.currency:
            raise CurrencyMismatchError(
                f"Currency must match application currency {self.currency}"
            )
        self.expenses.append(expense)
        try:
            self.expense_repository.save_expenses(self.expenses)
        except RepositoryError:
            self.expenses.pop()
            raise
        return expense

    def _is_duplicate_expense(
        self,
        date,
        amount,
        category,
        description,
        currency=None,
    ):
        """
        Check whether an identical expense already exists.

        An expense is considered a duplicate if it has the same:
            - date
            - amount
            - category
            - description

        Args:
            date (str | date): Expense date.
            amount (str | int | float | Decimal): Expense amount.
            category (str): Expense category.
            description (str): Expense description.

        Returns:
            bool: True if a duplicate exists, otherwise False.
        """

        currency = currency or self.currency
        for expense in self.expenses:
            if (
                expense.date == date
                and expense.amount == amount
                and expense.category == category.lower()
                and expense.description == description
                and expense.currency == currency
            ):
                return True

        return False

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
            today = self.clock.now().date()
            year = today.year if year is None else year
            month = today.month if month is None else month

        summary = {cat: Decimal("0.00") for cat in VALID_CATEGORIES}

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
                spending[category] = Decimal("0.00")

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
            spending.items(), key=lambda item: item[1], reverse=True
        )

        return ranked_categories[:limit]

    def get_expense_statistics(self):
        """
        Calculate summary statistics for all expenses.

        Returns:
            dict:
                {
                    "count": int,
                    "total": Decimal,
                    "highest": Expense | None,
                    "lowest": Expense | None,
                    "average": Decimal
                }
        """

        expenses = self.get_all_expenses()

        if not expenses:
            return {
                "count": 0,
                "total": Decimal("0.00"),
                "highest": None,
                "lowest": None,
                "average": Decimal("0.00"),
            }

        total = sum((expense.amount for expense in expenses), Decimal("0.00"))

        highest = max(expenses, key=lambda expense: expense.amount)

        lowest = min(expenses, key=lambda expense: expense.amount)

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
            index = self.expenses.index(expense)
            self.expenses.pop(index)
            try:
                self.expense_repository.save_expenses(self.expenses)
            except RepositoryError:
                self.expenses.insert(index, expense)
                raise
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
        previous_expenses = self.expenses.copy()
        self.expenses.clear()
        try:
            self.expense_repository.save_expenses(self.expenses)
        except RepositoryError:
            self.expenses.extend(previous_expenses)
            raise
        return True

    def update_expense(self, expense, amount, category, description):
        """
        Update an existing expense.
        """

        if expense not in self.expenses:
            return False

        # Validate all proposed values before mutating the original object.
        updated = Expense(
            str(expense.date),
            amount,
            category,
            description,
            expense_id=expense.id,
            currency=expense.currency,
            created_at=expense.created_at,
        )
        previous_values = (
            expense.amount,
            expense.category,
            expense.description,
        )
        expense.amount = updated.amount
        expense.category = updated.category
        expense.description = updated.description

        try:
            self.expense_repository.save_expenses(self.expenses)
        except RepositoryError:
            (
                expense.amount,
                expense.category,
                expense.description,
            ) = previous_values
            raise

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

        return self.add_expense(
            date=new_date,
            category=expense.category,
            amount=expense.amount,
            description=expense.description,
            currency=expense.currency,
        )

    def import_expenses(self, rows):
        """
        Import expenses from CSV rows.

        Args:
            rows (list): List of dictionaries returned by
                ExportService.read_expenses_csv().

        Returns:
            ExpenseImportResult: Neutral import counts and row errors.
        """

        imported = 0
        skipped_duplicates = 0
        errors = []

        for row_number, row in enumerate(rows, start=2):
            try:
                expense = Expense(
                    row["Date"],
                    row["Amount"],
                    row["Category"],
                    row["Description"],
                    expense_id=self.uuid_generator.new_uuid(),
                    currency=row.get("Currency", self.currency),
                    created_at=self.clock.now(),
                )

                if expense.currency != self.currency:
                    raise CurrencyMismatchError(
                        f"Currency must be {self.currency}, got {expense.currency}"
                    )

                if self._is_duplicate_expense(
                    expense.date,
                    expense.amount,
                    expense.category,
                    expense.description,
                    expense.currency,
                ):
                    skipped_duplicates += 1
                    continue

                self.expenses.append(expense)
                imported += 1

            except (CurrencyMismatchError, DomainValidationError, KeyError) as error:
                errors.append(
                    ExpenseImportError(
                        row_number=row_number,
                        date=str(row.get("Date", "")),
                        amount=str(row.get("Amount", "")),
                        category=str(row.get("Category", "")),
                        description=str(row.get("Description", "")),
                        reason=str(error),
                    )
                )
        if imported > 0:
            try:
                self.expense_repository.save_expenses(self.expenses)
            except RepositoryError:
                del self.expenses[-imported:]
                raise

        return ExpenseImportResult(
            imported=imported,
            skipped_duplicates=skipped_duplicates,
            errors=tuple(errors),
        )
