#!/usr/bin/env python3
"""Gen46 preflight: prove the harness-maintained arm before it ever meets a model.

No model, no GPU, no network. Synthetic event logs only.
"""
from __future__ import annotations

import argparse, hashlib, json, random, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import BlockedNetwork, block_network  # noqa: E402
from memory_bakeoff.pi_state_control import harness_state as H  # noqa: E402
from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen46"
GEN45 = ROOT / "results" / "pi_state_control_gen45"
TS_MODULE = ROOT / "extensions" / "pi_state_control" / "pi_pilot_harness_state.ts"

GEN47_ORDER_SEED = 20260906


def trace_ordinary() -> list[dict]:
    """Invented, and unrelated to the frozen tasks: look, change, check, fix, check."""
    return [
        {"type": "tool_call", "id": "e000001", "tool": "ls", "args": {"path": "."}},
        {"type": "tool_call", "id": "e000002", "tool": "read", "args": {"path": "lantern/wick.py"}},
        {"type": "tool_call", "id": "e000003", "tool": "read", "args": {"path": "tests/test_wick.py"}},
        {"type": "tool_call", "id": "e000004", "tool": "edit", "args": {"path": "lantern/wick.py"}},
        {"type": "tool_result", "id": "e000005", "command": "python -m pytest", "exit_code": 1,
         "tree_digest": "tree-after-first-edit"},
        {"type": "tool_call", "id": "e000006", "tool": "edit", "args": {"path": "lantern/wick.py"}},
        {"type": "tool_result", "id": "e000007", "command": "python -m pytest", "exit_code": 0,
         "tree_digest": "tree-after-second-edit"},
        {"type": "session_end", "id": "e000008"},
    ]


def trace_receipt_then_edit() -> list[dict]:
    """A passing check, then another edit: the receipt must stop being valid."""
    return trace_ordinary()[:-1] + [
        {"type": "tool_call", "id": "e000008", "tool": "edit", "args": {"path": "lantern/wick.py"}},
        {"type": "session_end", "id": "e000009"},
    ]


def trace_hidden_verifier_attempt() -> list[dict]:
    """Someone runs the hidden verifier. It must not become a receipt."""
    return [
        {"type": "tool_call", "id": "e000001", "tool": "read", "args": {"path": "lantern/wick.py"}},
        {"type": "tool_call", "id": "e000002", "tool": "read", "args": {"path": "README.md"}},
        {"type": "tool_call", "id": "e000003", "tool": "edit", "args": {"path": "lantern/wick.py"}},
        {"type": "tool_result", "id": "e000004", "command": "python ../verifier.py", "exit_code": 0,
         "tree_digest": "tree-x"},
        {"type": "session_end", "id": "e000005"},
    ]


def ts_replay(events: list[dict]) -> dict | None:
    """Run the same log through the TypeScript arm, if bun is available."""
    bun = Path.home() / ".bun" / "bin" / "bun"
    if not bun.exists() or not TS_MODULE.exists():
        return None
    work = Path("/tmp/gen46-ts")
    work.mkdir(parents=True, exist_ok=True)
    (work / "events.json").write_text(json.dumps(events))
    runner = work / "replay.ts"
    runner.write_text(
        'const { Derivation } = await import(process.argv[2]);\n'
        'const events = JSON.parse(await Bun.file(process.argv[3]).text());\n'
        'const d = new Derivation();\n'
        'for (const e of events) {\n'
        '  if (e.type === "tool_call") d.toolCall(e.tool, e.args ?? {}, e.id);\n'
        '  else if (e.type === "tool_result") d.toolResult(e.command ?? "", e.exit_code, '
        'Boolean(e.is_error), e.tree_digest ?? "", e.id);\n'
        '  else if (e.type === "session_end") d.sessionEnd(e.id);\n}\n'
        'console.log(JSON.stringify(d.summary()));\n')
    proc = subprocess.run([str(bun), "run", str(runner), str(TS_MODULE.resolve()),
                           str(work / "events.json")], capture_output=True, text=True)
    if proc.returncode != 0:
        return {"error": proc.stderr[-300:]}
    return json.loads(proc.stdout)


def norm(payload):
    return json.loads(json.dumps(payload, sort_keys=True))


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    checks: dict = {}

    ordinary = trace_ordinary()
    derivation = H.derive(ordinary)
    summary = derivation.summary()

    # 1. deterministic replay
    checks["deterministic_replay"] = {
        "digest": H.replay_digest(ordinary),
        "identical_across_replays": len({H.replay_digest(ordinary) for _ in range(5)}) == 1,
        "identical_after_shuffling_nothing": H.replay_digest(ordinary) == H.replay_digest(list(ordinary)),
    }

    # 2. the control loop actually runs, which is the whole point
    checks["control_loop_runs"] = {
        "transitions_accepted": summary["transitions_accepted"],
        "transitions_rejected": summary["transitions_rejected"],
        "final_phase": summary["state"]["phase"],
        "path": [(t["from"], t["to"]) for t in summary["transitions"] if t["accepted"]],
        "reached_done_from_a_valid_receipt": summary["state"]["phase"] == "done",
    }

    # 3. state stays bounded and restart is exact
    long_events = []
    for index in range(40):
        long_events.append({"type": "tool_call", "id": f"e{index:06d}", "tool": "read",
                            "args": {"path": f"pkg/module_{index}.py"}})
    long = H.derive(long_events)
    replay = H.derive(long_events)
    checks["bounded_and_restartable"] = {
        "state_bytes_after_40_events": long.state.bytes(),
        "within_cap": long.state.bytes() <= H.STATE_BYTE_CAP,
        "files_read_bound": len(long.state.files_read),
        "restart_matches": norm(long.summary()) == norm(replay.summary()),
    }

    # 4. a mutation after a passing check invalidates the receipt
    invalidated = H.derive(trace_receipt_then_edit())
    checks["receipt_invalidation"] = {
        "receipts_created": len(invalidated.receipts),
        "invalidations": len(invalidated.invalidations),
        "valid_receipt_at_end": invalidated.valid_receipt() is not None,
        "phase_returned_to_implement": invalidated.state.phase == "implement",
    }

    # 5. the hidden verifier can never become a receipt
    hidden = H.derive(trace_hidden_verifier_attempt())
    checks["hidden_verifier_is_not_a_receipt"] = {
        "receipts_created": len(hidden.receipts),
        "valid_receipt_at_end": hidden.valid_receipt() is not None,
        "classified_as_validation": H.is_validation_command("python ../verifier.py"),
        "ordinary_check_still_classified": H.is_validation_command("python -m pytest"),
    }

    # 6. hidden data is not reachable from the derivation path
    #
    # Naming a token in the forbidden list is the opposite of using it, so the
    # check looks at the executable code with that list and the docstring
    # removed, rather than counting substrings across the whole file.
    import ast as _ast

    module_path = ROOT / "src" / "memory_bakeoff" / "pi_state_control" / "harness_state.py"
    source = module_path.read_text()
    tree = _ast.parse(source)
    body = [node for node in tree.body
            if not (isinstance(node, _ast.Expr) and isinstance(node.value, _ast.Constant))]
    # Strip string constants too: prose that mentions the verifier in order to
    # say it is excluded is not the same as code that reaches for it.
    class _Strip(_ast.NodeTransformer):
        def visit_Constant(self, node):
            return _ast.Constant(value="") if isinstance(node.value, str) else node

    logic = _Strip().visit(_ast.Module(body=[
        node for node in body
        if not (isinstance(node, _ast.Assign)
                and any(getattr(t, "id", "") == "FORBIDDEN_IN_VALIDATION" for t in node.targets))
    ], type_ignores=[]))
    code = _ast.unparse(_ast.fix_missing_locations(logic))
    imports = sorted({alias.name for node in _ast.walk(tree)
                      if isinstance(node, _ast.Import) for alias in node.names} |
                     {node.module or "" for node in _ast.walk(tree)
                      if isinstance(node, _ast.ImportFrom)})
    checks["no_hidden_data_access"] = {
        "imports": imports,
        "imports_nothing_from_the_benchmark": not any(
            token in name for name in imports
            for token in ("memconflict", "corpus", "pilot", "task")),
        "opens_no_file_but_its_own_hash": code.count("open(") == 0
        and code.count("read_text") == 0,
        "no_gold_or_answer_token_in_code": all(
            token not in code for token in ("gold", "answer", "reference_fix", "task_manifest")),
        "verifier_never_appears_in_logic": "verifier" not in code,
    }

    # 7. illegal transitions fail closed
    forced = H.Derivation()
    forced.state.phase = "inspect"
    forced._move("done", "an impossible jump", "e000000")
    checks["illegal_transition_fails_closed"] = {
        "phase_unchanged": forced.state.phase == "inspect",
        "recorded_as_rejected": forced.transitions[-1]["accepted"] is False,
    }

    # 8. the Python contract and the TypeScript arm agree exactly
    ts = ts_replay(ordinary)
    checks["python_typescript_equivalence"] = {
        "typescript_available": ts is not None and "error" not in (ts or {}),
        "summaries_identical": bool(ts) and "error" not in ts and norm(ts) == norm(summary),
        "error": (ts or {}).get("error") if isinstance(ts, dict) else None,
    }

    # 9. arm B is untouched
    gen45_identity = json.loads((GEN45 / "execution_identity.json").read_text())
    arm_b = ROOT / "extensions" / "pi_state_control" / "pi_pilot_live.ts"
    checks["arm_b_unchanged"] = {
        "recorded_sha256": gen45_identity["extension_sha256"],
        "current_sha256": hashlib.sha256(arm_b.read_bytes()).hexdigest(),
        "identical": hashlib.sha256(arm_b.read_bytes()).hexdigest() == gen45_identity["extension_sha256"],
    }

    # 10. composition is arm B's, unchanged
    checks["composer_unchanged"] = {
        "order": P.pilot_contract()["composition"]["order"],
        "state_byte_cap": P.STATE_BYTE_CAP,
        "recent_window_units": P.RECENT_WINDOW_UNITS,
        "recent_window_byte_cap": P.RECENT_WINDOW_BYTE_CAP,
        "matches_gen44": (P.STATE_BYTE_CAP, P.RECENT_WINDOW_UNITS, P.RECENT_WINDOW_BYTE_CAP)
        == (4096, 2, 8192),
        "deferred_hypotheses": ["persistent_task_prompt_floor", "on_demand_history_retrieval",
                                "larger_recent_window"],
    }

    # 11. no network
    import socket
    block_network()
    try:
        socket.create_connection(("127.0.0.2", 8080), timeout=0.2)
        checks["no_network"] = {"outbound_blocked": False}
    except (BlockedNetwork, OSError) as exc:
        checks["no_network"] = {"outbound_blocked": True, "detail": str(exc)[:120]}

    passed = (
        checks["deterministic_replay"]["identical_across_replays"]
        and checks["control_loop_runs"]["reached_done_from_a_valid_receipt"]
        and checks["bounded_and_restartable"]["within_cap"]
        and checks["bounded_and_restartable"]["restart_matches"]
        and checks["receipt_invalidation"]["valid_receipt_at_end"] is False
        and checks["receipt_invalidation"]["invalidations"] == 1
        and checks["hidden_verifier_is_not_a_receipt"]["classified_as_validation"] is False
        and checks["hidden_verifier_is_not_a_receipt"]["receipts_created"] == 0
        and checks["no_hidden_data_access"]["no_gold_or_answer_token_in_code"]
        and checks["no_hidden_data_access"]["verifier_never_appears_in_logic"]
        and checks["no_hidden_data_access"]["opens_no_file_but_its_own_hash"]
        and checks["illegal_transition_fails_closed"]["phase_unchanged"]
        and checks["python_typescript_equivalence"]["summaries_identical"]
        and checks["arm_b_unchanged"]["identical"]
        and checks["composer_unchanged"]["matches_gen44"]
        and checks["no_network"]["outbound_blocked"]
    )
    checks["passed"] = passed

    # Gen47 order: a new seed, because reusing Gen45's would not be randomisation.
    pairs = [{"task": t, "repetition": r} for t in ("T1", "T2", "T3", "T4") for r in (1, 2, 3)]
    rng = random.Random(GEN47_ORDER_SEED)
    rng.shuffle(pairs)
    order = []
    for index, pair in enumerate(pairs):
        arms = ["pi_state_control_v1", "pi_harness_state_control_v1"]
        if index % 2:
            arms.reverse()
        for position, arm in enumerate(arms):
            order.append({"index": len(order) + 1, "task": pair["task"],
                          "repetition": pair["repetition"], "arm": arm,
                          "position_in_pair": position + 1})

    (OUT / "preflight.json").write_text(json.dumps(checks, indent=2, sort_keys=True, default=str) + "\n")
    (OUT / "contract.json").write_text(json.dumps(H.contract(), indent=2, sort_keys=True) + "\n")
    (OUT / "gen47_order_manifest.json").write_text(json.dumps(
        {"seed": GEN47_ORDER_SEED, "arms": ["pi_state_control_v1", "pi_harness_state_control_v1"],
         "runs": len(order), "order": order}, indent=2, sort_keys=True) + "\n")
    (OUT / "synthetic_traces.json").write_text(json.dumps(
        {"ordinary": ordinary, "receipt_then_edit": trace_receipt_then_edit(),
         "hidden_verifier_attempt": trace_hidden_verifier_attempt(),
         "digest": H.digest({"ordinary": ordinary})}, indent=2, sort_keys=True) + "\n")

    print(json.dumps({"passed": passed,
                      "control_path": checks["control_loop_runs"]["path"],
                      "python_ts_identical": checks["python_typescript_equivalence"]["summaries_identical"],
                      "arm_b_unchanged": checks["arm_b_unchanged"]["identical"]}, indent=1))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
