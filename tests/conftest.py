"""Shared pytest fixtures for the expense tracker test suite."""

from pathlib import Path

import pytest

from tests.fakes import make_expense


def _directory_snapshot(directory):
    """Capture file contents and mtimes so rewrites are also detected."""
    if not directory.exists():
        return {}
    return {
        path.relative_to(directory): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in directory.rglob("*")
        if path.is_file()
    }


@pytest.fixture(scope="session", autouse=True)
def protect_production_data():
    """Fail the suite if any test creates or changes repository runtime data."""
    data_directory = Path(__file__).parents[1] / "data"
    before = _directory_snapshot(data_directory)
    yield
    after = _directory_snapshot(data_directory)
    assert after == before, "Automated tests modified the repository data directory"


@pytest.fixture
def sample_expenses():
    """A deliberately unsorted collection used by service/export tests."""
    return [
        make_expense(
            "2025-05-28",
            50,
            "food",
            "Lunch",
            expense_id="00000000-0000-0000-0000-000000000001",
        ),
        make_expense(
            "2025-05-26",
            30,
            "transport",
            "Bus fare",
            expense_id="00000000-0000-0000-0000-000000000002",
        ),
        make_expense(
            "2025-06-01",
            100,
            "entertainment",
            "Concert",
            expense_id="00000000-0000-0000-0000-000000000003",
        ),
    ]
