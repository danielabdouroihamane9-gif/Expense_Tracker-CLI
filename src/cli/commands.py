"""Command handlers for CLI."""

from datetime import datetime

from src.providers import Clock
from src.utils import (
    VALID_CATEGORIES,
    validate_amount,
    validate_budget_amount,
    validate_currency,
)


class CommandHandler:
    """Handles user input for expense and budget operations."""

    def __init__(self, clock: Clock):
        self.clock = clock

    def get_user_date(self):
        """Get and validate date input from user.

        Returns:
            str: Date in YYYY-MM-DD format
        """
        while True:
            date_input = input(
                "Enter date (YYYY-MM-DD) [press Enter for today]: "
            ).strip()

            if not date_input:
                return str(self.clock.now().date())

            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                return date_input
            except ValueError:
                print("✗ Invalid format. Please use YYYY-MM-DD")

    @staticmethod
    def get_user_amount(currency):
        """Get and validate amount input from user.

        Returns:
            str: Valid amount as string
        """
        while True:
            amount_input = input(f"Enter amount ({currency}): ").strip()
            try:
                return format(validate_amount(amount_input), ".2f")
            except ValueError:
                print("✗ Invalid amount. Enter a number.")

    @staticmethod
    def get_user_category():
        """Get and validate category input from user.

        Returns:
            str: Valid category name
        """
        print(f"Available categories: {', '.join(sorted(VALID_CATEGORIES))}")

        while True:
            category = input("Enter category: ").strip().lower()
            if category in VALID_CATEGORIES:
                return category
            print(
                f"✗ Invalid category. Choose from: {', '.join(sorted(VALID_CATEGORIES))}"
            )

    @staticmethod
    def get_user_description():
        """Get description input from user.

        Returns:
            str: Non-empty description
        """
        while True:
            description = input("Enter description: ").strip()
            if description:
                return description
            print("✗ Description cannot be empty")

    @staticmethod
    def get_budget_amount(currency):
        """Get and validate budget amount from user.

        Returns:
            str: Valid budget amount as string
        """
        while True:
            amount_input = input(f"Enter budget amount ({currency}): ").strip()
            try:
                return format(validate_budget_amount(amount_input), ".2f")
            except ValueError:
                print("✗ Invalid amount. Enter a number.")

    @staticmethod
    def get_user_currency():
        """Get a validated three-letter currency code."""
        while True:
            currency = input("Enter currency code (for example USD or KMF): ")
            try:
                return validate_currency(currency)
            except ValueError as error:
                print(f"Invalid currency: {error}")

    @staticmethod
    def get_export_filename():
        """Get optional filename for export.

        Returns:
            str: Filename or None for auto-generated
        """
        filename = input("Enter filename (or press Enter for auto-generated): ").strip()
        return filename if filename else None

    @staticmethod
    def get_user_keyword():
        """Get search keyword from user.

        Returns:
            str: Search keyword
        """
        while True:
            keyword = input("Enter search keyword: ").strip()
            if keyword:
                return keyword
            print("✗ Keyword cannot be empty")

    @staticmethod
    def get_user_date_range():
        """
        Get and validate start and end dates.

        Returns:
            tuple:
                (start_date, end_date)
        """

        while True:
            start_input = input(
                "Enter start date (YYYY-MM-DD): "
            ).strip()

            end_input = input(
                "Enter end date (YYYY-MM-DD): "
            ).strip()

            try:
                start_date = datetime.strptime(
                    start_input,
                    "%Y-%m-%d"
                ).date()

                end_date = datetime.strptime(
                    end_input,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                print(
                    "✗ Invalid date format. Use YYYY-MM-DD."
                )
                continue


            if start_date > end_date:
                print(
                    "✗ Start date cannot be after end date."
                )
                continue

            return start_date, end_date

    def get_csv_file_path(self):
        """
        Prompt the user for a CSV file path.

        Returns:
            str | None: CSV file path, or None if cancelled.
        """
        print("\nEnter the CSV file path.")
        print("Enter 0 to cancel.")

        file_path = input("\nCSV file: ").strip()

        if file_path == "0":
            return None

        return file_path
