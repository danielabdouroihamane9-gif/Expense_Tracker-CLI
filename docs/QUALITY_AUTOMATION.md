# Quality Automation and Pull Request Gates

Phase 1 Milestone 5 defines one repeatable quality workflow for local changes
and GitHub pull requests.

## Supported Python versions

The project supports and tests Python 3.11, 3.12, 3.13, and 3.14. Python 3.11
is the minimum version and is also Ruff's configured compatibility target.

## Install development tools

From the repository root with the virtual environment active:

```powershell
python -m pip install -r requirements-dev.txt
python -m pip check
```

`requirements-dev.txt` installs the application dependencies, pytest,
coverage support, and the pinned Ruff version used by CI.

## Required local checks

Run these commands before every pull request:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m compileall -q src tests
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=85 -q
```

If Ruff reports safe lint or import-order findings, apply and verify them with:

```powershell
python -m ruff check . --fix
python -m ruff format .
python -m ruff check .
python -m ruff format --check .
```

Formatting is intentionally checked rather than applied in CI. Developers
apply formatting locally so every automated change remains visible in the
branch diff.

## GitHub Actions

`.github/workflows/tests.yml` runs once for each pull request and once after a
merge to `main`. Concurrency cancellation stops superseded runs for the same
branch.

The workflow has two gates:

1. **Static quality** on Python 3.14:
   - dependency compatibility;
   - Ruff lint rules and import order;
   - Ruff formatting;
   - source and test syntax compilation.
2. **Test matrix** on Python 3.11, 3.12, 3.13, and 3.14:
   - the complete pytest suite;
   - branch coverage with a mandatory 85% minimum;
   - verification that tests did not change tracked files.

All jobs must pass before a pull request is merged.

## Production-data protection

Tests use pytest temporary directories and explicit runtime configuration. An
autouse session fixture snapshots every file and modification timestamp inside
the repository `data` directory before the suite and compares it after the
suite. The suite fails if a test creates, rewrites, or deletes production data.

The CI checkout normally has no ignored runtime data. The same guard still
detects accidental creation of files in the repository `data` directory.

## Reliability and CLI smoke coverage

The automated suite includes:

- persistence-unit tests for atomic writes, interrupted writes, permission
  failures, backup validation, and recovery;
- a composed application integration test that corrupts a primary expense
  document and verifies recovery through the repository and service layers;
- subprocess CLI smoke tests for startup, redirected Windows output, clean
  exit, expense creation, versioned persistence, and reload behavior.

All smoke and recovery tests use isolated temporary paths.

## Pull request merge checklist

Before marking a pull request ready:

1. Review the complete diff and confirm it contains no production data,
   secrets, generated exports, coverage artifacts, or unrelated changes.
2. Run all required local checks.
3. Push the branch and wait for every GitHub Actions job.
4. Confirm the PR reports a clean merge state.
5. Merge only after the static-quality job and all four Python test jobs pass.
6. Synchronize local `main` with a fast-forward pull after merging.
