#!/usr/bin/env python3
"""Generate arm E from arm C, so the treatment cannot drift.

Arm E is arm C plus one deterministic termination policy and nothing else. It is
generated rather than hand-copied for the same reason arm D was: a hand-edited
copy of a 330-line extension is a place for a silent difference to hide.

Three documented inserts, and no other change to C's text:
  1. the stop-policy module, appended before the arm's entry point;
  2. `stop.observeCall(...)` in the tool_call handler;
  3. `stop.observeResult(...)` in the tool_result handler, and the same guard on
     `before_provider_request` as a second safe boundary.

Nothing the model can see changes. No new instruction, field, tool or token.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "extensions" / "pi_state_control"
ARM_C = EXT / "pi_pilot_harness_state.ts"
ARM_E = EXT / "pi_pilot_quiescent.ts"

STOP_MODULE = '''
/* ---------------------------------------------------------------------------
 * Arm E only: `quiescent-completion-toolcall-k3-v1`.
 *
 * K = 3 comes from the Gen51 offline calibration over 48 recorded runs: the
 * smallest tested K with zero observed progress truncations. It is frozen here
 * and is not tuned during Gen52.
 *
 * The rule sees only what the agent's own tool stream shows. The hidden
 * verifier, the reference fixes and post-hoc correctness are outside this path
 * by construction, and the recognizer is the same frozen one arm C uses.
 *
 * It never kills a tool that is still running. A trigger reached while other
 * calls from the same batch are still outstanding is held until the batch
 * drains, and the overshoot is recorded rather than hidden.
 * ------------------------------------------------------------------------ */
export const STOP_CONTRACT = "quiescent-completion-toolcall-k3-v1";
export const STOP_K = 3;

export class QuiescentStop {
  mutated = false;
  receiptDigest: string | null = null;
  receiptCommand = "";
  sinceReceipt = 0;
  pendingCalls = 0;
  toolIndex = 0;
  lastValidationEvent = "";
  armed = false;
  triggered = false;
  triggerToolIndex: number | null = null;
  effectiveStopToolIndex: number | null = null;
  sameBatchOvershootCalls = 0;
  mutationsBeforeTrigger = 0;
  eligible = false;
  reason = "";

  observeCall(tool: string): void {
    this.toolIndex += 1;
    this.pendingCalls += 1;
    if (MUTATION_TOOLS.has(tool)) {
      this.mutated = true;
      this.mutationsBeforeTrigger += 1;
      this.receiptDigest = null;
      this.sinceReceipt = 0;
    }
  }

  /** Returns true when the run should stop at this boundary. */
  observeResult(validation: any, treeDigest: string): boolean {
    this.pendingCalls = Math.max(0, this.pendingCalls - 1);
    if (this.armed) {
      // The trigger already fired; these are calls the batch had in flight.
      this.sameBatchOvershootCalls += 1;
      return this.pendingCalls === 0 && this.finish();
    }
    // A tree that moved without a mutation tool - a shell heredoc, say - voids
    // the receipt exactly as an edit would.
    if (this.receiptDigest !== null && treeDigest !== this.receiptDigest) {
      this.receiptDigest = null;
      this.sinceReceipt = 0;
      this.mutated = true;
    }
    // `state.validation` is sticky: it keeps describing the last check the run
    // made, so an ordinary tool result carries the previous check's verdict.
    // Only a new `event` ref means a check actually just ran.
    const fresh = validation && validation.event && validation.event !== this.lastValidationEvent;
    if (fresh) this.lastValidationEvent = validation.event;
    const passed = fresh && typeof validation.passed === "boolean" ? validation.passed : null;
    if (passed === true) {
      if (!this.mutated) { this.reason = "check passed before any mutation"; return false; }
      this.receiptDigest = treeDigest;
      this.receiptCommand = validation.command ?? "";
      this.sinceReceipt = 0;
      this.eligible = true;
      return false;
    }
    if (passed === false) {
      this.receiptDigest = null;
      this.sinceReceipt = 0;
      return false;
    }
    if (this.receiptDigest === null) return false;
    this.sinceReceipt += 1;
    if (this.sinceReceipt < STOP_K) return false;
    this.armed = true;
    this.triggerToolIndex = this.toolIndex;
    if (this.pendingCalls > 0) return false;   // a sibling call is still running
    return this.finish();
  }

  private finish(): boolean {
    this.triggered = true;
    this.effectiveStopToolIndex = this.toolIndex;
    this.reason = "quiescent_stop";
    return true;
  }

  summary(): Record<string, unknown> {
    return {
      contract: STOP_CONTRACT, k: STOP_K,
      became_eligible: this.eligible, triggered: this.triggered,
      qualifying_command: this.receiptCommand,
      qualifying_tree_digest: this.receiptDigest,
      trigger_tool_index: this.triggerToolIndex,
      effective_stop_tool_index: this.effectiveStopToolIndex,
      same_batch_overshoot_calls: this.sameBatchOvershootCalls,
      k_count_at_stop: this.sinceReceipt,
      mutations_before_trigger: this.mutationsBeforeTrigger,
      reason: this.reason,
    };
  }
}
'''

INSERT_CALL = """    stop.observeCall(tool);
"""

INSERT_RESULT = """    if (stop.observeResult(derivation.state.validation, derivation.state.tree_digest)) {
      writeFileSync(join(OUT, "quiescent_stop.json"), canonical(stop.summary()));
      ctx?.abort?.();
    }
"""


def generate() -> str:
    source = ARM_C.read_text()

    header = ("/**\n * Gen52 arm E: arm C plus `quiescent-completion-toolcall-k3-v1`, "
              "and nothing else.\n *\n * GENERATED from `pi_pilot_harness_state.ts` by "
              "`scripts/build_pi_pilot_gen52_quiescent.py`.\n * Do not edit this file; edit the "
              "generator or arm C.\n */\n")

    # 1. the stop module, immediately before the arm entry point
    anchor = "export default function harnessArm(pi: any) {"
    assert source.count(anchor) == 1
    source = source.replace(anchor, STOP_MODULE + "\n" + anchor.replace("harnessArm", "quiescentArm"))
    source = header + source

    # instantiate the policy alongside the derivation
    anchor = "  const derivation = new Derivation();\n"
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + "  const stop = new QuiescentStop();\n")

    # 2. observe every tool call
    anchor = '    derivation.toolCall(tool, event.input ?? {}, ref);\n'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + INSERT_CALL)

    # 3. observe every tool result, and stop at the safe boundary
    anchor = ('    line("derivation.ndjson", { ref, kind: "tool_result", command,\n'
              '      phase: derivation.state.phase, validation: derivation.state.validation });\n'
              "    persist();\n")
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + INSERT_RESULT)

    # the handlers need the context argument the runner already passes
    source = source.replace('pi.on("tool_call", (event: any) => {',
                            'pi.on("tool_call", (event: any, ctx: any) => {')
    source = source.replace('pi.on("tool_result", (event: any) => {',
                            'pi.on("tool_result", (event: any, ctx: any) => {')

    # a second safe boundary: never issue a new provider request once armed
    anchor = ('  pi.on("before_provider_request", (event: any) => {\n'
              '    line("payloads.ndjson", { bytes: JSON.stringify(event.payload ?? null).length });\n'
              "  });\n")
    assert source.count(anchor) == 1
    replacement = ('  pi.on("before_provider_request", (event: any, ctx: any) => {\n'
                   '    if (stop.armed) {\n'
                   '      writeFileSync(join(OUT, "quiescent_stop.json"), canonical(stop.summary()));\n'
                   '      ctx?.abort?.();\n'
                   '      return;\n'
                   '    }\n'
                   '    line("payloads.ndjson", { bytes: JSON.stringify(event.payload ?? null).length });\n'
                   "  });\n")
    source = source.replace(anchor, replacement)

    # the summary must survive a run that never triggered
    anchor = '  pi.on("session_shutdown", () => {\n    derivation.sessionEnd(nextRef());\n    persist();\n'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor +
                            '    writeFileSync(join(OUT, "quiescent_stop.json"), canonical(stop.summary()));\n')
    return source


if __name__ == "__main__":
    text = generate()
    ARM_E.write_text(text)
    print(f"{ARM_E.name} {hashlib.sha256(text.encode()).hexdigest()}")
    print(f"{ARM_C.name} {hashlib.sha256(ARM_C.read_bytes()).hexdigest()}")
