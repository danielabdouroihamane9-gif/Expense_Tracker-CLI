#!/usr/bin/env python3
"""Main entry point for Expense Tracker CLI application."""

import sys
from src.cli import Menu
from src.exceptions import ExpenseTrackerError
from src.services import (
    BudgetService,
    ExpenseTrackerService,
    ExportService,
    SettingsService,
)
from src.storage import JSONStorage, PersistenceError


def _configure_console_output():
    """Use UTF-8 for CLI symbols when Windows redirects standard streams."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def _compose_menu(data_dir="data", export_dir="exports"):
    """Construct current dependencies until Milestone 4 formalizes composition."""
    repository = JSONStorage(data_dir)
    settings = SettingsService(repository, repository, repository)
    currency = settings.get_currency()
    return Menu(
        settings,
        ExpenseTrackerService(repository, repository),
        BudgetService(repository, repository),
        ExportService(export_dir, currency),
    )


def main():
    """Run the expense tracker application."""
    _configure_console_output()
    try:
        menu = _compose_menu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\n✓ Application interrupted. Goodbye!\n")
        sys.exit(0)
    except PersistenceError as error:
        print(f"\n✗ The application could not access its data safely: {error}")
        print("Check the data files and their .bak backups before trying again.")
        sys.exit(1)
    except ExpenseTrackerError as error:
        print(f"\n✗ The application could not start: {error}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
