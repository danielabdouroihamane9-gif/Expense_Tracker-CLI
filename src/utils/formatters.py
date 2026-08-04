"""Formatting utilities for displaying expense data."""


def format_currency(amount):
    """Format amount as currency string."""
    return f"${amount:.2f}"

def format_date(date):
    """Format date object as string."""
    return str(date)

def display_expenses_table(expenses, title="Expenses"):
    """Display expenses in a formatted table using f-strings."""
    if not expenses:
        print(f"\n{title}: No expenses found.\n")
        return

    print(f"\n{title}:")
    print(f"{'No':<4} {'Date':<12} {'Amount':<10} {'Category':<15} {'Description':<30}")
    print("-" * 67)

    for index, expense in enumerate(expenses, start=1):
        print(
            f"{index:<4} {str(expense.date):<12} ${expense.amount:<9.2f} {expense.category:<15} {expense.description:<30}"
        )
    print()

def display_summary(summary, year=None, month=None):
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
        print(f"{category.capitalize():<20} ${amount:<14.2f}")

    print("-" * 50)
    print(f"{'Total':<20} ${total:<14.2f}")
    print(f"{'=' * 50}\n")

def display_budget_status(status):
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
            f"${spent:<11.2f}"
            f"${budget:<11.2f}"
            f"${remaining:<11.2f}"
            f"{percentage:<9.2f}"
            f"{status_text:<17}"
        )        
    print(f"{'=' * 80}\n")

def display_budgets(budgets):
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
            f"{index:<4}"
            f"{category.title():<18}"
            f"${amount:<9.2f}"
        )

    print()

def display_expense_details(expense):
    """Display detailed information for a single expense."""

    print("\nExpense Details")
    print("-" * 30)

    print(f"Date: {expense.date}")
    print(f"Amount: ${expense.amount:.2f}")
    print(f"Category: {expense.category}")
    print(f"Description: {expense.description}")

    print()

def display_spending_by_category(spending):
    """Display total spending grouped by category"""

    if not spending:
        print("\nNo expenses found.\n")
        return

    print("-" * 35)
    print(f"{'Category':<20}{'Total'}")
    print("-" * 35)

    grand_total = 0

    for category, total in spending.items():
        print(
            f"{category.title():<20}"
            f"${total:.2f}"
        )
        grand_total += total

    print("-" * 35)
    print(f"{'Grand Total':<20}${grand_total:.2f}\n")

def display_duplicate_expenses(expense):
    """Display duplicate expenses in a formatted table."""

    if expense is None:
        return
    
    print("\n--- Duplicate Expense ---")
    print(f"Category    : {expense.category}")
    print(f"Description : {expense.description}")
    print(f"Amount      : ${expense.amount:.2f}")
    print(f"Original Date : {expense.date}")

    print("\nEnter the new date.")

def display_expense_statistics(stats):
    """Display expense statistics in a formatted output."""
    if stats["count"] == 0:
        print("\nNo expenses found.\n")
        return

    print("-" * 45)

    print(
        f"{'Number of Expenses':<25}"
        f"{stats['count']}"
    )
    print(
        f"{'Total Spending':<25}"
        f"${stats['total']:.2f}"
    )
    print(
        f"{'Average Expense':<25}"
        f"${stats['average']:.2f}"
    )
    print(
        f"{'Highest Expense':<25}"
        f"${stats['highest'].amount:.2f}"
    )
    print(
        f"{'Lowest Expense':<25}"
        f"${stats['lowest'].amount:.2f}"
    )
    print("-" * 45)

    print("\nHighest Expense Details")

    print(
        f"{'ID':<15}"
        f"{stats['highest_index']}"
    )
    print(
        f"Category    : "
        f"{stats['highest'].category}"
    )
    print(
        f"Description : "
        f"{stats['highest'].description}"
    )
    print(
        f"Date        : "
        f"{stats['highest'].date}"
    )

    print("\nLowest Expense Details")

    print(
        f"{'ID':<15}"
        f"{stats['lowest_index']}"
    )
    print(
        f"Category    : "
        f"{stats['lowest'].category}"
    )
    print(
        f"Description : "
        f"{stats['lowest'].description}"
    )
    print(
        f"Date        : "
        f"{stats['lowest'].date}"
    )

    print()

def display_top_spending_categories(categories):
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
        print(
            f"{index}. "
            f"{category.title():<20}"
            f"${amount:.2f}"
        )

    print("-" * 40)
    print()

def display_budget_edit_preview(category, current_amount):
    """Display information about the budget being edited."""

    print(
        f"\nEditing budget: "
        f"{category.title()}"
    )

    print(
        f"Current amount: "
        f"${current_amount:.2f}"
    )

def display_import_summary(summary):
    """Display the results of a CSV import."""
    print(f"\n{'=' * 45}")
    print("CSV Import Summary")
    print(f"{'=' * 45}")

    print(
        f"{'Imported Successfully':<25}"
        f"{summary['imported']}"
    )

    print(
        f"{'Skipped Duplicates':<25}"
        f"{summary['skipped_duplicates']}"
    )

    print(
        f"{'Failed Imports':<25}"
        f"{summary['failed']}"
    )

    if summary["errors"]:
        print("-" * 45)
        print("Errors:")

        for error in summary["errors"]:
            print(f"• {error}")

    print(f"{'=' * 45}\n")