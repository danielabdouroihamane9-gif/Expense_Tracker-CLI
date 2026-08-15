"""Persistence-agnostic repository protocols."""

from decimal import Decimal
from typing import Mapping, Protocol, Sequence, runtime_checkable

from src.models import Expense


@runtime_checkable
class ExpenseRepository(Protocol):
    """Contract for loading and saving the complete expense collection."""

    def load_expenses(self) -> list[Expense]: ...

    def save_expenses(self, expenses: Sequence[Expense]) -> None: ...


@runtime_checkable
class BudgetRepository(Protocol):
    """Contract for loading and saving category budgets."""

    def load_budgets(self) -> dict[str, Decimal]: ...

    def save_budgets(self, budgets: Mapping[str, Decimal]) -> None: ...


@runtime_checkable
class SettingsRepository(Protocol):
    """Contract for loading and saving application settings."""

    def load_settings(self) -> dict[str, str]: ...

    def save_settings(self, settings: Mapping[str, str]) -> None: ...
