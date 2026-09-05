"""The critic's reader must fail safe, and must not confuse its two verdicts.

Frozen before any Gen62 critic call. NOT_ENTAILED contains the substring
ENTAILED, so a careless reader would keep every test it was asked to delete.
"""
from __future__ import annotations

import ast

from memory_bakeoff.evidence_ruler import entailment_critic as K


def test_a_plain_entailed_reply_keeps_the_test():
    result = K.parse_verdict("ENTAILED\nThe assertion follows directly.")
    assert result["verdict"] == "ENTAILED" and result["removed"] is False


def test_not_entailed_is_not_read_as_entailed():
    result = K.parse_verdict("NOT_ENTAILED\nThe sentence says nothing about drives.")
    assert result["verdict"] == "NOT_ENTAILED" and result["removed"] is True


def test_the_spaced_spelling_is_also_read_as_a_removal():
    assert K.parse_verdict("NOT ENTAILED - overreaches")["removed"] is True


def test_case_does_not_matter():
    assert K.parse_verdict("not_entailed\nnope")["removed"] is True
    assert K.parse_verdict("entailed\nyes")["removed"] is False


def test_an_unreadable_reply_keeps_the_test():
    """Fail safe: a malformed answer must never delete evidence."""
    result = K.parse_verdict("I am not sure how to answer this one.")
    assert result["readable"] is False
    assert result["removed"] is False
    assert result["verdict"] is None


def test_an_empty_reply_keeps_the_test():
    assert K.parse_verdict("")["removed"] is False


def test_the_prompt_shows_the_critic_only_the_quote_and_the_test():
    filled = K.CRITIC_PROMPT.format(quote="Q-SENTINEL", test="T-SENTINEL")
    assert "Q-SENTINEL" in filled and "T-SENTINEL" in filled
    for forbidden in ("verifier", "candidates.json", "repository", "implementation"):
        assert forbidden not in filled.lower()


def test_the_critic_module_does_no_io():
    """It is handed two strings; it cannot reach the repository or the answer."""
    tree = ast.parse(open(K.__file__).read())
    imported = {alias.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for alias in node.names}
    imported |= {node.module.split(".")[0] for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom) and node.module}
    assert imported <= {"__future__", "hashlib", "re", "typing"}


def test_the_contract_records_that_the_critic_is_the_same_model():
    contract = K.contract()
    assert "same pinned weights" in contract["critic_is_the_same_model"]
    assert contract["frozen_before_exposure"] is True
    assert contract["deletion_only"].startswith("the critic cannot edit")
