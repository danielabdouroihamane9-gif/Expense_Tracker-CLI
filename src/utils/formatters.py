"""Formatting utilities for displaying expense data."""


def format_currency(amount, currency="USD"):
    """Format amount as currency string."""
    return f"{currency} {amount:.2f}"


def format_date(date):
    """Format date object as string."""
    return str(date)


def display_expenses_table(expenses, title="Expenses"):
    """Display expenses in a formatted table using f-strings."""
    if not expenses:
        print(f"\n{title}: No expenses found.\n")
        return

    print(f"\n{title}:")
    print(f"{'No':<4} {'Date':<12} {'Amount':<15} {'Category':<15} {'Description':<30}")
    print("-" * 72)

    for index, expense in enumerate(expenses, start=1):
        print(
            f"{index:<4} {str(expense.date):<12} "
            f"{format_currency(expense.amount, expense.currency):<15} "
            f"{expense.category:<15} {expense.description:<30}"
        )
    print()


def display_summary(summary, year=None, month=None, currency="USD"):
    """Display monthly summary in formatted output."""
    if not summary:
        print(f"\nNo expenses for {year}-{month:02d}.\n")
        return

    total = sum(summary.values())

    print(f"\n{'=' * 50}")
    print(f"Monthly Summary: {year}-{month:02d}")
    print(f"{'=' * 50}")
    print(f"{'Category':<20} {'Amount':<15}")
    print("-" * 50)

    for category in sorted(summary.keys()):
        amount = summary[category]
        print(f"{category.capitalize():<20} {format_currency(amount, currency):<14}")

    print("-" * 50)
    print(f"{'Total':<20} {format_currency(total, currency):<14}")
    print(f"{'=' * 50}\n")


def display_budget_status(status, currency="USD"):
    """Display budget status with warnings."""
    if not status:
        print("\n✗ No budgets set. Use 'set-budget' to set budget limits.\n")
        return

    print(f"\n{'=' * 80}")
    print(f"{'Budget Status (Current Month)':<60}")
    print(f"{'=' * 80}")
    print(
        f"{'Category':<15}"
        f"{'Spent':<12}"
        f"{'Budget':<12}"
        f"{'Remaining':<12}"
        f"{'Used %':<10}"
        f"{'Status':<18}"
    )
    print("-" * 80)

    for category in sorted(status.keys()):
        info = status[category]
        spent = info["spent"]
        budget = info["budget"]
        remaining = info["remaining"]
        percentage = info["percentage"]
        warning = info["warning"]
        over_budget = info["over_budget"]
        limit = info["limit"]

        if over_budget:
            status_text = "❌  OVER BUDGET"
        elif warning:
            status_text = "⚠️  Near Budget Limit"
        elif limit:
            status_text = " ❗  At Budget Limit"
        else:
            status_text = "✅  Within Budget"

        print(
            f"{category.capitalize():<15}"
            f"{format_currency(spent, currency):<12}"
            f"{format_currency(budget, currency):<12}"
            f"{format_currency(remaining, currency):<12}"
            f"{percentage:<9.2f}"
            f"{status_text:<17}"
        )
    print(f"{'=' * 80}\n")


def display_budgets(budgets, currency="USD"):
    """Display budgets in a numbered table."""

    if not budgets:
        print("\nNo budgets found.\n")
        return

    print("\nBudgets")
    print(f"{'No':<4} {'Category':<18} {'Budget':<10}")
    print("-" * 35)

    for index, (category, amount) in enumerate(
        budgets.items(),
        start=1,
    ):
        print(
            f"{index:<4}{category.title():<18}{format_currency(amount, currency):<12}"
        )

    print()


def display_expense_details(expense):
    """Display detailed information for a single expense."""

    print("\nExpense Details")
    print("-" * 30)

    created_at = expense.created_at.isoformat().replace("+00:00", "Z")

    print(f"ID: {expense.id}")
    print(f"Occurred On: {expense.occurred_on}")
    print(f"Amount: {expense.amount:.2f}")
    print(f"Currency: {expense.currency}")
    print(f"Category: {expense.category}")
    print(f"Description: {expense.description}")
    print(f"Created At (UTC): {created_at}")

    print()


def display_spending_by_category(spending, currency="USD"):
    """Display total spending grouped by category"""

    if not spending:
        print("\nNo expenses found.\n")
        return

    print("-" * 35)
    print(f"{'Category':<20}{'Total'}")
    print("-" * 35)

    grand_total = 0

    for category, total in spending.items():
        print(f"{category.title():<20}{format_currency(total, currency)}")
        grand_total += total

    print("-" * 35)
    print(f"{'Grand Total':<20}{format_currency(grand_total, currency)}\n")


def display_duplicate_expenses(expense):
    """Display duplicate expenses in a formatted table."""

    if expense is None:
        return

    print("\n--- Duplicate Expense ---")
    print(f"Category    : {expense.category}")
    print(f"Description : {expense.description}")
    print(f"Amount      : {format_currency(expense.amount, expense.currency)}")
    print(f"Original Date : {expense.date}")

    print("\nEnter the new date.")


def display_expense_statistics(stats, currency="USD"):
    """Display expense statistics in a formatted output."""
    if stats["count"] == 0:
        print("\nNo expenses found.\n")
        return

    print("-" * 45)

    print(f"{'Number of Expenses':<25}{stats['count']}")
    print(f"{'Total Spending':<25}{format_currency(stats['total'], currency)}")
    print(f"{'Average Expense':<25}{format_currency(stats['average'], currency)}")
    print(
        f"{'Highest Expense':<25}{format_currency(stats['highest'].amount, currency)}"
    )
    print(f"{'Lowest Expense':<25}{format_currency(stats['lowest'].amount, currency)}")
    print("-" * 45)

    print("\nHighest Expense Details")

    print(f"{'ID':<15}{stats['highest_index']}")
    print(f"Category    : {stats['highest'].category}")
    print(f"Description : {stats['highest'].description}")
    print(f"Date        : {stats['highest'].date}")

    print("\nLowest Expense Details")

    print(f"{'ID':<15}{stats['lowest_index']}")
    print(f"Category    : {stats['lowest'].category}")
    print(f"Description : {stats['lowest'].description}")
    print(f"Date        : {stats['lowest'].date}")

    print()


def display_top_spending_categories(categories, currency="USD"):
    """Display highest spending categories."""

    if not categories:
        print("\nNo expenses found.\n")
        return

    print("\n--- Top Spending Categories ---")
    print("-" * 40)

    for index, (category, amount) in enumerate(
        categories,
        start=1,
    ):
        print(f"{index}. {category.title():<20}{format_currency(amount, currency)}")

    print("-" * 40)
    print()


def display_budget_edit_preview(category, current_amount, currency="USD"):
    """Display information about the budget being edited."""

    print(f"\nEditing budget: {category.title()}")

    print(f"Current amount: {format_currency(current_amount, currency)}")


def display_import_summary(summary):
    """Display the results of a CSV import."""
    print(f"\n{'=' * 45}")
    print("CSV Import Summary")
    print(f"{'=' * 45}")

    print(f"{'Imported Successfully':<25}{summary.imported}")

    print(f"{'Skipped Duplicates':<25}{summary.skipped_duplicates}")

    print(f"{'Failed Imports':<25}{summary.failed}")

    if summary.errors:
        print("-" * 45)
        print("Errors:")

        for error in summary.errors:
            print(f"• Row {error.row_number}")
            print(f"  Date        : {error.date}")
            print(f"  Amount      : {error.amount}")
            print(f"  Category    : {error.category}")
            print(f"  Description : {error.description}")
            print(f"  Reason      : {error.reason}")

    print(f"{'=' * 45}\n")
