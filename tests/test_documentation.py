"""Integrity checks for active project documentation."""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def active_markdown_files():
    """Return maintained Markdown files, excluding archived material."""
    return sorted(ROOT.glob("*.md")) + sorted((ROOT / "docs").glob("*.md"))


def test_relative_documentation_links_resolve():
    """Every local link in active documentation points to an existing path."""
    missing = []

    for document in active_markdown_files():
        for raw_target in MARKDOWN_LINK.findall(document.read_text(encoding="utf-8")):
            target = raw_target.strip().strip("<>")
            if (
                not target
                or target.startswith("#")
                or "://" in target
                or target.startswith("mailto:")
            ):
                continue

            relative_path = unquote(target.split("#", 1)[0])
            resolved = (document.parent / relative_path).resolve()
            if not resolved.exists():
                missing.append(f"{document.relative_to(ROOT)} -> {target}")

    assert not missing, "Broken local documentation links:\n" + "\n".join(missing)


def test_active_documentation_has_no_known_obsolete_claims():
    """Prevent reintroducing claims removed during Milestone 6."""
    obsolete_claims = (
        "35+ automated tests",
        "tests/test_expense_tracker.py",
        "Milestone 4 will move it",
        "Python 3.10+",
    )
    findings = []

    for document in active_markdown_files():
        content = document.read_text(encoding="utf-8")
        for claim in obsolete_claims:
            if claim in content:
                findings.append(f"{document.relative_to(ROOT)}: {claim}")

    assert not findings, "Obsolete documentation claims:\n" + "\n".join(findings)
