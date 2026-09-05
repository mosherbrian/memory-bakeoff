"""A deletion must arrive with a named condition; everything else keeps the test.

Frozen before any Gen64 critic call. Gen62's critic deleted 84% of a sound bank
because refusing was cheap, so these cases pin down every route back to KEEP.
"""
from __future__ import annotations

import ast

from memory_bakeoff.evidence_ruler import justified_critic as J


def test_a_plain_keep_keeps_the_test():
    result = J.parse_verdict("KEEP")
    assert result["verdict"] == "KEEP" and result["removed"] is False
    assert result["readable"] is True


def test_a_named_extra_condition_deletes_the_test():
    result = J.parse_verdict(
        "REMOVE\nEXTRA: it requires a Windows drive letter path to be rejected")
    assert result["removed"] is True
    assert "drive letter" in result["justification"]


def test_a_removal_without_an_extra_line_keeps_the_test():
    result = J.parse_verdict("REMOVE\nThis test is not entailed by the sentence.")
    assert result["verdict"] == "REMOVE"
    assert result["removed"] is False
    assert result["reason"].startswith("removal without an EXTRA line")


def test_a_two_word_justification_keeps_the_test():
    result = J.parse_verdict("REMOVE\nEXTRA: too strict")
    assert result["removed"] is False
    assert "too short" in result["reason"]


def test_a_vague_restatement_keeps_the_test():
    """The Gen62 failure mode: refusing without pointing at anything."""
    result = J.parse_verdict("REMOVE\nEXTRA: the sentence does not require this")
    assert result["removed"] is False
    assert "restates the complaint" in result["reason"]


def test_a_long_specific_justification_survives_the_vague_check():
    # Contains a vague phrase but goes on to name the condition, so it counts.
    result = J.parse_verdict(
        "REMOVE\nEXTRA: not required - it demands that close() also reset the "
        "running total to zero before any further add() call")
    assert result["removed"] is True


def test_an_unreadable_reply_keeps_the_test():
    result = J.parse_verdict("I think this one is probably fine, hard to say.")
    assert result["removed"] is False and result["readable"] is False


def test_an_empty_reply_keeps_the_test():
    assert J.parse_verdict("")["removed"] is False


def test_the_prompt_tells_the_critic_that_examples_are_not_extra_conditions():
    filled = J.CRITIC_PROMPT.format(quote="Q", test="T")
    flat = " ".join(filled.split())
    assert "several examples" in flat.lower()
    assert "If you cannot name the specific extra condition, reply KEEP." in flat


def test_the_prompt_shows_only_the_quote_and_the_test():
    filled = J.CRITIC_PROMPT.format(quote="Q-SENTINEL", test="T-SENTINEL")
    assert "Q-SENTINEL" in filled and "T-SENTINEL" in filled
    for forbidden in ("verifier", "candidates.json", "repository", "implementation"):
        assert forbidden not in filled.lower()


def test_the_module_does_no_io():
    tree = ast.parse(open(J.__file__).read())
    imported = {alias.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for alias in node.names}
    imported |= {node.module.split(".")[0] for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom) and node.module}
    assert imported <= {"__future__", "hashlib", "re", "typing"}


def test_the_contract_records_the_asymmetry_and_the_guardrail():
    contract = J.contract()
    assert contract["default_is_keep"].startswith("an unreadable reply")
    assert "gen63-retention-guardrail-v1" in contract["unchanged"]
    assert contract["frozen_before_exposure"] is True
