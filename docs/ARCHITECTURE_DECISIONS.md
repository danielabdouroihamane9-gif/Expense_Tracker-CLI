# Architecture decisions

These records explain Phase 1 decisions that later implementations must
preserve or deliberately supersede. Status `Accepted` means implemented in the
current CLI.

## ADR-001: Use Decimal for money

- **Status:** Accepted
- **Decision:** Parse money through `Decimal`, require positive finite values,
  quantize to two fractional digits with `ROUND_HALF_UP`, and serialize as
  strings.
- **Why:** Binary floating point cannot represent many decimal amounts exactly.
  Financial totals, budget comparisons, CSV values, and future database values
  need one exact convention.
- **Consequence:** A future Django model should use `DecimalField` with
  `decimal_places=2`. `max_digits` must be chosen from an explicit product
  limit before the model is implemented.

## ADR-002: Give expenses stable UUID identity

- **Status:** Accepted
- **Decision:** Every expense has a UUID supplied by an injected generator.
  Legacy records receive an ID during loading and persist it on the next save.
- **Why:** List positions and mutable field combinations are not durable
  identities. UUIDs can survive import, migration, and storage changes.
- **Consequence:** Preserve existing UUIDs during database import. Generate a
  new UUID only for genuinely new expenses.

## ADR-003: Separate occurrence date from creation time

- **Status:** Accepted
- **Decision:** `occurred_on` is the user-supplied business date;
  `created_at` is a timezone-aware UTC audit timestamp.
- **Why:** The date of a purchase and the time the application recorded it are
  different facts.
- **Consequence:** Future persistence needs a date field and a datetime field.
  Historical imports must preserve existing `created_at` values rather than
  replacing them with migration time.

## ADR-004: Use one persisted application currency

- **Status:** Accepted
- **Decision:** All expenses, budgets, reports, imports, and exports use one
  three-letter application currency. The initial default is `USD`. Changing it
  is blocked while financial data exists.
- **Why:** Relabelling `USD 100.00` as `KMF 100.00` without exchange conversion
  corrupts financial meaning.
- **Consequence:** This is deliberately not a multi-currency design. A later
  account or user model may own the setting, but real currency conversion must
  be a separate, explicit feature.

## ADR-005: Depend on repository protocols

- **Status:** Accepted
- **Decision:** Services depend on expense, budget, and settings protocols;
  the composition root injects the concrete adapter.
- **Why:** Business rules and tests should survive replacement of local JSON
  with another persistence technology.
- **Consequence:** Every new adapter runs the reusable repository contract
  tests. The current whole-collection methods are a migration seam, not a
  final concurrent-database API.

## ADR-006: Use versioned, atomic JSON persistence

- **Status:** Accepted
- **Decision:** Store separate version 2 JSON documents, validate each complete
  document, write through a flushed same-directory temporary file, atomically
  replace the primary, and retain the previous valid document as `.bak`.
- **Why:** A local application must not silently accept malformed data or leave
  a partially written primary file after failure.
- **Consequence:** Recovery can restore only the previous valid version, so the
  latest save may be lost. JSON remains a single-process store and is not a
  substitute for database transactions or concurrency control.

## ADR-007: Centralize composition and runtime providers

- **Status:** Accepted
- **Decision:** Construct concrete dependencies in `src/application.py`, read
  runtime configuration at one boundary, and inject clock and UUID providers.
- **Why:** Hidden filesystem, time, UUID, and construction dependencies make
  tests nondeterministic and framework migration expensive.
- **Consequence:** Future CLI or Django entry points may compose different
  adapters while reusing application rules. Production code outside provider
  implementations should not call ambient clocks or UUID generation directly.

## Changing a decision

Do not silently edit an accepted decision after behavior changes. Add a new ADR
or mark the old one superseded, identify the migration impact, and update the
schema, architecture, tests, and roadmap together.
