"""Shared domain and application exception hierarchy."""


class ExpenseTrackerError(Exception):
    """Base class for expected application errors."""


class DomainError(ExpenseTrackerError):
    """Base class for invalid domain data or rules."""


class DomainValidationError(DomainError, ValueError):
    """Raised when a domain value cannot be accepted."""


class ApplicationError(ExpenseTrackerError):
    """Base class for application use-case failures."""


class CurrencyMismatchError(ApplicationError):
    """Raised when financial data uses another application currency."""


class CurrencyChangeBlockedError(ApplicationError):
    """Raised when existing financial data prevents a currency change."""


class NoDataError(ApplicationError):
    """Raised when an operation requires data but none is available."""


class ExportError(ApplicationError):
    """Raised when an export cannot be written."""


class CSVImportError(ApplicationError):
    """Raised when a CSV file cannot be accepted for import."""
