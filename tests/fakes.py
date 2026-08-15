"""Deterministic test doubles for repository and runtime boundaries."""

from datetime import datetime, timezone
from itertools import count
from uuid import UUID

from src.models import Expense
from src.storage import JSONStorage


TEST_NOW = datetime(2025, 6, 16, 12, 30, tzinfo=timezone.utc)


class FixedClock:
    """Return one deterministic time for every call."""

    def __init__(self, current=TEST_NOW):
        self.current = current

    def now(self):
        return self.current


class SequentialUUIDGenerator:
    """Generate stable, unique UUIDs without randomness."""

    def __init__(self, start=1):
        self._values = count(start)

    def new_uuid(self):
        return UUID(int=next(self._values))


def make_json_storage(path, currency="USD", *, clock=None, uuid_generator=None):
    """Build JSON storage with all runtime dependencies explicit."""
    return JSONStorage(
        path,
        default_currency=currency,
        clock=clock or FixedClock(),
        uuid_generator=uuid_generator or SequentialUUIDGenerator(),
    )


def make_expense(
    date,
    amount,
    category,
    description,
    *,
    currency="USD",
    expense_id="12345678-1234-5678-1234-567812345678",
    created_at=TEST_NOW,
):
    """Build an expense without ambient time or random UUID behavior."""
    return Expense(
        date,
        amount,
        category,
        description,
        expense_id=expense_id,
        currency=currency,
        created_at=created_at,
    )


class InMemoryRepository:
    """Implement all three repository contracts without file or JSON behavior."""

    def __init__(self, currency="USD"):
        self.expenses = []
        self.budgets = {}
        self.settings = {"currency": currency}

    def load_expenses(self):
        return self.expenses.copy()

    def save_expenses(self, expenses):
        self.expenses = list(expenses)

    def load_budgets(self):
        return self.budgets.copy()

    def save_budgets(self, budgets):
        self.budgets = dict(budgets)

    def load_settings(self):
        return self.settings.copy()

    def save_settings(self, settings):
        self.settings = dict(settings)
