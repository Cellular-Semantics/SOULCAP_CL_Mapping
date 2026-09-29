"""Conservative protein/alias resolution and offline lexical candidate snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def marker_resolver(path: Path) -> dict:
    from soulcap_cl_mapping.marker_resolution import load

    return load(path)


def expand_axiom(row: dict, resolver: dict) -> tuple[set[str], list[dict]]:
    from soulcap_cl_mapping.marker_resolution import expand_axiom as expand

    return expand(row, resolver)


def load_terms(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("terms"), list):
        raise ValueError("Invalid lexical cache schema")
    result = {}
    for term in data["terms"]:
        if (
            not re.fullmatch(r"CL:\d{7}", term["cl_id"])
            or term["cl_id"] in result
            or not isinstance(term["label"], str)
            or not term["label"].strip()
        ):
            raise ValueError("Duplicate or malformed lexical term")
        if not isinstance(term["exact_synonyms"], list) or any(
            not isinstance(s, str) for s in term["exact_synonyms"]
        ):
            raise ValueError("Malformed lexical synonyms")
        result[term["cl_id"]] = term
    return result


def lexical_candidates(row: dict, index: dict, limit: int = 20) -> dict:
    query = normalize(row.get("Full Name", "") or row.get("Abbreviation", ""))
    words = set(query.split()) - {"cell", "cells"}
    if not words:
        return {}
    matches = []
    for cl_id, entry in index.items():
        if "lexical_names" not in entry:
            continue
        names = entry["lexical_names"]
        exact = any(query == normalize(n) for n in names)
        overlap = max(
            (
                len(words & (set(normalize(n).split()) - {"cell", "cells"}))
                / max(1, len(words | (set(normalize(n).split()) - {"cell", "cells"})))
                for n in names
            ),
            default=0,
        )
        if exact or overlap >= 0.5:
            matches.append(
                (
                    not exact,
                    -overlap,
                    cl_id,
                    {"query": query, "exact": exact, "token_jaccard": overlap},
                )
            )
    matches.sort()
    return {cl_id: evidence for _, _, cl_id, evidence in matches[:limit]}


def cache_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract active CL labels/exact synonyms from a local OAK SQLite snapshot; no downloads."
    )
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.database.resolve() == args.out.resolve():
        parser.error("Output must not overwrite the database")
    with sqlite3.connect(
        args.database.resolve().as_uri() + "?mode=ro", uri=True
    ) as connection:
        rows = connection.execute(
            "SELECT subject,predicate,value FROM statements WHERE subject LIKE 'CL:%' AND predicate IN ('rdfs:label','oio:hasExactSynonym','owl:deprecated')"
        ).fetchall()
    terms: dict = {}
    obsolete = set()
    for subject, predicate, value in rows:
        if not re.fullmatch(r"CL:\d{7}", subject):
            continue
        term = terms.setdefault(
            subject, {"cl_id": subject, "label": "", "exact_synonyms": []}
        )
        if predicate == "owl:deprecated" and str(value).lower() in ("true", "1"):
            obsolete.add(subject)
        elif predicate == "rdfs:label":
            term["label"] = value
        elif predicate == "oio:hasExactSynonym" and value:
            term["exact_synonyms"].append(value)
    active = [
        t for key, t in sorted(terms.items()) if key not in obsolete and t["label"]
    ]
    for term in active:
        term["exact_synonyms"] = sorted(set(term["exact_synonyms"]))
    if not active:
        parser.error("No active CL terms found")
    with args.database.open("rb") as fh:
        checksum = hashlib.file_digest(fh, "sha256").hexdigest()
    data = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_database_sha256": checksum,
        "upstream_checked": False,
        "terms": active,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Cached {len(active)} active CL terms in {args.out}")
    return 0
