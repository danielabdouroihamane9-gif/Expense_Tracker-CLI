"""CSV export service."""

import csv
from datetime import datetime
from pathlib import Path


class ExportService:
    """Handles exporting expenses and summaries to CSV."""

    def __init__(self, export_dir="exports"):
        """Initialize export service.

        Args:
            export_dir (str): Directory for storing export files
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)

    def export_expenses_to_csv(self, expenses, filename=None, category=None):
        """Export expenses to CSV file.

        Args:
            expenses (list): List of Expense objects
            filename (str): Output filename (auto-generated if None)
            category (str): Filter by category (optional)

        Returns:
            str: Success or error message
        """
        if filename is None:
            filename = f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            if category:
                expenses = [e for e in expenses if e.category == category.lower()]

            if not expenses:
                return "✗ No expenses to export"

            # Reverse to show oldest first in CSV
            expenses = list(reversed(expenses))

            filepath = self.export_dir / filename
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Amount", "Category", "Description"])

                for expense in expenses:
                    writer.writerow(
                        [
                            expense.date,
                            expense.amount,
                            expense.category,
                            expense.description,
                        ]
                    )

            return f"✓ Exported {len(expenses)} expenses to {filename}"
        except IOError as e:
            return f"✗ Error exporting to CSV: {e}"

    def export_summary_to_csv(self, summary, filename=None, year=None, month=None):
        """Export monthly summary to CSV file.

        Args:
            summary (dict): Monthly summary dictionary
            filename (str): Output filename (auto-generated if None)
            year (int): Year (for filename generation)
            month (int): Month (for filename generation)

        Returns:
            str: Success or error message
        """
        if filename is None:
            if year is None or month is None:
                today = datetime.now().date()
                year, month = today.year, today.month
            filename = f"summary_{year}_{month:02d}.csv"

        try:
            if not summary:
                return "✗ No summary to export"

            filepath = self.export_dir / filename
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Category", "Amount"])

                total = 0
                for category in sorted(summary.keys()):
                    amount = summary[category]
                    writer.writerow([category.capitalize(), amount])
                    total += amount

                writer.writerow(["Total", total])

            return f"✓ Exported summary to {filename}"
        except IOError as e:
            return f"✗ Error exporting summary: {e}"
