"""Expense model with validation."""

from src.utils.validators import (
    validate_date,
    validate_amount,
    validate_category,
    validate_description,
)


class Expense:
    """Represents a single expense with validation."""

    def __init__(self, date, amount, category, description):
        """Initialize an expense with validation.

        Args:
            date (str): Date in YYYY-MM-DD format
            amount (float): Expense amount
            category (str): Expense category
            description (str): Expense description
        """
        self.date = validate_date(date)
        self.amount = validate_amount(amount)
        self.category = validate_category(category)
        self.description = validate_description(description)

    def to_dict(self):
        """Convert expense to dictionary for JSON serialization."""
        return {
            "date": str(self.date),
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        """Create Expense from dictionary (for JSON deserialization)."""
        return cls(data["date"], data["amount"], data["category"], data["description"])

    def __repr__(self):
        return f"Expense({self.date}, ${self.amount:.2f}, {self.category}, {self.description})"

    def __eq__(self, other):
        """Check equality based on all attributes."""
        if not isinstance(other, Expense):
            return False
        return (
            self.date == other.date
            and self.amount == other.amount
            and self.category == other.category
            and self.description == other.description
        )
