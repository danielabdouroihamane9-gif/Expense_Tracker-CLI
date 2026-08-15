# Phase 1 Upgrade Roadmap

This is the authoritative milestone map for stabilizing the Core Python
Expense Tracker before beginning Roadmap Phase 2. Milestone numbers in this
document are upgrades **within Roadmap Phase 1**. They are not roadmap phases.

## Progress

| Milestone | Purpose | Status |
| --- | --- | --- |
| 1. Data Foundation | Establish stable, migration-ready financial data | Complete |
| 2. Persistence Reliability | Protect JSON data from corruption and failures | Complete |
| 3. Repository and Service Boundaries | Decouple business rules from JSON and CLI details | Complete |
| 4. Application Composition and Configuration | Centralize dependency construction and runtime configuration | Complete |
| 5. Quality Automation | Automate tests, coverage, style checks, and CI | Complete |
| 6. Documentation and Migration Readiness | Align documentation and prepare the Django handoff | Complete |
| 7. Phase 1 Release Gate | Complete acceptance and publish a stable Phase 1 release | Complete (`v1.0.0`) |

## Milestone 1 - Data Foundation

Completed capabilities:

- Stable expense UUIDs.
- Exact `Decimal` monetary values.
- One configurable application currency, initially USD.
- Separate expense occurrence dates and UTC creation timestamps.
- Versioned JSON documents.
- Backward-compatible legacy JSON loading.
- Currency-aware expenses, budgets, reports, imports, and exports.
- Migration, integration, and system tests.
- Data-contract and acceptance documentation.

## Milestone 2 - Persistence Reliability

Completed capabilities:

- Write JSON atomically through a temporary file and replacement.
- Prevent partial JSON from replacing valid data.
- Back up the previous valid document before overwriting it.
- Recover from a valid backup when the primary document is corrupted.
- Validate document structure before accepting loaded data.
- Reject unsupported future schema versions.
- Introduce explicit persistence exceptions.
- Stop silently treating serious storage failures as empty data.
- Handle persistence errors consistently in services and the CLI.
- Test permission failures, interrupted writes, invalid JSON, invalid schema,
  recovery, and legacy migration.
- Ensure failed saves do not leave incorrect in-memory service state.
- Document persistence guarantees and recovery procedures.

## Milestone 3 - Repository and Service Boundaries

Completed capabilities:

- Define repository contracts for expenses, budgets, and settings.
- Make services depend on repository contracts instead of constructing
  `JSONStorage` directly.
- Keep JSON-specific behavior inside the storage implementation.
- Separate business results from CLI presentation strings.
- Establish consistent domain and application exceptions.
- Keep the CLI responsible only for input and presentation.
- Add repository contract tests reusable by later implementations.

## Milestone 4 - Application Composition and Configuration

Completed capabilities:

- Created one application factory and composition root.
- Constructed repositories, services, CLI commands, and the menu in one
  location.
- Injected repositories and runtime providers instead of constructing them
  inside services or presentation components.
- Centralized data paths, export paths, initial currency, and environment
  configuration.
- Persisted the resolved initial currency before financial data can depend on
  it.
- Added injectable clock and UUID generation for entities, legacy migration,
  reports, input defaults, and export filenames.
- Kept `src/main.py` as a thin entry point.
- Isolated ambient time and UUID calls to system provider implementations.
- Added architecture, configuration, deterministic-provider, integration, and
  startup tests.

## Milestone 5 - Quality Automation

Completed capabilities:

- Runs the complete suite through GitHub Actions without duplicate branch and
  pull request runs.
- Enforces the 85% coverage threshold locally and in CI.
- Adds pinned Ruff linting, formatting, and import-order checks.
- Adds an explicit source and test syntax compilation gate.
- Tests every supported Python version from 3.11 through 3.14.
- Fails the suite if automated tests create or modify repository production
  data.
- Adds composed persistence recovery and subprocess CLI workflow tests.
- Verifies test jobs do not modify tracked files.
- Documents local quality commands, CI gates, and the pull request merge
  checklist.

## Milestone 6 - Documentation and Migration Readiness

Completed capabilities:

- Aligned the root orientation, project index, structure, setup, architecture,
  build summary, and release checklist with the implemented application.
- Replaced obsolete menu, test-count, Python-version, and completion claims.
- Consolidated active documentation around the existing schema, persistence,
  repository, composition, and quality contracts.
- Recorded accepted decisions for Decimal money, UUID identity, dates and UTC
  timestamps, application currency, repository boundaries, versioned atomic
  JSON, composition, and deterministic providers.
- Mapped current expenses, budget mappings, and settings to future Django
  concepts without presenting proposed models as implemented code.
- Documented source validation, transactional import, reconciliation, cutover,
  retention, and rollback requirements for a later Django migration.
- Recorded the scalability limit of whole-collection repository contracts and
  the need for granular transactional interfaces before multi-user use.
- Removed obsolete active completion reports while retaining their history in
  Git.
- Added automated checks for local documentation links and known stale claims.
- Confirmed Django is the later selected framework and that no web framework is
  implemented during Phase 1.

## Milestone 7 - Phase 1 Release Gate

Completed capabilities:

- Ran the full automated quality and acceptance suite in a clean environment.
- Verified a standard-library-only runtime environment starts the CLI safely.
- Re-tested legacy migration, backup recovery, invalid recovery, versioned data,
  configurable currency, CSV workflows, and subprocess CLI persistence.
- Confirmed documentation matches current behavior and local links resolve.
- Confirmed runtime data, generated files, and secrets are absent from tracked
  release content.
- Removed unused pandas, NumPy, and openpyxl runtime dependencies.
- Documented merged historical branches and the preserved obsolete stash.
- Published verification evidence in
  `PHASE_1_RELEASE_REPORT.md`.
- Passed the final pull-request quality matrix on every supported Python
  version and merged the reviewed release commit into `main`.
- Synchronized local `main` and published the stable `v1.0.0` tag.

## Boundary

These milestones do not implement HTTP APIs, Django, Django REST Framework,
PostgreSQL, authentication, multi-user accounts, or AI/ML. Those belong to
later roadmap phases after this upgrade roadmap is complete.
