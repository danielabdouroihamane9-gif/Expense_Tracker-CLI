# Phase 1 release completion checklist

This checklist belongs to Milestone 7. Earlier documents that called the whole
phase complete before the release gate were inaccurate.

## Clean installation

- [ ] Create a new virtual environment with a supported Python version.
- [ ] Install `requirements-dev.txt` without relying on the existing `.venv`.
- [ ] Run `python -m pip check` successfully.
- [ ] Decide whether each production dependency is used; remove unused ones
  only with a tested, documented change.

## Automated quality

- [ ] `python -m ruff check .`
- [ ] `python -m ruff format --check .`
- [ ] `python -m compileall -q src tests`
- [ ] `python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=85 -q`
- [ ] GitHub Actions passes static quality and every supported Python version.

## Acceptance and data safety

- [ ] Exercise all current CLI menu branches using isolated runtime paths.
- [ ] Verify version 2 files, exact rounding, UUIDs, occurrence dates, UTC
  timestamps, and currency labels.
- [ ] Verify CSV export and import, including currency mismatch rejection.
- [ ] Verify original unversioned JSON migration on the next save.
- [ ] Verify corrupt-primary recovery from a valid `.bak` file.
- [ ] Verify invalid primary plus invalid backup fails visibly.
- [ ] Confirm tests and manual checks did not alter real `data/` files.

## Documentation and repository hygiene

- [ ] Active documentation matches the current CLI, source structure, schema,
  configuration, and quality workflow.
- [ ] Local documentation links pass the documentation integrity test.
- [ ] No active document claims a future framework or database is implemented.
- [ ] Git contains no secrets, personal financial data, generated exports,
  caches, coverage files, or manual temporary data.
- [ ] Resolve or document outstanding branches and stashes.

## Release

- [ ] Merge the final Phase 1 pull request after review and CI.
- [ ] Fast-forward local `main` to the merged commit.
- [ ] Create and push the agreed stable Phase 1 version tag.
- [ ] Publish a completion report containing the verified command results,
  known limitations, and next-roadmap boundary.
- [ ] Mark Milestone 7 complete in
  [PHASE_1_UPGRADE_ROADMAP.md](PHASE_1_UPGRADE_ROADMAP.md).
