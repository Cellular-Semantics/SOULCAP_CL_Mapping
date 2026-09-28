import json

import pytest

from soulcap_cl_mapping import literature_evidence as le

NARRATIVE = """# NK Cell Marker Literature Support

> **Extraction note.** Not a quote.

## Markers with evidence

### CD56 (positive marker)

> "NK cells are CD56+ and
> CD3−" [Table 1]
— Smith et al. 2020 (PMID: 111; DOI: 10.1/abc)

### CD19 and CD20 (exclusion markers)

> "cells were CD19− before sorting"

> "no marker named here"

— Jones J et al. 2021 (DOI:10.2/xyz; PMC: PMC999)

**Discrepancy flag — Lee 2022:** differs.

> "CD20 is sometimes low"
— Lee 2022 (no identifier)

### Distinction: NK vs ILC

> "ILCs lack CD16"
— Kim 2019 (PMID: 222)

### CD16 (dangling)

> "CD16 without attribution"

## Markers with no direct evidence found

> "CD57 mentioned here"
— Park 2018 (PMID: 333)
"""


@pytest.fixture
def narrative(tmp_path):
    path = tmp_path / "nk_cell_markers.md"
    path.write_text(NARRATIVE, encoding="utf-8")
    return path


def test_heading_markers_and_bare_names():
    assert le.heading_markers("### CD11c / ITGAX (required high)") == [
        ["CD11c", "ITGAX"]
    ]
    assert le.heading_markers("### CD19 and CD20 (exclusion)") == [["CD19"], ["CD20"]]
    assert le.heading_markers("### Lineage exclusion markers (CD14, CD33)") == [
        ["CD14"],
        ["CD33"],
    ]
    assert le.heading_markers("### Distinction: NK vs ILC") == []
    assert le.bare("CD56bright") == "CD56"
    assert le.bare("CD127lo/-") == "CD127"
    assert le.bare("CD1d-α-GalCer Tetramer") == "CD1d-α-GalCer Tetramer"


def test_parse_citation_and_blockquote_note():
    cite = le.parse_citation(
        "— Smith et al. 2020 (PMID: 111; DOI: 10.1/abc; PMC: PMC5)"
    )
    assert (cite["pmid"], cite["doi"], cite["pmcid"]) == ("111", "10.1/abc", "PMC5")
    assert cite["first_author_year"] == "Smith et al. 2020"
    assert le.split_blockquote('"quoted text" \\[Table 2\\]') == (
        '"quoted text"',
        "Table 2",
    )


def test_parse_file_places_and_logs(narrative):
    rows, unplaced = le.migrate([narrative])
    by_marker = {(r["marker_token"], r["quote"]) for r in rows}
    assert ("CD56", '"NK cells are CD56+ and CD3−"') in by_marker
    assert ("CD19", '"cells were CD19− before sorting"') in by_marker
    first = rows[0]
    assert first["evidence_id"] == "EV00001"
    assert first["notes"] == "Table 1"
    assert first["verified"] == "not_checked"
    assert first["cell_type_label"] == "NK cell"
    assert first["subject_id"] == ""
    reasons = {u["reason"] for u in unplaced}
    assert (
        "section names several markers and the quote mentions none of them" in reasons
    )
    assert "citation has no PMID, DOI or PMCID" in reasons
    assert "section heading names no marker" in reasons
    assert "no attribution line before the next heading" in reasons
    assert "quote outside a 'Markers with evidence' part" in reasons
    # The extraction note is a blockquote without an attribution.
    assert any("Extraction note" in u["quote"] for u in unplaced)


def test_discrepancy_marks_qualifies_and_webfetch_default(tmp_path):
    text = NARRATIVE.replace("— Lee 2022 (no identifier)", "— Lee 2022 (PMID: 444)")
    path = tmp_path / "t_cell_markers.md"
    path.write_text(text, encoding="utf-8")
    rows, _ = le.migrate([path])
    lee = [r for r in rows if r["pmid"] == "444"]
    assert lee and lee[0]["supports_or_contradicts"] == "qualifies"
    assert lee[0]["cell_type_label"] == "T cell"
    assert all(r["verified"] == "no" for r in rows)


def test_check_quote_exact_near_and_mismatch():
    text = "Cells were CD38+++ and **CD24**hi. NK cells – rare."
    assert (
        le.check_quote('"Cells were CD38+++ and CD24hi"', text.replace("**", ""))[0]
        == "yes"
    )
    assert le.check_quote('"Cells were CD38+++" ... "rare"', text)[0] == "yes"
    assert le.check_quote('"cells were CD38+++"', text)[0] == "no"  # case matters
    verdict, note = le.check_quote('"NK cells - rare"', text)
    assert verdict == "no" and note.startswith("near-match")
    verdict, note = le.check_quote('"Cells were CD19+"', text)
    assert verdict == "no" and "first 13 of 16 chars match" in note
    assert le.fragments('"**ASC**: CD19+" and "*M*: CD27+"') == [
        "ASC: CD19+",
        "M: CD27+",
    ]
    assert le.fragments('"(*) LIN2 is"') == ["(*) LIN2 is"]


def fake_epmc(pages):
    def get(url):
        for key, body in pages.items():
            if key in url:
                if isinstance(body, Exception):
                    raise body
                return body
        raise OSError(url)

    return get


def test_verify_resolves_pmcid_and_fetches_once():
    xml = b"<article><body><p>NK cells are CD56<sup>+</sup> cells.</p></body></article>"
    search = json.dumps({"resultList": {"result": [{"pmcid": "PMC1"}]}}).encode()
    calls = []
    pages = {"search": search, "PMC1/fullTextXML": xml}

    def get(url):
        calls.append(url)
        return fake_epmc(pages)(url)

    rows = [
        dict(
            quote='"NK cells are CD56+ cells"',
            pmid="1",
            doi="",
            pmcid="",
            verified="no",
            verification_note="",
        ),
        dict(
            quote='"NK cells are CD57+"',
            pmid="",
            doi="10.1/a",
            pmcid="",
            verified="not_checked",
            verification_note="",
        ),
        dict(
            quote='"done"',
            pmid="",
            doi="",
            pmcid="PMC1",
            verified="yes",
            verification_note="kept",
        ),
    ]
    le.verify(rows, get)
    assert rows[0]["verified"] == "yes" and rows[0]["pmcid"] == "PMC1"
    assert rows[1]["verified"] == "no"
    assert rows[2]["verification_note"] == "kept"
    assert sum("fullTextXML" in c for c in calls) == 1


def test_verify_handles_missing_full_text_and_errors():
    none = json.dumps({"resultList": {"result": []}}).encode()
    rows = [
        dict(
            quote='"x"', pmid="5", doi="", pmcid="", verified="no", verification_note=""
        )
    ]
    le.verify(rows, fake_epmc({"search": none}))
    assert rows[0]["verification_note"].startswith("no open-access")
    rows = [
        dict(
            quote='"x"',
            pmid="",
            doi="",
            pmcid="PMC2",
            verified="no",
            verification_note="",
        )
    ]
    le.verify(rows, fake_epmc({"PMC2": b"not xml"}))
    assert "full text not available" in rows[0]["verification_note"]
    rows = [
        dict(
            quote='"x"', pmid="5", doi="", pmcid="", verified="no", verification_note=""
        )
    ]
    le.verify(rows, fake_epmc({"search": OSError("down")}))
    assert rows[0]["verification_note"].startswith("Europe PMC lookup failed")


def test_views_and_cli(tmp_path, narrative, monkeypatch, capsys):
    lit = narrative.parent
    assert le.main(["migrate", "--literature", str(lit)]) == 0
    assert le.main(["migrate", "--literature", str(lit)]) == 1  # refuses to overwrite
    assert le.main(["migrate", "--literature", str(lit), "--force"]) == 0
    assert (lit / "evidence_unplaced.tsv").exists()
    assert le.main(["views", "--literature", str(lit)]) == 0
    view = (lit / "by_marker" / "cd56.md").read_text(encoding="utf-8")
    assert "Do not edit by hand" in view and "EV00001" in view
    assert (lit / "by_cell_type" / "nk-cell.md").exists()
    monkeypatch.setattr(le, "http_get", lambda url: (_ for _ in ()).throw(OSError()))
    monkeypatch.setattr(le, "verify", lambda rows: None)
    assert le.main(["verify", "--literature", str(lit)]) == 0
    empty = tmp_path / "empty"
    empty.mkdir()
    assert le.main(["views", "--literature", str(empty)]) == 1
    assert le.slug("TCR Vδ2") == "tcr-v-2"


def test_committed_evidence_quotes_are_copied_exactly_from_their_source():
    """Every quote in literature/evidence.tsv appears verbatim in its source file."""
    root = le.ROOT
    rows = le.read_tsv(root / "literature" / "evidence.tsv")
    assert rows
    cache: dict[str, list[str]] = {}
    for row in rows:
        path = root / row["source_file"]
        if not path.exists():  # narrative archived; nothing to compare against
            continue
        if row["source_file"] not in cache:
            cache[row["source_file"]] = path.read_text(encoding="utf-8").splitlines()
        lines = cache[row["source_file"]]
        start = int(row["source_line"]) - 1
        block = []
        for line in lines[start:]:
            if not line.startswith(">"):
                break
            block.append(line[1:].strip())
        assert row["quote"] in " ".join(block), row["evidence_id"]
        assert row["verified"] in {"yes", "no", "not_checked"}
        if row["source_file"].endswith(tuple(le.WEBFETCH_FILES)):
            assert row["verified"] in {"yes", "no"}, row["evidence_id"]
