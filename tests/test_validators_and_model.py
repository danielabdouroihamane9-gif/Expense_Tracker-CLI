from datetime import date

import pytest

from src.models import Expense
from src.utils.validators import (
    VALID_CATEGORIES,
    validate_amount,
    validate_budget_amount,
    validate_category,
    validate_date,
    validate_description,
)


def test_valid_categories_are_stable():
    assert {"food", "transport", "rent", "utilities", "entertainment", "healthcare", "shopping", "other"} == VALID_CATEGORIES


@pytest.mark.parametrize("value, expected", [("10", 10.0), (19.999, 20.0), ("0.005", 0.01)])
def test_validate_amount_accepts_and_rounds_positive_numbers(value, expected):
    assert validate_amount(value) == expected


@pytest.mark.parametrize("validator", [validate_amount, validate_budget_amount])
@pytest.mark.parametrize("value", [0, -1, "not-a-number"])
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
    expense = Expense("2025-05-28", "12.345", " FOOD ", " Lunch ")
    restored = Expense.from_dict(expense.to_dict())

    assert restored == expense
    assert expense.to_dict() == {"date": "2025-05-28", "amount": 12.35, "category": "food", "description": "Lunch"}
    assert "Expense(2025-05-28, $12.35, food, Lunch)" == repr(expense)
    assert expense != object()
