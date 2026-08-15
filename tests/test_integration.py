"""System-level tests spanning CLI, services, persistence, and CSV."""

from src.cli.commands import CommandHandler
from src.cli.menu import Menu
from src.services import (
    BudgetService,
    ExpenseTrackerService,
    ExportService,
    SettingsService,
)
from src.storage import JSONStorage


def build_services(data_dir):
    repository = JSONStorage(data_dir)
    return (
        ExpenseTrackerService(repository, repository),
        BudgetService(repository, repository),
        SettingsService(repository, repository, repository),
    )


def test_interactive_add_expense_persists_through_menu(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    tracker, budgets, settings = build_services(data_dir)
    menu = Menu(
        settings,
        tracker,
        budgets,
        ExportService(tmp_path / "exports"),
    )
    answers = iter(["1", "1", "1", "2025-05-28", "25.50", "food", "Lunch", "0", "0", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    menu.run()
    reloaded, _, _ = build_services(data_dir)
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
    tracker, budgets, _ = build_services(data_dir)
    csv_service = ExportService(export_dir)
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
    assert csv_service.export_expenses_to_csv(
        tracker.get_all_expenses(), "result.csv"
    ).record_count == 3
    assert csv_service.export_summary_to_csv(summary, "summary.csv").kind == "summary"
    assert (export_dir / "result.csv").exists()
    assert (export_dir / "summary.csv").exists()
    reloaded_tracker, reloaded_budgets, _ = build_services(data_dir)
    assert reloaded_tracker.get_expense_count() == 3
    assert reloaded_budgets.get_budget("food") == 100.0


def test_configured_currency_flows_through_complete_system(tmp_path):
    data_dir, export_dir = tmp_path / "data", tmp_path / "exports"
    tracker, budgets, settings = build_services(data_dir)
    assert settings.set_currency("KMF").changed is True

    tracker, budgets, _ = build_services(data_dir)
    csv_service = ExportService(export_dir, currency="KMF")
    assert tracker.add_expense(
        "2025-05-01", "1200", "food", "Lunch"
    ).currency == "KMF"
    assert budgets.set_budget("food", "5000").amount == 5000

    reloaded_tracker, reloaded_budgets, _ = build_services(data_dir)
    expense = reloaded_tracker.expenses[0]
    assert expense.currency == "KMF"
    assert reloaded_budgets.currency == "KMF"
    assert csv_service.export_expenses_to_csv(
        [expense], "expenses.csv"
    ).record_count == 1
    assert csv_service.export_summary_to_csv(
        {"food": expense.amount}, "summary.csv"
    ).kind == "summary"
    assert ",KMF," in (export_dir / "expenses.csv").read_text()
    assert ",KMF" in (export_dir / "summary.csv").read_text()
