"""Architecture tests for repository and presentation boundaries."""

from decimal import Decimal
from pathlib import Path

from src.repositories import BudgetRepository, ExpenseRepository, SettingsRepository
from src.services import BudgetService, ExpenseTrackerService, SettingsService
from tests.fakes import FixedClock, InMemoryRepository, SequentialUUIDGenerator


def test_services_operate_with_a_non_json_repository():
    repository = InMemoryRepository()
    assert isinstance(repository, ExpenseRepository)
    assert isinstance(repository, BudgetRepository)
    assert isinstance(repository, SettingsRepository)

    clock = FixedClock()
    tracker = ExpenseTrackerService(
        repository,
        repository,
        clock=clock,
        uuid_generator=SequentialUUIDGenerator(),
    )
    budgets = BudgetService(repository, repository, clock=clock)
    settings = SettingsService(repository, repository, repository)

    expense = tracker.add_expense("2025-01-01", "12.50", "food", "Lunch")
    budgets.set_budget("food", "100")

    assert repository.expenses == [expense]
    assert repository.budgets == {"food": Decimal("100.00")}
    assert settings.get_currency() == "USD"


def test_service_modules_do_not_import_json_or_storage_implementations():
    service_directory = Path(__file__).parents[1] / "src" / "services"
    for path in service_directory.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "JSONStorage" not in source, path.name
        assert "src.storage" not in source, path.name
        for presentation_symbol in ("✓", "✗", "✅", "❌", "⚠", "❗"):
            assert presentation_symbol not in source, path.name


def test_cli_module_does_not_import_storage_implementations():
    menu_path = Path(__file__).parents[1] / "src" / "cli" / "menu.py"
    source = menu_path.read_text(encoding="utf-8")
    assert "JSONStorage" not in source
    assert "src.storage" not in source


def test_service_results_do_not_contain_cli_status_symbols():
    repository = InMemoryRepository()
    clock = FixedClock()
    tracker = ExpenseTrackerService(
        repository,
        repository,
        clock=clock,
        uuid_generator=SequentialUUIDGenerator(),
    )
    budgets = BudgetService(repository, repository, clock=clock)
    settings = SettingsService(repository, repository, repository)

    results = (
        tracker.add_expense("2025-01-01", 10, "food", "Lunch"),
        budgets.set_budget("food", 100),
        settings.set_currency("USD"),
    )

    for result in results:
        representation = repr(result)
        assert "✓" not in representation
        assert "✗" not in representation
