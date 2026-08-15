"""Validation utilities for expense tracker."""

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from src.exceptions import DomainValidationError

VALID_CATEGORIES = {
    "food",
    "transport",
    "rent",
    "utilities",
    "entertainment",
    "healthcare",
    "shopping",
    "other",
}


def validate_date(date):
    """Validate and parse date string (YYYY-MM-DD format)."""
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except (TypeError, ValueError) as error:
        raise DomainValidationError(
            f"Invalid date format. Use YYYY-MM-DD (got: {date})"
        ) from error


def validate_amount(amount):
    """Return a positive monetary amount rounded to two decimal places."""
    try:
        amount_decimal = Decimal(str(amount))
        if not amount_decimal.is_finite() or amount_decimal <= 0:
            raise DomainValidationError("Amount must be greater than 0")
        return amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError) as error:
        if isinstance(error, DomainValidationError):
            raise
        raise DomainValidationError(f"Invalid amount: {error}") from error


def validate_category(category):
    """Validate category is in predefined list."""
    if not isinstance(category, str):
        raise DomainValidationError("Category must be text")
    category_lower = category.lower().strip()
    if category_lower not in VALID_CATEGORIES:
        raise DomainValidationError(
            f"Invalid category. Choose from: {', '.join(sorted(VALID_CATEGORIES))}"
        )
    return category_lower


def validate_description(description):
    """Validate description is not empty."""
    if not isinstance(description, str):
        raise DomainValidationError("Description must be text")
    description_stripped = description.strip()
    if not description_stripped:
        raise DomainValidationError("Description cannot be empty")
    return description_stripped


def validate_budget_amount(amount):
    """Return a positive budget amount rounded to two decimal places."""
    try:
        amount_decimal = Decimal(str(amount))
        if not amount_decimal.is_finite() or amount_decimal <= 0:
            raise DomainValidationError("Budget must be greater than 0")
        return amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError) as error:
        if isinstance(error, DomainValidationError):
            raise
        raise DomainValidationError(f"Invalid budget amount: {error}") from error


def validate_currency(currency):
    """Normalize a three-letter currency code."""
    if not isinstance(currency, str):
        raise DomainValidationError("Currency must be a three-letter code")
    normalized = currency.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise DomainValidationError("Currency must be a three-letter code")
    return normalized
