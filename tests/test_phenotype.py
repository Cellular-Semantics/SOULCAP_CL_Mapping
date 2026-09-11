"""Semantic regressions: compare Boolean formulas, not parser internals."""

import itertools

import pytest

from soulcap_cl_mapping import cl_match, phenotype as p
from soulcap_cl_mapping.marker_syntax import (
    MarkerSyntaxError,
    parse_expression,
    extract_markers,
)


def satisfied(expr, entry):
    states = []
    for clause in p.clauses(expr):
        alternatives = [clause] if isinstance(clause, tuple) else clause
        values = [p.evaluate(m, s, entry) for m, s in alternatives]
        states.append(
            "matched"
            if "matched" in values
            else "contradicted"
            if all(v == "contradicted" for v in values)
            else "gap"
        )
    return (
        "contradicted"
        if "contradicted" in states
        else "matched"
        if all(v == "matched" for v in states)
        else "gap"
    )


@pytest.mark.parametrize("a,b,c", list(itertools.product([False, True], repeat=3)))
def test_nested_boolean_truth_table(a, b, c):
    entry = {
        "positive": {m for m, v in zip("ABC", (a, b, c)) if v},
        "negative": {m for m, v in zip("ABC", (a, b, c)) if not v},
    }
    assert (satisfied("[(A+|B+) C+]-", entry) == "matched") == (not ((a or b) and c))
    assert (satisfied("((A+ B+)|C+)", entry) == "matched") == ((a and b) or c)


@pytest.mark.parametrize(
    "expr,level,want",
    [
        ("CD16-/lo", "low", "matched"),
        ("CD16-/lo", "negative", "matched"),
        ("CD16-/lo", "high", "contradicted"),
        ("CD16lo", "negative", "contradicted"),
        ("CD16int", "positive", "gap"),
        ("CD16hi", "low", "contradicted"),
        ("CD16+", "low", "matched"),
        ("CD16+/-", "high", "contradicted"),
        ("CD16+/-", "negative", "matched"),
        ("CD16+/-", "low", "matched"),
        ("[CD16hi]-", "positive", "gap"),
        ("[CD16hi]-", "low", "matched"),
        ("CD16int", "intermediate", "matched"),
    ],
)
def test_expression_levels(expr, level, want):
    assert satisfied(expr, {level: {"CD16"}}) == want


def test_unknown_under_negation_and_inconsistent_axioms():
    assert satisfied("[CD16+]-", {}) == "gap"
    assert satisfied("CD16+", {"positive": {"CD16"}, "negative": {"CD16"}}) == "gap"
    assert satisfied("CD16hi", {"high": {"CD16"}, "low": {"CD16"}}) == "gap"


def test_ast_is_shared_and_unqualified_markers_remain_unknown():
    expr = " live/ [(CD3+|CD4lo) CD8]- "
    assert (
        parse_expression(expr).markers()
        == extract_markers(expr)
        == {"CD3", "CD4", "CD8"}
    )
    assert satisfied("CD8", {"positive": {"CD8"}}) == "gap"
    assert extract_markers("CD3+ (CD4-") == set()


def test_undefined_group_levels_are_flagged():
    parse_expression("[CD3+ CD4+]hi")  # valid grammar, undefined biology
    with pytest.raises(MarkerSyntaxError, match="clarification"):
        p.clauses("[CD3+ CD4+]hi")


def test_boolean_expansion_is_bounded():
    expr = "(" + "|".join("(A+ B+)" for _ in range(9)) + ")"
    with pytest.raises(MarkerSyntaxError, match="limit"):
        p.clauses(expr)
    with pytest.raises(MarkerSyntaxError, match="limit"):
        p.clauses(" ".join(["A+"] * 257))


def test_invalid_batch_profile_abstains_even_with_valid_other_columns():
    row = {
        "Abbreviation": "NK",
        "Required phenotypic markers": "CD56+",
        "Ideal exclusion": "CD3+)",
    }
    result = cl_match.score_marker_combinations_row(
        row, {"CL:1": {"label": "cell", "positive": {"CD56"}, "negative": set()}}
    )
    assert result["candidates"] == []
    assert "Ideal exclusion" in result["note"]


def test_intermediate_axiom_survives_index_and_ranking():
    index = cl_match.build_cl_index(
        [
            {
                "cell": "CL:1",
                "cell_label": "cell",
                "sense": "intermediate",
                "cd_synonym": "CD123 (exact)",
            }
        ]
    )
    result = cl_match.score_cl_terms(index, p.clauses("CD123int"), [])[0]
    assert result["matched"] and not result["contradictions"]
