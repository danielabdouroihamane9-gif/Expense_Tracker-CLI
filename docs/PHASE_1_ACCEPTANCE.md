# Phase 1 acceptance checklist

Phase 1 establishes a stable data contract for the current CLI and for later
pandas and Django phases.

## Automated acceptance

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=src --cov-report=term-missing -q
```

The suite covers exact decimal arithmetic, stable IDs, UTC creation times,
legacy JSON migration, configurable currency, cross-file currency mismatch
protection, budgets, reports, imports, exports, and CLI routing.

## Manual acceptance

1. Start with `python -m src.main`.
2. Confirm the main menu shows `Settings (Currency: USD)` for a legacy setup.
3. With no expenses or budgets, change the currency under **Settings** and
   restart the application. Confirm the choice persists.
4. Add an expense and budget. Confirm prompts, tables, details, totals, budget
   status, statistics, and confirmations use the configured currency code.
5. Confirm expense details show UUID, occurrence date, exact amount, currency,
   category, description, and UTC creation timestamp.
6. Export expenses and a summary. Confirm both CSV files include `Currency`.
7. Import an old four-column CSV. Confirm it receives the configured currency.
8. Import a CSV row with a different explicit currency. Confirm it fails with
   an explanatory row error.
9. Try changing currency while expenses or budgets exist. Confirm it is
   refused without modifying data.
10. Inspect `expenses.json`, `budgets.json`, and `settings.json`. Confirm all
    have `schema_version: 2` and use the same currency.

Phase 1 is accepted only when the automated suite passes and this manual flow
behaves as described.
