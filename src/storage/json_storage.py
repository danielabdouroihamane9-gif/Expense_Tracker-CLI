"""JSON storage layer for persistence."""

import json
from pathlib import Path
from src.models import Expense


class JSONStorage:
    """Handles JSON persistence for expenses and budgets."""

    def __init__(self, data_dir="data"):
        """Initialize storage with specified data directory.

        Args:
            data_dir (str): Directory path for storing JSON files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
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
                return [Expense.from_dict(item) for item in data]
        except (IOError, json.JSONDecodeError, ValueError) as e:
            print(f"✗ Error loading expenses: {e}")
            return []

    def save_expenses(self, expenses):
        """Persist all expenses to JSON file.

        Args:
            expenses (list): List of Expense objects to save
        """
        try:
            data = [expense.to_dict() for expense in expenses]
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
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"✗ Error loading budgets: {e}")
            return {}

    def save_budgets(self, budgets):
        """Persist all budgets to JSON file.

        Args:
            budgets (dict): Dictionary of budgets by category
        """
        try:
            with open(self.budgets_file, "w") as f:
                json.dump(budgets, f, indent=2)
        except IOError as e:
            print(f"✗ Error saving budgets: {e}")
