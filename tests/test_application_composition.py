"""Tests for centralized runtime configuration and composition."""

import json
from pathlib import Path

import pytest

from src.application import create_application
from src.config import (
    ApplicationConfig,
    DATA_DIR_ENV,
    DEFAULT_CURRENCY_ENV,
    EXPORT_DIR_ENV,
)
from src.exceptions import DomainValidationError
from src.providers import Clock, UUIDGenerator
from tests.fakes import FixedClock, SequentialUUIDGenerator, TEST_NOW


def test_environment_configuration_resolves_paths_and_currency(tmp_path):
    config = ApplicationConfig.from_environment(
        {
            DATA_DIR_ENV: "runtime/data",
            EXPORT_DIR_ENV: "runtime/exports",
            DEFAULT_CURRENCY_ENV: " kmf ",
        },
        base_dir=tmp_path,
    )

    assert config.data_dir == (tmp_path / "runtime" / "data").resolve()
    assert config.export_dir == (tmp_path / "runtime" / "exports").resolve()
    assert config.default_currency == "KMF"


def test_environment_configuration_uses_documented_defaults(tmp_path):
    config = ApplicationConfig.from_environment(
        {DATA_DIR_ENV: "", EXPORT_DIR_ENV: "   "},
        base_dir=tmp_path,
    )

    assert config.data_dir == (tmp_path / "data").resolve()
    assert config.export_dir == (tmp_path / "exports").resolve()
    assert config.default_currency == "USD"


def test_configuration_rejects_invalid_initial_currency(tmp_path):
    with pytest.raises(DomainValidationError, match="three-letter"):
        ApplicationConfig(tmp_path / "data", tmp_path / "exports", "US")


def test_factory_constructs_complete_application_with_shared_dependencies(tmp_path):
    config = ApplicationConfig(tmp_path / "data", tmp_path / "exports", "KMF")
    clock = FixedClock()
    uuid_generator = SequentialUUIDGenerator()

    application = create_application(
        config,
        clock=clock,
        uuid_generator=uuid_generator,
    )

    assert isinstance(application.clock, Clock)
    assert isinstance(application.uuid_generator, UUIDGenerator)
    assert application.repository is application.expense_service.expense_repository
    assert application.repository is application.budget_service.budget_repository
    assert application.repository is application.settings_service.settings_repository
    assert application.menu.expense_service is application.expense_service
    assert application.menu.commands is application.command_handler
    assert application.menu.currency == "KMF"
    assert application.config is config


def test_initial_currency_is_persisted_and_survives_environment_changes(tmp_path):
    data_dir = tmp_path / "data"
    first = create_application(
        ApplicationConfig(data_dir, tmp_path / "exports", "KMF"),
        clock=FixedClock(),
        uuid_generator=SequentialUUIDGenerator(),
    )
    assert first.settings_service.get_currency() == "KMF"
    assert json.loads((data_dir / "settings.json").read_text()) == {
        "schema_version": 2,
        "currency": "KMF",
    }

    restarted = create_application(
        ApplicationConfig(data_dir, tmp_path / "exports", "USD"),
        clock=FixedClock(),
        uuid_generator=SequentialUUIDGenerator(),
    )
    assert restarted.settings_service.get_currency() == "KMF"


def test_injected_time_and_uuid_control_entity_and_export_defaults(
    tmp_path, monkeypatch
):
    clock = FixedClock()
    application = create_application(
        ApplicationConfig(tmp_path / "data", tmp_path / "exports"),
        clock=clock,
        uuid_generator=SequentialUUIDGenerator(start=42),
    )

    expense = application.expense_service.add_expense(
        "2025-06-16", "12.50", "food", "Lunch"
    )
    assert expense.id.int == 42
    assert expense.created_at == TEST_NOW

    monkeypatch.setattr("builtins.input", lambda _prompt="": "")
    assert application.command_handler.get_user_date() == "2025-06-16"

    result = application.export_service.export_expenses_to_csv([expense])
    assert result.path == Path(tmp_path / "exports" / "expenses_20250616_123000.csv")


def test_injected_providers_control_legacy_metadata_migration(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "expenses.json").write_text(
        json.dumps(
            [
                {
                    "date": "2025-06-15",
                    "amount": "4.50",
                    "category": "transport",
                    "description": "Bus",
                }
            ]
        )
    )

    application = create_application(
        ApplicationConfig(data_dir, tmp_path / "exports"),
        clock=FixedClock(),
        uuid_generator=SequentialUUIDGenerator(start=99),
    )
    expense = application.expense_service.expenses[0]

    assert expense.id.int == 99
    assert expense.created_at == TEST_NOW


def test_only_composition_root_constructs_runtime_components():
    source_root = Path(__file__).parents[1] / "src"
    constructor_names = (
        "JSONStorage(",
        "ExpenseTrackerService(",
        "BudgetService(",
        "ExportService(",
        "SettingsService(",
        "CommandHandler(",
        "Menu(",
    )

    offenders = []
    for path in source_root.rglob("*.py"):
        if path.name == "application.py":
            continue
        source = path.read_text(encoding="utf-8")
        for constructor in constructor_names:
            if constructor in source:
                offenders.append(f"{path.relative_to(source_root)}: {constructor}")

    assert offenders == []


def test_main_is_a_thin_entry_point():
    main_path = Path(__file__).parents[1] / "src" / "main.py"
    source = main_path.read_text(encoding="utf-8")

    assert "create_application" in source
    assert "JSONStorage" not in source
    assert "ExpenseTrackerService" not in source
    assert "BudgetService" not in source
    assert '"data"' not in source
    assert '"exports"' not in source


def test_ambient_time_and_uuid_calls_are_isolated_to_providers():
    source_root = Path(__file__).parents[1] / "src"
    offenders = []
    for path in source_root.rglob("*.py"):
        if path.name == "providers.py":
            continue
        source = path.read_text(encoding="utf-8")
        if "datetime.now" in source or "uuid4(" in source or "date.today" in source:
            offenders.append(str(path.relative_to(source_root)))

    assert offenders == []
