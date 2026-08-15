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
| 5. Quality Automation | Automate tests, coverage, style checks, and CI | Pending |
| 6. Documentation and Migration Readiness | Align documentation and prepare the Django handoff | Pending |
| 7. Phase 1 Release Gate | Complete acceptance and publish a stable Phase 1 release | Pending |

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

- Run the complete suite through GitHub Actions.
- Enforce the coverage threshold automatically.
- Add linting, formatting, import, and syntax checks.
- Test the supported Python versions.
- Ensure automated tests never modify production data.
- Add persistence recovery integration tests and CLI smoke tests.
- Document the checks required before merging a pull request.

## Milestone 6 - Documentation and Migration Readiness

- Align `README.md`, `PROJECT_INDEX.md`, `STRUCTURE.md`, and architecture
  documentation with the actual application.
- Remove obsolete menu commands and examples.
- Document schemas, migration rules, repository contracts, and composition.
- Record architectural decisions for Decimal, UUID, currency, and storage.
- Map the Python domain model to future Django models.
- Create a Django migration checklist without implementing Django.
- Remove claims that FastAPI is the selected framework.

## Milestone 7 - Phase 1 Release Gate

- Run all automated and manual acceptance checks.
- Test a clean dependency installation.
- Test legacy migration and backup recovery.
- Confirm documentation matches behavior.
- Confirm secrets and temporary files are excluded from Git.
- Remove unused dependencies and resolve outstanding branches or stashes.
- Merge the final Phase 1 release pull request.
- Tag the stable Phase 1 version.
- Publish the final completion report.

## Boundary

These milestones do not implement HTTP APIs, Django, Django REST Framework,
PostgreSQL, authentication, multi-user accounts, or AI/ML. Those belong to
later roadmap phases after this upgrade roadmap is complete.
