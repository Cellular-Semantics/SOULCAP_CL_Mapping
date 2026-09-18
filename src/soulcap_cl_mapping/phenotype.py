"""Compile phenotype ASTs into bounded CNF and evaluate open-world evidence.

Unknown CL assertions stay unknown, including under negation. Positive means
expressed at an unspecified level; it cannot prove a high/low requirement.
The documented special qualifier +/- means low or absent.
"""

from __future__ import annotations

from soulcap_cl_mapping.marker_syntax import (
    Expression,
    MarkerSyntaxError,
    parse_expression,
)

Literal = tuple[str, str]
Clause = Literal | list[Literal]
LEVELS = {
    "+": "positive",
    "-": "negative",
    "hi": "high",
    "lo": "low",
    "int": "intermediate",
}
MAX_CLAUSES = 256


def _cnf(node: Expression, negate: bool = False) -> list[list[Literal]]:
    if node.operator == "atom":
        if not node.qualifier:
            return [[(node.marker.upper(), "unknown")]]
        levels = ["lo", "-"] if node.qualifier == "+/-" else node.qualifier.split("/")
        atoms = [
            (node.marker.upper(), ("not:" if negate else "") + LEVELS[q])
            for q in levels
        ]
        return [[a] for a in atoms] if negate else [atoms]
    if node.operator == "group":
        if node.qualifier not in ("+", "-"):
            raise MarkerSyntaxError(
                "group expression levels need clarification; only group + and - can be scored"
            )
        return _cnf(node.children[0], negate ^ (node.qualifier == "-"))
    is_and = (node.operator == "and") != negate
    parts = [_cnf(child, negate) for child in node.children]
    if is_and:
        result = [clause for part in parts for clause in part]
    else:
        result = [[]]
        for part in parts:
            if len(result) * len(part) > MAX_CLAUSES:
                raise MarkerSyntaxError("expression exceeds Boolean expansion limit")
            result = [list(dict.fromkeys(a + b)) for a in result for b in part]
    if len(result) > MAX_CLAUSES:
        raise MarkerSyntaxError("expression exceeds Boolean expansion limit")
    return result


def clauses(expr: str) -> list[Clause]:
    if not expr.strip():
        return []
    return [
        part[0] if len(part) == 1 else part for part in _cnf(parse_expression(expr))
    ]


def evaluate(marker: str, sense: str, entry: dict) -> str:
    """Return matched, contradicted, or gap without treating absence as negation."""
    if sense.startswith("not:"):
        return {"matched": "contradicted", "contradicted": "matched", "gap": "gap"}[
            evaluate(marker, sense[4:], entry)
        ]
    if sense == "unknown":
        return "gap"
    levels = {
        level
        for level in ("positive", "negative", "high", "low", "intermediate")
        if marker in entry.get(level, set())
    }
    if (
        not levels
        or ("negative" in levels and len(levels) > 1)
        or len(levels - {"positive"}) > 1
    ):
        return "gap"
    if sense == "positive":
        return "contradicted" if levels == {"negative"} else "matched"
    if sense == "negative":
        return "matched" if levels == {"negative"} else "contradicted"
    if sense in levels:
        return "matched"
    if levels == {"positive"}:
        return "gap"
    return "contradicted"


def has_qualified(clauses: list[Clause]) -> bool:
    """Whether at least one literal has a defined expression qualifier."""
    return any(
        s.removeprefix("not:") != "unknown"
        for clause in clauses
        for _, s in ([clause] if isinstance(clause, tuple) else clause)
    )


def display(clause: Clause) -> str:
    if isinstance(clause, list):
        return "(" + " OR ".join(display(a) for a in clause) + ")"
    marker, sense = clause
    return f"{marker}:{sense}"
