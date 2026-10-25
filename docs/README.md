# Technical documentation

## Current system

- [Architecture](ARCHITECTURE.md)
- [Architecture decisions](ARCHITECTURE_DECISIONS.md)
- [Application composition and configuration](APPLICATION_COMPOSITION.md)
- [Repository and service boundaries](REPOSITORY_CONTRACTS.md)
- [Data schema](DATA_SCHEMA.md)
- [Persistence reliability](PERSISTENCE_RELIABILITY.md)
- [Quality automation](QUALITY_AUTOMATION.md)

## Django backend deployment

Configure the Render backend's `CORS_ALLOWED_ORIGINS` environment variable
with the exact deployed frontend origin, including its scheme and hostname
but no path or trailing slash. Use the actual Vercel deployment origin; do
not use a placeholder domain or allow all origins. Separate multiple origins
with commas and redeploy Render after changing the setting.

## Phase 1 status

- [Upgrade roadmap](PHASE_1_UPGRADE_ROADMAP.md)
- [Data-foundation acceptance](PHASE_1_ACCEPTANCE.md)
- [Current build summary](BUILD_SUMMARY.md)
- [Release completion checklist](COMPLETION_CHECKLIST.md)
- [Release-candidate verification report](PHASE_1_RELEASE_REPORT.md)

## Later roadmap preparation

- [Django migration readiness](DJANGO_MIGRATION_READINESS.md)

The Django document is a future handoff plan, not implemented application
behavior. The repository remains a single-user local CLI throughout Roadmap
Phase 1.

The root [documentation index](../DOCUMENTATION_INDEX.md) also maps setup,
navigation, and repository-structure documents.
