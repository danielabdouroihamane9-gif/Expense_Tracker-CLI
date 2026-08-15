import json
from decimal import Decimal
import pytest

from src.models import Expense
from src.storage import JSONStorage


def test_missing_storage_files_return_empty_collections(tmp_path):
    storage = JSONStorage(tmp_path)
    assert storage.load_expenses() == []
    assert storage.load_budgets() == {}


def test_storage_creates_missing_parent_directories(tmp_path):
    nested_data_dir = tmp_path / "missing-parent" / "data"
    storage = JSONStorage(nested_data_dir)

    assert storage.data_dir == nested_data_dir
    assert nested_data_dir.is_dir()


def test_expenses_and_budgets_persist_between_instances(tmp_path):
    storage = JSONStorage(tmp_path)
    expenses = [Expense("2025-01-02", 8.5, "food", "Breakfast")]
    budgets = {"food": Decimal("250.00")}

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


def test_storage_writes_versioned_schema_and_exact_money(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.save_expenses([Expense("2025-01-02", "8.5", "food", "Breakfast")])
    storage.save_budgets({"food": Decimal("250")})

    expenses_document = json.loads(storage.expenses_file.read_text())
    budgets_document = json.loads(storage.budgets_file.read_text())
    assert expenses_document["schema_version"] == 2
    assert expenses_document["currency"] == "USD"
    assert expenses_document["expenses"][0]["amount"] == "8.50"
    assert expenses_document["expenses"][0]["currency"] == "USD"
    assert "id" in expenses_document["expenses"][0]
    assert "created_at" in expenses_document["expenses"][0]
    assert budgets_document == {
        "schema_version": 2,
        "currency": "USD",
        "budgets": {"food": "250.00"},
    }


def test_legacy_json_loads_and_is_upgraded_on_next_save(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text(json.dumps([{
        "date": "2025-01-02", "amount": 8.5,
        "category": "food", "description": "Breakfast",
    }]))
    storage.budgets_file.write_text(json.dumps({"food": 250.0}))

    expenses = storage.load_expenses()
    budgets = storage.load_budgets()
    assert expenses[0].amount == Decimal("8.50")
    assert expenses[0].currency == "USD"
    assert budgets == {"food": Decimal("250.0")}

    storage.save_expenses(expenses)
    storage.save_budgets(budgets)
    assert json.loads(storage.expenses_file.read_text())["schema_version"] == 2
    assert json.loads(storage.budgets_file.read_text())["schema_version"] == 2


def test_legacy_expense_uses_configured_currency(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.save_settings({"currency": "KMF"})
    storage.expenses_file.write_text(json.dumps([{
        "date": "2025-01-02", "amount": 1500,
        "category": "food", "description": "Lunch",
    }]))

    expenses = storage.load_expenses()
    assert expenses[0].currency == "KMF"
    storage.save_expenses(expenses)
    document = json.loads(storage.expenses_file.read_text())
    assert document["currency"] == "KMF"
    assert document["expenses"][0]["currency"] == "KMF"


@pytest.mark.parametrize(
    "filename, document, loader",
    [
        (
            "expenses.json",
            {"schema_version": 2, "currency": "EUR", "expenses": []},
            "load_expenses",
        ),
        (
            "budgets.json",
            {"schema_version": 2, "currency": "EUR", "budgets": {}},
            "load_budgets",
        ),
    ],
)
def test_versioned_document_currency_mismatch_is_rejected(
    tmp_path, filename, document, loader
):
    storage = JSONStorage(tmp_path)
    (tmp_path / filename).write_text(json.dumps(document))

    with pytest.raises(RuntimeError, match="configured for USD"):
        getattr(storage, loader)()
