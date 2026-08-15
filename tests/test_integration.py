"""System-level tests spanning CLI, services, persistence, and CSV."""

from src.cli.commands import CommandHandler
from src.cli.menu import Menu
from src.services import (
    BudgetService,
    ExpenseTrackerService,
    ExportService,
    SettingsService,
)


def test_interactive_add_expense_persists_through_menu(tmp_path, monkeypatch):
    menu = Menu(tmp_path / "data", tmp_path / "exports")
    answers = iter(["1", "1", "1", "2025-05-28", "25.50", "food", "Lunch", "0", "0", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    menu.run()
    reloaded = ExpenseTrackerService(tmp_path / "data")
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
    tracker = ExpenseTrackerService(data_dir)
    budgets = BudgetService(data_dir)
    csv_service = ExportService(export_dir)
    source = tmp_path / "expenses.csv"
    source.write_text(
        "Date,Amount,Category,Description\n"
        "2025-05-01,20,food,Breakfast\n"
        "2025-05-02,40,food,Dinner\n"
        "2025-05-03,15,transport,Bus\n"
    )
    success, rows, errors = csv_service.read_expenses_csv(source)
    assert success is True and errors == []
    assert tracker.import_expenses(rows)["imported"] == 3
    assert "Budget set" in budgets.set_budget("food", 100)
    summary = tracker.get_monthly_summary(2025, 5)
    status = budgets.get_budget_status(summary, 2025, 5)
    assert summary == {"food": 60.0, "transport": 15.0}
    assert status["food"]["remaining"] == 40.0
    assert status["food"]["warning"] is False
    assert "Exported 3 expenses" in csv_service.export_expenses_to_csv(tracker.get_all_expenses(), "result.csv")
    assert "Exported summary" in csv_service.export_summary_to_csv(summary, "summary.csv")
    assert (export_dir / "result.csv").exists()
    assert (export_dir / "summary.csv").exists()
    assert ExpenseTrackerService(data_dir).get_expense_count() == 3
    assert BudgetService(data_dir).get_budget("food") == 100.0


def test_configured_currency_flows_through_complete_system(tmp_path):
    data_dir, export_dir = tmp_path / "data", tmp_path / "exports"
    assert "changed to KMF" in SettingsService(data_dir).set_currency("KMF")

    tracker = ExpenseTrackerService(data_dir)
    budgets = BudgetService(data_dir)
    csv_service = ExportService(export_dir, currency="KMF")
    assert tracker.add_expense("2025-05-01", "1200", "food", "Lunch").startswith("✓")
    assert budgets.set_budget("food", "5000").startswith("✓")

    expense = ExpenseTrackerService(data_dir).expenses[0]
    assert expense.currency == "KMF"
    assert BudgetService(data_dir).currency == "KMF"
    assert csv_service.export_expenses_to_csv([expense], "expenses.csv").startswith("✓")
    assert csv_service.export_summary_to_csv(
        {"food": expense.amount}, "summary.csv"
    ).startswith("✓")
    assert ",KMF," in (export_dir / "expenses.csv").read_text()
    assert ",KMF" in (export_dir / "summary.csv").read_text()
