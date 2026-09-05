"""The repo-context critic must gain code, not gain the answer.

Frozen before any Gen66 call. The reader is imported from Gen64 rather than
rewritten, so these tests check the one thing that changed: what the prompt
carries, and what it must never carry.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

from memory_bakeoff.evidence_ruler import justified_critic as J
from memory_bakeoff.evidence_ruler import repo_context_critic as K

ROOT = Path(__file__).resolve().parents[1]


def test_the_verdict_reader_is_gen64s_not_a_reimplementation():
    """One variable changes between Gen64 and Gen66; the reader is not it."""
    assert K.parse_verdict is J.parse_verdict


def test_the_prompt_carries_the_shipped_tree():
    prompt = K.build_prompt(quote="Q", test="T", tree="TREE-SENTINEL")
    assert "TREE-SENTINEL" in prompt and "Q" in prompt and "T" in prompt


def test_the_prompt_says_the_code_is_the_original_not_a_solution():
    flat = " ".join(K.build_prompt(quote="Q", test="T", tree="X").split())
    assert "It is the ORIGINAL code, not anybody's solution" in flat


def test_the_prompt_still_refuses_vague_deletions():
    flat = " ".join(K.build_prompt(quote="Q", test="T", tree="X").split())
    assert "If you cannot name the specific extra condition, reply KEEP." in flat


def test_an_inference_from_the_code_is_declared_not_an_extra_condition():
    flat = " ".join(K.build_prompt(quote="Q", test="T", tree="X").split())
    assert "follows plainly from what the code is" in flat


def test_isolation_report_flags_a_forbidden_token():
    report = K.isolation_report("this mentions the verifier", ("verifier",))
    assert report["clean"] is False and report["found"] == ["verifier"]


def test_isolation_report_passes_a_clean_prompt():
    assert K.isolation_report("nothing to see", ("verifier",))["clean"] is True


def test_the_contract_forbids_the_candidate_and_says_why():
    contract = K.contract()
    assert "the candidate under test" in contract["critic_inputs_forbidden"]
    assert "the known-wrong labels" in contract["critic_inputs_forbidden"]
    assert contract["candidate_blind"].startswith("the repository shown is the pre-work")
    assert "NOT a continuation" in contract["experimental_family"]


def test_the_recorded_preflight_found_no_leak():
    payload = json.loads(
        (ROOT / "results/pi_repo_context_gen66/isolation_preflight.json").read_text())
    assert payload["clean"] is True and payload["total_leaks"] == 0
    for task, finding in payload["tasks"].items():
        assert finding["found"] == []
        assert finding["candidate_lines_in_prompt"] == []


def test_the_module_reads_nothing_from_disk():
    tree = ast.parse(open(K.__file__).read())
    called = {node.func.id for node in ast.walk(tree)
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "open" not in called
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not attributes & {"read_text", "read_bytes", "run", "system"}
