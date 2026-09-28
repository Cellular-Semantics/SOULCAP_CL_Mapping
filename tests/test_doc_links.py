"""Every relative link in the hand-written Markdown docs must resolve."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Hand-written docs. Generated reports are excluded: they are rewritten by
# their CLI, and archived copies are frozen snapshots.
DOC_GLOBS = [
    "*.md",
    "**/README.md",
    "docs/**/*.md",
    "cell_type_reviews/*.md",
    "literature/*.md",
    "reports/candidate_cl_mappings_narrative.md",
    "reports/cl_term_issues.md",
    "reports/marker_string_issues.md",
]
SKIP_DIRS = {".venv", ".uv-cache", ".test-runs", ".pytest_cache", "node_modules"}
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^(```|~~~).*?^\1", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")


def doc_files() -> list[Path]:
    found = set()
    for pattern in DOC_GLOBS:
        for path in ROOT.glob(pattern):
            rel = path.relative_to(ROOT)
            if not SKIP_DIRS.intersection(rel.parts):
                found.add(path)
    return sorted(found)


def relative_links(text: str) -> list[str]:
    text = INLINE_CODE.sub("", FENCE.sub("", text))
    links = []
    for target in LINK.findall(text):
        target = target.strip("<>")
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue  # http:, https:, mailto:, ...
        path = target.split("#", 1)[0]
        if path:
            links.append(path)
    return links


def test_finds_docs() -> None:
    names = {p.relative_to(ROOT).as_posix() for p in doc_files()}
    assert {"README.md", "CLAUDE.md", "reports/README.md"} <= names


def test_relative_links_extraction() -> None:
    text = (
        "[a](x.md) [b](https://e.org) [c](#anchor) [d](y.md#s) `[e](no.md)`\n"
        "```\n[f](fenced.md)\n```\n"
    )
    assert relative_links(text) == ["x.md", "y.md"]


@pytest.mark.parametrize(
    "doc", doc_files(), ids=lambda p: p.relative_to(ROOT).as_posix()
)
def test_relative_links_resolve(doc: Path) -> None:
    missing = []
    for link in relative_links(doc.read_text(encoding="utf-8")):
        target = (doc.parent / link).resolve()
        # data/ is a gitignored cache that CI never has.
        if target.is_relative_to(ROOT / "data"):
            continue
        if not target.exists():
            missing.append(link)
    assert not missing, f"Broken links in {doc.relative_to(ROOT)}: {missing}"
