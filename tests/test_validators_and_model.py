from datetime import date
from decimal import Decimal

import pytest

from src.exceptions import DomainValidationError
from src.models import Expense
from src.utils.validators import (
    VALID_CATEGORIES,
    validate_amount,
    validate_budget_amount,
    validate_category,
    validate_date,
    validate_description,
    validate_currency,
)


def test_valid_categories_are_stable():
    assert {"food", "transport", "rent", "utilities", "entertainment", "healthcare", "shopping", "other"} == VALID_CATEGORIES


@pytest.mark.parametrize("value, expected", [("10", Decimal("10.00")), (19.999, Decimal("20.00")), ("0.005", Decimal("0.01"))])
def test_validate_amount_accepts_and_rounds_positive_numbers(value, expected):
    assert validate_amount(value) == expected


@pytest.mark.parametrize("validator", [validate_amount, validate_budget_amount])
@pytest.mark.parametrize("value", [0, -1, "not-a-number", "NaN", "Infinity"])
def test_amount_validators_reject_invalid_values(validator, value):
    with pytest.raises(ValueError):
        validator(value)


def test_date_category_and_description_are_normalized():
    assert validate_date("2025-02-28") == date(2025, 2, 28)
    assert validate_category("  FOOD ") == "food"
    assert validate_description("  lunch  ") == "lunch"


@pytest.mark.parametrize("value", ["2025-02-29", "28/02/2025", ""])
def test_invalid_dates_are_rejected(value):
    with pytest.raises(ValueError, match="Invalid date format"):
        validate_date(value)


def test_invalid_category_and_blank_description_are_rejected():
    with pytest.raises(ValueError, match="Invalid category"):
        validate_category("travel")
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_description("   ")


def test_expense_round_trip_equality_and_repr():
    expense = Expense(
        "2025-05-28", "12.345", " FOOD ", " Lunch ",
        expense_id="12345678-1234-5678-1234-567812345678",
        currency="usd", created_at="2025-05-28T10:00:00Z",
    )
    restored = Expense.from_dict(expense.to_dict(), default_currency="USD")

    assert restored == expense
    assert expense.to_dict() == {
        "id": "12345678-1234-5678-1234-567812345678",
        "amount": "12.35", "currency": "USD", "category": "food",
        "description": "Lunch", "occurred_on": "2025-05-28",
        "created_at": "2025-05-28T10:00:00Z",
    }
    assert "Expense(2025-05-28, USD 12.35, food, Lunch)" == repr(expense)
    assert expense != object()


def test_expense_requires_identity_and_creation_time():
    with pytest.raises(DomainValidationError, match="ID is required"):
        Expense(
            "2025-05-28",
            12.5,
            "food",
            "Lunch",
            expense_id=None,
            currency="USD",
            created_at="2025-05-28T10:00:00Z",
        )


@pytest.mark.parametrize("value, expected", [(" usd ", "USD"), ("eur", "EUR")])
def test_currency_is_normalized(value, expected):
    assert validate_currency(value) == expected


@pytest.mark.parametrize("value", ["US", "USDD", "12A", None])
def test_invalid_currency_is_rejected(value):
    with pytest.raises(ValueError):
        validate_currency(value)
