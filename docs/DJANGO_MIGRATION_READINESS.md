# Django migration readiness

This is a future handoff design for the selected web framework. It does not add
Django, database models, migrations, views, APIs, authentication, or
PostgreSQL to Roadmap Phase 1.

The field names below are proposals that preserve current semantics. Before
implementation, select the supported Django version and database, then verify
the design against that version's official documentation.

## Current-to-Django data map

### Expense

| Current value | Future Django concept | Preservation rule |
| --- | --- | --- |
| `id: UUID` | `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` | Import the existing UUID; generate only for new rows |
| `occurred_on: date` | `DateField` | Preserve the calendar date exactly |
| `amount: Decimal` | `DecimalField(decimal_places=2, max_digits=...)` | Choose `max_digits` from a documented business limit; never convert through float |
| `currency: str` | `CharField(max_length=3)` | Normalize uppercase and enforce the owning account's currency rule |
| `category: str` | `CharField` with choices | Preserve the current eight normalized values |
| `description: str` | `CharField` or `TextField` | Decide and document a maximum length before schema creation |
| `created_at: datetime` | `DateTimeField(default=timezone.now)` | Import the existing UTC timestamp |

Do not use `auto_now_add` for the initial historical migration. Existing
creation timestamps must be assignable rather than replaced by import time.

Django's official model-field reference defines `UUIDField`, `DecimalField`,
`DateField`, and `DateTimeField` and shows UUID primary-key defaults:
[model field reference](https://docs.djangoproject.com/en/5.2/ref/models/fields/).

### Budget

The current budget document is a category-to-`Decimal` mapping. It has no
budget UUID, audit timestamp, or owner. A future relational representation
needs one row per owner/account and category:

| Proposed field | Purpose |
| --- | --- |
| owner/account foreign key | Defines whose budget it is once multi-user scope exists |
| category | One of the supported expense categories |
| amount | Exact two-decimal positive value |
| currency or inherited setting | Must follow one explicit ownership rule |
| created/updated timestamps | Add only after their product meaning is defined |

Add a database `UniqueConstraint` for `(owner, category)` and a positive-amount
check where the selected database supports the intended constraint. Django
documents database constraints in its
[constraints reference](https://docs.djangoproject.com/en/5.2/ref/models/constraints/).
Do not invent budget IDs or timestamps during Phase 1 merely to resemble a
future schema.

### Settings

The current setting is globally persisted as `{"currency": "USD"}`. In a
multi-user Django system it will probably belong to an account or user profile,
but that ownership decision depends on the later authentication and tenancy
design. Until that decision is made, do not create a global singleton model and
assume it will scale.

## Repository transition

The current contracts load or save an entire collection. They are useful for
proving that services do not know about JSON and may be implemented by a first
Django adapter during a controlled migration.

That compatibility adapter has limits:

- whole-table reads waste memory and database work;
- whole-collection writes can overwrite concurrent changes;
- process-local service state becomes stale across requests;
- transaction scope is not expressed by the current protocols;
- filtering and aggregation cannot benefit fully from database queries.

Before multi-user or high-volume release, evolve the application boundary to
granular operations such as get/list/create/update/delete, paginated queries,
database-side filtering/aggregation, and explicit units of work. Preserve the
business rules and expand the reusable contract tests while doing so.

## Migration checklist

### 1. Freeze and inventory

- [ ] Select and pin the supported Python, Django, and database versions.
- [ ] Define ownership: single account, user, household, or organization.
- [ ] Define amount maximum, description length, timezone policy, and currency
  ownership before creating fields.
- [ ] Stop writes during the final export or define a real synchronization
  strategy; do not migrate a moving JSON target casually.
- [ ] Copy all primary and `.bak` documents outside the application directory.

### 2. Validate the source

- [ ] Load every document through the existing validated repository.
- [ ] Reject unresolved corruption, unsupported schemas, invalid categories,
  duplicate expense UUIDs, nonpositive amounts, and currency conflicts.
- [ ] Record source counts, per-currency totals, category totals, minimum and
  maximum dates, and a cryptographic hash of the frozen input files.
- [ ] Convert legacy documents to version 2 with the existing application and
  verify the result before database import.

### 3. Build the target schema

- [ ] Create Django models and schema migrations from the reviewed mapping.
- [ ] Add database constraints for uniqueness and invariant enforcement.
- [ ] Keep importable historical timestamps; do not substitute current time.
- [ ] Write reversible data migrations or a separately versioned import command.
- [ ] Test forward and rollback behavior on disposable databases.

The official Django migration guide discusses historical models, data
migrations, and operational considerations:
[writing migrations](https://docs.djangoproject.com/en/5.2/howto/writing-migrations/).

### 4. Import atomically

- [ ] Parse decimal strings directly to `Decimal`.
- [ ] Preserve expense UUIDs, occurrence dates, UTC timestamps, descriptions,
  categories, and currency values.
- [ ] Create budgets only after their target ownership is known.
- [ ] Run a bounded import inside an explicit database transaction.
- [ ] Let database exceptions escape the atomic block so rollback is reliable.

Django's `transaction.atomic()` commits the complete block on success and
rolls it back on exception; its official guidance also recommends keeping
transactions short:
[database transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/).

### 5. Verify before cutover

- [ ] Compare source and target expense and budget counts.
- [ ] Compare exact grand, category, month, and currency totals.
- [ ] Sample and then programmatically compare all UUIDs and field values.
- [ ] Run repository contract tests against the Django adapter plus
  database-specific transaction and concurrency tests.
- [ ] Run end-to-end application tests using the database adapter.
- [ ] Record evidence and require an independent review before cutover.

### 6. Cut over and retain rollback

- [ ] Choose a maintenance-window or rehearsed dual-read strategy.
- [ ] Keep the frozen JSON snapshot read-only for the agreed retention period.
- [ ] Define the exact rollback trigger and who can execute it.
- [ ] Monitor errors, row counts, totals, and latency after cutover.
- [ ] Do not delete JSON source or backups until reconciliation and retention
  requirements are satisfied.

## Decisions still required later

- Django and database versions
- user/account/household ownership model
- API versus server-rendered UI boundary
- `max_digits` and description length
- currency ownership and eventual multi-currency policy
- category evolution strategy
- granular repository/use-case interface
- migration downtime, retention, and rollback policy

Leaving these items explicit is safer than encoding guesses in Phase 1.
