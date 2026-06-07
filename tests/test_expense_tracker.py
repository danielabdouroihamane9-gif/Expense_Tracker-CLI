"""
Test script for Expense Tracker - validates all core functionality
"""

from expense_tracker import Expense, ExpenseTracker, VALID_CATEGORIES
import json
import os


def test_expense_validation():
    """Test Expense class validation."""
    print("\n" + "=" * 50)
    print("TEST 1: Expense Class Validation")
    print("=" * 50)

    # Valid expense
    try:
        exp = Expense("2025-05-28", 50.00, "food", "Lunch")
        print(f"✓ Valid expense created: {exp}")
    except ValueError as e:
        print(f"✗ Failed: {e}")

    # Invalid date
    try:
        exp = Expense("28/05/2025", 50.00, "food", "Lunch")
        print(f"✗ Should have failed on invalid date")
    except ValueError as e:
        print(f"✓ Caught invalid date: {e}")

    # Invalid amount (negative)
    try:
        exp = Expense("2025-05-28", -50.00, "food", "Lunch")
        print(f"✗ Should have failed on negative amount")
    except ValueError as e:
        print(f"✓ Caught negative amount: {e}")

    # Invalid category
    try:
        exp = Expense("2025-05-28", 50.00, "pizza", "Lunch")
        print(f"✗ Should have failed on invalid category")
    except ValueError as e:
        print(f"✓ Caught invalid category: {e}")

    # Empty description
    try:
        exp = Expense("2025-05-28", 50.00, "food", "")
        print(f"✗ Should have failed on empty description")
    except ValueError as e:
        print(f"✓ Caught empty description: {e}")


def test_tracker_crud():
    """Test ExpenseTracker CRUD operations."""
    print("\n" + "=" * 50)
    print("TEST 2: ExpenseTracker CRUD Operations")
    print("=" * 50)

    # Clean up old test file
    if os.path.exists("expenses.json"):
        os.remove("expenses.json")

    tracker = ExpenseTracker()

    # Add expenses
    print("\nAdding test expenses...")
    result = tracker.add_expense("2025-05-28", 50.00, "food", "Lunch")
    print(f"  {result}")

    result = tracker.add_expense("2025-05-27", 30.00, "transport", "Bus fare")
    print(f"  {result}")

    result = tracker.add_expense("2025-05-26", 1000.00, "rent", "Monthly rent")
    print(f"  {result}")

    result = tracker.add_expense("2025-05-28", 25.00, "food", "Coffee")
    print(f"  {result}")

    # Get all expenses
    print(f"\n✓ Total expenses: {len(tracker.expenses)}")

    # Get by category
    food_expenses = tracker.get_by_category("food")
    print(f"✓ Food expenses: {len(food_expenses)}")
    for exp in food_expenses:
        print(f"  - ${exp.amount:.2f} on {exp.date}: {exp.description}")

    # Monthly summary
    summary = tracker.get_monthly_summary(2025, 5)
    print(f"\n✓ May 2025 Summary:")
    for category, total in sorted(summary.items()):
        print(f"  - {category.capitalize()}: ${total:.2f}")


def test_persistence():
    """Test JSON save/load functionality."""
    print("\n" + "=" * 50)
    print("TEST 3: JSON Persistence")
    print("=" * 50)

    # Create and save
    tracker1 = ExpenseTracker()
    tracker1.add_expense("2025-05-28", 50.00, "food", "Dinner")
    tracker1.add_expense("2025-05-27", 100.00, "entertainment", "Movie")

    print(f"✓ Created and saved {len(tracker1.expenses)} expenses")

    # Load into new tracker
    tracker2 = ExpenseTracker()
    print(f"✓ Loaded {len(tracker2.expenses)} expenses from file")

    if len(tracker1.expenses) == len(tracker2.expenses):
        print("✓ Persistence working correctly")
    else:
        print(
            f"✗ Mismatch: saved {len(tracker1.expenses)}, loaded {len(tracker2.expenses)}"
        )


def test_edge_cases():
    """Test edge cases."""
    print("\n" + "=" * 50)
    print("TEST 4: Edge Cases")
    print("=" * 50)

    tracker = ExpenseTracker()

    # Zero amount
    result = tracker.add_expense("2025-05-28", 0, "food", "Free meal")
    print(f"  Zero amount: {result}")

    # Non-numeric amount
    result = tracker.add_expense("2025-05-28", "abc", "food", "Lunch")
    print(f"  Non-numeric: {result}")

    # Decimal precision
    result = tracker.add_expense("2025-05-28", 19.99, "food", "Precise amount")
    print(f"  Decimal precision: {result}")

    # Case-insensitive category
    result = tracker.add_expense("2025-05-28", 50.00, "FOOD", "Uppercase category")
    print(f"  Case insensitive: {result}")

    # Future date
    result = tracker.add_expense("2099-12-31", 50.00, "food", "Future expense")
    print(f"  Future date: {result}")


if __name__ == "__main__":
    print("\n" + "█" * 50)
    print("█  EXPENSE TRACKER - COMPREHENSIVE TEST SUITE  █")
    print("█" * 50)

    test_expense_validation()
    test_tracker_crud()
    test_persistence()
    test_edge_cases()

    print("\n" + "█" * 50)
    print("█  ALL TESTS COMPLETED                        █")
    print("█" * 50 + "\n")
