#!/usr/bin/env python3
"""Render the Gen45 live pilot report from the committed leaves."""
from __future__ import annotations

import hashlib, json, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen45"
VOLATILE = {"wall_seconds", "wall_seconds_median", "generated_at", "host", "path", "install_path",
            "executed_on", "isolated_agent_dir"}


def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in sorted(obj.items()) if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def main() -> int:
    agg = json.loads((OUT / "aggregate.json").read_text())
    pairs = json.loads((OUT / "pairs.json").read_text())
    smoke = json.loads((OUT / "compatibility_smoke.json").read_text())
    seed = json.loads((OUT / "seed_policy.json").read_text())
    ident = json.loads((OUT / "execution_identity.json").read_text())

    A, B = agg["by_arm"]["pi_default_v1"], agg["by_arm"]["pi_state_control_v1"]
    leaves = agg["leaves"]

    task_rows = "\n".join(
        f"| {t} | {agg['by_task'][t]['pi_default_v1']['verifier_passes']}/3 | "
        f"{agg['by_task'][t]['pi_default_v1']['request_bytes_median']:,} | "
        f"{agg['by_task'][t]['pi_state_control_v1']['verifier_passes']}/3 | "
        f"{agg['by_task'][t]['pi_state_control_v1']['request_bytes_median']:,} | "
        f"{agg['by_task'][t]['pi_state_control_v1']['timeouts']} |"
        for t in ("T1", "T2", "T3", "T4"))

    pair_rows = "\n".join(
        f"| {p['task']} r{p['repetition']} | {'pass' if p['A']['verifier_passed'] else 'FAIL'} "
        f"({p['A']['request_bytes_total']:,}B) | {'pass' if p['B']['verifier_passed'] else 'FAIL'} "
        f"({p['B']['request_bytes_total']:,}B{', timeout' if p['B']['status'] == 'timeout' else ''}) | "
        f"{p['bytes_delta_b_minus_a']:+,} |" for p in pairs)

    def trajectory(task: str, arm: str) -> tuple[int, int, int]:
        leaf = next(f for f in sorted((OUT / "runs").glob("*/leaf.json"))
                    if json.loads(f.read_text())["slot"]["task"] == task
                    and json.loads(f.read_text())["slot"]["arm"] == arm)
        series = json.loads(leaf.read_text())["measured"]["request_bytes_by_turn"]
        return len(series), series[0], series[-1]

    traj_rows = "\n".join(
        f"| {task} | {arm.replace('pi_', '').replace('_v1', '')} | {n} | {first:,} | {last:,} | "
        f"{last / first:.1f}x |"
        for task in ("T1", "T3")
        for arm in ("pi_default_v1", "pi_state_control_v1")
        for n, first, last in [trajectory(task, arm)])

    control = agg["arm_b_control_totals"]
    digest = hashlib.sha256(P.canonical(strip({"aggregate": agg, "pairs": pairs, "smoke": smoke,
                                               "seed": seed, "identity": ident})).encode()).hexdigest()

    doc = f"""# The first live paired Pi coding pilot

**Evidence class:** `architecture_pilot_paired_live`. Four invented tasks, two arms, three
repetitions, 24 runs, one local model. This is a mechanism pilot, not a coding benchmark and not
a model result. Nothing here generalises past these four tasks.

**The headline is negative, and the reason is not the one the design anticipated.** Arm B —
bounded composed context plus executable control — passed {B['verifier_passes']} of
{B['runs']} verifiers against arm A's {A['verifier_passes']} of {A['runs']}, and used *more*
cumulative context, not less. But the mechanism underneath is more interesting than the score,
and it splits cleanly in two.

## What ran

{ident['model']['name']} {ident['model']['quantization']}, sha256
`{ident['model']['sha256'][:16]}…`, on {ident['server']['device']}, server
{ident['server']['version_line']}, sampling temp {ident['sampling']['temperature']} / top_p
{ident['sampling']['top_p']} / top_k {ident['sampling']['top_k']}, reasoning
`{ident['reasoning']}`, context {ident['context_window']:,}. Pi 0.73.0 in an isolated agent
directory — {ident['pi']['why_isolated']}.

Every run: fresh worktree reset to the frozen tree, fresh Pi session, serial, {ident['run_timeout_seconds']}s
timeout, network offline apart from the local endpoint.

## Seed policy: no seed, so these are samples

{seed['consequence']}

Pi 0.73.0 exposes no seed anywhere in its provider or stream options, and the only injection point
would have put an extension in front of arm A's requests, which is exactly the baseline
contamination the rule forbids. **Every comparison below is between stochastic samples.** With
three per cell, a one-run difference is not a finding; a three-for-three pattern is worth naming.

## Compatibility smoke

Passed on the third attempt. The first two failures were mine, not the model's: the composed view
never showed the `state_revision` the patch protocol requires nor which fields were patchable, and
the rejection message named the fault without naming the remedy. Both were fixed before any frozen
task was exposed, and a cap was declared before the third attempt — one more repair, then publish
`compatibility_blocked`. No exposed `thinking`, `reasoning` or `reasoning_content` field appeared
in either arm's captured stream; that is a statement about exposed fields, not about hidden
internal reasoning.

## Result

| | arm A `pi_default_v1` | arm B `pi_state_control_v1` |
| --- | --- | --- |
| verifier passes | **{A['verifier_passes']}/{A['runs']}** | **{B['verifier_passes']}/{B['runs']}** |
| timeouts | {A['timeouts']} | {B['timeouts']} |
| request bytes, median | {A['request_bytes_median']:,} | {B['request_bytes_median']:,} |
| request bytes, mean | {A['request_bytes_mean']:,} | {B['request_bytes_mean']:,} |
| requests, median | {A['request_count_median']} | {B['request_count_median']} |
| tool calls, median | {A['tool_calls_median']} | {B['tool_calls_median']} |
| repeated or redundant calls, median | {A['churn_total_median']} | {B['churn_total_median']} |

By task, verifier passes and median cumulative request bytes:

| task | A passes | A bytes | B passes | B bytes | B timeouts |
| --- | --- | --- | --- | --- | --- |
{task_rows}

Every pair, because averaging away the failures would hide the whole story:

| pair | A | B | bytes delta |
| --- | --- | --- | --- |
{pair_rows}

{agg['pairs_with_same_outcome']} of 12 pairs agreed on outcome.

## The mechanism: per-request context is bounded, total work is not

This is the finding worth keeping.

| task | arm | requests | first request | last request | growth |
| --- | --- | --- | --- | --- | --- |
{traj_rows}

Arm A's request grows steeply with the run because the transcript is replayed — on T3, 208 bytes
to 43,477, a 209-fold increase over six requests. Arm B's does not: 1,538 to 4,074 over
**337 requests**. The bounded view works exactly as designed.

And that is why arm B loses. Its per-request context is flat, but it needs far more requests,
because each one starts from a composed view with a higher floor (about 1.5 KB against arm A's
200 bytes) and no memory of what the previous turns established beyond two interaction units and
the state the model bothered to write down. On T3 that becomes a loop: 337 requests, 591 tool
calls, 900 seconds, timeout, three times out of three.

So **H2 is supported and H1 is falsified at the same time**, and they are not in conflict: bounding
the size of each request did not bound the size of the run.

## The half of the treatment that never ran

Across all twelve arm B runs:

| control quantity | total |
| --- | --- |
| state patches accepted | {control['patches_accepted']} |
| state patches rejected | {control['patches_rejected']} |
| **transitions accepted** | **{control['transitions_accepted']}** |
| transitions rejected | {control['transitions_rejected']} |
| completions blocked by the artifact gate | {control['blocked_completions']} |
| artifact revalidations | {control['artifact_revalidations']} |
| Pi compactions cancelled | {control['compaction_cancelled']} |

Every one of the twelve runs ended in phase `inspect`. The model never requested a transition,
never recorded a receipt, and therefore never reached the completion gate. Six accepted patches
across twelve runs is the entire use it made of the control layer.

This has to change how the rest is read. Arm B as executed was **not** "state and control"; it was
a bounded context window plus three tools the model largely ignored. Its failures cannot be
attributed to control gating, because nothing was ever gated. H5 is untested rather than
supported: the artifact gate never fired because no completion was ever attempted through it.

Pi's own compaction never triggered either — these runs are far too short to reach it — so that
part of the treatment boundary was also inert.

## Hypotheses

- **H1 — B materially reduces cumulative request bytes.** Falsified here. B's median is
  {B['request_bytes_median']:,} against A's {A['request_bytes_median']:,}, and its mean is five
  times A's because of the T3 loops.
- **H2 — B reduces the growth of request size with run length.** Supported, strongly: 2.6x over
  337 requests against 209x over six.
- **H3 — B does not reduce success so far that the architecture is unusable.** Not met as
  configured. {B['verifier_passes']}/12 against 12/12.
- **H4 — churn direction, exploratory.** B's median repeated-or-redundant calls is
  {B['churn_total_median']} against {A['churn_total_median']}; on T3 it is dominated by the loops.
- **H5 — the artifact gate prevents unearned completion.** Untested. No completion was attempted
  through the control layer.
- **H6 — a failure caused by missing older context is a first-class result.** Taken literally.
  T2 failed 0/3 while using *half* arm A's bytes and making zero repository mutations in the run
  inspected — it never made the coordinated edit. T3 looped. Neither the window nor the caps were
  touched afterwards.

## What this does and does not say

It says that this specific composition — two interaction units, a 4 KB state the model must
maintain by hand, and three tools it did not reach for — is not sufficient for this model on these
four tasks, and that bounding per-request context does not by itself bound the work.

It does not say the architecture is wrong. The control layer was never exercised, so it was never
tested. It does not say anything about a different model, a larger window, or a design where state
is written by the harness rather than volunteered by the model. Four tasks, three stochastic
samples each, one local 35B model at temperature 0.6.

Scientific digest `{digest}`, rebuilt with wall clock, cache warmth and host-local paths excluded.
"""
    (ROOT / "research" / "PI_STATE_CONTROL_GEN45_LIVE_PILOT.md").write_text(doc)
    (OUT / "scientific_digest.txt").write_text(digest + "\n")
    print("wrote report, digest", digest[:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
