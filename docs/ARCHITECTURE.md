# Current architecture

This document describes the implemented Roadmap Phase 1 application. It does
not describe a future web application as though it already exists.

## Dependency direction

```text
src/main.py
    |
    v
src/application.py (composition root)
    |
    +--> CLI presentation
    |        |
    |        v
    +--> application services --> repository protocols <-- JSONStorage
                      |
                      v
             Expense model and validation
```

Outer components depend on stable inner behavior. Services receive repository,
clock, and UUID dependencies through constructors. The CLI receives constructed
services and owns all user-facing input and messages.

## Components

### Entry point and composition

`src/main.py` configures safe console output, calls `create_application()`,
runs the application, and converts startup persistence failures into a nonzero
exit code.

`src/application.py` is the only production composition root. It constructs
`ApplicationConfig`, providers, `JSONStorage`, services, commands, and `Menu`.
One repository instance implements all three repository protocols.

### Domain and validation

`Expense` is the current domain entity. Its invariants include:

- a valid UUID;
- an occurrence date;
- a positive `Decimal` quantized to two fractional digits;
- the configured three-letter currency;
- one of eight supported categories;
- a nonempty description;
- a timezone-aware creation timestamp normalized to UTC.

Budgets are currently `dict[str, Decimal]`. Settings are currently a mapping
containing the application currency. They have service and repository rules,
but no dedicated model classes.

### Services

- `ExpenseTrackerService` owns expense CRUD, search, filtering, sorting,
  reports, and import mutation.
- `BudgetService` owns category budgets and budget-status calculations.
- `SettingsService` prevents currency changes from silently relabelling
  existing financial data.
- `ExportService` reads and writes currency-aware CSV files.

Services return domain objects or typed result values. They do not return
terminal-decorated success messages.

### Repository boundary

The expense, budget, and settings protocols currently load and save complete
collections. `JSONStorage` satisfies them structurally. Reusable contract tests
define the minimum behavior for another adapter.

Whole-collection contracts are appropriate for this small single-process CLI,
but they are not the final multi-user database design. A Django adapter may
temporarily satisfy them during migration; granular queries, writes, and
explicit transaction boundaries must replace them before concurrent or
high-volume operation.

### JSON persistence

`JSONStorage` validates complete versioned documents. Saves use a temporary
file, flush, and atomic replacement. The previous valid primary is stored as a
`.bak` file. Recovery uses a backup only after it passes the same validation.
Future schema versions and unrecoverable corruption are explicit failures.

See [DATA_SCHEMA.md](DATA_SCHEMA.md) and
[PERSISTENCE_RELIABILITY.md](PERSISTENCE_RELIABILITY.md).

## Runtime flows

### Startup

```text
environment -> ApplicationConfig -> JSONStorage -> initialize settings
            -> construct services -> construct CLI -> run menu
```

The initial configured currency is persisted only when settings do not exist.
Persisted settings remain authoritative on later starts.

### Expense mutation

```text
terminal input -> CommandHandler validation -> ExpenseTrackerService
               -> Expense validation -> repository save -> CLI result
```

If persistence fails, the service restores its prior in-memory state before
the error reaches the CLI.

### Load and recovery

```text
read primary -> validate complete document -> return values
       |
       `-- corrupt/missing -> validate backup -> atomic restore -> warning
```

Unsupported newer schemas and unreadable files do not fall back silently.

## Configuration and determinism

Runtime paths and the initial currency belong to `ApplicationConfig`. Time and
UUID creation are isolated behind protocols, allowing deterministic tests and
repeatable legacy migrations. Details are in
[APPLICATION_COMPOSITION.md](APPLICATION_COMPOSITION.md).

## Current boundary

The application is local, single-user, and JSON-backed. Roadmap Phase 1 does
not implement Django, an HTTP API, PostgreSQL, authentication, authorization,
multi-user ownership, background jobs, or AI/ML. The future handoff is mapped
in [DJANGO_MIGRATION_READINESS.md](DJANGO_MIGRATION_READINESS.md).
