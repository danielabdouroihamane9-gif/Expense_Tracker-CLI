"""Shared pytest fixtures for the expense tracker test suite."""

import pytest

from tests.fakes import make_expense


@pytest.fixture
def sample_expenses():
    """A deliberately unsorted collection used by service/export tests."""
    return [
        make_expense("2025-05-28", 50, "food", "Lunch", expense_id="00000000-0000-0000-0000-000000000001"),
        make_expense("2025-05-26", 30, "transport", "Bus fare", expense_id="00000000-0000-0000-0000-000000000002"),
        make_expense("2025-06-01", 100, "entertainment", "Concert", expense_id="00000000-0000-0000-0000-000000000003"),
    ]
