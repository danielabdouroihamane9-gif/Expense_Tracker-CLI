"""CSV export service."""

import csv
from datetime import datetime
from pathlib import Path

from src.exceptions import CSVImportError, CurrencyMismatchError, ExportError, NoDataError
from src.utils import validate_currency

from .results import ExportResult


class ExportService:
    """Handles exporting expenses and summaries to CSV."""

    def __init__(self, export_dir="exports", currency="USD"):
        """Initialize export service.

        Args:
            export_dir (str): Directory for storing export files
        """
        self.export_dir = Path(export_dir)
        try:
            self.export_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ExportError(
                f"Cannot create export directory '{self.export_dir}': {error}"
            ) from error
        self.currency = validate_currency(currency)

    def export_expenses_to_csv(self, expenses, filename=None, category=None):
        """Export expenses to CSV file.

        Args:
            expenses (list): List of Expense objects
            filename (str): Output filename (auto-generated if None)
            category (str): Filter by category (optional)

        Returns:
            ExportResult: Path and count for the completed export.
        """
        if filename is None:
            filename = f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        if category:
            expenses = [e for e in expenses if e.category == category.lower()]

        if not expenses:
            raise NoDataError("No expenses to export")

        if any(expense.currency != self.currency for expense in expenses):
            raise CurrencyMismatchError(
                "Cannot export expenses that do not match "
                f"application currency {self.currency}"
            )

        # Reverse to show oldest first in CSV
        expenses = list(reversed(expenses))

        filepath = self.export_dir / filename
        try:
            with filepath.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["Date", "Amount", "Currency", "Category", "Description"]
                )

                for expense in expenses:
                    writer.writerow(
                        [
                            expense.date,
                            expense.amount,
                            expense.currency,
                            expense.category,
                            expense.description,
                        ]
                    )

        except (OSError, csv.Error) as error:
            raise ExportError(f"Cannot export expenses to '{filepath}': {error}") from error
        return ExportResult(filepath, len(expenses), "expenses")

    def export_summary_to_csv(self, summary, filename=None, year=None, month=None):
        """Export monthly summary to CSV file.

        Args:
            summary (dict): Monthly summary dictionary
            filename (str): Output filename (auto-generated if None)
            year (int): Year (for filename generation)
            month (int): Month (for filename generation)

        Returns:
            ExportResult: Path and count for the completed export.
        """
        if filename is None:
            if year is None or month is None:
                today = datetime.now().date()
                year, month = today.year, today.month
            filename = f"summary_{year}_{month:02d}.csv"

        if not summary:
            raise NoDataError("No summary to export")

        filepath = self.export_dir / filename
        try:
            with filepath.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Category", "Amount", "Currency"])

                total = 0
                for category in sorted(summary.keys()):
                    amount = summary[category]
                    writer.writerow([category.capitalize(), amount, self.currency])
                    total += amount

                writer.writerow(["Total", total, self.currency])

        except (OSError, csv.Error) as error:
            raise ExportError(f"Cannot export summary to '{filepath}': {error}") from error
        return ExportResult(filepath, len(summary), "summary")

    def read_expenses_csv(self, file_path):
        """
        Read expenses from a CSV file.

        Args:
            file_path (str): Path to CSV file.

        Returns:
            list[dict]: Normalized CSV rows.
        """

        # Accept both CLI strings and standard os.PathLike objects.
        if not str(file_path).strip():
            raise CSVImportError("CSV file path cannot be empty")

        filepath = Path(file_path)

        if filepath.suffix.lower() != ".csv":
            raise CSVImportError("File must be a CSV file")

        # If only a filename was provided, also search
        # inside the default exports directory.
        if not filepath.exists() and not filepath.parent.parts:
            alternate_path = self.export_dir / filepath.name

            if alternate_path.exists():
                filepath = alternate_path

        if not filepath.exists():
            raise CSVImportError(f"CSV file does not exist: {filepath}")

        try:
            with filepath.open("r", newline="", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                if reader.fieldnames is None:
                    raise CSVImportError("CSV file has no header")

                # Normalize CSV headers
                normalized_headers = {
                    header.strip().lower(): header
                    for header in reader.fieldnames
                }

                expected_headers = {
                    "date",
                    "amount",
                    "category",
                    "description",
                }

                missing_columns = (
                    expected_headers
                    - set(normalized_headers.keys())
                )

                if missing_columns:
                    raise CSVImportError(
                        f"Missing columns: {', '.join(sorted(missing_columns))}"
                    )

                rows = []

                for row in reader:
                    normalized_row = {
                        "Date": row[normalized_headers["date"]],
                        "Amount": row[normalized_headers["amount"]],
                        "Currency": (
                            row[normalized_headers["currency"]]
                            if "currency" in normalized_headers
                            else self.currency
                        ),
                        "Category": row[normalized_headers["category"]],
                        "Description": row[normalized_headers["description"]],
                    }

                    rows.append(normalized_row)

                if not rows:
                    raise CSVImportError("CSV file is empty")

                return rows

        except CSVImportError:
            raise
        except (OSError, UnicodeError, csv.Error) as error:
            raise CSVImportError(f"Cannot read CSV file '{filepath}': {error}") from error
