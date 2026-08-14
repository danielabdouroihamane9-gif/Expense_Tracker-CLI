"""Output contract tests for terminal formatters."""

import pytest

from src.models import Expense
from src.utils.formatters import (
    display_budget_edit_preview, display_budget_status, display_budgets,
    display_duplicate_expenses, display_expense_details, display_expense_statistics,
    display_expenses_table, display_import_summary, display_spending_by_category,
    display_summary, display_top_spending_categories, format_currency, format_date,
)


@pytest.fixture
def expense():
    return Expense("2025-01-02", 12.5, "food", "Lunch")


def test_basic_formatters():
    assert format_currency(12.5) == "$12.50"
    assert format_date("2025-01-02") == "2025-01-02"


def test_expense_displays(expense, capsys):
    display_expenses_table([], "Empty")
    assert "No expenses" in capsys.readouterr().out
    display_expenses_table([expense], "Items")
    display_expense_details(expense)
    display_duplicate_expenses(expense)
    output = capsys.readouterr().out
    assert "Items" in output and "$12.50" in output and "Lunch" in output


def test_summary_and_category_displays(capsys):
    display_summary({}, 2025, 1)
    assert "No expenses" in capsys.readouterr().out
    display_summary({"food": 12.5}, 2025, 1)
    display_spending_by_category({"food": 12.5})
    display_top_spending_categories([("food", 12.5)])
    output = capsys.readouterr().out
    assert "Monthly Summary: 2025-01" in output
    assert "Grand Total" in output
    assert "Top Spending Categories" in output


def test_budget_displays(capsys):
    display_budgets({})
    display_budget_status({})
    assert "No budgets" in capsys.readouterr().out
    display_budgets({"food": 100})
    display_budget_edit_preview("food", 100)
    display_budget_status({"food": {"spent": 80, "budget": 100, "remaining": 20, "percentage": 80, "warning": True, "over_budget": False, "limit": False}})
    output = capsys.readouterr().out
    assert "Food" in output and "$100.00" in output and "80.00" in output


def test_statistics_empty_and_populated(expense, capsys):
    display_expense_statistics({"count": 0, "total": 0, "highest": None, "lowest": None, "average": 0})
    assert "No expenses" in capsys.readouterr().out
    display_expense_statistics({"count": 1, "total": 12.5, "average": 12.5, "highest": expense, "lowest": expense, "highest_index": 1, "lowest_index": 1})
    assert "Number of Expenses" in capsys.readouterr().out


def test_import_summary_includes_errors(capsys):
    display_import_summary({"imported": 1, "skipped_duplicates": 2, "failed": 1, "errors": ["Row 4 failed"]})
    output = capsys.readouterr().out
    assert "Imported Successfully" in output and "Row 4 failed" in output
