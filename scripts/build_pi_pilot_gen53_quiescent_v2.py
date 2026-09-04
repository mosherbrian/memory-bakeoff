#!/usr/bin/env python3
"""Generate the v2 stop arm from arm C, so the treatment cannot drift.

Gen52's v1 arm is left exactly as it is. Its hash is recorded evidence for that
generation and rewriting it would rewrite history, so this is a new file.

Two rule changes, both forced by what Gen52 measured live:
  * a run whose tree is back at its starting digest is never quiescent-complete;
  * a pass on a tree that already holds a valid receipt is an idle action, not
    a re-arm.

And one evidence repair: the quiescence snapshot is written on every tool
result, atomically, rather than only at a stop or a clean shutdown. Gen52 lost
that summary for its one timeout because the process was killed first.

The semantics mirror `quiescent_v2.py` exactly; the preflight replays the same
synthetic traces through both and requires them to agree.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "extensions" / "pi_state_control"
ARM_C = EXT / "pi_pilot_harness_state.ts"
ARM_V2 = EXT / "pi_pilot_quiescent_v2.ts"

STOP_MODULE = '''
/* ---------------------------------------------------------------------------
 * `quiescent-completion-toolcall-v2`, the Gen52 repair.
 *
 * v1 stopped a run that had reverted its own correct fix, because it asked only
 * whether a mutation had happened and never whether the tree had changed. And
 * it never stopped a run that ran the same passing test 144 times, because each
 * pass re-armed the receipt and reset the count.
 *
 * So: a tree back at its starting digest is never complete, and a pass on a
 * tree that already holds a receipt is an idle action. Nothing else changes.
 *
 * The hidden verifier is outside this path by construction, and the recognizer
 * is arm C's own. A tool that is still running is never killed.
 * ------------------------------------------------------------------------ */
export const STOP_CONTRACT = "quiescent-completion-toolcall-v2";
export const STOP_K = 3;

export class QuiescentStopV2 {
  initialTree = "";
  currentTree = "";
  mutated = false;
  receiptTree: string | null = null;
  receiptIndex: number | null = null;
  idle = 0;
  toolIndex = 0;
  pendingCalls = 0;
  armed = false;
  triggered = false;
  triggerToolIndex: number | null = null;
  effectiveStopToolIndex: number | null = null;
  sameBatchOvershootCalls = 0;
  mutations = 0;
  sameTreePassesCountedIdle = 0;
  becameEligible = false;
  lastValidationEvent = "";
  lastVisibleCheckPassed: boolean | null = null;
  reason = "";

  netTreeChanged(): boolean {
    return Boolean(this.currentTree) && this.currentTree !== this.initialTree;
  }

  eligible(): boolean {
    return this.mutated && this.netTreeChanged()
      && this.receiptTree !== null && this.receiptTree === this.currentTree;
  }

  observeCall(tool: string): void {
    this.toolIndex += 1;
    this.pendingCalls += 1;
    if (MUTATION_TOOLS.has(tool)) {
      this.mutated = true;
      this.mutations += 1;
      this.invalidate();
    }
  }

  observeResult(validation: any, treeDigest: string): boolean {
    this.pendingCalls = Math.max(0, this.pendingCalls - 1);
    if (treeDigest) {
      if (!this.initialTree) this.initialTree = treeDigest;
      if (this.currentTree && treeDigest !== this.currentTree) {
        this.invalidate();      // the tree moved without a mutation tool
        this.mutated = true;
      }
      this.currentTree = treeDigest;
    }

    if (this.armed) {
      this.sameBatchOvershootCalls += 1;
      return this.pendingCalls === 0 && this.finish();
    }

    // `state.validation` is sticky, so only a new `event` ref means a check ran.
    const fresh = validation && validation.event && validation.event !== this.lastValidationEvent;
    if (fresh) this.lastValidationEvent = validation.event;
    const passed = fresh && typeof validation.passed === "boolean" ? validation.passed : null;
    if (passed !== null) this.lastVisibleCheckPassed = passed;

    if (passed === false) {
      this.invalidate();
      return false;
    }
    if (passed === true) {
      if (this.receiptTree !== null && this.receiptTree === this.currentTree) {
        this.sameTreePassesCountedIdle += 1;
        this.idle += 1;
      } else {
        this.receiptTree = this.currentTree;
        this.receiptIndex = this.toolIndex;
        this.idle = 0;
        if (this.eligible()) this.becameEligible = true;
        return false;
      }
    } else if (this.receiptTree !== null) {
      this.idle += 1;
    }

    if (!this.eligible()) return false;
    this.becameEligible = true;
    if (this.idle < STOP_K) return false;
    this.armed = true;
    this.triggerToolIndex = this.toolIndex;
    if (this.pendingCalls > 0) return false;
    return this.finish();
  }

  private invalidate(): void {
    this.receiptTree = null;
    this.receiptIndex = null;
    this.idle = 0;
  }

  private finish(): boolean {
    this.triggered = true;
    this.effectiveStopToolIndex = this.toolIndex;
    this.reason = "quiescent_stop";
    return true;
  }

  snapshot(): Record<string, unknown> {
    return {
      contract: STOP_CONTRACT, k: STOP_K,
      initial_tree_digest: this.initialTree,
      current_tree_digest: this.currentTree,
      net_tree_changed: this.netTreeChanged(),
      valid_receipt_tree: this.receiptTree,
      valid_receipt_tool_index: this.receiptIndex,
      idle_count: this.idle,
      eligible: this.eligible(),
      became_eligible: this.becameEligible,
      mutations: this.mutations,
      same_tree_passes_counted_idle: this.sameTreePassesCountedIdle,
      last_visible_check_passed: this.lastVisibleCheckPassed,
      triggered: this.triggered,
      trigger_tool_index: this.triggerToolIndex,
      effective_stop_tool_index: this.effectiveStopToolIndex,
      same_batch_overshoot_calls: this.sameBatchOvershootCalls,
      tool_index: this.toolIndex,
      reason: this.reason,
    };
  }
}
'''

# Written on every tool result, and atomically, so a killed process still leaves
# a readable, internally consistent snapshot. This is the Gen52 evidence gap.
PERSIST = '''  const persistStop = () => {
    const target = join(OUT, "quiescent_stop.json");
    const staging = join(OUT, `.quiescent_stop.json.${process.pid}`);
    writeFileSync(staging, canonical(stop.snapshot()));
    renameSync(staging, target);
  };
'''


def generate() -> str:
    source = ARM_C.read_text()
    header = ("/**\n * Gen53 arm E-v2: arm C plus `quiescent-completion-toolcall-v2`.\n *\n"
              " * GENERATED from `pi_pilot_harness_state.ts` by\n"
              " * `scripts/build_pi_pilot_gen53_quiescent_v2.py`. Do not edit this file;\n"
              " * edit the generator or arm C.\n */\n")

    anchor = "export default function harnessArm(pi: any) {"
    assert source.count(anchor) == 1
    source = header + source.replace(anchor, STOP_MODULE + "\n"
                                     + anchor.replace("harnessArm", "quiescentV2Arm"))

    source = source.replace('import { appendFileSync, mkdirSync, rmSync, writeFileSync } from "node:fs";',
                            'import { appendFileSync, mkdirSync, renameSync, rmSync, writeFileSync } from "node:fs";')

    anchor = "  const derivation = new Derivation();\n"
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + "  const stop = new QuiescentStopV2();\n")

    # The initial tree must be the tree BEFORE the agent's first action. Taking it
    # from the first tool result is too late: if that first action is a mutation,
    # the "initial" tree is already the mutated one, and a later revert to the real
    # starting point would not be recognised.
    anchor = "  const persist = () => writeFileSync(join(OUT, \"harness_state.json\"),\n"
    assert source.count(anchor) == 1
    source = source.replace(anchor,
                            "  stop.initialTree = treeDigest();\n"
                            "  stop.currentTree = stop.initialTree;\n\n" + anchor)

    assert source.count(anchor) == 1
    source = source.replace(anchor, PERSIST + "\n" + anchor)

    anchor = '    derivation.toolCall(tool, event.input ?? {}, ref);\n'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + "    stop.observeCall(tool);\n")

    anchor = ('    line("derivation.ndjson", { ref, kind: "tool_result", command,\n'
              '      phase: derivation.state.phase, validation: derivation.state.validation });\n'
              "    persist();\n")
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor +
                            "    const stopNow = stop.observeResult(derivation.state.validation,\n"
                            "                                       derivation.state.tree_digest);\n"
                            "    persistStop();   // every result, not only at a stop\n"
                            "    if (stopNow) ctx?.abort?.();\n")

    source = source.replace('pi.on("tool_call", (event: any) => {',
                            'pi.on("tool_call", (event: any, ctx: any) => {')
    source = source.replace('pi.on("tool_result", (event: any) => {',
                            'pi.on("tool_result", (event: any, ctx: any) => {')

    anchor = ('  pi.on("before_provider_request", (event: any) => {\n'
              '    line("payloads.ndjson", { bytes: JSON.stringify(event.payload ?? null).length });\n'
              "  });\n")
    assert source.count(anchor) == 1
    source = source.replace(anchor,
                            '  pi.on("before_provider_request", (event: any, ctx: any) => {\n'
                            '    if (stop.armed) { persistStop(); ctx?.abort?.(); return; }\n'
                            '    line("payloads.ndjson", { bytes: JSON.stringify(event.payload ?? null).length });\n'
                            "  });\n")

    anchor = '  pi.on("session_shutdown", () => {\n    derivation.sessionEnd(nextRef());\n    persist();\n'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + "    persistStop();\n")
    return source


if __name__ == "__main__":
    text = generate()
    ARM_V2.write_text(text)
    print(f"{ARM_V2.name} {hashlib.sha256(text.encode()).hexdigest()}")
    print(f"{ARM_C.name} {hashlib.sha256(ARM_C.read_bytes()).hexdigest()}")
