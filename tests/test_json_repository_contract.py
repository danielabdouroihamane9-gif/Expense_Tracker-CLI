"""Apply reusable repository contracts to the JSON implementation."""

from src.repositories import BudgetRepository, ExpenseRepository, SettingsRepository
from src.storage import JSONStorage

from tests.repository_contracts import (
    assert_budget_repository_contract,
    assert_expense_repository_contract,
    assert_settings_repository_contract,
)


def test_json_storage_implements_declared_repository_protocols(tmp_path):
    repository = JSONStorage(tmp_path)
    assert isinstance(repository, ExpenseRepository)
    assert isinstance(repository, BudgetRepository)
    assert isinstance(repository, SettingsRepository)


def test_json_expense_repository_contract(tmp_path):
    assert_expense_repository_contract(JSONStorage(tmp_path))


def test_json_budget_repository_contract(tmp_path):
    assert_budget_repository_contract(JSONStorage(tmp_path))


def test_json_settings_repository_contract(tmp_path):
    assert_settings_repository_contract(JSONStorage(tmp_path))
