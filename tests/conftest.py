"""Shared pytest fixtures for the expense tracker test suite."""

import pytest

from src.models import Expense


@pytest.fixture
def sample_expenses():
    """A deliberately unsorted collection used by service/export tests."""
    return [
        Expense("2025-05-28", 50, "food", "Lunch"),
        Expense("2025-05-26", 30, "transport", "Bus fare"),
        Expense("2025-06-01", 100, "entertainment", "Concert"),
    ]
