"""
Enhanced Test Suite for Expense Tracker - Tests all Phase 2 features
"""

from expense_tracker_enhanced import Expense, ExpenseTracker, VALID_CATEGORIES
import json
import os
import csv
from pathlib import Path


def cleanup():
    """Clean up test files."""
    for file in [
        "expenses.json",
        "budgets.json",
        "test_expenses.csv",
        "test_summary.csv",
    ]:
        if Path(file).exists():
            os.remove(file)


def test_budget_features():
    """Test budget limit features."""
    print("\n" + "=" * 50)
    print("TEST 1: Budget Limit Features")
    print("=" * 50)

    cleanup()
    tracker = ExpenseTracker()

    # Set budgets
    print("\nSetting budgets...")
    result = tracker.set_budget("food", 300)
    print(f"  {result}")
    assert "✓" in result

    result = tracker.set_budget("transport", 100)
    print(f"  {result}")
    assert "✓" in result

    # Get budget
    budget = tracker.get_budget("food")
    print(f"✓ Food budget: ${budget:.2f}")
    assert budget == 300.0

    # Get all budgets
    budgets = tracker.get_all_budgets()
    print(f"✓ Total budgets set: {len(budgets)}")
    assert len(budgets) == 2

    # Add expenses
    print("\nAdding expenses...")
    tracker.add_expense("2025-05-28", 150, "food", "Groceries")
    tracker.add_expense("2025-05-27", 120, "food", "Restaurant")
    tracker.add_expense("2025-05-26", 60, "transport", "Gas")

    # Get budget status (should show warnings)
    print("\nChecking budget status...")
    today = os.getcwd()  # Just for demo
    status = tracker.get_budget_status()

    for category, info in status.items():
        percentage = info["percentage"]
        warning = info["warning"]

        if warning:
            print(
                f"  ⚠️  {category.capitalize()}: {percentage:.1f}% (WARNING - 80%+ threshold)"
            )
        else:
            print(f"  ✓ {category.capitalize()}: {percentage:.1f}% (OK)")

        assert info["spent"] > 0
        assert info["budget"] > 0

    # Test invalid category
    result = tracker.set_budget("invalid", 100)
    print(f"\n✓ Invalid budget: {result}")
    assert "✗" in result

    print("\n✓ Budget features working correctly!")


def test_csv_export():
    """Test CSV export features."""
    print("\n" + "=" * 50)
    print("TEST 2: CSV Export Features")
    print("=" * 50)

    cleanup()
    tracker = ExpenseTracker()

    # Add test expenses
    print("\nAdding test expenses...")
    tracker.add_expense("2025-05-28", 50, "food", "Lunch")
    tracker.add_expense("2025-05-27", 30, "transport", "Bus")
    tracker.add_expense("2025-05-26", 100, "entertainment", "Movie")
    print(f"✓ Added 3 expenses")

    # Export all expenses
    print("\nExporting all expenses...")
    result = tracker.export_to_csv("test_all.csv")
    print(f"  {result}")
    assert "✓" in result
    assert Path("test_all.csv").exists()

    # Verify CSV content
    with open("test_all.csv", "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 4  # Header + 3 expenses
        assert rows[0] == ["Date", "Amount", "Category", "Description"]
    print("✓ CSV format correct")

    # Export by category
    print("\nExporting filtered expenses...")
    result = tracker.export_to_csv("test_food.csv", "food")
    print(f"  {result}")
    assert Path("test_food.csv").exists()

    with open("test_food.csv", "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2  # Header + 1 food expense
    print("✓ Category filter working")

    # Export summary
    print("\nExporting summary...")
    result = tracker.export_summary_to_csv("test_summary.csv")
    print(f"  {result}")
    assert Path("test_summary.csv").exists()

    with open("test_summary.csv", "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert rows[0] == ["Category", "Amount"]
        assert len(rows) == 5  # Header + 3 categories + total
    print("✓ Summary export working")

    print("\n✓ CSV export features working correctly!")


def test_persistence_with_budgets():
    """Test that budgets persist like expenses."""
    print("\n" + "=" * 50)
    print("TEST 3: Budget Persistence")
    print("=" * 50)

    cleanup()

    # Create and save budgets
    print("\nCreating tracker and setting budgets...")
    tracker1 = ExpenseTracker()
    tracker1.set_budget("food", 500)
    tracker1.set_budget("rent", 1500)
    print(f"✓ Set 2 budgets")

    # Load into new tracker
    print("\nLoading into new tracker...")
    tracker2 = ExpenseTracker()
    budgets = tracker2.get_all_budgets()

    assert len(budgets) == 2
    assert budgets["food"] == 500.0
    assert budgets["rent"] == 1500.0

    print(f"✓ Budgets persisted correctly")


def test_export_with_budgets():
    """Test exporting with budget context."""
    print("\n" + "=" * 50)
    print("TEST 4: Export with Budget Context")
    print("=" * 50)

    cleanup()
    tracker = ExpenseTracker()

    # Set budget
    tracker.set_budget("food", 100)

    # Add expenses
    tracker.add_expense("2025-05-28", 40, "food", "Breakfast")
    tracker.add_expense("2025-05-28", 35, "food", "Lunch")
    tracker.add_expense("2025-05-28", 30, "food", "Dinner")

    # Export
    result = tracker.export_to_csv("test_budget.csv")
    print(f"  {result}")
    assert "✓" in result

    # Get status
    status = tracker.get_budget_status()
    food_status = status["food"]

    print(f"\n  Budget: ${food_status['budget']:.2f}")
    print(f"  Spent: ${food_status['spent']:.2f}")
    print(f"  Percentage: {food_status['percentage']:.1f}%")
    print(f"  Warning: {food_status['warning']}")

    assert food_status["percentage"] > 100
    assert food_status["warning"] == True

    print("\n✓ Budget context working correctly!")


def test_edge_cases_enhanced():
    """Test edge cases for new features."""
    print("\n" + "=" * 50)
    print("TEST 5: Edge Cases for Enhanced Features")
    print("=" * 50)

    cleanup()
    tracker = ExpenseTracker()

    # Zero budget
    print("\nTesting edge cases...")
    result = tracker.set_budget("food", 0)
    print(f"  Zero budget: {result}")
    assert "✗" in result

    # Negative budget
    result = tracker.set_budget("food", -100)
    print(f"  Negative budget: {result}")
    assert "✗" in result

    # Export with no expenses
    result = tracker.export_to_csv("empty.csv")
    print(f"  Export empty: {result}")
    assert "✗" in result or "No expenses" in result

    # Budget status with no budgets
    status = tracker.get_budget_status()
    print(f"  Budget status (no budgets): {len(status)} items")
    assert len(status) == 0

    print("\n✓ Edge cases handled correctly!")


def test_integration():
    """Integration test combining all features."""
    print("\n" + "=" * 50)
    print("TEST 6: Full Integration Test")
    print("=" * 50)

    cleanup()
    tracker = ExpenseTracker()

    print("\n1. Setting budgets...")
    tracker.set_budget("food", 300)
    tracker.set_budget("transport", 100)
    tracker.set_budget("entertainment", 200)
    print("✓ Budgets set")

    print("\n2. Adding expenses...")
    tracker.add_expense("2025-05-28", 50, "food", "Lunch")
    tracker.add_expense("2025-05-27", 40, "food", "Dinner")
    tracker.add_expense("2025-05-26", 30, "transport", "Gas")
    tracker.add_expense("2025-05-25", 80, "entertainment", "Movie")
    print("✓ 4 expenses added")

    print("\n3. Checking summary...")
    summary = tracker.get_monthly_summary()
    print(f"✓ Summary: {len(summary)} categories")

    print("\n4. Checking budget status...")
    status = tracker.get_budget_status()
    print(f"✓ Budget status: {len(status)} categories tracked")

    print("\n5. Exporting all data...")
    r1 = tracker.export_to_csv("integration.csv")
    r2 = tracker.export_summary_to_csv("integration_summary.csv")
    print(f"  Expenses: {r1}")
    print(f"  Summary: {r2}")
    print("✓ Both exports successful")

    print("\n6. Verifying persistence...")
    tracker2 = ExpenseTracker()
    assert len(tracker2.expenses) == 4
    assert len(tracker2.budgets) == 3
    print("✓ All data persisted")

    print("\n✓ Full integration test passed!")


if __name__ == "__main__":
    print("\n" + "█" * 50)
    print("█  ENHANCED EXPENSE TRACKER - TEST SUITE       █")
    print("█" * 50)

    test_budget_features()
    test_csv_export()
    test_persistence_with_budgets()
    test_export_with_budgets()
    test_edge_cases_enhanced()
    test_integration()

    cleanup()

    print("\n" + "█" * 50)
    print("█  ALL TESTS COMPLETED SUCCESSFULLY           █")
    print("█" * 50 + "\n")
