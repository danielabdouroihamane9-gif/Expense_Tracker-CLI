"""Main menu for CLI."""

from datetime import datetime
from src.services import ExpenseTrackerService, BudgetService, ExportService
from src.utils import (
    display_expenses_table,
    display_summary,
    display_budget_status,
    display_budgets,
)
from src.cli.commands import CommandHandler


class Menu:
    """Interactive menu for expense tracker."""

    def __init__(self):
        """Initialize menu with services."""
        self.expense_service = ExpenseTrackerService()
        self.budget_service = BudgetService()
        self.export_service = ExportService()
        self.commands = CommandHandler()

    def run(self):
        """Run the main interactive menu loop."""
        print("\n" + "=" * 60)
        print("   Expense Tracker CLI - Manage Your Finances with Ease")
        print("=" * 60)

        while True:
            print("\nMenu:")
            print("1. Add Expense")
            print("2. View All Expenses")
            print("3. Filter by Category")
            print("4. Monthly Summary")
            print("5. Set Budget")
            print("6. View Budget Status")
            print("7. View All Budgets")
            print("8. Export Expenses to CSV")
            print("9. Export Summary to CSV")
            print("0. Exit")

            choice = input("\nEnter your choice (0-9): ").strip()

            if choice == "1":
                self._add_expense()
            elif choice == "2":
                self._view_all_expenses()
            elif choice == "3":
                self._filter_by_category()
            elif choice == "4":
                self._monthly_summary()
            elif choice == "5":
                self._set_budget()
            elif choice == "6":
                self._view_budget_status()
            elif choice == "7":
                self._view_all_budgets()
            elif choice == "8":
                self._export_expenses()
            elif choice == "9":
                self._export_summary()
            elif choice == "0":
                print("\n✓ Goodbye!\n")
                break
            else:
                print("✗ Invalid choice. Enter 0-9.")

    def _add_expense(self):
        """Add a new expense."""
        print("\n--- Add Expense ---")
        date = self.commands.get_user_date()
        amount = self.commands.get_user_amount()
        category = self.commands.get_user_category()
        description = self.commands.get_user_description()

        result = self.expense_service.add_expense(date, amount, category, description)
        print(result)

    def _view_all_expenses(self):
        """View all expenses."""
        expenses = self.expense_service.get_all_expenses()
        display_expenses_table(expenses, "All Expenses")
        if expenses:
            total = sum(e.amount for e in expenses)
            print(f"Total: ${total:.2f}\n")

    def _filter_by_category(self):
        """Filter and display expenses by category."""
        category = self.commands.get_user_category()
        expenses = self.expense_service.get_by_category(category)
        display_expenses_table(expenses, f"Expenses - {category.capitalize()}")
        if expenses:
            total = sum(e.amount for e in expenses)
            print(f"Total: ${total:.2f}\n")

    def _monthly_summary(self):
        """Display monthly summary."""
        today = datetime.now().date()
        summary = self.expense_service.get_monthly_summary(today.year, today.month)
        display_summary(summary, today.year, today.month)

    def _set_budget(self):
        """Set a budget limit for a category."""
        print("\n--- Set Budget ---")
        category = self.commands.get_user_category()
        amount = self.commands.get_budget_amount()

        result = self.budget_service.set_budget(category, amount)
        print(result)

    def _view_budget_status(self):
        """View budget status for current month."""
        today = datetime.now().date()
        monthly_summary = self.expense_service.get_monthly_summary(
            today.year, today.month
        )
        status = self.budget_service.get_budget_status(
            monthly_summary, today.year, today.month
        )
        display_budget_status(status)

    def _view_all_budgets(self):
        """View all set budgets."""
        budgets = self.budget_service.get_all_budgets()
        display_budgets(budgets)

    def _export_expenses(self):
        """Export expenses to CSV."""
        print("\n--- Export Expenses to CSV ---")
        filename = self.commands.get_export_filename()
        expenses = self.expense_service.get_all_expenses()

        if filename:
            result = self.export_service.export_expenses_to_csv(expenses, filename)
        else:
            result = self.export_service.export_expenses_to_csv(expenses)

        print(result)

    def _export_summary(self):
        """Export monthly summary to CSV."""
        print("\n--- Export Monthly Summary to CSV ---")
        filename = self.commands.get_export_filename()
        today = datetime.now().date()
        summary = self.expense_service.get_monthly_summary(today.year, today.month)

        if filename:
            result = self.export_service.export_summary_to_csv(
                summary, filename, today.year, today.month
            )
        else:
            result = self.export_service.export_summary_to_csv(
                summary, year=today.year, month=today.month
            )

        print(result)
