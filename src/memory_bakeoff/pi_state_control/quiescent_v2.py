"""`quiescent-completion-toolcall-v2`: the Gen52 repair, in two changes.

Gen52 let the first version of this rule actually stop runs, and it failed in
two ways that 48 runs of offline calibration had not shown.

A run made the correct fix, found that the project's own stale test rejected it,
put the old value back, and earned a receipt on a tree byte-identical to the one
it started with. The rule stopped it. It had asked only whether *a mutation
happened*, never whether *the tree had changed*.

Another run ran the same passing test 144 times on an unchanged tree and timed
out. Every pass re-armed the receipt and reset the count, so the loop the rule
existed to catch could never accumulate three quiet actions.

So v2 changes exactly two things and nothing else:

  A. a run whose tree is back at its starting digest is never quiescent-complete;
  B. a pass on a tree that already holds a valid receipt is an idle action, not
     fresh evidence, and does not postpone the stop.

Everything else - the recognizer, the hidden-verifier exclusions, the safe-stop
boundary, the K unit - is v1 unchanged.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .harness_state import FORBIDDEN_IN_VALIDATION, MUTATION_TOOLS, VALIDATION_RE

CONTRACT_VERSION = "quiescent-completion-toolcall-v2"
K_SWEEP = (1, 2, 3, 5, 10)


def is_visible_check(command: str) -> bool:
    """The frozen harness recognizer, reused unchanged."""
    return (bool(command)
            and not any(token in command for token in FORBIDDEN_IN_VALIDATION)
            and bool(VALIDATION_RE.search(command)))


@dataclass
class QuiescentV2:
    """The rule as a state machine over one run's observable tool stream."""

    k: int
    initial_tree: str = ""
    current_tree: str = ""
    mutated: bool = False
    receipt_tree: str | None = None
    receipt_command: str = ""
    receipt_index: int | None = None
    idle: int = 0
    tool_index: int = 0
    pending_calls: int = 0
    armed: bool = False
    triggered: bool = False
    trigger_index: int | None = None
    effective_stop_index: int | None = None
    overshoot: int = 0
    mutations: int = 0
    same_tree_passes_counted_idle: int = 0
    became_eligible: bool = False
    reason: str = ""
    events: list[dict[str, Any]] = field(default_factory=list)

    # --- the two v2 predicates ------------------------------------------------

    def net_tree_changed(self) -> bool:
        """A run that is back where it started has not finished; it went in a circle."""
        return bool(self.current_tree) and self.current_tree != self.initial_tree

    def eligible(self) -> bool:
        return (self.mutated and self.net_tree_changed()
                and self.receipt_tree is not None and self.receipt_tree == self.current_tree)

    # --- the observable stream ------------------------------------------------

    def observe_call(self, tool: str) -> None:
        self.tool_index += 1
        self.pending_calls += 1
        if tool in MUTATION_TOOLS:
            self.mutated = True
            self.mutations += 1
            self._invalidate("mutation")

    def observe_result(self, *, passed: bool | None, tree: str, fresh_check: bool) -> bool:
        """One tool result. Returns True when the run should stop at this boundary."""
        self.pending_calls = max(0, self.pending_calls - 1)
        if not self.initial_tree:
            # The initial tree must be captured before the agent's first action.
            # Adopting the first result's digest would be too late: if that first
            # action is a mutation, the "initial" tree is already the mutated one
            # and a later revert to the real starting point goes unnoticed.
            raise ValueError("initial_tree must be set before the first tool result")
        if tree:
            if tree != self.current_tree and self.current_tree:
                # The tree moved without a mutation tool - a shell heredoc, say.
                self._invalidate("tree changed")
                self.mutated = True
            self.current_tree = tree

        if self.armed:
            self.overshoot += 1
            return self.pending_calls == 0 and self._finish()

        if fresh_check and passed is False:
            self._invalidate("visible check failed")
            return False

        if fresh_check and passed is True:
            if self.receipt_tree is not None and self.receipt_tree == self.current_tree:
                # B: a valid receipt already covers this exact tree. Another pass
                # is new validation evidence and no new progress, so it is idle.
                self.same_tree_passes_counted_idle += 1
                self.idle += 1
            else:
                self.receipt_tree = self.current_tree
                self.receipt_command = ""
                self.receipt_index = self.tool_index
                self.idle = 0
                if self.eligible():
                    self.became_eligible = True
                return False
        elif self.receipt_tree is not None:
            self.idle += 1

        if not self.eligible():
            return False
        self.became_eligible = True
        if self.idle < self.k:
            return False
        self.armed = True
        self.trigger_index = self.tool_index
        if self.pending_calls > 0:
            return False        # a sibling call is still running; never kill it
        return self._finish()

    def _invalidate(self, reason: str) -> None:
        self.receipt_tree = None
        self.receipt_index = None
        self.idle = 0

    def _finish(self) -> bool:
        self.triggered = True
        self.effective_stop_index = self.tool_index
        self.reason = "quiescent_stop"
        return True

    def snapshot(self) -> dict[str, Any]:
        """What a live runner must persist on every tool result, not only at a stop."""
        return {
            "contract": CONTRACT_VERSION, "k": self.k,
            "initial_tree_digest": self.initial_tree,
            "current_tree_digest": self.current_tree,
            "net_tree_changed": self.net_tree_changed(),
            "valid_receipt_tree": self.receipt_tree,
            "valid_receipt_tool_index": self.receipt_index,
            "idle_count": self.idle,
            "eligible": self.eligible(),
            "became_eligible": self.became_eligible,
            "mutations": self.mutations,
            "same_tree_passes_counted_idle": self.same_tree_passes_counted_idle,
            "triggered": self.triggered,
            "trigger_tool_index": self.trigger_index,
            "effective_stop_tool_index": self.effective_stop_index,
            "same_batch_overshoot_calls": self.overshoot,
            "tool_index": self.tool_index,
            "reason": self.reason,
        }


def contract() -> dict[str, Any]:
    source = Path(__file__).read_bytes()
    return {
        "contract_version": CONTRACT_VERSION,
        "derived_from": "quiescent-completion-toolcall-k3-v1",
        "k_unit": "tool calls",
        "k_sweep": list(K_SWEEP),
        "changes_from_v1": [
            "net-tree-change eligibility: a run whose current tree equals its initial tree is "
            "never quiescent-complete, however many mutation events it made",
            "a recognized visible pass on a tree that already holds a valid receipt is an idle "
            "completion, not a re-arm, and increments the K count instead of resetting it",
        ],
        "unchanged_from_v1": [
            "the harness-state-v1 validation recognizer, reused unchanged",
            "hidden verifier, reference fixes and scorer paths excluded by the same tokens",
            "at least one repository mutation event is still required",
            "a visible fail invalidates the receipt and resets the count",
            "a mutation invalidates the receipt and resets the count",
            "the stop waits for an in-flight batch to drain and records the overshoot",
            "K is counted in tool calls",
        ],
        "never_an_input": ["hidden verifier", "reference fix", "task manifest answers",
                           "post-hoc correctness", "model self-report"],
        "hidden_verifier_exclusion": list(FORBIDDEN_IN_VALIDATION),
        "mutation_tools": sorted(MUTATION_TOOLS),
        "contract_sha256": hashlib.sha256(source).hexdigest(),
    }
