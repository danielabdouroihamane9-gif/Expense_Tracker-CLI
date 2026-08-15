from datetime import date
from unittest.mock import MagicMock

import pytest

from src.models import Expense
from src.services import ExpenseTrackerService
from src.exceptions import CurrencyMismatchError, DomainValidationError
from src.storage import JSONStorage, StorageWriteError


def build_service(data_dir):
    repository = JSONStorage(data_dir)
    return ExpenseTrackerService(repository, repository)


def make_service(tmp_path, expenses=()):
    service = build_service(tmp_path)
    service.expenses = list(expenses)
    return service


def test_add_expense_validates_and_persists(tmp_path):
    service = make_service(tmp_path)
    expense = service.add_expense("2025-05-28", "12.50", "FOOD", "Lunch")
    assert expense.amount == 12.50
    assert service.get_expense_count() == 1
    assert build_service(tmp_path).expenses == service.expenses


def test_invalid_expense_is_reported_and_not_saved(tmp_path):
    service = make_service(tmp_path)
    with pytest.raises(DomainValidationError):
        service.add_expense("bad-date", 10, "food", "Lunch")
    assert service.expenses == []


def test_query_filter_search_and_monthly_summary(tmp_path, sample_expenses):
    service = make_service(tmp_path, sample_expenses)
    assert [e.date for e in service.get_all_expenses()] == [date(2025, 6, 1), date(2025, 5, 28), date(2025, 5, 26)]
    assert [e.description for e in service.get_by_category(" FOOD ")] == ["Lunch"]
    assert service.get_by_category("invalid") == []
    assert [e.description for e in service.search_expenses("BUS")] == ["Bus fare"]
    assert len(service.search_expenses("entertain")) == 1
    assert service.get_monthly_summary(2025, 5) == {"food": 50.0, "transport": 30.0}


def test_analytics_cover_empty_and_populated_data(tmp_path, sample_expenses):
    service = make_service(tmp_path)
    assert service.get_spending_by_category() == {}
    assert service.get_top_spending_categories() == []
    assert service.get_expense_statistics() == {"count": 0, "total": 0, "highest": None, "lowest": None, "average": 0}

    service.expenses = sample_expenses
    assert service.get_spending_by_category() == {"entertainment": 100.0, "food": 50.0, "transport": 30.0}
    assert service.get_top_spending_categories(2) == [("entertainment", 100.0), ("food", 50.0)]
    stats = service.get_expense_statistics()
    assert (stats["count"], stats["total"], stats["average"]) == (3, 180.0, 60.0)
    assert stats["highest"].description == "Concert"
    assert stats["lowest"].description == "Bus fare"


def test_sort_and_date_range(tmp_path, sample_expenses):
    service = make_service(tmp_path, sample_expenses)
    assert [e.amount for e in service.get_sorted_expenses("amount", True)] == [100.0, 50.0, 30.0]
    assert [e.category for e in service.get_sorted_expenses("category")] == ["entertainment", "food", "transport"]
    assert len(service.get_by_date_range(date(2025, 5, 27), date(2025, 6, 1))) == 2
    assert service.get_sorted_expenses("unknown") == service.get_all_expenses()


def test_update_delete_duplicate_and_clear_persist(tmp_path):
    service = make_service(tmp_path)
    service.add_expense("2025-05-28", 10, "food", "Lunch")
    original = service.expenses[0]

    assert service.update_expense(original, 20, "transport", "Taxi") is True
    assert build_service(tmp_path).expenses[0].to_dict()["amount"] == "20.00"
    duplicate = service.duplicate_expense(original, "2025-05-29")
    assert duplicate.date == date(2025, 5, 29)
    assert service.get_expense_count() == 2
    assert service.delete_expense(object()) is False
    assert service.delete_expense(original) is True
    assert service.clear_all_expenses() is True


def test_add_rejects_currency_different_from_application_setting(tmp_path):
    service = make_service(tmp_path)
    with pytest.raises(CurrencyMismatchError, match="application currency USD"):
        service.add_expense(
            "2025-05-28", 10, "food", "Lunch", currency="EUR"
        )
    assert service.expenses == []
    assert build_service(tmp_path).expenses == []


def test_update_is_validated_and_atomic(tmp_path):
    service = make_service(tmp_path, [Expense("2025-05-28", 10, "food", "Lunch")])
    expense = service.expenses[0]
    before = expense.to_dict()

    with pytest.raises(ValueError):
        service.update_expense(expense, -1, "invalid", "")

    assert expense.to_dict() == before
    assert service.update_expense(object(), 10, "food", "Lunch") is False


def test_duplicate_does_not_claim_success_when_new_date_is_invalid(tmp_path):
    original = Expense("2025-05-28", 10, "food", "Lunch")
    service = make_service(tmp_path, [original])
    with pytest.raises(DomainValidationError):
        service.duplicate_expense(original, "not-a-date")
    assert service.get_expense_count() == 1


def test_import_reports_success_duplicates_and_bad_rows(tmp_path):
    existing = Expense("2025-05-28", 10, "food", "Lunch")
    service = make_service(tmp_path, [existing])
    rows = [
        {"Date": "2025-05-28", "Amount": "10", "Category": "FOOD", "Description": "Lunch"},
        {"Date": "2025-05-29", "Amount": "20", "Category": "transport", "Description": "Taxi"},
        {"Date": "bad", "Amount": "3", "Category": "food", "Description": "Invalid"},
        {"Date": "2025-05-30"},
    ]
    result = service.import_expenses(rows)
    assert result.imported == 1
    assert result.skipped_duplicates == 1
    assert result.failed == 2
    assert result.errors[0].row_number == 4
    assert build_service(tmp_path).get_expense_count() == 2


def test_failed_saves_roll_back_every_expense_mutation(tmp_path):
    first = Expense("2025-05-28", 10, "food", "Lunch")
    second = Expense("2025-05-29", 20, "transport", "Taxi")
    service = make_service(tmp_path, [first, second])
    before = [expense.to_dict() for expense in service.expenses]
    service.expense_repository.save_expenses = MagicMock(
        side_effect=StorageWriteError("simulated disk failure")
    )

    with pytest.raises(StorageWriteError):
        service.add_expense("2025-05-30", 30, "rent", "Rent")
    assert [expense.to_dict() for expense in service.expenses] == before

    with pytest.raises(StorageWriteError):
        service.update_expense(first, 99, "shopping", "Changed")
    assert [expense.to_dict() for expense in service.expenses] == before

    with pytest.raises(StorageWriteError):
        service.delete_expense(first)
    assert [expense.to_dict() for expense in service.expenses] == before

    with pytest.raises(StorageWriteError):
        service.clear_all_expenses()
    assert [expense.to_dict() for expense in service.expenses] == before

    with pytest.raises(StorageWriteError):
        service.import_expenses([{
            "Date": "2025-06-01",
            "Amount": "40",
            "Category": "other",
            "Description": "Imported",
        }])
    assert [expense.to_dict() for expense in service.expenses] == before
