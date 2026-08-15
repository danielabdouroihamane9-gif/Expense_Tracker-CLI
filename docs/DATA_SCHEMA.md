# Data schema

The JSON persistence format is versioned so the CLI can evolve into the later
pandas and Django phases without redefining its core data contract.

## Version 2 expense document

```json
{
  "schema_version": 2,
  "currency": "USD",
  "expenses": [
    {
      "id": "12345678-1234-5678-1234-567812345678",
      "amount": "12.35",
      "currency": "USD",
      "category": "food",
      "description": "Lunch",
      "occurred_on": "2025-05-28",
      "created_at": "2025-05-28T10:00:00Z"
    }
  ]
}
```

- `id` is a stable UUID suitable for future database primary-key mapping.
- Monetary values are decimal strings with two fractional digits. They must
  not be converted to binary floating-point values.
- `currency` is a normalized three-letter code and must match the application
  setting. Existing repositories default to `USD`.
- `occurred_on` is the business date supplied by the user.
- `created_at` is the UTC timestamp at which the record was created.

Budgets use the same document version and decimal-string convention:

```json
{
  "schema_version": 2,
  "currency": "USD",
  "budgets": {"food": "250.00"}
}
```

## Application currency

The application uses one currency for every expense, budget, total, report,
and export. The initial default is `USD`. A different currency can be selected
from **Main Menu > Settings > Change Currency** while no expenses or budgets
exist.

The setting is stored separately:

```json
{
  "schema_version": 2,
  "currency": "USD"
}
```

The application refuses to change currency while financial data exists. This
prevents a value such as `USD 100.00` from being silently relabelled as
`KMF 100.00` without an exchange-rate conversion. Versioned expense and budget
documents whose currency conflicts with the setting are also rejected.

## Backward compatibility

The reader accepts the original unversioned expense list with `date` and
numeric `amount` fields, as well as the original unversioned budget object.
Missing IDs and creation timestamps are generated in memory. A missing
currency receives the configured application currency.
The next successful save upgrades the file to version 2.

Versioned documents must declare integer `schema_version: 2` and contain the
correct collection type. All records are validated before any are accepted.
Schema versions greater than 2 are rejected explicitly so an older application
cannot overwrite data created by a newer version.

CSV imports keep the original four required columns (`Date`, `Amount`,
`Category`, `Description`). `Currency` is optional and defaults to the current
application currency. A row declaring another currency is rejected. New
expense and summary exports include the currency explicitly.

## Persistence and backups

Primary documents are written through a flushed temporary file and atomic
replacement. Before an existing valid document is overwritten, its previous
contents are saved as `expenses.json.bak`, `budgets.json.bak`, or
`settings.json.bak`.

Corrupt or missing primary data is restored automatically only when its backup
passes the same schema and domain validation. Serious read, validation, and
recovery failures are raised explicitly rather than treated as empty data. See
[`PERSISTENCE_RELIABILITY.md`](PERSISTENCE_RELIABILITY.md) for guarantees and
manual recovery instructions.
