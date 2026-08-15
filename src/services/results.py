"""Presentation-neutral results returned by application services."""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True)
class BudgetUpdateResult:
    category: str
    amount: Decimal


@dataclass(frozen=True)
class CurrencyUpdateResult:
    currency: str
    changed: bool


@dataclass(frozen=True)
class ExpenseImportError:
    row_number: int
    date: str
    amount: str
    category: str
    description: str
    reason: str


@dataclass(frozen=True)
class ExpenseImportResult:
    imported: int
    skipped_duplicates: int
    errors: tuple[ExpenseImportError, ...]

    @property
    def failed(self) -> int:
        return len(self.errors)


@dataclass(frozen=True)
class ExportResult:
    path: Path
    record_count: int
    kind: str
