"""Full marker review: deterministic checks + an optional agentic pass.

This complements the grammar-only validator in :mod:`marker_syntax`. It runs in
two layers (see Roadmap M1):

* **Deterministic** (tested code, no LLM): builds a marker inventory and flags
  high-confidence issues — casing collisions, orphan fragments (the tell-tale of
  a marker name containing spaces), and unparseable tokens.
* **Agentic** (headless ``claude -p``): judgement calls the deterministic layer
  can't make — reconstructing space-split reagent names, unifying inconsistent
  nomenclature to a canonical form, and spotting alias pairs.

The deterministic layer always runs first and feeds the agentic layer. The two
can be run **together** (``mode="both"``) or **separately**
(``mode="deterministic"`` / ``mode="agentic"``); a deterministic run can persist
its inventory to JSON so a later agentic run reuses it without recomputing.

CLI: ``soulcap-review [csv] [--mode both|deterministic|agentic] ...``
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pandas as pd

from soulcap_cl_mapping.marker_syntax import (
    GATE,
    MARKER_COLUMNS,
    MarkerSyntaxError,
    _split_word,
    _tokenize,
)

MODES = ("both", "deterministic", "agentic")

# Tokens that strongly suggest a space-split marker name when they appear as a
# standalone "marker" (e.g. "TCR V delta 1" -> TCR, V, delta, 1...).
_FRAGMENT_WORDS = {"delta", "gamma", "alpha", "beta", "tetramer"}


class AgentUnavailable(RuntimeError):
    """The headless agent could not be run or produced no usable output."""


# --------------------------------------------------------------------------- #
# Deterministic layer
# --------------------------------------------------------------------------- #
def extract_inventory(csv: str | Path) -> dict:
    """Build the marker inventory from a ``Marker Combinations`` CSV.

    Returns ``{"markers": {name: {count, columns, rows}}, "unparseable":
    {word: rows}, "cells": [distinct cell strings]}``.
    """
    df = pd.read_csv(csv)
    cols = [c for c in MARKER_COLUMNS if c in df.columns]
    markers: dict[str, dict] = {}
    unparseable: dict[str, set] = {}
    cells: list[str] = []
    seen_cells: set[str] = set()

    for idx, row in df.iterrows():
        sheet_row = idx + 2  # +1 header, +1 for 1-based
        for col in cols:
            value = row[col]
            if pd.isna(value):
                continue
            text = str(value).strip()
            if text and text not in seen_cells:
                seen_cells.add(text)
                cells.append(text)
            for kind, tok in _tokenize(str(value)):
                if kind != "WORD" or tok == GATE:
                    continue
                try:
                    name, _ = _split_word(tok)
                except MarkerSyntaxError:
                    unparseable.setdefault(tok, set()).add(sheet_row)
                    continue
                entry = markers.setdefault(
                    name, {"count": 0, "columns": set(), "rows": set()}
                )
                entry["count"] += 1
                entry["columns"].add(col)
                entry["rows"].add(sheet_row)
    return {"markers": markers, "unparseable": unparseable, "cells": cells}


def deterministic_findings(inventory: dict) -> dict:
    """High-confidence checks over the inventory (no LLM)."""
    markers = inventory["markers"]

    # 1. Casing collisions: same token ignoring case, >1 distinct spelling.
    by_lower: dict[str, set] = {}
    for name in markers:
        by_lower.setdefault(name.lower(), set()).add(name)
    casing = sorted(
        [sorted(v) for v in by_lower.values() if len(v) > 1]
    )

    # 2. Orphan fragments: standalone tokens that look like pieces of a
    #    space-split marker name.
    fragments = sorted(
        name
        for name in markers
        if len(name) == 1
        or name.lower() in _FRAGMENT_WORDS
        or (name.isalpha() and name.islower() and len(name) >= 4)
    )

    # 3. Unparseable tokens (also caught by the grammar validator).
    unparseable = sorted(inventory["unparseable"])

    return {
        "casing_collisions": casing,
        "orphan_fragments": fragments,
        "unparseable_tokens": unparseable,
    }


def run_deterministic(csv: str | Path) -> dict:
    """Inventory + findings, JSON-serialisable (sets -> sorted lists)."""
    inventory = extract_inventory(csv)
    markers = {
        name: {
            "count": e["count"],
            "columns": sorted(e["columns"]),
            "rows": sorted(e["rows"]),
        }
        for name, e in sorted(inventory["markers"].items())
    }
    return {
        "markers": markers,
        "unparseable": {k: sorted(v) for k, v in inventory["unparseable"].items()},
        "cells": inventory["cells"],
        "findings": deterministic_findings(inventory),
    }


# --------------------------------------------------------------------------- #
# Agentic layer (headless claude -p)
# --------------------------------------------------------------------------- #
_AGENT_INSTRUCTIONS = """\
You are auditing flow-cytometry marker names from the SOULCAP dataset.
Markers were extracted by splitting on spaces, so a reagent whose name contains
a space (e.g. "MR1 Tetramer", "TCR V delta 1") appears as several fragment
tokens. Using the marker inventory, the deterministic hints, and the raw cell
strings below, identify:

1. spaced_marker_names: marker names that were split across tokens and should be
   a single token. Give the text as written, a proposed space-free canonical
   name, and the sheet rows.
2. inconsistent_names: the same antigen written differently (casing or
   nomenclature, e.g. "TCRVB11" vs "TCR VB11", "Vd1" vs "TCR V delta 1"). Give
   the variants and one canonical form.
3. alias_pairs: CD-number / common-name pairs for the same antigen
   (e.g. CD183 / CXCR3). Give the variants and a preferred form.
4. other: anything else suspect.

Respond with ONLY a JSON object, no prose, with exactly these keys:
{"spaced_marker_names": [{"as_written": str, "canonical": str, "rows": [int]}],
 "inconsistent_names": [{"variants": [str], "canonical": str, "note": str}],
 "alias_pairs": [{"variants": [str], "preferred": str, "note": str}],
 "other": [{"summary": str, "markers": [str], "note": str}]}
"""


def build_prompt(deterministic: dict) -> str:
    """Assemble the agent prompt from the deterministic output."""
    markers = deterministic["markers"]
    token_lines = "\n".join(
        f"- {name} (x{info['count']})" for name, info in markers.items()
    )
    hints = json.dumps(deterministic["findings"], indent=2)
    cells = "\n".join(f"- {c}" for c in deterministic["cells"])
    return (
        f"{_AGENT_INSTRUCTIONS}\n"
        f"## Distinct marker tokens\n{token_lines}\n\n"
        f"## Deterministic hints\n{hints}\n\n"
        f"## Raw cell strings\n{cells}\n"
    )


def invoke_claude(prompt: str, model: str | None = None, timeout: int = 180) -> str:
    """Run the prompt headlessly via the `claude` CLI; return raw stdout."""
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError as exc:
        raise AgentUnavailable("`claude` CLI not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise AgentUnavailable(f"`claude` timed out after {timeout}s") from exc
    if proc.returncode != 0:
        raise AgentUnavailable(
            f"`claude` exited {proc.returncode}: {proc.stderr.strip()[:200]}"
        )
    return proc.stdout


def parse_agent_output(stdout: str) -> dict:
    """Extract the model's JSON answer from `claude -p` stdout."""
    text = stdout
    try:  # `claude --output-format json` wraps the answer in {"result": ...}
        wrapper = json.loads(stdout)
        if isinstance(wrapper, dict) and "result" in wrapper:
            text = wrapper["result"]
    except (json.JSONDecodeError, TypeError):
        pass
    # Strip ``` fences and pull out the JSON object.
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise AgentUnavailable("no JSON object in agent output")
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise AgentUnavailable(f"could not parse agent JSON: {exc}") from exc


def run_agentic(
    deterministic: dict, agent_fn=invoke_claude, model=None, timeout=180
) -> dict:
    """Run the agentic pass; returns parsed findings or {'error': ...}."""
    prompt = build_prompt(deterministic)
    try:
        raw = agent_fn(prompt, model, timeout)
        return parse_agent_output(raw)
    except AgentUnavailable as exc:
        return {"error": str(exc)}


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def _esc(text: str) -> str:
    return str(text).replace("|", "\\|")


def render_report(
    mode: str, deterministic: dict | None, agentic: dict | None, source_name: str
) -> str:
    lines = [
        "# Marker Review (deterministic + agentic)",
        "",
        "> **Auto-generated** by `soulcap-review`. Do not edit by hand — edit the "
        "Google Sheet master and re-run.",
        "",
        f"- Source: `{source_name}`",
        f"- Mode: **{mode}**",
        "",
    ]

    if deterministic is not None:
        f = deterministic["findings"]
        lines += [
            "## Deterministic checks",
            "",
            f"- Distinct markers: **{len(deterministic['markers'])}**",
            "",
            "### Casing collisions",
        ]
        if f["casing_collisions"]:
            lines += [f"- {_esc(' / '.join(v))}" for v in f["casing_collisions"]]
        else:
            lines.append("- none")
        lines += ["", "### Orphan fragments (possible space-split names)"]
        lines.append(
            "- " + ", ".join(_esc(x) for x in f["orphan_fragments"])
            if f["orphan_fragments"]
            else "- none"
        )
        lines += ["", "### Unparseable tokens"]
        lines.append(
            "- " + ", ".join(f"`{_esc(x)}`" for x in f["unparseable_tokens"])
            if f["unparseable_tokens"]
            else "- none"
        )
        lines.append("")

    if agentic is not None:
        lines += ["## Agentic review", ""]
        if "error" in agentic:
            lines += [f"> ⚠️ Agentic pass skipped: {agentic['error']}", ""]
        else:
            lines += _render_agentic(agentic)

    return "\n".join(lines) + "\n"


def _render_agentic(agentic: dict) -> list[str]:
    out: list[str] = []
    spaced = agentic.get("spaced_marker_names") or []
    out.append("### Space-split marker names")
    if spaced:
        out += ["| As written | Canonical | Rows |", "|---|---|---|"]
        out += [
            f"| {_esc(s.get('as_written',''))} | {_esc(s.get('canonical',''))} "
            f"| {_esc(s.get('rows',''))} |"
            for s in spaced
        ]
    else:
        out.append("- none")
    out.append("")

    inconsistent = agentic.get("inconsistent_names") or []
    out.append("### Inconsistent nomenclature")
    if inconsistent:
        out += ["| Variants | Canonical | Note |", "|---|---|---|"]
        out += [
            f"| {_esc(', '.join(i.get('variants', [])))} "
            f"| {_esc(i.get('canonical',''))} | {_esc(i.get('note',''))} |"
            for i in inconsistent
        ]
    else:
        out.append("- none")
    out.append("")

    aliases = agentic.get("alias_pairs") or []
    out.append("### Alias pairs")
    if aliases:
        out += ["| Variants | Preferred | Note |", "|---|---|---|"]
        out += [
            f"| {_esc(', '.join(a.get('variants', [])))} "
            f"| {_esc(a.get('preferred',''))} | {_esc(a.get('note',''))} |"
            for a in aliases
        ]
    else:
        out.append("- none")
    out.append("")

    other = agentic.get("other") or []
    if other:
        out.append("### Other")
        out += [f"- {_esc(o.get('summary',''))} {_esc(o.get('note',''))}" for o in other]
        out.append("")
    return out


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def review(
    csv: str | Path,
    mode: str = "both",
    agent_fn=invoke_claude,
    model: str | None = None,
    report_path: str | Path | None = None,
    det_json: str | Path | None = None,
    timeout: int = 180,
) -> dict:
    """Run the review and write the Markdown report; return the results.

    ``mode``:
      * ``deterministic`` — checks only (no LLM); persists inventory if
        ``det_json`` is given.
      * ``agentic`` — agentic pass only; reuses ``det_json`` if it exists,
        otherwise computes the inventory first to feed the agent.
      * ``both`` — deterministic first, then agentic (default).
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    csv = Path(csv)
    repo_root = Path(__file__).resolve().parents[2]
    report_path = Path(report_path or repo_root / "reports" / "marker_review.md")

    # Deterministic input (needed by every mode; agentic may reuse a saved copy).
    if mode == "agentic" and det_json and Path(det_json).exists():
        deterministic = json.loads(Path(det_json).read_text())
    else:
        deterministic = run_deterministic(csv)
        if det_json:
            Path(det_json).write_text(json.dumps(deterministic, indent=2))

    agentic = None
    if mode in ("both", "agentic"):
        agentic = run_agentic(deterministic, agent_fn, model, timeout)

    det_for_report = deterministic if mode in ("both", "deterministic") else None
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_report(mode, det_for_report, agentic, csv.name)
    )

    print(f"Marker review ({mode}) -> {report_path}")
    if agentic and "error" in agentic:
        print(f"  agentic pass skipped: {agentic['error']}")
    return {"deterministic": deterministic, "agentic": agentic, "report": report_path}


def main(argv: list[str] | None = None) -> int:
    import argparse

    repo_root = Path(__file__).resolve().parents[2]
    default_csv = repo_root / "data" / "marker_combinations.csv"

    parser = argparse.ArgumentParser(
        description="Deterministic + agentic review of marker strings."
    )
    parser.add_argument("csv", nargs="?", type=Path, default=default_csv)
    parser.add_argument("--mode", choices=MODES, default="both")
    parser.add_argument("--model", default=None, help="Model for `claude -p`.")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument(
        "--det-json",
        type=Path,
        default=None,
        help="Persist/reuse the deterministic inventory at this path.",
    )
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args(argv)

    if not args.csv.exists():
        print(f"error: {args.csv} not found — run `soulcap-sync` first.")
        return 2

    result = review(
        args.csv,
        mode=args.mode,
        model=args.model,
        report_path=args.report,
        det_json=args.det_json,
        timeout=args.timeout,
    )
    agentic = result["agentic"]
    return 1 if (agentic and "error" in agentic) else 0


if __name__ == "__main__":
    raise SystemExit(main())
