# Project index

This index describes the application that exists on the current Phase 1
branch. Future Django components are documented separately and are not part of
the runtime.

## Runtime entry points

| File | Responsibility |
| --- | --- |
| `src/main.py` | Console setup, application start, and startup error-to-exit-code mapping |
| `src/application.py` | The production composition root and complete runtime object graph |
| `src/config.py` | Validated paths and initial currency from environment variables |
| `src/providers.py` | Injectable clock and UUID-generation protocols and system implementations |

## Application packages

| Package | Responsibility |
| --- | --- |
| `src/cli/` | Input collection, terminal menus, and presentation |
| `src/models/` | Expense domain entity |
| `src/services/` | Expense, budget, settings, import/export, report, and application rules |
| `src/repositories/` | Persistence-neutral protocols and repository error boundary |
| `src/storage/` | Versioned JSON implementation, validation, backups, and recovery |
| `src/utils/` | Domain validation and terminal formatting helpers |

Budgets and settings are currently mappings managed by services and repository
contracts; they are not domain model classes. This distinction matters for the
future Django mapping.

## CLI navigation

```text
Main Menu
|-- 1. Expense Management
|   |-- 1. Manage Expenses
|   |   |-- Add, edit, duplicate, view all, view details, delete, clear
|   |-- 2. Search & Filter
|   |   |-- Search, category filter, date-range filter
|   `-- 3. Sort Expenses
|       `-- Date, amount, category, or description in both directions
|-- 2. Budget Management
|   `-- Set, edit, view, delete, or clear budgets
|-- 3. Reports
|   |-- Expense Reports
|   |   `-- Monthly summary, statistics, category totals, top categories
|   `-- Budget Reports
|       `-- Budget status
|-- 4. Export
|   |-- Export expenses or a monthly summary
|   `-- Import expenses from CSV
|-- 5. Settings
|   `-- Change currency when no financial records exist
`-- 0. Exit
```

## Persistent and generated files

| Location | Contents | Git status |
| --- | --- | --- |
| `data/` | `expenses.json`, `budgets.json`, `settings.json`, and `.bak` files | Runtime files ignored |
| `exports/` | Generated CSV exports | CSV files ignored |
| `tmp/` | Isolated manual-test data and exports | Runtime patterns ignored |
| `.coverage`, `htmlcov/`, `coverage.xml` | Coverage artifacts | Ignored |

Versioned document shapes and legacy compatibility are defined in
[docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md). Recovery behavior is defined in
[docs/PERSISTENCE_RELIABILITY.md](docs/PERSISTENCE_RELIABILITY.md).

## Tests

| Test area | Representative files |
| --- | --- |
| Domain and validation | `tests/test_validators_and_model.py` |
| Services and result values | `tests/test_expense_service.py`, `tests/test_budget_service.py`, `tests/test_settings_service.py`, `tests/test_export_service.py` |
| Repository behavior | `tests/repository_contracts.py`, `tests/test_json_repository_contract.py`, `tests/test_storage.py` |
| CLI input/presentation | `tests/test_commands.py`, `tests/test_formatters.py`, `tests/test_menu.py` |
| Composition and boundaries | `tests/test_application_composition.py`, `tests/test_service_boundaries.py` |
| Integration and executable | `tests/test_integration.py`, `tests/test_main.py` |

The exact test count can change. The supported guarantee is that the complete
suite passes the quality gates in
[docs/QUALITY_AUTOMATION.md](docs/QUALITY_AUTOMATION.md).

## Documentation authority

- Project orientation: [README.md](README.md)
- Source tree: [STRUCTURE.md](STRUCTURE.md)
- Technical document map: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- Phase 1 milestone status:
  [docs/PHASE_1_UPGRADE_ROADMAP.md](docs/PHASE_1_UPGRADE_ROADMAP.md)
- Django handoff design:
  [docs/DJANGO_MIGRATION_READINESS.md](docs/DJANGO_MIGRATION_READINESS.md)

This project has selected Django for the later web roadmap. It has not selected
FastAPI, and neither framework is implemented during Phase 1 stabilization.
