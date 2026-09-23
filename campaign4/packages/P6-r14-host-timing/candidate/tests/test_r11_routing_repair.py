"""P6-r11 routing repair focused tests (case_entry only).

The harness returns structured error dicts {"error": CODE, ...} with NO
"decision" key for authority/routing failures. The entrypoint must surface
the original code/reason BEFORE timing/case gates (never E_NO_LATENCY),
while legitimate decision results pass through untouched.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from case_entry import StageCFault, _raise_for_harness_error


def test_forged_route_error_propagates():
    try:
        _raise_for_harness_error(
            {"error": "E_FORGED_ROUTE",
             "detail": "worker field route rejected",
             "owner": "cairn"}, "run-fixture")
    except StageCFault as e:
        assert e.code == "E_FORGED_ROUTE"
        assert "worker field route rejected" in e.detail
    else:
        raise AssertionError("forged-route error swallowed")


def test_claim_mismatch_error_propagates():
    try:
        _raise_for_harness_error(
            {"error": "E_CLAIM_MISMATCH",
             "detail": "execution does not match launch manifest"},
            "run-fixture")
    except StageCFault as e:
        assert e.code == "E_CLAIM_MISMATCH"
    else:
        raise AssertionError("claim-mismatch error swallowed")


def test_unrelated_harness_failure_propagates_with_own_code():
    try:
        _raise_for_harness_error(
            {"error": "E_BIND_CARRY", "detail": "binding restore failed"},
            "reattach")
    except StageCFault as e:
        assert e.code == "E_BIND_CARRY"
        assert e.code != "E_NO_LATENCY"
    else:
        raise AssertionError("unrelated failure swallowed")


def test_decision_results_pass_through():
    for out in ({"decision": "verified-rejection"},
                {"decision": "transition-committed"},
                {"decision": "terminal-rest"},
                {"decision": "owned-recovery", "reason": "E_X"},
                {"raw": "..."}):
        _raise_for_harness_error(out, "run-fixture")
