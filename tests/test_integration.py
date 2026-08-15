"""System-level tests spanning composition, CLI, persistence, and CSV."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.application import create_application
from src.config import ApplicationConfig
from src.storage import StorageRecoveryWarning
from tests.fakes import FixedClock, SequentialUUIDGenerator


def build_application(data_dir, export_dir=None, currency="USD"):
    return create_application(
        ApplicationConfig(
            data_dir=data_dir,
            export_dir=export_dir or data_dir.parent / "exports",
            default_currency=currency,
        ),
        clock=FixedClock(),
        uuid_generator=SequentialUUIDGenerator(),
    )


def test_interactive_add_expense_persists_through_menu(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    application = build_application(data_dir, tmp_path / "exports")
    answers = iter(
        ["1", "1", "1", "2025-05-28", "25.50", "food", "Lunch", "0", "0", "0"]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    application.menu.run()
    reloaded = build_application(data_dir).expense_service
    assert reloaded.get_expense_count() == 1
    stored = reloaded.expenses[0].to_dict()
    assert stored["occurred_on"] == "2025-05-28"
    assert stored["amount"] == "25.50"
    assert stored["currency"] == "USD"
    assert stored["category"] == "food"
    assert stored["description"] == "Lunch"
    assert stored["id"] and stored["created_at"]


def test_import_budget_report_export_and_reload_workflow(tmp_path):
    data_dir, export_dir = tmp_path / "data", tmp_path / "exports"
    application = build_application(data_dir, export_dir)
    tracker = application.expense_service
    budgets = application.budget_service
    csv_service = application.export_service
    source = tmp_path / "expenses.csv"
    source.write_text(
        "Date,Amount,Category,Description\n"
        "2025-05-01,20,food,Breakfast\n"
        "2025-05-02,40,food,Dinner\n"
        "2025-05-03,15,transport,Bus\n"
    )
    rows = csv_service.read_expenses_csv(source)
    assert tracker.import_expenses(rows).imported == 3
    assert budgets.set_budget("food", 100).amount == 100
    summary = tracker.get_monthly_summary(2025, 5)
    status = budgets.get_budget_status(summary, 2025, 5)
    assert summary == {"food": 60.0, "transport": 15.0}
    assert status["food"]["remaining"] == 40.0
    assert status["food"]["warning"] is False
    assert (
        csv_service.export_expenses_to_csv(
            tracker.get_all_expenses(), "result.csv"
        ).record_count
        == 3
    )
    assert csv_service.export_summary_to_csv(summary, "summary.csv").kind == "summary"
    assert (export_dir / "result.csv").exists()
    assert (export_dir / "summary.csv").exists()
    reloaded_application = build_application(data_dir, export_dir)
    reloaded_tracker = reloaded_application.expense_service
    reloaded_budgets = reloaded_application.budget_service
    assert reloaded_tracker.get_expense_count() == 3
    assert reloaded_budgets.get_budget("food") == 100.0


def test_configured_currency_flows_through_complete_system(tmp_path):
    data_dir, export_dir = tmp_path / "data", tmp_path / "exports"
    application = build_application(data_dir, export_dir)
    tracker = application.expense_service
    budgets = application.budget_service
    settings = application.settings_service
    assert settings.set_currency("KMF").changed is True

    application = build_application(data_dir, export_dir)
    tracker = application.expense_service
    budgets = application.budget_service
    csv_service = application.export_service
    assert tracker.add_expense("2025-05-01", "1200", "food", "Lunch").currency == "KMF"
    assert budgets.set_budget("food", "5000").amount == 5000

    reloaded_application = build_application(data_dir, export_dir)
    reloaded_tracker = reloaded_application.expense_service
    reloaded_budgets = reloaded_application.budget_service
    expense = reloaded_tracker.expenses[0]
    assert expense.currency == "KMF"
    assert reloaded_budgets.currency == "KMF"
    assert (
        csv_service.export_expenses_to_csv([expense], "expenses.csv").record_count == 1
    )
    assert (
        csv_service.export_summary_to_csv({"food": expense.amount}, "summary.csv").kind
        == "summary"
    )
    assert ",KMF," in (export_dir / "expenses.csv").read_text()
    assert ",KMF" in (export_dir / "summary.csv").read_text()


def test_application_recovers_from_backup_through_complete_composition(tmp_path):
    data_dir = tmp_path / "data"
    application = build_application(data_dir)
    application.expense_service.add_expense("2025-05-01", "10", "food", "First")
    application.expense_service.add_expense("2025-05-02", "20", "transport", "Second")
    (data_dir / "expenses.json").write_text("not valid JSON")

    with pytest.warns(StorageRecoveryWarning, match="Recovered 'expenses.json'"):
        recovered = build_application(data_dir)

    assert [expense.description for expense in recovered.expense_service.expenses] == [
        "First"
    ]
    restored_document = json.loads((data_dir / "expenses.json").read_text())
    assert len(restored_document["expenses"]) == 1


def test_real_cli_add_and_reload_smoke_workflow(tmp_path):
    repository_root = Path(__file__).parents[1]
    data_dir = tmp_path / "cli-data"
    export_dir = tmp_path / "cli-exports"
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONPATH": str(repository_root),
            "EXPENSE_TRACKER_DATA_DIR": str(data_dir),
            "EXPENSE_TRACKER_EXPORT_DIR": str(export_dir),
            "EXPENSE_TRACKER_DEFAULT_CURRENCY": "USD",
        }
    )
    answers = "\n".join(
        [
            "1",
            "1",
            "1",
            "2025-05-28",
            "25.50",
            "food",
            "CLI smoke",
            "0",
            "0",
            "0",
            "",
        ]
    )

    completed = subprocess.run(
        [sys.executable, "-m", "src.main"],
        input=answers,
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=environment,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Expense added: USD 25.50" in completed.stdout
    assert "Goodbye" in completed.stdout
    document = json.loads((data_dir / "expenses.json").read_text())
    assert document["schema_version"] == 2
    assert document["currency"] == "USD"
    assert document["expenses"][0]["description"] == "CLI smoke"
