# Application Composition and Runtime Configuration

Phase 1 Milestone 4 centralizes construction and runtime configuration so the
CLI, services, and persistence implementation do not discover dependencies on
their own.

## Composition root

`src/application.py` is the only production module that constructs the runtime
object graph. `create_application()` creates, in order:

1. the configured JSON repository;
2. settings, expense, budget, and export services;
3. the command handler and menu;
4. an `Application` container that owns the complete graph.

The same repository instance is injected into every repository contract. The
same clock is injected into storage migration, services, exports, commands,
and the menu. UUID generation is injected into storage migration and expense
creation. `src/main.py` only configures console output, creates the application,
runs it, and maps startup failures to exit codes.

## Runtime configuration

`ApplicationConfig` owns all filesystem and initial-currency configuration.
Defaults preserve the current CLI behavior:

| Setting | Environment variable | Default |
| --- | --- | --- |
| Data directory | `EXPENSE_TRACKER_DATA_DIR` | `data` |
| Export directory | `EXPENSE_TRACKER_EXPORT_DIR` | `exports` |
| Initial currency | `EXPENSE_TRACKER_DEFAULT_CURRENCY` | `USD` |

Relative environment paths are resolved from the process working directory at
the configuration boundary and converted to absolute paths. Other modules do
not read environment variables or the working directory.

The initial currency is used only when a repository has no `settings.json` or
settings backup. It is persisted during first application composition, before
financial data can depend on it. The persisted currency remains authoritative
on later runs even if the environment variable changes or is removed.

PowerShell example using isolated runtime directories:

```powershell
$env:EXPENSE_TRACKER_DATA_DIR = "tmp/demo-data"
$env:EXPENSE_TRACKER_EXPORT_DIR = "tmp/demo-exports"
$env:EXPENSE_TRACKER_DEFAULT_CURRENCY = "KMF"
python -m src.main
```

Remove the temporary settings from the current PowerShell session with:

```powershell
Remove-Item Env:EXPENSE_TRACKER_DATA_DIR
Remove-Item Env:EXPENSE_TRACKER_EXPORT_DIR
Remove-Item Env:EXPENSE_TRACKER_DEFAULT_CURRENCY
```

## Deterministic providers

`src/providers.py` defines the `Clock` and `UUIDGenerator` protocols and their
system implementations. Business and CLI code never calls `datetime.now()`,
`date.today()`, or `uuid4()` directly. Tests inject fixed providers to control:

- expense IDs and creation timestamps;
- default dates and reporting periods;
- generated export filenames;
- legacy-record metadata assigned during JSON loading.

This keeps tests deterministic and lets a later Django application replace
runtime providers without changing business rules.

## Architectural rules

- Concrete runtime components are constructed only in `src/application.py`.
- Services receive repositories and providers through constructors.
- The CLI receives fully constructed services, command handlers, and clocks.
- Runtime paths and the initial currency come from `ApplicationConfig`.
- Ambient time and UUID calls are isolated to system provider implementations.
- `src/main.py` remains a thin executable entry point.

Automated architecture tests in `tests/test_application_composition.py`
enforce these rules.
