# Quick start and verification

## 1. Create the environment

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip check
```

If PowerShell blocks activation, either update the execution policy for the
current process or invoke `.\.venv\Scripts\python.exe` directly.

## 2. Run safely with isolated data

```powershell
$env:EXPENSE_TRACKER_DATA_DIR = "tmp/quick-start-data"
$env:EXPENSE_TRACKER_EXPORT_DIR = "tmp/quick-start-exports"
$env:EXPENSE_TRACKER_DEFAULT_CURRENCY = "USD"
python -m src.main
```

Suggested smoke workflow:

1. Open **Settings** and confirm `USD`.
2. Add an expense with amount `12.345`; confirm it displays as `USD 12.35`.
3. View its details; confirm the UUID and UTC creation timestamp appear.
4. Set a budget for the same category and view Budget Status.
5. Export expenses, then inspect the CSV under the isolated export directory.
6. Exit and restart; confirm the expense and budget reload.

Do not run manual experiments against important files in `data/`. Isolated
directories make verification repeatable and protect real records.

## 3. Inspect version 2 JSON

```powershell
Get-Content tmp\quick-start-data\expenses.json
Get-Content tmp\quick-start-data\budgets.json
Get-Content tmp\quick-start-data\settings.json
```

Expected top-level fields include `schema_version` and `currency`. Expense
records also include `id`, `occurred_on`, `amount`, `currency`, `category`,
`description`, and `created_at`. See
[docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md) for the exact contract.

## 4. Run automated verification

```powershell
python -m ruff check .
python -m ruff format --check .
python -m compileall -q src tests
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=85 -q
```

The test suite uses temporary directories and checks that repository
production data is unchanged.

## 5. Clear the temporary environment variables

```powershell
Remove-Item Env:EXPENSE_TRACKER_DATA_DIR
Remove-Item Env:EXPENSE_TRACKER_EXPORT_DIR
Remove-Item Env:EXPENSE_TRACKER_DEFAULT_CURRENCY
```

The temporary files remain ignored by Git and may be inspected after the run.
The full quality policy is in
[docs/QUALITY_AUTOMATION.md](docs/QUALITY_AUTOMATION.md).
