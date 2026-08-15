# Documentation index

This is the canonical map of active project documentation. If two documents
appear to conflict, the narrower technical contract governs behavior and the
Phase 1 roadmap governs milestone status.

## Start here

| Document | Purpose |
| --- | --- |
| [README.md](README.md) | Project purpose, capabilities, setup, and status |
| [QUICK_START.md](QUICK_START.md) | Safe manual start and automated verification |
| [PROJECT_INDEX.md](PROJECT_INDEX.md) | Code areas, menu map, test map, and runtime artifacts |
| [STRUCTURE.md](STRUCTURE.md) | Source tree, ownership, and dependency direction |
| [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) | Environment and contributor readiness checklist |

## Architecture and contracts

| Document | Authority |
| --- | --- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Current component boundaries and runtime flows |
| [docs/ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md) | Recorded Phase 1 design decisions and consequences |
| [docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md) | Version 2 JSON and legacy migration contract |
| [docs/PERSISTENCE_RELIABILITY.md](docs/PERSISTENCE_RELIABILITY.md) | Atomic save, backup, recovery, and failure behavior |
| [docs/REPOSITORY_CONTRACTS.md](docs/REPOSITORY_CONTRACTS.md) | Repository protocols and service boundary |
| [docs/APPLICATION_COMPOSITION.md](docs/APPLICATION_COMPOSITION.md) | Composition root, configuration, clock, and UUID providers |

## Quality and release progress

| Document | Purpose |
| --- | --- |
| [docs/QUALITY_AUTOMATION.md](docs/QUALITY_AUTOMATION.md) | Local checks and GitHub Actions gates |
| [docs/PHASE_1_UPGRADE_ROADMAP.md](docs/PHASE_1_UPGRADE_ROADMAP.md) | Authoritative milestone map |
| [docs/PHASE_1_ACCEPTANCE.md](docs/PHASE_1_ACCEPTANCE.md) | Data-foundation acceptance evidence |
| [docs/COMPLETION_CHECKLIST.md](docs/COMPLETION_CHECKLIST.md) | Remaining Phase 1 release-gate checklist |
| [docs/BUILD_SUMMARY.md](docs/BUILD_SUMMARY.md) | Concise current implementation summary |
| [docs/PHASE_1_RELEASE_REPORT.md](docs/PHASE_1_RELEASE_REPORT.md) | Verified release-candidate evidence, limitations, and remaining publication work |

## Future Django handoff

[docs/DJANGO_MIGRATION_READINESS.md](docs/DJANGO_MIGRATION_READINESS.md) maps
the current data and boundaries to future Django models and provides a
verification-first migration checklist. It is a design artifact only; Django
is not installed or implemented in this phase.

## Documentation maintenance rule

Every behavior change must update its narrow contract document, any affected
setup or menu guidance, and the roadmap status in the same pull request. Avoid
fixed test-count claims because the suite grows; the CI result is the source of
truth. Historical reports belong in Git history rather than active files that
claim an unfinished phase is complete.
