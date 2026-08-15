# Repository and service boundaries

Milestone 3 separates application behavior from JSON persistence and terminal
presentation. Services now receive repository dependencies that satisfy typed
`Protocol` contracts; they do not import or construct `JSONStorage`.

## Dependency direction

```text
CLI presentation
      |
      v
Application services --> repository protocols <-- JSONStorage
      |
      v
Domain model and validation
```

The CLI receives fully constructed services. The current entry point performs
that temporary construction. Milestone 4 will move it into a formal,
configuration-aware composition root without changing service behavior.

## Repository contracts

`src/repositories/contracts.py` defines three independent protocols:

- `ExpenseRepository`: `load_expenses()` and `save_expenses(expenses)`.
- `BudgetRepository`: `load_budgets()` and `save_budgets(budgets)`.
- `SettingsRepository`: `load_settings()` and `save_settings(settings)`.

`JSONStorage` implements all three protocols structurally. Services depend only
on the protocols and `RepositoryError`, so a future database implementation can
be injected without changing business rules or the CLI.

The reusable assertions in `tests/repository_contracts.py` define the behavior
every later repository must satisfy. `tests/test_json_repository_contract.py`
applies those assertions to `JSONStorage`. A Django repository should run the
same contract assertions in addition to its database-specific tests.

## Service constructor contract

- `ExpenseTrackerService(expense_repository, settings_repository)`
- `BudgetService(budget_repository, settings_repository)`
- `SettingsService(settings_repository, expense_repository, budget_repository)`

Services never accept a data-directory path. Path selection and implementation
choice belong to application composition, not business logic.

## Presentation-neutral results

Mutation and export services return domain objects or immutable result values:

- expense creation and duplication return `Expense`;
- budget updates return `BudgetUpdateResult`;
- currency updates return `CurrencyUpdateResult`;
- imports return `ExpenseImportResult` with typed row errors;
- exports return `ExportResult`.

These values contain no checkmarks, crosses, or terminal-ready success
sentences. The CLI owns those messages and the formatter owns import-summary
layout.

## Exception boundaries

The shared hierarchy in `src/exceptions.py` distinguishes:

- domain validation errors;
- application rule failures such as blocked currency changes;
- export and CSV import failures.

Repository failures derive from `RepositoryError`. JSON-specific failures add
the more precise persistence exceptions documented in
`PERSISTENCE_RELIABILITY.md`. The CLI translates expected exceptions into user
messages; unexpected programming errors remain visible to the entry point.
