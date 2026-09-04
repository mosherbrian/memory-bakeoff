#!/usr/bin/env python3
"""Render the Gen46 design report."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import harness_state as H  # noqa: E402
from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen46"
VOLATILE = {"generated_at", "host", "digest"}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in sorted(o.items()) if k not in VOLATILE}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def main() -> int:
    pre = json.loads((OUT / "preflight.json").read_text())
    contract = json.loads((OUT / "contract.json").read_text())
    order = json.loads((OUT / "gen47_order_manifest.json").read_text())
    gen45 = json.loads((ROOT / "results/pi_state_control_gen45/aggregate.json").read_text())

    transitions = "\n".join(f"| `{a}` | {', '.join(f'`{b}`' for b in bs)} |"
                            for a, bs in contract["automatic_transitions"].items())
    path = " → ".join([pre["control_loop_runs"]["path"][0][0]] +
                      [step[1] for step in pre["control_loop_runs"]["path"]])
    # Some blocks are supposed to contain False - "the hidden verifier was not
    # classified as a check" is the desired answer - so the table shows the
    # booleans rather than collapsing them into a verdict that would misread them.
    checks = "\n".join(
        f"| {name.replace('_', ' ')} | "
        + ", ".join(f"{k}={str(v).lower()}" for k, v in sorted(block.items()) if isinstance(v, bool))
        + " |"
        for name, block in sorted(pre.items())
        if isinstance(block, dict) and any(isinstance(v, bool) for v in block.values()))

    digest = hashlib.sha256(H.canonical(strip({"pre": pre, "contract": contract, "order": order})).encode()).hexdigest()

    doc = f"""# Harness-maintained state and control: the Gen47 ablation, frozen

**Evidence class:** `architecture_state_control_ablation_design_no_score`. No model, no GPU, no
network. Synthetic event logs only.

Gen45 produced a negative result for the model-maintained arm, but it also showed *why* the result
cannot be read as a test of the architecture: across all twelve runs the control layer accepted
**{gen45['arm_b_control_totals']['transitions_accepted']} transitions**, reached the completion
gate {gen45['arm_b_control_totals']['blocked_completions']} times, and every run ended in phase
`inspect`. The model did not adopt the three tools, so there was no control loop to evaluate.

Gen46 removes that dependency and freezes the arm that tests the architecture's actual claim.

## The change, and only this change

Arm **C** `pi_harness_state_control_v1` keeps arm B's composer, caps, history treatment and
compaction handling **exactly**, and changes one thing: the state and the phase are derived by the
harness from ordinary visible tool events instead of waiting for the model to call unfamiliar
tools. C does not offer the three state/control tools at all — their non-adoption is the mechanism
being removed, so keeping them for symmetry would defeat the point.

Deliberately **not** changed, and recorded as deferred rather than quietly folded in:
{', '.join(f"`{d}`" for d in pre['composer_unchanged']['deferred_hypotheses'])}. The task-prompt
floor is a real suspect from Gen45 and it stays a separate experiment.

## The derivation contract, `{contract['derivation_version']}`

The line this design will not cross is semantic interpretation. It records what was observed —
files read, the repository changed, a visible check run and its exit status — and never what any of
it means. No inferred cause, no plan, no next action. If a field would need a model to fill it in,
it is not in the state.

| from | automatic next |
| --- | --- |
{transitions}

Rules: two inspection calls leave `inspect`; the first repository mutation enters `implement`; a
recognised visible check after a mutation enters `validate`; a failed check returns to `implement`;
a mutation after a passing check **invalidates the receipt** and returns to `implement`; `done` is
recorded only if a passing receipt still matches the current tree digest at session end.

Validation commands are classified by a frozen pattern family drawn from the fixtures' own public
tooling — pytest, unittest, `run_checks.py` — and the hidden verifier is excluded by name in
`FORBIDDEN_IN_VALIDATION`, so a run that invokes it gets no receipt at all.

State is bounded exactly as before: {contract['state_byte_cap']:,} bytes, the last
{contract['recent_files_bound']} files read or modified, the last {contract['checkpoint_bound']}
objective checkpoints, which may only be one of
{', '.join(f"`{c}`" for c in contract['objective_checkpoints'])}.

## Preflight

| check | result |
| --- | --- |
{checks}

The control loop the model never drove now runs on its own: on the ordinary synthetic trace the
phase path is **{path}**, {pre['control_loop_runs']['transitions_accepted']} transitions accepted,
ending with a receipt valid for the current tree.

Three results are worth naming individually.

**Receipt invalidation works.** A passing check followed by another edit produces one receipt, one
invalidation, no valid receipt at the end, and a return to `implement`. Artifacts still outrank
state, and now they do so without the model's cooperation.

**The hidden verifier cannot become a receipt.** `python ../verifier.py` is not classified as a
validation command, produces no receipt, and leaves the phase in `implement`, while
`python -m pytest` is classified normally.

**The Python contract and the TypeScript arm agree byte for byte.** The same synthetic event log
replayed through `harness_state.py` and through the extension that will actually run in Gen47
produces identical summaries. That is the check that stops the frozen contract and the live code
drifting apart between generations.

Arm B is untouched: its extension still hashes to the value Gen45 recorded
(`{pre['arm_b_unchanged']['recorded_sha256'][:16]}…`).

## What Gen47 would run

{order['runs']} runs, {order['arms'][0]} against {order['arms'][1]}, on the same frozen T1–T4
tasks, three stochastic samples per cell, serial, fresh worktree and session each time, at the
Gen45 model identity and sampling. A **new** order seed, {order['seed']}, because reusing Gen45's
ordering would not be randomisation. Same 900 s timeout, same retry policy, same hidden verifier,
plus direct adoption metrics: for B, each tool offered, called, accepted, rejected and its
first-call turn; for C, harness-derived updates, automatic transitions, receipts and invalidations
with their source events.

Gen47 needs Brian's authorization again. Gen45's does not carry over.

## What this can and cannot show

If C exercises the loop on every run — which the preflight says it will, because it is event-driven
— then a difference between B and C is about *maintenance of state*, not about whether the model
volunteers to maintain it. If C still fails T2 and T3 the way B did, the bounded composer becomes
the leading suspect and the deferred task-prompt floor gets its own experiment.

What it cannot show is which part of the bundle did the work. C changes maintenance and removes
three tools at once. That is stated here rather than discovered later.

Contract `src/memory_bakeoff/pi_state_control/harness_state.py`, sha256
`{contract['contract_sha256']}`. Design digest `{digest}`.
"""
    (ROOT / "research" / "PI_STATE_CONTROL_GEN46_HARNESS_STATE_DESIGN.md").write_text(doc)
    (OUT / "design_digest.txt").write_text(digest + "\n")
    print("wrote report, digest", digest[:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
