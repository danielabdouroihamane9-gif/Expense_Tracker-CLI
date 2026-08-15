"""Application-wide currency configuration tests."""

import json

from src.services import BudgetService, ExpenseTrackerService, SettingsService


def test_default_currency_is_usd(tmp_path):
    settings = SettingsService(tmp_path)
    assert settings.get_currency() == "USD"


def test_currency_change_is_persisted_when_financial_data_is_empty(tmp_path):
    settings = SettingsService(tmp_path)
    assert "changed to KMF" in settings.set_currency(" kmf ")
    assert SettingsService(tmp_path).get_currency() == "KMF"
    assert json.loads((tmp_path / "settings.json").read_text()) == {
        "schema_version": 2,
        "currency": "KMF",
    }


def test_currency_change_is_blocked_when_expenses_exist(tmp_path):
    tracker = ExpenseTrackerService(tmp_path)
    tracker.add_expense("2025-01-01", 10, "food", "Lunch")

    result = SettingsService(tmp_path).set_currency("KMF")
    assert "cannot be changed" in result
    assert SettingsService(tmp_path).get_currency() == "USD"


def test_currency_change_is_blocked_when_budgets_exist(tmp_path):
    budgets = BudgetService(tmp_path)
    budgets.set_budget("food", 100)

    result = SettingsService(tmp_path).set_currency("EUR")
    assert "cannot be changed" in result
    assert SettingsService(tmp_path).get_currency() == "USD"


def test_invalid_currency_does_not_change_settings(tmp_path):
    settings = SettingsService(tmp_path)
    assert "three-letter" in settings.set_currency("US")
    assert settings.get_currency() == "USD"
