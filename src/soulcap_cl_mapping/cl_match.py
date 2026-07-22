"""Score and rank CL terms against a SOULCAP marker profile.

Loads ``reports/cl_pro_relationships.tsv`` and scores every CL term by how
well its known marker axioms match your positive/negative marker profile.
Pass the four marker-column strings exactly as they appear in the sheet.

Usage::

    soulcap-match \\
        --req-excl "(CD14-|CD33-|CD64-) CD34- CD3- CD19-" \\
        --req-pheno "live/ CD45+ CD56+/hi CD127lo/-"

    soulcap-match \\
        --req-excl "(CD14-|CD33-|CD64-) CD34- CD3- CD19-" \\
        --ideal-excl "[HLA-DR+ CD11chi]- (CD15-|CD66b-) CD123-" \\
        --req-pheno "live/ CD45+ CD56+/hi CD127lo/-" \\
        --ideal-pheno "[CD33-|CD64-]" \\
        --parent "NK cell" --subset "CD56bright" --top 8

Batch mode scores every row of ``data/marker_combinations.csv`` (the synced
SOULCAP sheet) in one pass and writes the top-N candidates per row to a TSV::

    soulcap-match --batch --batch-out reports/candidate_cl_mappings_batch.tsv
    soulcap-match --batch --top 3 --ready-only

Marker-axiom scoring can only ever suggest CL terms that already have a PR
marker axiom recorded in ``cl_pro_relationships.tsv`` — many CL terms
(including some "obvious" parent classes) have none and are structurally
invisible to it. ``--lexical`` adds a name-based OLS4 CL search per row as a
second, independent candidate source, and writes an agreement report showing
where the two approaches concur (higher confidence) or diverge (needs review)::

    soulcap-match --batch --lexical
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from pathlib import Path

from soulcap_cl_mapping import ols4_lookup
from soulcap_cl_mapping.marker_syntax import GATE, _is_qualifier, _split_word, _tokenize

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TSV = REPO_ROOT / "reports" / "cl_pro_relationships.tsv"
DEFAULT_MARKER_COMBINATIONS = REPO_ROOT / "data" / "marker_combinations.csv"
DEFAULT_BATCH_OUT = REPO_ROOT / "reports" / "candidate_cl_mappings_batch.tsv"
DEFAULT_AGREEMENT_OUT = REPO_ROOT / "reports" / "candidate_cl_mappings_agreement.tsv"
DEFAULT_TOP = 8
DEFAULT_BATCH_TOP = 3

BATCH_TSV_FIELDS = [
    "abbreviation",
    "full_name",
    "parent",
    "type_of_match",
    "existing_cl_id",
    "rank",
    "cl_id",
    "cl_label",
    "score",
    "hint_bonus",
    "matched",
    "contradictions",
    "gaps",
    "disqualified",
    "note",
]

# Weight applied to required vs ideal marker columns.
_REQUIRED_WEIGHT = 2
_IDEAL_WEIGHT = 1
# Score bonus per hint word found in a CL term label.
_HINT_BONUS = 1


# --------------------------------------------------------------------------- #
# TSV loading
# --------------------------------------------------------------------------- #
def load_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _parse_cd_synonyms(synonym_str: str) -> set[str]:
    """Extract uppercase CD tokens from ``'CD56 (exact); CD11B (related)'``."""
    tokens: set[str] = set()
    for part in synonym_str.split(";"):
        name = part.strip().split("(")[0].strip()
        if name:
            tokens.add(name.upper())
    return tokens


def build_cl_index(rows: list[dict]) -> dict[str, dict]:
    """Return ``{cl_id: {label, positive, negative, high, low}}`` from TSV rows.

    ``high``/``low`` track "has high/low plasma membrane amount" axioms
    separately from plain ``positive``/``negative`` — both still mean the
    marker is *expressed* (just at a given level), so they are never treated
    as equivalent to ``negative`` (marker absent) during scoring.
    """
    index: dict[str, dict] = {}
    for row in rows:
        cl_id = row["cell"]
        if cl_id not in index:
            index[cl_id] = {
                "label": row["cell_label"],
                "positive": set(),
                "negative": set(),
                "high": set(),
                "low": set(),
            }
        sense = row.get("sense", "")
        cd_tokens = _parse_cd_synonyms(row.get("cd_synonym", ""))
        if sense in ("positive", "negative", "high", "low"):
            index[cl_id][sense].update(cd_tokens)
    return index


# --------------------------------------------------------------------------- #
# Name-hint helpers
# --------------------------------------------------------------------------- #
def _hint_words(*texts: str) -> set[str]:
    """Return lowercase words (≥3 chars) from one or more name hint strings."""
    words: set[str] = set()
    for text in texts:
        for word in re.split(r"[\s\-_]+", text):
            if len(word) >= 3:
                words.add(word.lower())
    return words


# --------------------------------------------------------------------------- #
# Marker expression → (token, sense) extraction
# --------------------------------------------------------------------------- #
def _qual_sense(qual: str) -> str:
    """Map a qualifier string to ``'positive'``, ``'negative'``, or ``'variable'``."""
    parts = qual.split("/")
    first = parts[0]
    if first in ("+", "hi"):
        return "positive"
    if first in ("-", "lo", "int"):
        return "negative"
    return "variable"


def extract_signed_markers(expr: str) -> list[tuple[str, str]]:
    """Return ``(MARKER_UPPER, sense)`` for every qualified token in *expr*.

    Sense is ``'positive'`` or ``'negative'``. Tokens with no qualifier and
    group-level-only qualifiers are skipped (ambiguous without full parse).
    The live/ gate prefix is ignored.
    """
    try:
        tokens = _tokenize(expr)
    except Exception:  # noqa: BLE001
        return []

    results: list[tuple[str, str]] = []
    # Track the qualifier of the most recently closed group so we can apply it
    # to unqualified members. Stack entries: qualifier string or None.
    pending_group_qual: list[str | None] = []
    i = 0
    n = len(tokens)

    while i < n:
        kind, text = tokens[i]
        if kind == "WS" or kind == "|":
            i += 1
        elif kind in ("(", "["):
            pending_group_qual.append(None)
            i += 1
        elif kind in (")", "]"):
            i += 1
            # Peek: is the next WORD a standalone qualifier?
            if i < n and tokens[i][0] == "WORD" and _is_qualifier(tokens[i][1]):
                pending_group_qual.append(tokens[i][1])
                i += 1
            else:
                pending_group_qual.append(None)
        elif kind == "WORD":
            if text == GATE:
                i += 1
                continue
            try:
                marker, qual = _split_word(text)
            except Exception:  # noqa: BLE001
                i += 1
                continue
            if qual:
                sense = _qual_sense(qual)
            elif pending_group_qual and pending_group_qual[-1]:
                sense = _qual_sense(pending_group_qual[-1])
            else:
                i += 1
                continue  # truly unqualified — skip
            if sense != "variable":
                results.append((marker.upper(), sense))
            i += 1
        else:
            i += 1

    return results


# A required/ideal marker "clause" for score_cl_terms: either a plain
# (MARKER, sense) tuple (a single required condition) or a list of such
# tuples — an OR-group satisfied by *any one* alternative, not all.
Clause = tuple[str, str] | list[tuple[str, str]]


def extract_marker_clauses(expr: str) -> list[Clause]:
    """Tokenize *expr* into AND-joined clauses, modelling ``|`` as true OR.

    :func:`extract_signed_markers` flattens a ``|``-joined OR-group like
    ``(CD193+|FceR1a+|HLA-DR-|CD303-)`` into four independently-**required**
    markers — i.e. it silently turns "at least one of these" into "all of
    these", which is wrong per MARKER_SYNTAX.md §1.4. That mistranslation
    made scoring reject candidates that only need to satisfy one
    alternative: ``CL:0000043`` (mature basophil) never scored as a match
    for SOULCAP's Basophil profile, because CL doesn't assert *all four*
    alternatives simultaneously — only some.

    This function fixes that for the common case: a bracket directly
    containing ``|``-joined atoms that **each already carry their own
    qualifier** (every real example in the current sheet looks like this)
    is returned as one clause — a list of alternatives — instead of being
    flattened. :func:`score_cl_terms` treats such a clause as satisfied if
    *any* alternative matches, and contradicted only if *every* alternative
    is actively contradicted.

    Scope: anything more complex — an unqualified member relying on a
    group-level qualifier, a nested group, or a trailing qualifier negating
    a compound AND-group (``[HLA-DR+ CD11chi]-``, MARKER_SYNTAX.md §1.6,
    which needs De Morgan expansion) — falls back to flattening every leaf
    as independently required, i.e. :func:`extract_signed_markers`'s
    existing (imperfect but non-regressed) behaviour.
    """
    try:
        tokens = _tokenize(expr)
    except Exception:  # noqa: BLE001
        return []

    # frames[d] holds items collected directly at nesting depth d (index 0
    # = top level). An item is ("leaf", marker, sense) or ("clause", alts).
    frames: list[list[tuple]] = [[]]
    saw_pipe: list[bool] = [False]

    i = 0
    n = len(tokens)
    while i < n:
        kind, text = tokens[i]
        if kind == "WS":
            i += 1
        elif kind == "|":
            saw_pipe[-1] = True
            i += 1
        elif kind in ("(", "["):
            frames.append([])
            saw_pipe.append(False)
            i += 1
        elif kind in (")", "]"):
            if len(frames) <= 1:
                # Unbalanced closing bracket with no matching open — nothing
                # to pop; skip it (and any trailing qualifier) and keep the
                # top-level frame intact, matching extract_signed_markers's
                # leniency toward malformed input.
                i += 1
                if i < n and tokens[i][0] == "WORD" and _is_qualifier(tokens[i][1]):
                    i += 1
                continue
            items = frames.pop()
            had_pipe = saw_pipe.pop()
            i += 1
            group_qual = None
            if i < n and tokens[i][0] == "WORD" and _is_qualifier(tokens[i][1]):
                group_qual = tokens[i][1]
                i += 1
            parent = frames[-1]
            all_leaves = bool(items) and all(kind_ == "leaf" for kind_, *_ in items)
            simple_group = group_qual is None or _qual_sense(group_qual) == "variable"
            if had_pipe and all_leaves and simple_group:
                parent.append(("clause", [(m, s) for _, m, s in items]))
            else:
                parent.extend(items)
        elif kind == "WORD":
            if text == GATE:
                i += 1
                continue
            try:
                marker, qual = _split_word(text)
            except Exception:  # noqa: BLE001
                i += 1
                continue
            if qual:
                sense = _qual_sense(qual)
                if sense != "variable":
                    frames[-1].append(("leaf", marker.upper(), sense))
            # else: truly unqualified — skip (matches extract_signed_markers)
            i += 1
        else:
            i += 1

    # Unbalanced open brackets: flatten remaining frames into the top level.
    while len(frames) > 1:
        items = frames.pop()
        frames[-1].extend(items)

    clauses: list[Clause] = []
    for kind_, *rest in frames[0]:
        if kind_ == "leaf":
            marker, sense = rest
            clauses.append((marker, sense))
        else:
            clauses.append(rest[0])
    return clauses


def _eval_alternative(
    marker: str,
    sense: str,
    expressed: set[str],
    absent: set[str],
    high: set[str],
    low: set[str],
) -> tuple[str, str]:
    """Evaluate one (marker, sense) alternative against a CL term's axioms.

    Returns ``(status, display)`` where status is ``"matched"``,
    ``"contradicted"``, or ``"gap"``.
    """
    in_expressed = marker in expressed
    in_absent = marker in absent
    symbol = "+" if sense == "positive" else "-"
    tag = " (hi)" if marker in high else " (dim)" if marker in low else ""
    display = f"{marker}{symbol}{tag}"
    if sense == "positive":
        if in_expressed:
            return "matched", display
        if in_absent:
            return "contradicted", display
        return "gap", display
    if in_absent:
        return "matched", display
    if in_expressed:
        return "contradicted", display
    return "gap", display


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
def score_cl_terms(
    cl_index: dict[str, dict],
    required: list[Clause],
    ideal: list[Clause],
    name_hints: set[str] | None = None,
) -> list[dict]:
    """Score every CL term and return a list of result dicts, best first.

    Each result dict has keys: ``cl_id``, ``label``, ``score``,
    ``matched``, ``gaps``, ``contradictions``, ``hint_bonus``,
    ``disqualified``.

    *required*/*ideal* are lists of :data:`Clause` — each a plain
    ``(marker, sense)`` tuple (a single required condition) or a ``list`` of
    such tuples (an OR-group from :func:`extract_marker_clauses`, satisfied
    by *any one* alternative). A single-alternative clause behaves exactly
    as a plain tuple always has.

    A contradiction on a *required* clause sets ``disqualified`` — that
    candidate is sorted below every non-disqualified one regardless of raw
    score, so shared negative-exclusion markers (common across many
    unrelated lineages) can no longer pile up enough points to outrank a
    candidate that outright conflicts with a required marker. For an
    OR-group clause, "contradiction" only fires when *every* alternative is
    actively contradicted — if even one alternative is unknown (a gap) or
    matched, the group as a whole isn't disqualifying. A contradiction on an
    *ideal* clause is never disqualifying — it still just subtracts
    ``_IDEAL_WEIGHT`` — since ideal markers are soft signals. Disqualified
    candidates are kept (not dropped) so a plausible-but-imperfect answer
    still surfaces when nothing clean exists.

    *name_hints* is a set of lowercase words derived from ``--parent`` /
    ``--subset``; each word found in the CL label adds ``_HINT_BONUS`` to
    the score, breaking ties toward biologically named matches.
    """
    hints = name_hints or set()
    results = []
    for cl_id, entry in cl_index.items():
        pos = entry["positive"]
        high = entry.get("high", set())
        low = entry.get("low", set())
        expressed = pos | high | low
        absent = entry["negative"]
        score = 0
        matched: list[str] = []
        gaps: list[str] = []
        contradictions: list[str] = []
        disqualified = False

        for markers, weight, is_required in (
            (required, _REQUIRED_WEIGHT, True),
            (ideal, _IDEAL_WEIGHT, False),
        ):
            for clause in markers:
                alternatives = [clause] if isinstance(clause, tuple) else clause
                statuses = [
                    _eval_alternative(m, s, expressed, absent, high, low)
                    for m, s in alternatives
                ]
                matched_display = next(
                    (d for st, d in statuses if st == "matched"), None
                )
                multi = len(alternatives) > 1
                if matched_display is not None:
                    score += weight * 2
                    matched.append(
                        f"{matched_display} (1 of {len(alternatives)} alt.)"
                        if multi
                        else matched_display
                    )
                elif all(st == "contradicted" for st, _ in statuses):
                    score -= weight
                    disqualified = disqualified or is_required
                    contradictions.append(
                        "/".join(d for _, d in statuses) + " (all alt. conflict)"
                        if multi
                        else statuses[0][1]
                    )
                else:
                    gaps.append(
                        "/".join(d for _, d in statuses) + " (no axiom on any alt.)"
                        if multi
                        else statuses[0][1]
                    )

        hint_bonus = 0
        if hints:
            label_lower = entry["label"].lower()
            for word in hints:
                if word in label_lower:
                    hint_bonus += _HINT_BONUS
            score += hint_bonus

        results.append(
            {
                "cl_id": cl_id,
                "label": entry["label"],
                "score": score,
                "matched": matched,
                "gaps": gaps,
                "contradictions": contradictions,
                "hint_bonus": hint_bonus,
                "disqualified": disqualified,
            }
        )

    results.sort(key=lambda r: (r["disqualified"], -r["score"]))
    return results


# --------------------------------------------------------------------------- #
# Batch mode — score every row of marker_combinations.csv in one pass
# --------------------------------------------------------------------------- #
def load_marker_combinations(path: Path) -> list[dict]:
    """Load the synced SOULCAP ``Marker Combinations`` tab (sheet columns)."""
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def score_marker_combinations_row(
    row: dict,
    cl_index: dict[str, dict],
    top_n: int = DEFAULT_BATCH_TOP,
) -> dict:
    """Score one ``marker_combinations.csv`` row against every CL term.

    Returns a dict with the row's identity columns plus ``candidates`` — the
    top *top_n* :func:`score_cl_terms` results — or an empty ``candidates``
    list and a ``note`` explaining why (e.g. no qualified markers found).
    """
    abbreviation = row.get("Abbreviation", "").strip()
    full_name = row.get("Full Name", "").strip()
    parent = row.get("Parent", "").strip()
    type_of_match = row.get("Type of Match", "").strip()
    existing_cl_id = row.get("OLS CL identifier", "").strip()

    identity = {
        "abbreviation": abbreviation,
        "full_name": full_name,
        "parent": parent,
        "type_of_match": type_of_match,
        "existing_cl_id": existing_cl_id,
    }

    required = extract_marker_clauses(
        row.get("Required exclusion", "")
    ) + extract_marker_clauses(row.get("Required phenotypic markers", ""))
    ideal = extract_marker_clauses(
        row.get("Ideal exclusion", "")
    ) + extract_marker_clauses(row.get("Ideal phenotypic markers", ""))

    if not required and not ideal:
        return {**identity, "candidates": [], "note": "no qualified markers found"}

    hints = _hint_words(full_name, parent, abbreviation)
    scored = score_cl_terms(cl_index, required, ideal, hints)
    return {**identity, "candidates": scored[:top_n], "note": ""}


def run_batch(
    rows: list[dict],
    cl_index: dict[str, dict],
    top_n: int = DEFAULT_BATCH_TOP,
    ready_only: bool = False,
) -> list[dict]:
    """Score every row (optionally filtered to ``Ready for OLS == yes``).

    Rows with no ``Abbreviation``/``Full Name`` at all are skipped (blank
    sheet rows); every other row is scored, even if no marker could be
    extracted, so gaps are visible in the output rather than silently
    dropped.
    """
    results = []
    for row in rows:
        if ready_only and row.get("Ready for OLS", "").strip().lower() != "yes":
            continue
        if (
            not row.get("Abbreviation", "").strip()
            and not row.get("Full Name", "").strip()
        ):
            continue
        results.append(score_marker_combinations_row(row, cl_index, top_n))
    return results


def batch_results_to_tsv_rows(results: list[dict]) -> list[dict]:
    """Flatten batch results into one output row per (cell type, candidate)."""
    tsv_rows: list[dict] = []
    for r in results:
        identity = {
            k: r[k]
            for k in (
                "abbreviation",
                "full_name",
                "parent",
                "type_of_match",
                "existing_cl_id",
            )
        }
        if not r["candidates"]:
            tsv_rows.append(
                {
                    **identity,
                    "rank": "",
                    "cl_id": "",
                    "cl_label": "",
                    "score": "",
                    "hint_bonus": "",
                    "matched": "",
                    "contradictions": "",
                    "gaps": "",
                    "disqualified": "",
                    "note": r["note"],
                }
            )
            continue
        for rank, cand in enumerate(r["candidates"], 1):
            tsv_rows.append(
                {
                    **identity,
                    "rank": rank,
                    "cl_id": cand["cl_id"],
                    "cl_label": cand["label"],
                    "score": cand["score"],
                    "hint_bonus": cand["hint_bonus"],
                    "matched": ", ".join(cand["matched"]),
                    "contradictions": ", ".join(cand["contradictions"]),
                    "gaps": ", ".join(cand["gaps"]),
                    "disqualified": "yes" if cand.get("disqualified") else "no",
                    "note": "",
                }
            )
    return tsv_rows


def write_batch_tsv(path: Path, results: list[dict]) -> None:
    """Write batch results to *path* as a TSV, one line per candidate."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=BATCH_TSV_FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(batch_results_to_tsv_rows(results))


# --------------------------------------------------------------------------- #
# Lexical batch mode — name-based CL search via OLS4, as a complement to
# marker-axiom scoring (which can only rank CL terms already present in
# cl_pro_relationships.tsv — many CL terms, including "obvious" parent
# classes, have no marker axiom at all and are invisible to it).
# --------------------------------------------------------------------------- #
def _lexical_query_for_row(row: dict) -> str:
    """Pick the best available search text for a row: Full Name, else Abbreviation."""
    full_name = row.get("Full Name", "").strip()
    return full_name or row.get("Abbreviation", "").strip()


# OLS4's free-text relevance ranking does not reliably put an exact label
# match first — searching the literal label "Natural Killer Cell" ranks its
# own exact match (CL:0000623) 23rd, behind dozens of qualified subtype
# variants that merely share more words. Fetch a wider pool so an exact hit
# is likely present, then promote it.
_LEXICAL_FETCH_ROWS = 25


def run_lexical_batch(
    rows: list[dict],
    top_n: int = DEFAULT_BATCH_TOP,
    ready_only: bool = False,
    sleep_between: float = 0.2,
) -> list[dict]:
    """Search CL by name (OLS4) for every ``marker_combinations.csv`` row.

    Pure lexical similarity — no marker-conflict checking at all — so it
    trades the false-positive risk of :func:`run_batch` for a different
    failure mode (name collisions / no ranking by biological plausibility).
    Meant to be read alongside marker-based results, not instead of them.

    An exact (case-insensitive) label match is promoted to rank 1 when
    present in the fetched pool, since OLS4's own relevance order does not
    do this (see :data:`_LEXICAL_FETCH_ROWS`).
    """
    results = []
    for row in rows:
        if ready_only and row.get("Ready for OLS", "").strip().lower() != "yes":
            continue
        abbreviation = row.get("Abbreviation", "").strip()
        full_name = row.get("Full Name", "").strip()
        if not abbreviation and not full_name:
            continue

        identity = {
            "abbreviation": abbreviation,
            "full_name": full_name,
            "parent": row.get("Parent", "").strip(),
            "type_of_match": row.get("Type of Match", "").strip(),
            "existing_cl_id": row.get("OLS CL identifier", "").strip(),
        }

        query = _lexical_query_for_row(row)
        if not query:
            results.append({**identity, "candidates": [], "note": "no name to search"})
            continue

        if sleep_between > 0:
            time.sleep(sleep_between)
        try:
            hits = ols4_lookup.search(
                query, ontology="cl", rows=max(top_n, _LEXICAL_FETCH_ROWS)
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                {**identity, "candidates": [], "note": f"OLS4 search failed: {exc}"}
            )
            continue

        candidates = [
            {"cl_id": h["obo_id"], "label": h["label"]}
            for h in hits
            if h.get("obo_id", "").startswith("CL:")
        ]
        query_lower = query.strip().lower()
        candidates.sort(key=lambda c: c["label"].strip().lower() != query_lower)
        candidates = candidates[:top_n]
        note = "" if candidates else "no CL hits"
        results.append({**identity, "candidates": candidates, "note": note})
    return results


def merge_marker_and_lexical(
    marker_results: list[dict],
    lexical_results: list[dict],
) -> list[dict]:
    """Combine marker-based and lexical-based top-1 picks into an agreement report.

    ``agreement == "yes"`` (both approaches converge on the same CL ID) is a
    much stronger signal than either approach alone — it means the pick
    survives both a marker-axiom check and an independent name-similarity
    check.
    """
    lexical_by_key = {r["abbreviation"]: r for r in lexical_results}
    merged = []
    for m in marker_results:
        lex = lexical_by_key.get(m["abbreviation"], {"candidates": [], "note": ""})
        marker_top = m["candidates"][0] if m["candidates"] else None
        lexical_top = lex["candidates"][0] if lex["candidates"] else None
        agreement = bool(
            marker_top and lexical_top and marker_top["cl_id"] == lexical_top["cl_id"]
        )
        merged.append(
            {
                "abbreviation": m["abbreviation"],
                "full_name": m["full_name"],
                "parent": m["parent"],
                "type_of_match": m["type_of_match"],
                "existing_cl_id": m["existing_cl_id"],
                "marker_cl_id": marker_top["cl_id"] if marker_top else "",
                "marker_cl_label": marker_top["label"] if marker_top else "",
                "marker_score": marker_top["score"] if marker_top else "",
                "marker_conflict": (
                    ", ".join(marker_top["contradictions"]) if marker_top else ""
                ),
                "marker_note": m["note"],
                "lexical_cl_id": lexical_top["cl_id"] if lexical_top else "",
                "lexical_cl_label": lexical_top["label"] if lexical_top else "",
                "lexical_note": lex["note"],
                "agreement": "yes" if agreement else "no",
            }
        )
    return merged


AGREEMENT_TSV_FIELDS = [
    "abbreviation",
    "full_name",
    "parent",
    "type_of_match",
    "existing_cl_id",
    "marker_cl_id",
    "marker_cl_label",
    "marker_score",
    "marker_conflict",
    "marker_note",
    "lexical_cl_id",
    "lexical_cl_label",
    "lexical_note",
    "agreement",
]


def write_agreement_tsv(path: Path, merged_rows: list[dict]) -> None:
    """Write the marker/lexical agreement report to *path* as a TSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=AGREEMENT_TSV_FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(merged_rows)


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def _format_clause(clause: Clause) -> str:
    """Render a Clause for CLI display: ``MARKER+``/``-``, or ``(A+|B-)`` for
    an OR-group."""
    if isinstance(clause, tuple):
        marker, sense = clause
        return f"{marker}{'+' if sense == 'positive' else '-'}"
    return "(" + "|".join(_format_clause(alt) for alt in clause) + ")"


def format_result(rank: int, r: dict) -> str:
    hint_tag = f" +{r['hint_bonus']} name" if r.get("hint_bonus") else ""
    dq_tag = (
        " [DISQUALIFIED: required-marker conflict]" if r.get("disqualified") else ""
    )
    lines = [
        f"  {rank}. {r['cl_id']}  {r['label']}  [score: {r['score']}{hint_tag}]{dq_tag}"
    ]
    if r["matched"]:
        lines.append(f"     Matched:  {', '.join(r['matched'])}")
    if r["contradictions"]:
        lines.append(f"     Conflict: {', '.join(r['contradictions'])}")
    if r["gaps"]:
        lines.append(f"     No axiom: {', '.join(r['gaps'])}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulcap-match",
        description="Rank CL terms against a SOULCAP marker profile.",
    )
    parser.add_argument(
        "--req-excl",
        default="",
        metavar="EXPR",
        help="Required exclusion markers (sheet column).",
    )
    parser.add_argument(
        "--ideal-excl",
        default="",
        metavar="EXPR",
        help="Ideal exclusion markers (sheet column).",
    )
    parser.add_argument(
        "--req-pheno",
        default="",
        metavar="EXPR",
        help="Required phenotypic markers (sheet column).",
    )
    parser.add_argument(
        "--ideal-pheno",
        default="",
        metavar="EXPR",
        help="Ideal phenotypic markers (sheet column).",
    )
    parser.add_argument(
        "--parent",
        default="",
        metavar="NAME",
        help="Parent cell type name from the sheet (e.g. 'NK cell').",
    )
    parser.add_argument(
        "--subset",
        default="",
        metavar="ABBREV",
        help="Subset abbreviation from the sheet (e.g. 'CD56bright').",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help=f"Number of top results per cell type "
        f"(default: {DEFAULT_TOP}, or {DEFAULT_BATCH_TOP} in --batch mode).",
    )
    parser.add_argument(
        "--tsv",
        type=Path,
        default=DEFAULT_TSV,
        help="Path to cl_pro_relationships.tsv.",
    )
    parser.add_argument(
        "--batch",
        nargs="?",
        const=str(DEFAULT_MARKER_COMBINATIONS),
        default=None,
        metavar="PATH",
        help="Score every row of marker_combinations.csv instead of a single "
        f"profile (default path: {DEFAULT_MARKER_COMBINATIONS}).",
    )
    parser.add_argument(
        "--batch-out",
        type=Path,
        default=DEFAULT_BATCH_OUT,
        metavar="PATH",
        help=f"Batch-mode output TSV path (default: {DEFAULT_BATCH_OUT}).",
    )
    parser.add_argument(
        "--ready-only",
        action="store_true",
        help="Batch mode: only score rows with 'Ready for OLS' == yes.",
    )
    parser.add_argument(
        "--lexical",
        action="store_true",
        help="Batch mode: also run a name-based OLS4 CL search per row and "
        "write a marker/lexical agreement report (see --agreement-out).",
    )
    parser.add_argument(
        "--agreement-out",
        type=Path,
        default=DEFAULT_AGREEMENT_OUT,
        metavar="PATH",
        help=f"--lexical output TSV path (default: {DEFAULT_AGREEMENT_OUT}).",
    )
    args = parser.parse_args(argv)

    if args.batch is None and not any(
        [args.req_excl, args.ideal_excl, args.req_pheno, args.ideal_pheno]
    ):
        parser.print_help()
        return 2

    if not args.tsv.exists():
        print(
            f"error: {args.tsv} not found — run `soulcap-cl-pro` to regenerate it.",
            file=sys.stderr,
        )
        return 1

    if args.batch is not None:
        combos_path = Path(args.batch)
        if not combos_path.exists():
            print(
                f"error: {combos_path} not found — run `soulcap-sync` to regenerate it.",
                file=sys.stderr,
            )
            return 1
        top_n = args.top if args.top is not None else DEFAULT_BATCH_TOP
        try:
            rows = load_tsv(args.tsv)
            cl_index = build_cl_index(rows)
            combo_rows = load_marker_combinations(combos_path)
            results = run_batch(
                combo_rows, cl_index, top_n=top_n, ready_only=args.ready_only
            )
            write_batch_tsv(args.batch_out, results)
            unscored = sum(1 for r in results if not r["candidates"])
            print(
                f"Scored {len(results)} SOULCAP cell types against "
                f"{len(cl_index)} CL terms ({unscored} had no qualified markers)."
            )
            print(f"Wrote {args.batch_out}")

            if args.lexical:
                print("Running lexical OLS4 search per cell type (rate-limited)...")
                lexical_results = run_lexical_batch(
                    combo_rows, top_n=top_n, ready_only=args.ready_only
                )
                merged = merge_marker_and_lexical(results, lexical_results)
                write_agreement_tsv(args.agreement_out, merged)
                agree = sum(1 for m in merged if m["agreement"] == "yes")
                print(
                    f"Marker/lexical agreement: {agree}/{len(merged)} cell types "
                    "converge on the same CL term."
                )
                print(f"Wrote {args.agreement_out}")
        except Exception as exc:  # noqa: BLE001
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    top_n = args.top if args.top is not None else DEFAULT_TOP

    try:
        rows = load_tsv(args.tsv)
        cl_index = build_cl_index(rows)

        required = extract_marker_clauses(args.req_excl) + extract_marker_clauses(
            args.req_pheno
        )
        ideal = extract_marker_clauses(args.ideal_excl) + extract_marker_clauses(
            args.ideal_pheno
        )

        if not required and not ideal:
            print("error: no qualified markers found in expressions.", file=sys.stderr)
            return 1

        hints = _hint_words(args.parent, args.subset)

        header_parts = []
        if args.parent:
            header_parts.append(f"parent={args.parent!r}")
        if args.subset:
            header_parts.append(f"subset={args.subset!r}")
        header_tag = f" [{', '.join(header_parts)}]" if header_parts else ""

        req_str = ", ".join(_format_clause(c) for c in required)
        ideal_str = ", ".join(_format_clause(c) for c in ideal)
        print(f"Scoring {len(cl_index)} CL terms{header_tag}:")
        if req_str:
            print(f"  Required : {req_str}")
        if ideal_str:
            print(f"  Ideal    : {ideal_str}")
        if hints:
            print(f"  Name hints: {', '.join(sorted(hints))}")
        print()

        scored = score_cl_terms(cl_index, required, ideal, hints)
        for i, result in enumerate(scored[:top_n], 1):
            print(format_result(i, result))
            print()

    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
