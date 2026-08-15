# Setup and contributor checklist

## Environment

- [ ] Python is version 3.11 through 3.14: `python --version`.
- [ ] A repository-local virtual environment is active.
- [ ] Development dependencies are installed from `requirements-dev.txt`.
- [ ] `python -m pip check` reports no broken requirements.

## Runtime safety

- [ ] Manual experiments use `EXPENSE_TRACKER_DATA_DIR` pointing to an
  isolated directory.
- [ ] Manual exports use `EXPENSE_TRACKER_EXPORT_DIR` pointing to an isolated
  directory.
- [ ] The initial currency is a three-letter code; the default is `USD`.
- [ ] Existing `data/*.json` and `.bak` files have been copied elsewhere before
  any manual recovery attempt.
- [ ] Runtime JSON, backups, CSV exports, environment files, caches, and
  coverage artifacts are not staged by Git.

## Required checks

```powershell
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m compileall -q src tests
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=85 -q
```

- [ ] All commands exit successfully.
- [ ] `git status --short` contains only intentional source or documentation
  changes.
- [ ] Tests did not change tracked files.

## Pull request

- [ ] The branch has one milestone purpose and is based on current `main`.
- [ ] The diff contains no personal financial data, secrets, temporary output,
  generated exports, or unrelated edits.
- [ ] Documentation matches the behavior changed by the branch.
- [ ] Static quality and all supported-Python test jobs pass.
- [ ] Review comments are resolved and the merge state is clean.

## Phase 1 release gate

Milestone completion is tracked in
[docs/PHASE_1_UPGRADE_ROADMAP.md](docs/PHASE_1_UPGRADE_ROADMAP.md). Do not label
Phase 1 stable until every item in
[docs/COMPLETION_CHECKLIST.md](docs/COMPLETION_CHECKLIST.md) is verified and
Milestone 7 is complete.
