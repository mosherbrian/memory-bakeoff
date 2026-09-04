#!/usr/bin/env python3
"""Render the Gen44 pilot design report."""
from __future__ import annotations

import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402

OUT = ROOT / "results" / "pi_state_control_gen44"
VOLATILE = {"wall_seconds", "generated_at", "install_path", "host", "config_path", "repo_path",
            "verifier_path", "binary", "path"}


def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in sorted(obj.items()) if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def main() -> int:
    ident = json.loads((OUT / "model_candidate_identity.json").read_text())
    contract = json.loads((OUT / "pilot_contract.json").read_text())
    tasks = json.loads((OUT / "task_manifest.json").read_text())
    pre = json.loads((OUT / "preflight.json").read_text())
    arms = json.loads((OUT / "pi_arm_verification.json").read_text())
    order = json.loads((OUT / "order_manifest.json").read_text())

    digest = hashlib.sha256(P.canonical(strip({
        "identity": ident, "contract": contract, "tasks": tasks,
        "preflight": pre, "arms": arms, "order": order})).encode()).hexdigest()

    task_rows = "\n".join(
        f"| {tid} | {t['title']} | {t['file_count']} | `{t['git_tree_digest'][:12]}` | "
        f"{t['solvable']['verifier_fails_on_initial_tree']} | "
        f"{t['solvable']['verifier_passes_after_reference_fix']} |"
        for tid, t in sorted(tasks["tasks"].items()))
    pressure_rows = "\n".join(f"- **{tid}** — {t['pressure']}" for tid, t in sorted(tasks["tasks"].items()))
    risk_rows = "\n".join(f"{i}. {risk}" for i, risk in enumerate(ident["open_risks_for_gen45"], start=1))
    check_rows = "\n".join(f"| {name.replace('_', ' ')} | {value} |"
                           for name, value in sorted(arms["checks"].items()))

    doc = f"""# The first paired Pi coding pilot: design, frozen

**Evidence class:** `{contract['evidence_class']}`. Nothing here was run against a model. No
inference, no GPU, no hosted API, no network during the preflight — the last of those is proved
by blocking the socket layer and attempting a connection, not asserted.

Gen43 showed the architecture is mechanically implementable on Pi. Gen44 turns it into an
experiment that can be run once and read honestly: arms, composition, tasks, measurements, order
and model identity are all frozen and digested **before** any live run exists.

## The model candidate, pinned without generating a token

| field | value |
| --- | --- |
| served alias | `{ident['served_alias']}` |
| model | {ident['model']['name']}, {ident['model']['quantization']} |
| model file | {ident['model']['bytes']:,} bytes, sha256 `{ident['model']['sha256'][:24]}…` |
| architecture | {ident['model']['architecture']}, GGUF v{ident['model']['gguf_version']}, {ident['model']['tensor_count']} tensors |
| chat template | embedded, applied via `--jinja`, sha256 `{ident['model']['chat_template']['sha256'][:24]}…` |
| server | {ident['inference_server']['version_line']}, {ident['inference_server']['backend']} |
| device | {ident['inference_server']['device']} |
| context | {ident['runtime_flags']['ctx_size']:,} tokens, reasoning `{ident['runtime_flags']['reasoning']}` |
| sampling | temp {ident['runtime_flags']['sampling']['temperature']}, top_p {ident['runtime_flags']['sampling']['top_p']}, top_k {ident['runtime_flags']['sampling']['top_k']}, min_p {ident['runtime_flags']['sampling']['min_p']} |
| router | {ident['router']['software']} on {ident['router']['listen']}, TTL {ident['router']['ttl_seconds']}s |

Status **{ident['status']}**. Everything above comes from the on-disk config, the GGUF header,
the binary's own `--version` and `--list-devices`, and the running unit. The server was never
started for this generation.

### Risks Brian should see before authorising Gen45

{risk_rows}

The first one is the one I would not proceed past quietly. A paired design with three
repetitions per cell assumes the repetitions mean something; at temperature 0.6 with no pinned
seed they are samples, not reproductions. That is survivable — it just has to be *decided*, and
said out loud in the report, rather than discovered afterwards.

## Arms

**A `pi_default_v1`** — stock Pi context and history, its own compaction enabled, ordinary coding
tools, no extension touching the request.

**B `pi_state_control_v1`** — the Gen43 lineage: composed context replaces transcript replay,
history is externalized losslessly, Pi's compaction is cancelled, control gates completion on a
validated artifact, and three tools exist to drive state and control.

The treatment is that whole bundle:

{chr(10).join(f"- {component}" for component in contract['treatment_components'])}

Arm B is not "arm A with fewer bytes", and this report will not pretend otherwise. Four tasks
cannot attribute a difference to any single component of that bundle.

There is no arm C. On-demand historical retrieval is a later ablation; first find out whether B
is sufficient without it.

## What B sends, frozen now

Composition order: {', '.join(f'`{c}`' for c in contract['composition']['order'])}.

Caps: state {contract['composition']['state_byte_cap']:,} bytes (inherited from Gen43), recent
window {contract['composition']['recent_window_units']} complete interaction units under
{contract['composition']['recent_window_byte_cap']:,} bytes, latest observation
{contract['composition']['latest_observation_byte_cap']:,} bytes. Overflow stays in history with a
stable reference; nothing is deleted.

The unit rule is mechanical rather than a matter of judgement, because Gen43's one-message
composition was too brittle to assume for a real model:

> {contract['composition']['interaction_unit_rule']}

That rule is tested against fixtures, including the orphan case of messages that precede the
first user turn.

## Both arms verified inside the installed Pi

Handed a synthetic transcript of {arms['arm_a']['incoming_messages']} messages and
{arms['arm_a']['incoming_bytes']:,} bytes:

| check | result |
| --- | --- |
{check_rows}

Arm A passed {arms['arm_a']['incoming_bytes']:,} bytes through untouched and returned no
replacement, so the baseline is genuinely stock Pi with instrumentation beside it rather than in
front of it. Arm B returned {arms['arm_b']['replacement_messages']} messages of
{arms['arm_b']['replacement_bytes']:,} bytes. Pi {arms['pi_version']}, core patched
{str(arms['core_patched']).lower()}.

## Tasks

Four invented fixture repositories, unrelated to every corpus here and to the Gen43 trace.

| task | shape | files | frozen tree | fails before | passes after reference fix |
| --- | --- | --- | --- | --- | --- |
{task_rows}

What each one puts pressure on:

{pressure_rows}

Each task was proved solvable here, without a model, by applying a reference fix that lives only
in the builder script. It is never written into a fixture tree, never appears in a prompt, and is
not committed anywhere the agent can reach. The hidden verifier sits beside the repository, not
inside it — the preflight checks that the agent cannot see the verifier
({pre['task_isolation']['verifier_never_inside_repo']}) and that neither the repository nor the
prompt names it ({pre['task_isolation']['verifier_never_named_to_the_agent']}).

## Measurements, frozen

Primary: {contract['primary_outcome']}.

Co-primary: {', '.join(contract['co_primary_outcomes'])}.

Churn is defined before it is counted, because a definition settled after the fact can be bent:

{chr(10).join(f"- **{name.replace('_', ' ')}** — {text}" for name, text in contract['churn_definitions'].items())}

The definitions deliberately overlap. A verifier re-run after an edit is an exact repeat but not
a redundant invocation, and both counts are reported rather than merged. The counters were
checked against a hand-written log whose expected numbers were written down first
({pre['churn_counters']['match']} for the match).

Termination is classified separately from task success, because artifact-gated completion will
produce runs that stop short rather than declare victory:

{chr(10).join(f"- **{name.replace('_', ' ')}** — {text}" for name, text in contract['termination_classes'].items())}

## Run plan

{contract['run_plan']['runs']} runs: {len(contract['run_plan']['tasks'])} tasks x
{contract['run_plan']['repetitions']} repetitions x 2 arms, serial, fresh worktree and fresh Pi
session each time. Order is deterministic from seed {order['seed']}, arms paired on task and
repetition, adjacent within a pair, with the first position counterbalanced
({pre['order']['counterbalanced_first_position']}) so arm order cannot align with machine drift
or cache warmth.

## Reading rules, agreed in advance

{chr(10).join(f"- {rule}" for rule in contract['reading_rules'])}

Hypotheses are directional only: {'; '.join(f"{k}: {v}" for k, v in contract['hypotheses'].items())}.

## Preflight

Passed: **{pre['passed']}**. Composition caps respected, arm A carries no extra tools, all four
tasks isolated and solvable, worktree reset returns to the frozen tree, order deterministic and
counterbalanced, Gen43's state/control guarantees still hold under the pilot caps — completion
earned from a receipt, state surviving restart, artifact mutation invalidating completion — churn
counters matching the hand-checked log, both Pi arms verified, and outbound network blocked.

## What Gen45 needs from Brian

1. Authorization to run 24 live coding-agent runs against the local Strix Halo server.
2. A decision on the seed question above: pin a per-request seed if the path allows it, or accept
   repetitions as samples and say so in the result.
3. Acceptance that tool-call formatting under this chat template is unverified until the first
   live run, and that a format incompatibility is a plausible early blocker rather than a result.

One operational note: Pi and the inference server are both on the Linux workstation, while this
repository lives on the Mac. Gen45 has to run on Linux, so the fixtures and harness need to be
present there before the first run.

Contract `src/memory_bakeoff/pi_state_control/pilot.py`, sha256 `{contract['contract_sha256']}`.
Design digest `{digest}`, rebuilt with wall-clock and machine-local paths excluded.
"""
    out = ROOT / "research" / "PI_STATE_CONTROL_GEN44_PILOT_DESIGN.md"
    out.write_text(doc)
    (OUT / "design_digest.txt").write_text(digest + "\n")
    print("wrote", out.relative_to(ROOT), "digest", digest[:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
