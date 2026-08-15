"""Expense domain model with validation and stable identity."""

from datetime import datetime, timezone
from uuid import UUID

from src.exceptions import DomainValidationError
from src.utils.validators import (
    validate_date,
    validate_amount,
    validate_category,
    validate_description,
    validate_currency,
)


class Expense:
    """Represents a single expense with validation."""

    def __init__(
        self,
        date,
        amount,
        category,
        description,
        *,
        expense_id,
        currency,
        created_at,
    ):
        """Initialize an expense with validation.

        Args:
            date (str): Date in YYYY-MM-DD format
            amount (str | int | float | Decimal): Positive monetary amount
            category (str): Expense category
            description (str): Expense description
            expense_id (UUID | str): Identifier supplied by the application
            currency (str): Three-letter application currency
            created_at (datetime | str): Creation time supplied by the clock
        """
        self.id = self._validate_id(expense_id)
        self.occurred_on = validate_date(date)
        self.amount = validate_amount(amount)
        self.currency = validate_currency(currency)
        self.category = validate_category(category)
        self.description = validate_description(description)
        self.created_at = self._validate_created_at(created_at)

    @staticmethod
    def _validate_id(expense_id):
        if expense_id is None:
            raise DomainValidationError("Expense ID is required")
        try:
            return expense_id if isinstance(expense_id, UUID) else UUID(str(expense_id))
        except (TypeError, ValueError, AttributeError) as error:
            raise DomainValidationError(f"Invalid expense ID: {expense_id}") from error

    @staticmethod
    def _validate_created_at(created_at):
        if created_at is None:
            raise DomainValidationError("Expense creation timestamp is required")
        if isinstance(created_at, str):
            value = created_at.replace("Z", "+00:00")
            try:
                created_at = datetime.fromisoformat(value)
            except ValueError as error:
                raise DomainValidationError(
                    f"Invalid creation timestamp: {created_at}"
                ) from error
        if not isinstance(created_at, datetime):
            raise DomainValidationError("Invalid creation timestamp")
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return created_at.astimezone(timezone.utc)

    @property
    def date(self):
        """Backward-compatible alias for the expense occurrence date."""
        return self.occurred_on

    def to_dict(self):
        """Convert expense to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "amount": format(self.amount, ".2f"),
            "currency": self.currency,
            "category": self.category,
            "description": self.description,
            "occurred_on": str(self.occurred_on),
            "created_at": self.created_at.isoformat().replace("+00:00", "Z"),
        }

    @classmethod
    def from_dict(cls, data, *, default_currency):
        """Create Expense from dictionary (for JSON deserialization)."""
        return cls(
            data.get("occurred_on", data.get("date")),
            data["amount"],
            data["category"],
            data["description"],
            expense_id=data["id"],
            currency=data.get("currency", default_currency),
            created_at=data["created_at"],
        )

    def __repr__(self):
        return (
            f"Expense({self.occurred_on}, {self.currency} {self.amount:.2f}, "
            f"{self.category}, {self.description})"
        )

    def __eq__(self, other):
        """Check equality based on all attributes."""
        if not isinstance(other, Expense):
            return False
        return (
            self.id == other.id
            and self.occurred_on == other.occurred_on
            and self.amount == other.amount
            and self.currency == other.currency
            and self.category == other.category
            and self.description == other.description
            and self.created_at == other.created_at
        )
