"""The grounding filter must drop invented requirements and keep real ones.

Frozen before any Gen61 generation ran. These cases are hand-written, so a later
change to the rule fails here rather than silently changing what Gen61 measured.
"""
from __future__ import annotations

import ast

from memory_bakeoff.evidence_ruler import spec_grounded as G

SPEC = ("Change the gauge so that position_mm(80) returns 10.\n"
        "The telemetry frame must keep reporting 40 steps for 10 mm.\n")


def bank(*functions: str) -> str:
    return "import pytest\n\n" + "\n\n".join(functions)


def cited(quote: str, name: str = "test_one") -> str:
    return (f'def {name}():\n    """REQUIREMENT: {quote}"""\n    assert True\n')


def test_a_verbatim_quote_is_grounded():
    assert G.is_grounded("position_mm(80) returns 10", SPEC)


def test_wrapping_and_case_do_not_break_a_real_quote():
    assert G.is_grounded("POSITION_MM(80)\n   RETURNS   10", SPEC)


def test_an_invented_requirement_is_not_grounded():
    assert not G.is_grounded("the gauge must round half to even", SPEC)


def test_a_missing_citation_is_not_grounded():
    assert not G.is_grounded(None, SPEC)


def test_a_quote_too_short_to_mean_anything_is_refused():
    # "the gauge" really is in the spec, and proves nothing.
    assert not G.is_grounded("the gauge", SPEC)


def test_the_marker_must_lead_the_docstring():
    node = ast.parse('def test_x():\n    """checks REQUIREMENT: something"""\n    pass'
                     ).body[0]
    assert G.cited_requirement(node) is None


def test_an_ungrounded_test_is_removed_and_a_grounded_one_survives():
    code = bank(cited("position_mm(80) returns 10", "test_good"),
                cited("must round half to even", "test_bad"))
    result = G.ground_bank(code, SPEC)
    assert [k["test"] for k in result["kept"]] == ["test_good"]
    assert [d["test"] for d in result["dropped"]] == ["test_bad"]
    assert "test_bad" not in result["code"]


def test_imports_and_helpers_survive_because_a_kept_test_may_need_them():
    code = ("import pytest\n\nHELPER = 3\n\n"
            + cited("position_mm(80) returns 10", "test_good"))
    result = G.ground_bank(code, SPEC)
    assert "import pytest" in result["code"]
    assert "HELPER = 3" in result["code"]


def test_tests_inside_a_class_are_filtered_too():
    code = ("class TestGauge:\n"
            '    def test_good(self):\n        """REQUIREMENT: position_mm(80) returns 10"""\n        assert True\n'
            '    def test_bad(self):\n        """REQUIREMENT: must round half to even"""\n        assert True\n')
    result = G.ground_bank(code, SPEC)
    assert [k["test"] for k in result["kept"]] == ["test_good"]
    assert result["dropped_count"] == 1


def test_a_class_that_loses_every_test_still_parses():
    code = ("class TestGauge:\n"
            '    def test_bad(self):\n        """REQUIREMENT: invented entirely"""\n        assert True\n')
    result = G.ground_bank(code, SPEC)
    ast.parse(result["code"])
    assert result["kept_count"] == 0


def test_the_filter_cannot_reach_the_hidden_answer_because_it_does_no_io():
    """The isolation guarantee, stated as something checkable.

    Gen57 taught that a text search for a forbidden word matches the module's
    own prose saying it does not use it - and Gen61's contract text names the
    hidden verifier precisely to record that it is off limits. So test the real
    property: this module reads nothing. It is handed the generated code and the
    visible spec, and it has no way to open a file, import a path, or run
    anything. It therefore cannot consult the answer even by accident.
    """
    tree = ast.parse(open(G.__file__).read())
    imported = {node.module.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module}
    imported |= {alias.name.split(".")[0] for node in ast.walk(tree)
                 if isinstance(node, ast.Import) for alias in node.names}
    assert imported <= {"__future__", "ast", "hashlib", "re", "typing"}
    called = {node.func.id for node in ast.walk(tree)
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "open" not in called and "eval" not in called and "exec" not in called
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not attributes & {"read_text", "read_bytes", "open", "run", "system"}


def test_the_contract_hash_is_stable():
    assert G.contract()["contract_sha256"] == G.contract()["contract_sha256"]
    assert G.contract()["frozen_before_exposure"] is True
