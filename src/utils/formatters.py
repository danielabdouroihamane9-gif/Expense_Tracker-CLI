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

    print(f"\n{'=' * 70}")
    print(f"{'Budget Status (Current Month)':<70}")
    print(f"{'=' * 70}")
    print(f"{'Category':<15} {'Spent':<12} {'Budget':<12} {'%':<8} {'Status':<15}")
    print("-" * 70)

    for category in sorted(status.keys()):
        info = status[category]
        spent = info["spent"]
        budget = info["budget"]
        percentage = info["percentage"]
        warning = info["warning"]

        status_text = "⚠️  ALERT 80%" if warning else "✓ OK"

        print(
            f"{category.capitalize():<15} ${spent:<11.2f} ${budget:<11.2f} {percentage:<7.1f}% {status_text:<15}"
        )

    print(f"{'=' * 70}\n")


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