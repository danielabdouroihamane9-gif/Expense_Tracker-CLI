"""Validation utilities for expense tracker."""

from datetime import datetime

VALID_CATEGORIES = {
    "food",
    "transport",
    "rent",
    "utilities",
    "entertainment",
    "healthcare",
    "other",
}


def validate_date(date):
    """Validate and parse date string (YYYY-MM-DD format)."""
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD (got: {date})")


def validate_amount(amount):
    """Validate amount is positive number."""
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValueError("Amount must be greater than 0")
        return round(amount_float, 2)
    except ValueError as e:
        raise ValueError(f"Invalid amount: {e}")


def validate_category(category):
    """Validate category is in predefined list."""
    category_lower = category.lower().strip()
    if category_lower not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category. Choose from: {', '.join(sorted(VALID_CATEGORIES))}"
        )
    return category_lower


def validate_description(description):
    """Validate description is not empty."""
    description_stripped = description.strip()
    if not description_stripped:
        raise ValueError("Description cannot be empty")
    return description_stripped


def validate_budget_amount(amount):
    """Validate budget amount is positive."""
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValueError("Budget must be greater than 0")
        return round(amount_float, 2)
    except ValueError as e:
        raise ValueError(f"Invalid budget amount: {e}")
