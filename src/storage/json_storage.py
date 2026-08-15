"""Reliable JSON persistence for application data."""

import json
import os
import tempfile
import warnings
from pathlib import Path

from src.models import Expense
from src.utils import VALID_CATEGORIES, validate_budget_amount, validate_currency

from .exceptions import (
    DataCorruptionError,
    StorageReadError,
    StorageRecoveryWarning,
    StorageWriteError,
    UnsupportedSchemaVersionError,
)


class JSONStorage:
    """Persist versioned JSON documents with backups and atomic replacement."""

    SCHEMA_VERSION = 2
    DEFAULT_CURRENCY = "USD"

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise StorageWriteError(
                f"Cannot create data directory '{self.data_dir}': {error}"
            ) from error

        self.expenses_file = self.data_dir / "expenses.json"
        self.budgets_file = self.data_dir / "budgets.json"
        self.settings_file = self.data_dir / "settings.json"

    def load_expenses(self):
        """Load and validate expenses, recovering a corrupt primary if possible."""
        currency = self.load_settings()["currency"]
        return self._load_document(
            self.expenses_file,
            lambda document: self._parse_expenses(document, currency),
            default=[],
        )

    def save_expenses(self, expenses):
        """Atomically persist all expenses after validating the complete document."""
        currency = self.load_settings()["currency"]
        if any(expense.currency != currency for expense in expenses):
            raise DataCorruptionError(
                f"All expenses must use the configured currency {currency}"
            )
        document = {
            "schema_version": self.SCHEMA_VERSION,
            "currency": currency,
            "expenses": [expense.to_dict() for expense in expenses],
        }
        self._write_document(
            self.expenses_file,
            document,
            lambda value: self._parse_expenses(value, currency),
        )

    def load_budgets(self):
        """Load and validate budgets, recovering a corrupt primary if possible."""
        currency = self.load_settings()["currency"]
        return self._load_document(
            self.budgets_file,
            lambda document: self._parse_budgets(document, currency),
            default={},
        )

    def save_budgets(self, budgets):
        """Atomically persist all budgets after validating the complete document."""
        currency = self.load_settings()["currency"]
        document = {
            "schema_version": self.SCHEMA_VERSION,
            "currency": currency,
            "budgets": {
                category: format(validate_budget_amount(amount), ".2f")
                for category, amount in budgets.items()
            },
        }
        self._write_document(
            self.budgets_file,
            document,
            lambda value: self._parse_budgets(value, currency),
        )

    def load_settings(self):
        """Load settings, defaulting to USD only for a new repository."""
        return self._load_document(
            self.settings_file,
            self._parse_settings,
            default={"currency": self.DEFAULT_CURRENCY},
        )

    def save_settings(self, settings):
        """Atomically persist validated application settings."""
        document = {
            "schema_version": self.SCHEMA_VERSION,
            "currency": validate_currency(settings["currency"]),
        }
        self._write_document(
            self.settings_file,
            document,
            self._parse_settings,
        )

    def _load_document(self, path, parser, default):
        """Load one document and recover only schema-corrupt primary data."""
        if not path.exists():
            backup = self._backup_path(path)
            if not backup.exists():
                return default.copy() if hasattr(default, "copy") else default
            return self._recover_from_backup(path, backup, parser)

        try:
            document = self._read_json(path)
            return parser(document)
        except UnsupportedSchemaVersionError:
            # Falling back could discard data created by a newer application.
            raise
        except DataCorruptionError as primary_error:
            backup = self._backup_path(path)
            if not backup.exists():
                raise primary_error
            return self._recover_from_backup(path, backup, parser, primary_error)

    def _recover_from_backup(self, primary, backup, parser, primary_error=None):
        """Validate a backup, restore it atomically, and return parsed data."""
        try:
            document = self._read_json(backup)
            parsed = parser(document)
        except UnsupportedSchemaVersionError:
            raise
        except (DataCorruptionError, StorageReadError) as backup_error:
            detail = f" Primary error: {primary_error}." if primary_error else ""
            raise DataCorruptionError(
                f"Cannot recover '{primary.name}': backup is invalid or unreadable."
                f"{detail} Backup error: {backup_error}"
            ) from backup_error

        self._atomic_dump(primary, document)
        warnings.warn(
            f"Recovered '{primary.name}' from '{backup.name}'.",
            StorageRecoveryWarning,
            stacklevel=2,
        )
        return parsed

    def _write_document(self, path, document, parser):
        """Back up a valid primary and atomically replace it with validated data."""
        parser(document)

        if path.exists():
            current_document = self._read_json(path)
            parser(current_document)
            self._atomic_dump(self._backup_path(path), current_document)

        self._atomic_dump(path, document)

    @staticmethod
    def _backup_path(path):
        return path.with_suffix(path.suffix + ".bak")

    @staticmethod
    def _read_json(path):
        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as error:
            raise DataCorruptionError(
                f"'{path.name}' contains invalid JSON: {error}"
            ) from error
        except OSError as error:
            raise StorageReadError(f"Cannot read '{path}': {error}") from error

    @staticmethod
    def _atomic_dump(path, document):
        """Write a complete JSON temp file, flush it, then replace the target."""
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                prefix=f".{path.name}.",
                suffix=".tmp",
                dir=path.parent,
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                json.dump(document, temporary, indent=2)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, path)
            temporary_path = None
        except (OSError, TypeError, ValueError) as error:
            raise StorageWriteError(f"Cannot safely write '{path}': {error}") from error
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def _parse_expenses(self, document, configured_currency):
        if isinstance(document, list):
            records = document
            stored_currency = configured_currency
        else:
            self._require_versioned_document(document, "expenses")
            stored_currency = self._document_currency(
                document, configured_currency, "expenses"
            )
            records = document.get("expenses")
            if not isinstance(records, list):
                raise DataCorruptionError("expenses.json field 'expenses' must be a list")

        try:
            expenses = [
                Expense.from_dict(record, default_currency=stored_currency)
                for record in records
            ]
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            raise DataCorruptionError(
                f"expenses.json contains an invalid expense: {error}"
            ) from error

        if any(expense.currency != stored_currency for expense in expenses):
            raise DataCorruptionError(
                "expenses.json contains an expense with a different currency"
            )
        return expenses

    def _parse_budgets(self, document, configured_currency):
        if not isinstance(document, dict):
            raise DataCorruptionError("budgets.json must contain a JSON object")

        if "schema_version" in document:
            self._require_versioned_document(document, "budgets")
            self._document_currency(document, configured_currency, "budgets")
            budgets = document.get("budgets")
            if not isinstance(budgets, dict):
                raise DataCorruptionError("budgets.json field 'budgets' must be an object")
        else:
            budgets = document

        try:
            if any(category not in VALID_CATEGORIES for category in budgets):
                raise ValueError("unknown budget category")
            return {
                category: validate_budget_amount(amount)
                for category, amount in budgets.items()
            }
        except (AttributeError, TypeError, ValueError) as error:
            raise DataCorruptionError(
                f"budgets.json contains an invalid budget: {error}"
            ) from error

    def _parse_settings(self, document):
        if not isinstance(document, dict):
            raise DataCorruptionError("settings.json must contain a JSON object")
        if "schema_version" in document:
            self._require_versioned_document(document, "settings")
        try:
            return {"currency": validate_currency(document["currency"])}
        except (KeyError, TypeError, ValueError) as error:
            raise DataCorruptionError(
                f"settings.json contains invalid settings: {error}"
            ) from error

    def _require_versioned_document(self, document, name):
        if not isinstance(document, dict):
            raise DataCorruptionError(f"{name}.json must contain a JSON object")
        version = document.get("schema_version")
        if isinstance(version, bool) or not isinstance(version, int):
            raise DataCorruptionError(
                f"{name}.json field 'schema_version' must be an integer"
            )
        if version > self.SCHEMA_VERSION:
            raise UnsupportedSchemaVersionError(
                f"{name}.json uses schema version {version}; this application "
                f"supports up to version {self.SCHEMA_VERSION}"
            )
        if version != self.SCHEMA_VERSION:
            raise DataCorruptionError(
                f"{name}.json uses unsupported schema version {version}"
            )

    @staticmethod
    def _document_currency(document, configured_currency, name):
        try:
            stored_currency = validate_currency(document["currency"])
        except (KeyError, TypeError, ValueError) as error:
            raise DataCorruptionError(
                f"{name}.json contains an invalid currency: {error}"
            ) from error
        if stored_currency != configured_currency:
            raise DataCorruptionError(
                f"{name} data uses {stored_currency}, but the application is "
                f"configured for {configured_currency}"
            )
        return stored_currency
