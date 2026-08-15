import json
import os
from decimal import Decimal
from pathlib import Path
import pytest

from src.storage import (
    DataCorruptionError,
    JSONStorage,
    StorageReadError,
    StorageRecoveryWarning,
    StorageWriteError,
    UnsupportedSchemaVersionError,
)
from tests.fakes import make_expense


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
    expenses = [make_expense("2025-01-02", 8.5, "food", "Breakfast")]
    budgets = {"food": Decimal("250.00")}

    storage.save_expenses(expenses)
    storage.save_budgets(budgets)

    reloaded = JSONStorage(tmp_path)
    assert reloaded.load_expenses() == expenses
    assert reloaded.load_budgets() == budgets


def test_corrupt_json_without_backup_raises_explicit_error(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text("not-json")
    storage.budgets_file.write_text("{")

    with pytest.raises(DataCorruptionError, match="invalid JSON"):
        storage.load_expenses()
    with pytest.raises(DataCorruptionError, match="invalid JSON"):
        storage.load_budgets()


def test_invalid_expense_records_raise_explicit_error(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text(json.dumps([{"date": "bad", "amount": 1, "category": "food", "description": "x"}]))
    with pytest.raises(DataCorruptionError, match="invalid expense"):
        storage.load_expenses()


def test_storage_writes_versioned_schema_and_exact_money(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.save_expenses([make_expense("2025-01-02", "8.5", "food", "Breakfast")])
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


def test_transitional_v2_documents_without_envelope_currency_are_upgraded(
    tmp_path,
):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text(json.dumps({
        "schema_version": 2,
        "expenses": [{
            "date": "2025-01-02",
            "amount": "8.50",
            "currency": "USD",
            "category": "food",
            "description": "Breakfast",
        }],
    }))
    storage.budgets_file.write_text(json.dumps({
        "schema_version": 2,
        "budgets": {"food": "250.00"},
    }))

    expenses = storage.load_expenses()
    budgets = storage.load_budgets()
    assert expenses[0].currency == "USD"
    assert budgets == {"food": Decimal("250.00")}

    storage.save_expenses(expenses)
    storage.save_budgets(budgets)
    assert json.loads(storage.expenses_file.read_text())["currency"] == "USD"
    assert json.loads(storage.budgets_file.read_text())["currency"] == "USD"


def test_transitional_v2_expense_currency_conflict_is_rejected(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text(json.dumps({
        "schema_version": 2,
        "expenses": [{
            "date": "2025-01-02",
            "amount": "8.50",
            "currency": "EUR",
            "category": "food",
            "description": "Breakfast",
        }],
    }))

    with pytest.raises(DataCorruptionError, match="different currency"):
        storage.load_expenses()


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

    with pytest.raises(DataCorruptionError, match="configured for USD"):
        getattr(storage, loader)()


def test_second_save_backs_up_previous_valid_document(tmp_path):
    storage = JSONStorage(tmp_path)
    first = make_expense("2025-01-01", 10, "food", "First")
    second = make_expense("2025-01-02", 20, "transport", "Second")

    storage.save_expenses([first])
    storage.save_expenses([first, second])

    backup = json.loads((tmp_path / "expenses.json.bak").read_text())
    assert [record["description"] for record in backup["expenses"]] == ["First"]


def test_corrupt_primary_is_restored_from_valid_backup(tmp_path):
    storage = JSONStorage(tmp_path)
    first = make_expense("2025-01-01", 10, "food", "First")
    second = make_expense("2025-01-02", 20, "transport", "Second")
    storage.save_expenses([first])
    storage.save_expenses([first, second])
    storage.expenses_file.write_text("truncated")

    with pytest.warns(StorageRecoveryWarning, match="Recovered 'expenses.json'"):
        recovered = storage.load_expenses()

    assert recovered == [first]
    assert JSONStorage(tmp_path).load_expenses() == [first]


def test_budget_and_settings_documents_recover_from_their_own_backups(tmp_path):
    budget_storage = JSONStorage(tmp_path / "budgets")
    budget_storage.save_budgets({"food": Decimal("100")})
    budget_storage.save_budgets({"food": Decimal("200")})
    budget_storage.budgets_file.write_text("invalid")

    settings_storage = JSONStorage(tmp_path / "settings")
    settings_storage.save_settings({"currency": "USD"})
    settings_storage.save_settings({"currency": "KMF"})
    settings_storage.settings_file.write_text("invalid")

    with pytest.warns(StorageRecoveryWarning):
        assert budget_storage.load_budgets() == {"food": Decimal("100.00")}
    with pytest.warns(StorageRecoveryWarning):
        assert settings_storage.load_settings() == {"currency": "USD"}


def test_missing_primary_is_restored_when_valid_backup_exists(tmp_path):
    storage = JSONStorage(tmp_path)
    expense = make_expense("2025-01-01", 10, "food", "First")
    storage.save_expenses([expense])
    os.replace(storage.expenses_file, tmp_path / "expenses.json.bak")

    with pytest.warns(StorageRecoveryWarning):
        assert storage.load_expenses() == [expense]
    assert storage.expenses_file.exists()


def test_invalid_primary_and_backup_raise_recovery_error(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text("invalid")
    (tmp_path / "expenses.json.bak").write_text("also-invalid")

    with pytest.raises(DataCorruptionError, match="Cannot recover"):
        storage.load_expenses()


def test_future_schema_is_rejected_without_falling_back(tmp_path):
    storage = JSONStorage(tmp_path)
    expense = make_expense("2025-01-01", 10, "food", "First")
    storage.save_expenses([expense])
    storage.save_expenses([expense])
    storage.expenses_file.write_text(json.dumps({
        "schema_version": 999,
        "currency": "USD",
        "expenses": [],
    }))

    with pytest.raises(UnsupportedSchemaVersionError, match="version 999"):
        storage.load_expenses()


@pytest.mark.parametrize(
    "document",
    [
        {"schema_version": "2", "currency": "USD", "expenses": []},
        {"schema_version": 2, "currency": "USD", "expenses": {}},
    ],
)
def test_invalid_expense_schema_is_rejected(tmp_path, document):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text(json.dumps(document))

    with pytest.raises(DataCorruptionError):
        storage.load_expenses()


def test_interrupted_replace_preserves_primary_and_removes_temp_file(
    tmp_path, monkeypatch
):
    storage = JSONStorage(tmp_path)
    first = make_expense("2025-01-01", 10, "food", "First")
    second = make_expense("2025-01-02", 20, "transport", "Second")
    storage.save_expenses([first])
    original_document = storage.expenses_file.read_text()
    real_replace = os.replace

    def fail_primary_replace(source, destination):
        if Path(destination) == storage.expenses_file:
            raise OSError("simulated interrupted replacement")
        real_replace(source, destination)

    monkeypatch.setattr("src.storage.json_storage.os.replace", fail_primary_replace)

    with pytest.raises(StorageWriteError, match="interrupted replacement"):
        storage.save_expenses([first, second])

    assert storage.expenses_file.read_text() == original_document
    assert list(tmp_path.glob("*.tmp")) == []
    assert list(tmp_path.glob(".*.tmp")) == []


def test_write_permission_failure_is_explicit_and_creates_no_primary(
    tmp_path, monkeypatch
):
    storage = JSONStorage(tmp_path)

    def deny_temporary_file(*args, **kwargs):
        raise PermissionError("simulated write permission failure")

    monkeypatch.setattr(
        "src.storage.json_storage.tempfile.NamedTemporaryFile",
        deny_temporary_file,
    )

    with pytest.raises(StorageWriteError, match="permission failure"):
        storage.save_expenses([])
    assert not storage.expenses_file.exists()


def test_save_refuses_to_overwrite_a_corrupt_primary(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text("damaged existing data")

    with pytest.raises(DataCorruptionError, match="invalid JSON"):
        storage.save_expenses([])

    assert storage.expenses_file.read_text() == "damaged existing data"
    assert not (tmp_path / "expenses.json.bak").exists()


def test_read_permission_failure_is_not_treated_as_empty_data(tmp_path, monkeypatch):
    storage = JSONStorage(tmp_path)
    storage.expenses_file.write_text("[]")
    real_open = Path.open

    def deny_expenses(path, *args, **kwargs):
        if path == storage.expenses_file:
            raise PermissionError("simulated permission failure")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", deny_expenses)

    with pytest.raises(StorageReadError, match="permission failure"):
        storage.load_expenses()


def test_corrupt_settings_do_not_silently_reset_currency(tmp_path):
    storage = JSONStorage(tmp_path)
    storage.settings_file.write_text("not-json")

    with pytest.raises(DataCorruptionError, match="invalid JSON"):
        storage.load_settings()
