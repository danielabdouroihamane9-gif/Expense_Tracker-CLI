"""Storage module for expense tracker."""

from .exceptions import (
    DataCorruptionError,
    PersistenceError,
    StorageReadError,
    StorageRecoveryWarning,
    StorageWriteError,
    UnsupportedSchemaVersionError,
)
from .json_storage import JSONStorage

__all__ = [
    "DataCorruptionError",
    "JSONStorage",
    "PersistenceError",
    "StorageReadError",
    "StorageRecoveryWarning",
    "StorageWriteError",
    "UnsupportedSchemaVersionError",
]
