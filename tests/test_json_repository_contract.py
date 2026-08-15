"""Apply reusable repository contracts to the JSON implementation."""

from src.repositories import BudgetRepository, ExpenseRepository, SettingsRepository
from tests.repository_contracts import (
    assert_budget_repository_contract,
    assert_expense_repository_contract,
    assert_settings_repository_contract,
)
from tests.fakes import make_json_storage


def test_json_storage_implements_declared_repository_protocols(tmp_path):
    repository = make_json_storage(tmp_path)
    assert isinstance(repository, ExpenseRepository)
    assert isinstance(repository, BudgetRepository)
    assert isinstance(repository, SettingsRepository)


def test_json_expense_repository_contract(tmp_path):
    assert_expense_repository_contract(make_json_storage(tmp_path))


def test_json_budget_repository_contract(tmp_path):
    assert_budget_repository_contract(make_json_storage(tmp_path))


def test_json_settings_repository_contract(tmp_path):
    assert_settings_repository_contract(make_json_storage(tmp_path))
