"""Command handlers for CLI."""

from datetime import datetime
from src.utils import VALID_CATEGORIES


class CommandHandler:
    """Handles user input for expense and budget operations."""

    @staticmethod
    def get_user_date():
        """Get and validate date input from user.

        Returns:
            str: Date in YYYY-MM-DD format
        """
        while True:
            date_input = input(
                "Enter date (YYYY-MM-DD) [press Enter for today]: "
            ).strip()

            if not date_input:
                return str(datetime.now().date())

            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                return date_input
            except ValueError:
                print("✗ Invalid format. Please use YYYY-MM-DD")

    @staticmethod
    def get_user_amount():
        """Get and validate amount input from user.

        Returns:
            str: Valid amount as string
        """
        while True:
            amount_input = input("Enter amount ($): ").strip()
            try:
                amount = float(amount_input)
                if amount <= 0:
                    print("✗ Amount must be greater than 0")
                    continue
                return str(amount)
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
    def get_budget_amount():
        """Get and validate budget amount from user.

        Returns:
            str: Valid budget amount as string
        """
        while True:
            amount_input = input("Enter budget amount ($): ").strip()
            try:
                amount = float(amount_input)
                if amount <= 0:
                    print("✗ Budget must be greater than 0")
                    continue
                return str(amount)
            except ValueError:
                print("✗ Invalid amount. Enter a number.")

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
