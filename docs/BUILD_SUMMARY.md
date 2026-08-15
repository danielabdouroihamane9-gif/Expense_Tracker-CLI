# Current build summary

## Implemented

- Complete interactive CLI expense, budget, report, settings, CSV import, and
  CSV export workflows.
- Exact two-decimal `Decimal` money, stable expense UUIDs, business dates, and
  UTC creation timestamps.
- One persisted application currency, initially `USD`, with safe change rules.
- Version 2 JSON documents with legacy reading and controlled upgrade on save.
- Atomic replacement, previous-valid backups, validated recovery, and explicit
  persistence errors.
- Persistence-neutral repository protocols and service injection.
- Central composition, environment configuration, and deterministic clock and
  UUID providers.
- Automated lint, format, syntax, coverage, integration, subprocess, storage,
  and multi-version CI gates.

## Phase 1 milestone status

Milestones 1 through 6 are complete. Milestone 6 aligned active documentation,
recorded architecture decisions, and prepared a future Django migration plan.
Milestone 7 remains the final clean-install, acceptance, merge, tag, and release
gate.

The authoritative state is
[PHASE_1_UPGRADE_ROADMAP.md](PHASE_1_UPGRADE_ROADMAP.md).

## Explicitly not implemented

- Django or Django REST Framework
- an HTTP API
- PostgreSQL or another database adapter
- authentication, authorization, or multiple users
- AI/ML features

Those capabilities belong to later roadmap phases. The migration-readiness
document records preparation without expanding the current implementation
scope.

## Known release-gate work

- Verify a clean development installation.
- Re-run all automated and manual acceptance workflows.
- Review runtime dependencies and remove any that are demonstrably unused.
- Confirm branch, stash, secret, and generated-file hygiene.
- Merge, tag, and publish the stable Phase 1 completion report.

See [COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md).
