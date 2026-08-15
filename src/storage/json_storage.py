"""JSON storage layer for persistence."""

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from src.models import Expense
from src.utils import validate_currency


class JSONStorage:
    """Handles JSON persistence for expenses and budgets."""

    SCHEMA_VERSION = 2
    DEFAULT_CURRENCY = "USD"

    def __init__(self, data_dir="data"):
        """Initialize storage with specified data directory.

        Args:
            data_dir (str): Directory path for storing JSON files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.expenses_file = self.data_dir / "expenses.json"
        self.budgets_file = self.data_dir / "budgets.json"

    def load_expenses(self):
        """Load all expenses from JSON file.

        Returns:
            list: List of Expense objects
        """
        if not self.expenses_file.exists():
            return []

        try:
            with open(self.expenses_file, "r") as f:
                data = json.load(f)
                self._require_configured_currency(data, "expenses")
                records = data if isinstance(data, list) else data.get("expenses", [])
                currency = self.load_settings()["currency"]
                return [
                    Expense.from_dict(item, default_currency=currency)
                    for item in records
                ]
        except (IOError, json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"✗ Error loading expenses: {e}")
            return []

    def save_expenses(self, expenses):
        """Persist all expenses to JSON file.

        Args:
            expenses (list): List of Expense objects to save
        """
        try:
            currency = self.load_settings()["currency"]
            if any(expense.currency != currency for expense in expenses):
                raise ValueError(
                    f"All expenses must use the configured currency {currency}"
                )
            data = {
                "schema_version": self.SCHEMA_VERSION,
                "currency": currency,
                "expenses": [expense.to_dict() for expense in expenses],
            }
            with open(self.expenses_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"✗ Error saving expenses: {e}")

    def load_budgets(self):
        """Load all budgets from JSON file.

        Returns:
            dict: Dictionary of budgets by category
        """
        if not self.budgets_file.exists():
            return {}

        try:
            with open(self.budgets_file, "r") as f:
                data = json.load(f)
                self._require_configured_currency(data, "budgets")
                budgets = data.get("budgets", {}) if "schema_version" in data else data
                return {category: Decimal(str(amount)) for category, amount in budgets.items()}
        except (IOError, json.JSONDecodeError, InvalidOperation, TypeError, ValueError) as e:
            print(f"✗ Error loading budgets: {e}")
            return {}

    def load_settings(self):
        """Load settings, using USD for repositories created before settings."""
        settings_file = self.data_dir / "settings.json"
        if not settings_file.exists():
            return {"currency": self.DEFAULT_CURRENCY}

        try:
            with open(settings_file, "r") as file:
                data = json.load(file)
            return {"currency": validate_currency(data["currency"])}
        except (
            IOError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            print(f"Error loading settings: {error}")
            return {"currency": self.DEFAULT_CURRENCY}

    def _require_configured_currency(self, document, document_name):
        """Reject versioned financial data labelled with another currency."""
        if not isinstance(document, dict) or "currency" not in document:
            return
        stored_currency = validate_currency(document["currency"])
        configured_currency = self.load_settings()["currency"]
        if stored_currency != configured_currency:
            raise RuntimeError(
                f"{document_name} data uses {stored_currency}, but the "
                f"application is configured for {configured_currency}"
            )

    def save_settings(self, settings):
        """Persist validated application settings."""
        settings_file = self.data_dir / "settings.json"
        data = {
            "schema_version": self.SCHEMA_VERSION,
            "currency": validate_currency(settings["currency"]),
        }
        with open(settings_file, "w") as file:
            json.dump(data, file, indent=2)

    def save_budgets(self, budgets):
        """Persist all budgets to JSON file.

        Args:
            budgets (dict): Dictionary of budgets by category
        """
        try:
            with open(self.budgets_file, "w") as f:
                data = {
                    "schema_version": self.SCHEMA_VERSION,
                    "currency": self.load_settings()["currency"],
                    "budgets": {
                        category: format(amount, ".2f")
                        for category, amount in budgets.items()
                    },
                }
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"✗ Error saving budgets: {e}")
