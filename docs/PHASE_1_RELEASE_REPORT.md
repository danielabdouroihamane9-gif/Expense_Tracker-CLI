# Phase 1 v1.0.0 release verification report

**Verification date:** 2026-08-15

**Branch:** `feature/phase1-milestone7-release-gate`

**Base commit:** `30fd24b`

**Release tag:** `v1.0.0`

**Status:** Phase 1 release gate verified. This report is part of the release
commit published through the final pull request and stable tag.

## Outcome

The Phase 1 CLI satisfies the release gate. No application defect or
data-safety regression was found. The only implementation change required by
the audit was removal of three unused production dependencies.

## Clean-install evidence

A new seeded Python 3.14.7 virtual environment was created without using the
repository `.venv`.

1. `requirements-dev.txt` installed successfully with pip.
2. `python -m pip check` reported no broken requirements.
3. Ruff linting and formatting passed inside the clean environment.
4. Source and tests compiled inside the clean environment.
5. The complete coverage-gated test suite passed inside the clean environment.

A second new Python 3.14.7 environment installed only `requirements.txt`. It
started `python -m src.main`, exited normally through menu option `0`, and
created a valid version 2 `settings.json` with currency `USD` in an isolated
directory.

Both temporary environments and their isolated runtime data were deleted after
verification. They contained no user data and are reproducible from the
requirements files.

## Dependency decision

`pandas`, `numpy`, and `openpyxl` were removed from `requirements.txt`.
Repository-wide import and reference searches proved that no active source or
test uses them. Phase 1 uses the Python standard library at runtime; pytest,
pytest-cov, and Ruff remain development-only dependencies.

Future data-analysis or spreadsheet work must add the smallest required
dependency in the milestone that implements that behavior, with tests proving
its use.

## Automated quality results

| Gate | Result |
| --- | --- |
| Ruff lint and import order | Pass |
| Ruff formatting | Pass |
| Source and test compilation | Pass |
| Tests | 193 passed |
| Coverage | 88.55% |
| Required coverage | 85% |
| Production-data mutation guard | Pass |
| Documentation links and stale claims | Pass |

The final pull request repeats static quality and the test matrix on Python
3.11, 3.12, 3.13, and 3.14 before merge.

## Acceptance evidence

- Every current main-menu and submenu route is enumerated by parametrized tests
  in `tests/test_menu.py`, including invalid input and return navigation.
- CLI-to-service orchestration is tested for expense, budget, reports,
  settings, CSV import, and CSV export actions.
- `tests/test_integration.py` exercises interactive expense creation, import,
  budgets, reports, exports, configurable currency, reload, backup recovery,
  and a real subprocess CLI workflow using isolated temporary paths.
- Version 2 envelopes, decimal-string money, half-up rounding, UUIDs,
  occurrence dates, UTC timestamps, and currency consistency are covered by
  model, validator, storage, service, and integration tests.
- Original unversioned expense and budget documents are loaded and upgraded on
  their next successful save.
- A corrupt primary with a valid backup is restored; invalid primary and backup
  documents fail visibly; unsupported future schemas are rejected.
- CSV currency mismatches are rejected, while compatible imports and exports
  preserve the application currency.

The suite snapshots repository `data/` files before and after testing and
fails on any content, creation, deletion, or modification-time change.

## Repository hygiene

- No files under `data/`, `exports/`, or `tmp/` are tracked.
- JSON runtime files, `.json.bak`, CSV, environment, cache, and coverage files
  are covered by active ignore rules.
- No secret-like key, password, token, or private-key assignment was found in
  active source, tests, or workflows.
- The working branch began from synchronized `main` and contains only the
  release-gate changes.
- Dependency scans confirmed that the ignored `.archive/` legacy programs,
  tests, FastAPI-era documents, and reports had no active consumer. The archive
  and seven isolated `tmp/` manual-test directories were permanently removed;
  they were never tracked and are therefore not recoverable from Git.
- Historical milestone branches are already merged into `main`; retaining
  their branch names does not change the release tree.
- One stash is deliberately preserved: `stash@{0}` contains formatting-only
  changes to a superseded `PROJECT_INDEX.md` plus obsolete menu and FastAPI
  guidance. It is not applied, staged, or part of the release. Deleting it
  requires explicit user approval because stash deletion is destructive.

## Known Phase 1 limitations

- The application is a local, single-user CLI.
- JSON storage is reliable for this scope but is not a concurrent database.
- Repository contracts currently load and save complete collections.
- One application currency is supported; currency conversion is not.
- Authentication, authorization, multiple accounts, Django, HTTP APIs,
  PostgreSQL, background processing, and AI/ML are not implemented.
- Coverage exceeds the release threshold but does not prove every terminal
  presentation edge case is defect-free.

These limits are intentional roadmap boundaries, not undocumented promises.
The Django handoff and required interface evolution are defined in
[DJANGO_MIGRATION_READINESS.md](DJANGO_MIGRATION_READINESS.md).

## Publication contract

This report is authoritative when read from tag `v1.0.0`. The release workflow
requires the final pull request checks to pass, merges that reviewed commit to
`main`, fast-forwards the local branch, and creates the annotated tag on the
resulting merge commit. GitHub pull-request, Actions, and tag history provide
the external publication evidence.
