# Repository structure

```text
expense_tracker/
|-- .github/workflows/tests.yml
|-- docs/
|-- src/
|   |-- cli/
|   |   |-- commands.py
|   |   `-- menu.py
|   |-- models/
|   |   `-- expense.py
|   |-- repositories/
|   |   |-- contracts.py
|   |   `-- exceptions.py
|   |-- services/
|   |   |-- budget_service.py
|   |   |-- expense_tracker.py
|   |   |-- export_service.py
|   |   |-- results.py
|   |   `-- settings_service.py
|   |-- storage/
|   |   |-- exceptions.py
|   |   `-- json_storage.py
|   |-- utils/
|   |   |-- formatters.py
|   |   `-- validators.py
|   |-- application.py
|   |-- config.py
|   |-- exceptions.py
|   |-- main.py
|   `-- providers.py
|-- tests/
|-- data/                 # ignored runtime JSON and backups
|-- exports/              # ignored generated CSV files
|-- requirements.txt
|-- requirements-dev.txt
|-- pytest.ini
|-- ruff.toml
`-- README.md
```

Package `__init__.py` files are omitted above for readability.

## Dependency ownership

- `src/main.py` owns process-level startup and exit behavior.
- `src/application.py` owns concrete construction and dependency injection.
- `src/cli/` owns all terminal input and output.
- `src/services/` owns use cases and application rules.
- `src/models/` owns the `Expense` entity and its invariants.
- `src/repositories/` owns persistence-neutral interfaces.
- `src/storage/` owns the JSON adapter and file reliability.
- `src/utils/` owns shared validation and presentation helpers.

Dependencies point toward protocols and domain rules. Services do not import
`JSONStorage`, and persistence does not print terminal messages.

## Runtime object graph

```text
ApplicationConfig ----+
SystemClock -----------+--> create_application()
SystemUUIDGenerator ---+          |
                                  +--> JSONStorage
                                  +--> services
                                  +--> CommandHandler
                                  `--> Menu --> Application
```

The one `JSONStorage` instance structurally implements the expense, budget,
and settings repository protocols. The application injects the same clock and
UUID provider wherever deterministic runtime values are needed.

## Storage shape

The repository persists three independent version 2 documents:

- `expenses.json`: expense collection with UUIDs and timestamps;
- `budgets.json`: category-to-decimal-string budget mapping;
- `settings.json`: one application currency.

Each may have a `.bak` previous-version backup. The complete contract is in
[docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md).

## Test structure

Tests mirror the production boundaries:

- model and validator unit tests;
- service unit tests using in-memory fakes;
- reusable repository contract tests;
- JSON storage failure and recovery tests;
- CLI command, formatter, and menu tests;
- composition, integration, and subprocess entry-point tests.

All test writes use temporary directories. See
[docs/QUALITY_AUTOMATION.md](docs/QUALITY_AUTOMATION.md).

## Intended evolution

The current structure allows a later Django repository adapter to sit on the
right side of the repository protocols. It does not imply that whole-collection
load/save contracts are the final database interface. Before multi-user or
high-volume operation, those contracts need deliberate granular and
transactional evolution. See
[docs/DJANGO_MIGRATION_READINESS.md](docs/DJANGO_MIGRATION_READINESS.md).
