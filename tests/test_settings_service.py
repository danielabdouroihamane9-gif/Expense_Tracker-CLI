"""Application-wide currency configuration tests."""

import json
from unittest.mock import MagicMock

import pytest

from src.exceptions import CurrencyChangeBlockedError, DomainValidationError
from src.services import BudgetService, ExpenseTrackerService, SettingsService
from src.storage import JSONStorage, StorageWriteError


def build_services(data_dir):
    repository = JSONStorage(data_dir)
    return (
        SettingsService(repository, repository, repository),
        ExpenseTrackerService(repository, repository),
        BudgetService(repository, repository),
    )


def test_default_currency_is_usd(tmp_path):
    settings, _, _ = build_services(tmp_path)
    assert settings.get_currency() == "USD"


def test_currency_change_is_persisted_when_financial_data_is_empty(tmp_path):
    settings, _, _ = build_services(tmp_path)
    result = settings.set_currency(" kmf ")
    assert result.changed is True and result.currency == "KMF"
    assert build_services(tmp_path)[0].get_currency() == "KMF"
    assert json.loads((tmp_path / "settings.json").read_text()) == {
        "schema_version": 2,
        "currency": "KMF",
    }


def test_currency_change_is_blocked_when_expenses_exist(tmp_path):
    settings, tracker, _ = build_services(tmp_path)
    tracker.add_expense("2025-01-01", 10, "food", "Lunch")

    with pytest.raises(CurrencyChangeBlockedError, match="cannot be changed"):
        settings.set_currency("KMF")
    assert build_services(tmp_path)[0].get_currency() == "USD"


def test_currency_change_is_blocked_when_budgets_exist(tmp_path):
    settings, _, budgets = build_services(tmp_path)
    budgets.set_budget("food", 100)

    with pytest.raises(CurrencyChangeBlockedError, match="cannot be changed"):
        settings.set_currency("EUR")
    assert build_services(tmp_path)[0].get_currency() == "USD"


def test_invalid_currency_does_not_change_settings(tmp_path):
    settings, _, _ = build_services(tmp_path)
    with pytest.raises(DomainValidationError, match="three-letter"):
        settings.set_currency("US")
    assert settings.get_currency() == "USD"


def test_failed_settings_save_does_not_change_in_memory_currency(tmp_path):
    settings, _, _ = build_services(tmp_path)
    settings.settings_repository.save_settings = MagicMock(
        side_effect=StorageWriteError("simulated disk failure")
    )

    with pytest.raises(StorageWriteError):
        settings.set_currency("KMF")

    assert settings.get_currency() == "USD"
