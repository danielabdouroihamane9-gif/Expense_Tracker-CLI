"""Main menu for CLI."""

from ast import keyword
from datetime import datetime
from src.services import ExpenseTrackerService, BudgetService, ExportService
from src.utils import (
    display_expenses_table,
    display_summary,
    display_budget_status,
    display_budgets,
    display_expense_details,
    display_spending_by_category,
    display_duplicate_expenses,
    display_expense_statistics,
    display_top_spending_categories,
    display_budget_edit_preview,
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
        """Run the main menu loop with submenu architecture."""
        print("\n" + "=" * 60)
        print("   Expense Tracker CLI - Manage Your Finances with Ease")
        print("=" * 60)

        while True:
            print("\nMain Menu:")
            print("1. Expense Management")
            print("2. Budget Management")
            print("3. Reports")
            print("4. Export")
            print("0. Exit")

            choice = input("\nEnter your choice (0-4): ").strip()

            if choice == "1":
                self._expense_menu()
            elif choice == "2":
                self._budget_menu()
            elif choice == "3":
                self._reports_menu()
            elif choice == "4":
                self._export_menu()
            elif choice == "0":
                print("\n✓ Goodbye!\n")
                break
            else:
                print("✗ Invalid choice. Enter 0-4.")

    def _expense_menu(self):
        """Expense management submenu."""
        while True:
            print("\nExpense Management:")
            print("1. Add Expense")
            print("2. Edit Expense")
            print("3. Duplicate Expense")
            print("4. View All Expenses")
            print("5. View Expense Details")
            print("6. Search Expenses")
            print("7. Filter by Category")
            print("8. Filter by Date Range")
            print("9. Sort Expenses")
            print("10. Delete Expense")
            print("11. Clear All Expenses")
            print("0. Back")

            choice = input("\nEnter your choice (0-11): ").strip()

            if choice == "1":
                self._add_expense()
            elif choice == "2":
                self._edit_expense()
            elif choice == "3":
                self._duplicate_expense()
            elif choice == "4":
                self._view_all_expenses()
            elif choice == "5":
                self._view_expense_details()
            elif choice == "6":
                self._search_expenses()
            elif choice == "7":
                self._filter_by_category()
            elif choice == "8":
                self._filter_by_date_range()
            elif choice == "9":
                self._sort_expenses()
            elif choice == "10":
                self._delete_expense()
            elif choice == "11":
                self._clear_all_expenses()
            elif choice == "0":
                break
            else:
                print("✗ Invalid choice. Enter 0-11.")

    def _budget_menu(self):
        """Budget management submenu."""
        while True:
            print("\nBudget Management:")
            print("1. Set Budget")
            print("2. Edit Budget")
            print("3. Budget Status")
            print("4. View Budgets")
            print("5. Delete Budget")
            print("6. Clear All Budgets")
            print("0. Back")

            choice = input("\nEnter your choice (0-6): ").strip()

            if choice == "1":
                self._set_budget()
            elif choice == "2":
                self._edit_budget()
            elif choice == "3":
                self._view_budget_status()
            elif choice == "4":
                self._view_all_budgets()
            elif choice == "5":
                self._delete_budget()
            elif choice == "6":
                self._clear_all_budgets()
            elif choice == "0":
                break
            else:
                print("✗ Invalid choice. Enter 0-6.")

    def _reports_menu(self):
        """Reports submenu."""
        while True:
            print("\nReports:")
            print("1. Monthly Summary")
            print("2. Spending by Category")
            print("3. Expense Statistics")
            print("4. Top Spending Categories")
            print("0. Back")

            choice = input("\nEnter your choice (0-4): ").strip()

            if choice == "1":
                self._monthly_summary()
            elif choice == "2":
                self._spending_by_category()
            elif choice == "3":
                self._expense_statistics()
            elif choice == "4":
                self._top_spending_categories()
            elif choice == "0":
                break
            else:
                print("✗ Invalid choice. Enter 0-4.")

    def _export_menu(self):
        """Export submenu."""
        while True:
            print("\nExport:")
            print("1. Export Expenses")
            print("2. Export Summary")
            print("3. Import Expenses")
            print("0. Back")

            choice = input("\nEnter your choice (0-3): ").strip()

            if choice == "1":
                self._export_expenses()
            elif choice == "2":
                self._export_summary()
            elif choice == "3":
                self._import_expenses()
            elif choice == "0":
                break
            else:
                print("✗ Invalid choice. Enter 0-3.")

    def _add_expense(self):
        """Add a new expense."""
        print("\n--- Add Expense ---")
        date = self.commands.get_user_date()
        amount = self.commands.get_user_amount()
        category = self.commands.get_user_category()
        description = self.commands.get_user_description()

        result = self.expense_service.add_expense(date, amount, category, description)
        print(result)

    def _edit_expense(self):
        """Edit an existing expense."""
        expense = self._select_expense()

        if expense is None:
            return

        print("\nLeave blank to keep current value\n")

        amount = input(
            f"Amount ({expense.amount}): "
        ).strip()

        category = input(
            f"Category ({expense.category}): "
        ).strip()

        description = input(
            f"Description ({expense.description}): "
        ).strip()

        if amount:
            amount = float(amount)
        else:
            amount = expense.amount

        if not category:
            category = expense.category

        if not description:
            description = expense.description

        self.expense_service.update_expense(
            expense,
            amount,
            category,
            description
        )
        print("\n✓ Expense updated successfully.\n")

    def _view_all_expenses(self):
        """View all expenses."""
        expenses = self.expense_service.get_all_expenses()
        display_expenses_table(expenses, "All Expenses")
        if expenses:
            total = sum(e.amount for e in expenses)
            print(f"Total: ${total:.2f}\n")

    def _sort_expenses(self):
        """Display expenses sorted by a selected field."""
        if not self.expense_service.get_all_expenses():
            print("\nNo expenses found.\n")
            return

        while True:

            print("\n--- Sort Expenses ---")
            print("1. Date (Newest First)")
            print("2. Date (Oldest First)")
            print("3. Amount (Highest First)")
            print("4. Amount (Lowest First)")
            print("5. Category (A-Z)")
            print("6. Category (Z-A)")
            print("7. Description (A-Z)")
            print("8. Description (Z-A)")
            print("0. Back")

            choice = input("\nChoose an option: ").strip()

            mapping = {
                "1": ("date", True),
                "2": ("date", False),
                "3": ("amount", True),
                "4": ("amount", False),
                "5": ("category", False),
                "6": ("category", True),
                "7": ("description", False),
                "8": ("description", True),
            }

            if choice == "0":
                return

            if choice not in mapping:
                print("✗ Invalid option.")
                continue

            sort_by, reverse = mapping[choice]

            expenses = self.expense_service.get_sorted_expenses(
                sort_by,
                reverse,
            )

            display_expenses_table(
                expenses,
                "Sorted Expenses",
            )
            return

    def _duplicate_expense(self):
        """Duplicate an existing expense."""

        expense = self._select_expense()

        if expense is None:
            return

        display_duplicate_expenses(expense)
        new_date = self.commands.get_user_date()

        message = self.expense_service.duplicate_expense(
            expense,
            new_date,
        )

        print(f"\n{message}")

    def _select_expense(self):
        """
        Display all expenses and let the user select one.

        Returns:
            Expense: The selected expense object.
            None: If the user cancels.
        """

        expenses = self.expense_service.get_all_expenses()

        if not expenses:
            print("\nNo expenses found.\n")
            return None

        display_expenses_table(expenses, "Select Expense")

        while True:

            choice = input(
                "\nEnter expense number (0 to cancel): "
            ).strip()

            if choice == "0":
                print("Operation cancelled.")
                return None

            if not choice.isdigit():
                print("✗ Please enter a valid number.")
                continue

            index = int(choice)

            if index < 1 or index > len(expenses):
                print("✗ Invalid expense number.")
                continue

            return expenses[index - 1]

    def _view_expense_details(self):
        """Display detailed information about one expense."""

        expense = self._select_expense()

        if expense is None:
            return

        display_expense_details(expense)
        print()

    def _delete_expense(self):
        """Delete an expense selected by the user."""
        expense = self._select_expense()

        if expense is None:
            return

        confirm = input(
            f"\nDelete '{expense.description}' "
            f"(${expense.amount:.2f})? (y/n): "
        ).strip().lower()

        if confirm != "y":
            print("Deletion cancelled.")
            return

        if self.expense_service.delete_expense(expense):
            print("✓ Expense deleted successfully.")
        else:
            print("✗ Failed to delete expense.")

    def _clear_all_expenses(self):
        """Clear all expenses after confirmation."""

        expenses = self.expense_service.get_all_expenses()

        if not expenses:
            print("\nNo expenses to clear.\n")
            return

        print("\n⚠ WARNING")
        print("This will permanently delete ALL expenses.")
        print("This action cannot be undone.\n")

        confirm = input("Type 'YES' to continue: ").strip()

        if confirm != "YES":
            print("\nOperation cancelled.")
            return

        self.expense_service.clear_all_expenses()

        print("\n✓ All expenses have been deleted successfully.\n")

    def _filter_by_date(self):
        """Filter expenses by date range."""

        print("\n--- Filter Expenses by Date ---")

        start_date, end_date = (
            self.commands.get_user_date_range()
        )

        expenses = (
            self.expense_service.get_by_date_range(
                start_date,
                end_date
            )
        )

        if not expenses:
            print(
                "\nNo expenses found in this date range.\n"
            )
            return

        display_expenses_table(
            expenses,
            f"{start_date} to {end_date}"
        )

        total = sum(
            expense.amount
            for expense in expenses
        )

        print(
            f"Total: ${total:.2f}\n"
        )

    def _filter_by_category(self):
        """Filter and display expenses by category."""
        category = self.commands.get_user_category()
        expenses = self.expense_service.get_by_category(category)
        display_expenses_table(expenses, f"Expenses - {category.capitalize()}")
        if expenses:
            total = sum(e.amount for e in expenses)
            print(f"Total: ${total:.2f}\n")

    def _search_expenses(self):
        """
        Search expenses by keyword.
        """

        print("\n--- Search Expenses ---")

        keyword = self.commands.get_user_keyword()

        expenses = self.expense_service.search_expenses(keyword)

        if not expenses:
            print("\nNo matching expenses found.\n")
            return

        display_expenses_table(
            expenses,
            f"Search Results: {keyword}"
        )

        total = sum(
            expense.amount
            for expense in expenses
        )

        print(f"Total: ${total:.2f}\n")

    def _monthly_summary(self):
        """Display monthly summary based on user-requested year and month."""
        today = datetime.now().date()
    
        # 1. Get and validate the year input
        year_input = input(f"Enter year (Press Enter for current year {today.year}): ").strip()
        if not year_input:
            year = today.year
        else:
            try:
                year = int(year_input)
            except ValueError:
                print("❌ Invalid year format. Using current year.")
                year = today.year

        # 2. Get and validate the month input
        month_input = input(f"Enter month 1-12 (Press Enter for current month {today.month}): ").strip()
        if not month_input:
            month = today.month
        else:
            try:
                month = int(month_input)
                if not (1 <= month <= 12):
                    raise ValueError
            except ValueError:
                print("❌ Invalid month. Must be between 1 and 12. Using current month.")
                month = today.month

        # 3. Fetch and display data using the user's selected dates
        summary = self.expense_service.get_monthly_summary(year, month)
        display_summary(summary, year, month)

    def _spending_by_category(self):
        """
        Display total spending grouped by category.
        """
        print("\n--- Spending by Category ---")

        spending = self.expense_service.get_spending_by_category()       
        display_spending_by_category(spending)

    def _top_spending_categories(self):
        """Display highest spending categories."""

        categories = (
            self.expense_service
            .get_top_spending_categories()
        )

        display_top_spending_categories(categories)

    def _expense_statistics(self):
        """
        Display expense statistics.
        """

        print("\n--- Expense Statistics ---")

        stats = (
            self.expense_service
            .get_expense_statistics()
        )

        display_expense_statistics(stats)

    def _set_budget(self):
        """Set a budget limit for a category."""
        print("\n--- Set Budget ---")
        category = self.commands.get_user_category()
        amount = self.commands.get_budget_amount()

        result = self.budget_service.set_budget(category, amount)
        print(result)

    def _edit_budget(self):
        """Edit an existing budget for a category."""

        budget = self._select_budget()

        if budget is None:
            return

        category, current_amount = budget

        display_budget_edit_preview(category, current_amount)

        new_amount = self.commands.get_budget_amount()

        result = self.budget_service.set_budget(
            category,
            new_amount
        )
        print(result)

    def _select_budget(self):
        """
        Display budgets and allow user selection.

        Returns:
            tuple:
                (category, amount)
            None:
                if cancelled or no budgets exist
        """

        budgets = self.budget_service.get_all_budgets()

        if not budgets:
            print("\nNo budgets have been set.\n")
            return None

        print("\nSelect Budget")
        print("-" * 35)

        categories = list(budgets.keys())

        for index, category in enumerate(categories, start=1):
            print(
                f"{index}. "
                f"{category.title():<15}"
                f"${budgets[category]:.2f}"
            )

        while True:

            choice = input(
                "\nEnter budget number (0 to cancel): "
            ).strip()

            if choice == "0":
                print("Operation cancelled.")
                return None

            if not choice.isdigit():
                print(
                    "✗ Please enter a valid number."
                )
                continue

            index = int(choice)

            if index < 1 or index > len(categories):
                print(
                    "✗ Invalid budget number."
                )
                continue

            category = categories[index - 1]

            return (
                category,
                budgets[category]
            )

    def _delete_budget(self):
        """Delete a budget for a selected category."""

        budget = self._select_budget()

        if budget is None:
            return

        category, amount = budget

        confirm = input(
            f"\nDelete budget for "
            f"'{category.title()}' "
            f"(${amount:.2f})? (y/n): "
        ).strip().lower()

        if confirm != "y":
            print(
                "Deletion cancelled."
            )
            return

        if self.budget_service.delete_budget(category):
            print(
                "✓ Budget deleted successfully."
            )
        else:
            print(
                "✗ Budget could not be deleted."
            )

    def _clear_all_budgets(self):
        """Clear all budgets after confirmation."""

        budgets = self.budget_service.get_all_budgets()

        if not budgets:
            print("\nNo budgets to clear.\n")
            return

        print("\n⚠ WARNING")
        print("This will permanently delete ALL budgets.")
        print("This action cannot be undone.\n")

        confirm = input(
            "Type 'YES' to continue: "
        ).strip()

        if confirm != "YES":
            print("\nOperation cancelled.")
            return

        self.budget_service.clear_all_budgets()

        print("\n✓ All budgets have been deleted successfully.\n")

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

    def _import_expenses(self):
        """Import expenses from a CSV file."""
        print("\n--- Import Expenses from CSV ---")

        file_path = self.commands.get_csv_file_path()

        if file_path is None:
            return

        print(f"\nSelected file: {file_path}")
        print("\nCSV import service is not implemented yet.")