"""Reusable behavioral contracts for future repository implementations."""

from decimal import Decimal

from src.models import Expense


def assert_expense_repository_contract(repository):
    """Verify the minimum expense repository behavior expected by services."""
    expense = Expense(
        "2025-01-02",
        "12.50",
        "food",
        "Contract lunch",
        expense_id="12345678-1234-5678-1234-567812345678",
        created_at="2025-01-02T10:30:00Z",
    )
    assert repository.load_expenses() == []
    repository.save_expenses([expense])
    assert repository.load_expenses() == [expense]
    repository.save_expenses([])
    assert repository.load_expenses() == []


def assert_budget_repository_contract(repository):
    """Verify the minimum budget repository behavior expected by services."""
    assert repository.load_budgets() == {}
    repository.save_budgets({"food": Decimal("125.50")})
    assert repository.load_budgets() == {"food": Decimal("125.50")}
    repository.save_budgets({})
    assert repository.load_budgets() == {}


def assert_settings_repository_contract(repository):
    """Verify the minimum settings repository behavior expected by services."""
    assert repository.load_settings() == {"currency": "USD"}
    repository.save_settings({"currency": "KMF"})
    assert repository.load_settings() == {"currency": "KMF"}
