#!/usr/bin/env python3
"""Main entry point for Expense Tracker CLI application."""

import sys
from src.cli import Menu
from src.storage import PersistenceError


def main():
    """Run the expense tracker application."""
    try:
        menu = Menu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\n✓ Application interrupted. Goodbye!\n")
        sys.exit(0)
    except PersistenceError as error:
        print(f"\n✗ The application could not access its data safely: {error}")
        print("Check the data files and their .bak backups before trying again.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
