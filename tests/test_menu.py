"""Unit tests for menu routing and CLI orchestration."""

from datetime import date
from unittest.mock import MagicMock

import pytest

from src.cli.menu import Menu
from src.models import Expense


@pytest.fixture
def menu():
    instance = Menu.__new__(Menu)
    instance.expense_service = MagicMock()
    instance.budget_service = MagicMock()
    instance.export_service = MagicMock()
    instance.commands = MagicMock()
    return instance


def set_inputs(monkeypatch, *values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))


@pytest.mark.parametrize(
    "method, choice, target",
    [
        ("run", "1", "_expense_menu"), ("run", "2", "_budget_menu"),
        ("run", "3", "_reports_menu"), ("run", "4", "_export_menu"),
        ("_expense_menu", "1", "_manage_expenses_menu"), ("_expense_menu", "2", "_search_filter_menu"),
        ("_expense_menu", "3", "_sort_expenses"),
        ("_reports_menu", "1", "_expense_reports_menu"), ("_reports_menu", "2", "_budget_reports_menu"),
        ("_export_menu", "1", "_export_data_menu"), ("_export_menu", "2", "_import_data_menu"),
    ],
)
def test_menu_routes_to_selected_submenu(menu, monkeypatch, method, choice, target):
    action = MagicMock()
    setattr(menu, target, action)
    set_inputs(monkeypatch, choice, "0")
    getattr(menu, method)()
    action.assert_called_once_with()


@pytest.mark.parametrize(
    "method, choice, target",
    [
        ("_manage_expenses_menu", "1", "_add_expense"), ("_manage_expenses_menu", "2", "_edit_expense"),
        ("_manage_expenses_menu", "3", "_duplicate_expense"), ("_manage_expenses_menu", "4", "_view_all_expenses"),
        ("_manage_expenses_menu", "5", "_view_expense_details"), ("_manage_expenses_menu", "6", "_delete_expense"),
        ("_manage_expenses_menu", "7", "_clear_all_expenses"),
        ("_search_filter_menu", "1", "_search_expenses"), ("_search_filter_menu", "2", "_filter_by_category"),
        ("_search_filter_menu", "3", "_filter_by_date"),
        ("_budget_menu", "1", "_set_budget"), ("_budget_menu", "2", "_edit_budget"),
        ("_budget_menu", "3", "_view_all_budgets"), ("_budget_menu", "4", "_delete_budget"),
        ("_budget_menu", "5", "_clear_all_budgets"),
        ("_expense_reports_menu", "1", "_monthly_summary"), ("_expense_reports_menu", "2", "_expense_statistics"),
        ("_expense_reports_menu", "3", "_spending_by_category"), ("_expense_reports_menu", "4", "_top_spending_categories"),
        ("_budget_reports_menu", "1", "_view_budget_status"),
        ("_export_data_menu", "1", "_export_expenses"), ("_export_data_menu", "2", "_export_summary"),
        ("_import_data_menu", "1", "_import_expenses"),
    ],
)
def test_submenu_routes_to_selected_action(menu, monkeypatch, method, choice, target):
    action = MagicMock()
    setattr(menu, target, action)
    set_inputs(monkeypatch, choice, "0")
    getattr(menu, method)()
    action.assert_called_once_with()


@pytest.mark.parametrize("method", ["run", "_expense_menu", "_manage_expenses_menu", "_search_filter_menu", "_budget_menu", "_reports_menu", "_expense_reports_menu", "_budget_reports_menu", "_export_menu", "_export_data_menu", "_import_data_menu"])
def test_menus_reject_invalid_choice_then_allow_back(menu, monkeypatch, capsys, method):
    set_inputs(monkeypatch, "invalid", "0")
    getattr(menu, method)()
    assert "Invalid" in capsys.readouterr().out


def test_add_expense_collects_inputs_and_calls_service(menu, capsys):
    menu.commands.get_user_date.return_value = "2025-01-01"
    menu.commands.get_user_amount.return_value = "12"
    menu.commands.get_user_category.return_value = "food"
    menu.commands.get_user_description.return_value = "Lunch"
    menu.expense_service.add_expense.return_value = "added"
    menu._add_expense()
    menu.expense_service.add_expense.assert_called_once_with("2025-01-01", "12", "food", "Lunch")
    assert "added" in capsys.readouterr().out


def test_select_expense_retries_and_returns_selection(menu, monkeypatch, capsys):
    expenses = [Expense("2025-01-02", 20, "food", "Dinner")]
    menu.expense_service.get_all_expenses.return_value = expenses
    set_inputs(monkeypatch, "x", "2", "1")
    assert menu._select_expense() is expenses[0]
    assert "valid number" in capsys.readouterr().out


def test_select_expense_handles_empty_and_cancel(menu, monkeypatch):
    menu.expense_service.get_all_expenses.return_value = []
    assert menu._select_expense() is None
    menu.expense_service.get_all_expenses.return_value = [Expense("2025-01-01", 1, "food", "x")]
    set_inputs(monkeypatch, "0")
    assert menu._select_expense() is None


def test_sort_expenses_maps_choice(menu, monkeypatch):
    expense = Expense("2025-01-01", 1, "food", "x")
    menu.expense_service.get_all_expenses.return_value = [expense]
    menu.expense_service.get_sorted_expenses.return_value = [expense]
    set_inputs(monkeypatch, "bad", "3")
    menu._sort_expenses()
    menu.expense_service.get_sorted_expenses.assert_called_once_with("amount", True)


def test_delete_and_clear_expenses_respect_confirmation(menu, monkeypatch):
    expense = Expense("2025-01-01", 1, "food", "x")
    menu._select_expense = MagicMock(return_value=expense)
    set_inputs(monkeypatch, "n")
    menu._delete_expense()
    menu.expense_service.delete_expense.assert_not_called()
    menu.expense_service.get_all_expenses.return_value = [expense]
    set_inputs(monkeypatch, "YES")
    menu._clear_all_expenses()
    menu.expense_service.clear_all_expenses.assert_called_once_with()


def test_select_budget_retries_and_delete_confirms(menu, monkeypatch):
    menu.budget_service.get_all_budgets.return_value = {"food": 100.0}
    set_inputs(monkeypatch, "x", "2", "1")
    assert menu._select_budget() == ("food", 100.0)
    menu._select_budget = MagicMock(return_value=("food", 100.0))
    menu.budget_service.delete_budget.return_value = True
    set_inputs(monkeypatch, "y")
    menu._delete_budget()
    menu.budget_service.delete_budget.assert_called_once_with("food")


def test_edit_expense_handles_invalid_amount_without_crashing(menu, monkeypatch, capsys):
    expense = Expense("2025-01-01", 1, "food", "x")
    menu._select_expense = MagicMock(return_value=expense)
    set_inputs(monkeypatch, "not-a-number", "", "")
    menu._edit_expense()
    menu.expense_service.update_expense.assert_not_called()
    assert "Unable to update" in capsys.readouterr().out


def test_filter_search_and_reports_delegate(menu, monkeypatch):
    expense = Expense("2025-01-01", 5, "food", "Lunch")
    menu.commands.get_user_date_range.return_value = (date(2025, 1, 1), date(2025, 1, 31))
    menu.expense_service.get_by_date_range.return_value = [expense]
    menu._filter_by_date()
    menu.commands.get_user_keyword.return_value = "lunch"
    menu.expense_service.search_expenses.return_value = [expense]
    menu._search_expenses()
    menu.expense_service.get_spending_by_category.return_value = {"food": 5.0}
    menu.expense_service.get_top_spending_categories.return_value = [("food", 5.0)]
    menu.expense_service.get_expense_statistics.return_value = {
        "count": 1, "total": 5.0, "average": 5.0,
        "highest": expense, "lowest": expense,
        "highest_index": 1, "lowest_index": 1,
    }
    menu._spending_by_category()
    menu._top_spending_categories()
    menu._expense_statistics()
    menu.expense_service.get_by_date_range.assert_called_once()
    menu.expense_service.search_expenses.assert_called_once_with("lunch")


def test_export_and_import_orchestration(menu):
    expense = Expense("2025-01-01", 5, "food", "Lunch")
    menu.commands.get_export_filename.return_value = "out.csv"
    menu.expense_service.get_all_expenses.return_value = [expense]
    menu.export_service.export_expenses_to_csv.return_value = "ok"
    menu._export_expenses()
    menu.export_service.export_expenses_to_csv.assert_called_once_with([expense], "out.csv")

    menu.commands.get_csv_file_path.return_value = "in.csv"
    rows = [{"Date": "2025-01-01", "Amount": "5", "Category": "food", "Description": "Lunch"}]
    menu.export_service.read_expenses_csv.return_value = (True, rows, [])
    menu.expense_service.import_expenses.return_value = {"imported": 1, "skipped_duplicates": 0, "failed": 0, "errors": []}
    menu._import_expenses()
    menu.expense_service.import_expenses.assert_called_once_with(rows)


def test_import_cancel_and_read_failure_do_not_import(menu, capsys):
    menu.commands.get_csv_file_path.return_value = None
    menu._import_expenses()
    menu.export_service.read_expenses_csv.assert_not_called()
    menu.commands.get_csv_file_path.return_value = "bad.csv"
    menu.export_service.read_expenses_csv.return_value = (False, [], ["bad file"])
    menu._import_expenses()
    menu.expense_service.import_expenses.assert_not_called()
    assert "bad file" in capsys.readouterr().out
