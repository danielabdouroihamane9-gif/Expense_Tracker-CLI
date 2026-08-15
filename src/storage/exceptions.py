"""Explicit errors raised by the persistence layer."""

from src.repositories import RepositoryError


class PersistenceError(RepositoryError):
    """Base class for storage failures that callers must handle."""


class StorageReadError(PersistenceError):
    """Raised when a persisted document cannot be read."""


class StorageWriteError(PersistenceError):
    """Raised when a document cannot be saved safely."""


class DataCorruptionError(PersistenceError):
    """Raised when stored data is malformed or violates its schema."""


class UnsupportedSchemaVersionError(DataCorruptionError):
    """Raised when data was written by a newer, unsupported application."""


class StorageRecoveryWarning(UserWarning):
    """Warn that a damaged primary document was restored from backup."""
