"""Repository-level exceptions independent of any storage technology."""

from src.exceptions import ExpenseTrackerError


class RepositoryError(ExpenseTrackerError):
    """Base class for repository operations that cannot be completed."""
