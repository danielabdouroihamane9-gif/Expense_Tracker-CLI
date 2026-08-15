#!/usr/bin/env python3
"""Main entry point for Expense Tracker CLI application."""

import sys
from src.application import create_application
from src.exceptions import ExpenseTrackerError
from src.storage import PersistenceError


def _configure_console_output():
    """Use UTF-8 for CLI symbols when Windows redirects standard streams."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def main():
    """Run the expense tracker application."""
    _configure_console_output()
    try:
        create_application().run()
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
