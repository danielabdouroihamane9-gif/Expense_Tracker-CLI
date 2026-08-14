import json

from src.models import Expense
from src.storage import JSONStorage


def test_missing_storage_files_return_empty_collections(tmp_path):
    storage = JSONStorage(tmp_path)
    assert storage.load_expenses() == []
    assert storage.load_budgets() == {}


def test_expenses_and_budgets_persist_between_instances(tmp_path):
    storage = JSONStorage(tmp_path)
    expenses = [Expense("2025-01-02", 8.5, "food", "Breakfast")]
    budgets = {"food": 250.0}

    storage.save_expenses(expenses)
    storage.save_budgets(budgets)

    reloaded = JSONStorage(tmp_path)
    assert reloaded.load_expenses() == expenses
    assert reloaded.load_budgets() == budgets


def test_corrupt_json_is_handled_without_crashing(tmp_path, capsys):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text("not-json")
    storage.budgets_file.write_text("{")

    assert storage.load_expenses() == []
    assert storage.load_budgets() == {}
    assert "Error loading" in capsys.readouterr().out


def test_invalid_expense_records_are_ignored_as_a_failed_load(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text(json.dumps([{"date": "bad", "amount": 1, "category": "food", "description": "x"}]))
    assert storage.load_expenses() == []
