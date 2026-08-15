# Phase 1 release completion checklist

This checklist belongs to Milestone 7. Earlier documents that called the whole
phase complete before the release gate were inaccurate.

The release gate was verified on 2026-08-15 and published as `v1.0.0` through
the reviewed release workflow. Evidence is in
[PHASE_1_RELEASE_REPORT.md](PHASE_1_RELEASE_REPORT.md) and GitHub history.

## Clean installation

- [x] Create a new virtual environment with a supported Python version.
- [x] Install `requirements-dev.txt` without relying on the existing `.venv`.
- [x] Run `python -m pip check` successfully.
- [x] Decide whether each production dependency is used; remove unused ones
  only with a tested, documented change.

## Automated quality

- [x] `python -m ruff check .`
- [x] `python -m ruff format --check .`
- [x] `python -m compileall -q src tests`
- [x] `python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=85 -q`
- [x] GitHub Actions passes static quality and every supported Python version.

## Acceptance and data safety

- [x] Verify every current CLI route and exercise system workflows using
  isolated runtime paths.
- [x] Verify version 2 files, exact rounding, UUIDs, occurrence dates, UTC
  timestamps, and currency labels.
- [x] Verify CSV export and import, including currency mismatch rejection.
- [x] Verify original unversioned JSON migration on the next save.
- [x] Verify corrupt-primary recovery from a valid `.bak` file.
- [x] Verify invalid primary plus invalid backup fails visibly.
- [x] Confirm tests and automated acceptance checks did not alter real `data/`
  files.

## Documentation and repository hygiene

- [x] Active documentation matches the current CLI, source structure, schema,
  configuration, and quality workflow.
- [x] Local documentation links pass the documentation integrity test.
- [x] No active document claims a future framework or database is implemented.
- [x] Git contains no secrets, personal financial data, generated exports,
  caches, coverage files, or manual temporary data.
- [x] Resolve or document outstanding branches and stashes.

## Release

- [x] Merge the final Phase 1 pull request after review and CI.
- [x] Fast-forward local `main` to the merged commit.
- [x] Create and push the agreed stable Phase 1 version tag (`v1.0.0`).
- [x] Publish a completion report containing the verified command results,
  known limitations, and next-roadmap boundary.
- [x] Mark Milestone 7 complete in
  [PHASE_1_UPGRADE_ROADMAP.md](PHASE_1_UPGRADE_ROADMAP.md).
