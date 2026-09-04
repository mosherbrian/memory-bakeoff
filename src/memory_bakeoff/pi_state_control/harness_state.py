"""Gen46: harness-maintained execution state, derived from visible tool events.

Gen45's arm B never exercised its control layer: the model did not call the
three state and control tools, so zero transitions were accepted and every run
ended in `inspect`. Arm C removes that dependency. The state and the phase are
derived by the harness from ordinary tool activity the agent itself can see.

The line this module will not cross: **no semantic interpretation**. It records
what happened — files read, the repository mutated, a visible check run and its
exit status — and never what any of it means. No inferred cause, no plan, no
next action. If a field would need a model to fill it in, it is not here.

It also never touches hidden data. The final verifier, the reference fixes and
every scorer-only field are outside the derivation path by construction, and a
test asserts the module names none of them.

Evidence class: architecture_state_control_ablation_design_no_score.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

DERIVATION_VERSION = "harness-state-v1"

# --- what counts as an observable event --------------------------------------

READ_TOOLS = frozenset({"read", "ls", "grep", "find", "glob"})
MUTATION_TOOLS = frozenset({"edit", "write", "multi_edit"})
SHELL_TOOLS = frozenset({"bash"})

# Frozen, model-independent classification of a validation command. These come
# from the public fixtures' own tooling: three tasks ship a visible test file and
# one ships `run_checks.py`. The hidden verifier is deliberately absent, and
# `FORBIDDEN_IN_VALIDATION` makes reading it impossible to mistake for a check.
VALIDATION_PATTERNS = (
    r"\bpytest\b",
    r"\bpython3?\s+-m\s+pytest\b",
    r"\bpython3?\s+-m\s+unittest\b",
    r"\bpython3?\s+run_checks\.py\b",
)
VALIDATION_RE = re.compile("|".join(VALIDATION_PATTERNS))
FORBIDDEN_IN_VALIDATION = ("verifier.py", "verifier_path", "reference_fix")

# Two distinct inspection calls are enough to leave `inspect`; the criterion is
# fixed here so it cannot be tuned against a live failure later.
INSPECTION_CALLS_TO_LEAVE_INSPECT = 2

PHASES = ("inspect", "plan", "implement", "validate", "done", "blocked")

# Automatic transitions. The table is the same shape as the Gen43 contract, but
# every edge here is driven by an event rather than by a request.
AUTOMATIC_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "inspect": ("plan", "implement", "blocked"),
    "plan": ("implement", "inspect", "blocked"),
    "implement": ("validate", "plan", "blocked"),
    "validate": ("done", "implement", "blocked"),
    "done": ("implement",),   # a mutation after done reopens the run
    "blocked": ("inspect", "plan", "implement", "validate"),
}

STATE_BYTE_CAP = 4096          # unchanged from Gen43/44/45
RECENT_FILES_BOUND = 6
CHECKPOINT_BOUND = 6

OBJECTIVE_CHECKPOINTS = ("repository_mutated", "validation_failed", "validation_passed")


class DerivationError(RuntimeError):
    """An event that cannot be interpreted without guessing."""


def canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def digest(payload: Any) -> str:
    return hashlib.sha256(canonical(payload).encode()).hexdigest()


def is_validation_command(command: str) -> bool:
    """Deterministic, model-independent, and blind to the hidden verifier."""
    if not command:
        return False
    if any(token in command for token in FORBIDDEN_IN_VALIDATION):
        return False
    return bool(VALIDATION_RE.search(command))


# --- the derived state -------------------------------------------------------


@dataclass
class HarnessState:
    """Objective execution state. Every field is something that was observed."""

    phase: str = "inspect"
    revision: int = 0
    tree_digest: str = ""
    files_read: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    last_tool: str = ""
    last_tool_ref: str = ""
    last_observation_ref: str = ""
    checkpoints: list[str] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)
    validated_artifact_refs: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "derivation": DERIVATION_VERSION,
            "phase": self.phase,
            "revision": self.revision,
            "tree_digest": self.tree_digest,
            "files_read": self.files_read,
            "files_modified": self.files_modified,
            "last_tool": self.last_tool,
            "last_tool_ref": self.last_tool_ref,
            "last_observation_ref": self.last_observation_ref,
            "checkpoints": self.checkpoints,
            "validation": self.validation,
            "validated_artifact_refs": self.validated_artifact_refs,
        }

    def bytes(self) -> int:
        return len(canonical(self.to_dict()).encode())


def _bounded(values: Sequence[str], bound: int) -> list[str]:
    return list(values)[-bound:]


@dataclass
class Derivation:
    """Replayable derivation: the same event log always yields the same state."""

    state: HarnessState = field(default_factory=HarnessState)
    transitions: list[dict[str, Any]] = field(default_factory=list)
    receipts: list[dict[str, Any]] = field(default_factory=list)
    invalidations: list[dict[str, Any]] = field(default_factory=list)
    inspection_calls: int = 0

    # --- transitions ---------------------------------------------------------

    def _move(self, target: str, because: str, event_ref: str) -> None:
        current = self.state.phase
        if target == current:
            return
        if target not in AUTOMATIC_TRANSITIONS.get(current, ()):  # fails closed
            self.transitions.append({"from": current, "to": target, "accepted": False,
                                     "reason": "not an automatic transition", "event": event_ref})
            return
        self.state.phase = target
        self.state.revision += 1
        self.transitions.append({"from": current, "to": target, "accepted": True,
                                 "because": because, "event": event_ref})

    # --- events --------------------------------------------------------------

    def apply(self, event: dict[str, Any]) -> None:
        kind = event.get("type")
        ref = event.get("id", "")
        if kind == "tool_call":
            self._tool_call(event, ref)
        elif kind == "tool_result":
            self._tool_result(event, ref)
        elif kind == "session_end":
            self._session_end(ref)
        else:
            raise DerivationError(f"unknown event type {kind!r}")

    def _tool_call(self, event: dict[str, Any], ref: str) -> None:
        tool = event.get("tool", "")
        args = event.get("args") or {}
        self.state.last_tool = tool
        self.state.last_tool_ref = ref
        self.state.revision += 1

        if tool in READ_TOOLS:
            self.inspection_calls += 1
            path = args.get("path") or args.get("pattern") or ""
            if path:
                self.state.files_read = _bounded(
                    [p for p in self.state.files_read if p != path] + [path], RECENT_FILES_BOUND)
            if (self.state.phase == "inspect"
                    and self.inspection_calls >= INSPECTION_CALLS_TO_LEAVE_INSPECT):
                self._move("plan", "enough inspection activity to have looked around", ref)

        elif tool in MUTATION_TOOLS:
            path = args.get("path") or ""
            if path:
                self.state.files_modified = _bounded(
                    [p for p in self.state.files_modified if p != path] + [path], RECENT_FILES_BOUND)
            self._checkpoint("repository_mutated")
            self._invalidate_on_mutation(ref)
            if self.state.phase in ("inspect", "plan", "validate", "done"):
                self._move("implement", "the repository was modified", ref)

    def _tool_result(self, event: dict[str, Any], ref: str) -> None:
        self.state.last_observation_ref = ref
        command = (event.get("command") or "").strip()
        tree = event.get("tree_digest") or self.state.tree_digest
        self.state.tree_digest = tree
        if not command or not is_validation_command(command):
            return
        passed = bool(event.get("exit_code") == 0) if "exit_code" in event else not event.get("is_error")
        self.state.validation = {"command": command, "passed": passed,
                                 "tree_digest": tree, "event": ref}
        if self.state.phase == "implement":
            self._move("validate", "a visible check ran after a change", ref)
        if passed:
            self._checkpoint("validation_passed")
            receipt = {"kind": "validation_receipt", "command": command,
                       "tree_digest": tree, "passed": True, "event": ref}
            self.state.validated_artifact_refs = [receipt]
            self.receipts.append(receipt)
        else:
            self._checkpoint("validation_failed")
            self.state.validated_artifact_refs = []
            if self.state.phase == "validate":
                self._move("implement", "the visible check failed", ref)

    def _session_end(self, ref: str) -> None:
        """`done` is recorded only if a receipt still matches the current tree."""
        valid = self.valid_receipt()
        if valid and self.state.phase == "validate":
            self._move("done", "the run ended with a valid receipt for this tree", ref)

    # --- receipts ------------------------------------------------------------

    def _invalidate_on_mutation(self, ref: str) -> None:
        if not self.state.validated_artifact_refs:
            return
        self.invalidations.append({"reason": "repository mutated after the check",
                                   "receipt": self.state.validated_artifact_refs[0], "event": ref})
        self.state.validated_artifact_refs = []

    def valid_receipt(self) -> dict[str, Any] | None:
        """A receipt is valid only for the exact tree the check ran against."""
        for receipt in self.state.validated_artifact_refs:
            if receipt.get("passed") and receipt.get("tree_digest") == self.state.tree_digest:
                return receipt
        return None

    def _checkpoint(self, name: str) -> None:
        if name not in OBJECTIVE_CHECKPOINTS:
            raise DerivationError(f"{name!r} is not an objective checkpoint")
        self.state.checkpoints = _bounded(self.state.checkpoints + [name], CHECKPOINT_BOUND)

    # --- replay --------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        return {
            "state": self.state.to_dict(),
            "state_bytes": self.state.bytes(),
            "transitions": self.transitions,
            "transitions_accepted": sum(1 for t in self.transitions if t["accepted"]),
            "transitions_rejected": sum(1 for t in self.transitions if not t["accepted"]),
            "receipts": self.receipts,
            "receipt_invalidations": self.invalidations,
            "valid_receipt_at_end": self.valid_receipt() is not None,
        }


def derive(events: Iterable[dict[str, Any]]) -> Derivation:
    derivation = Derivation()
    for event in events:
        derivation.apply(event)
    return derivation


def replay_digest(events: Iterable[dict[str, Any]]) -> str:
    return digest(derive(events).summary())


def contract_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def contract() -> dict[str, Any]:
    return {
        "derivation_version": DERIVATION_VERSION,
        "read_tools": sorted(READ_TOOLS),
        "mutation_tools": sorted(MUTATION_TOOLS),
        "shell_tools": sorted(SHELL_TOOLS),
        "validation_patterns": list(VALIDATION_PATTERNS),
        "forbidden_in_validation": list(FORBIDDEN_IN_VALIDATION),
        "inspection_calls_to_leave_inspect": INSPECTION_CALLS_TO_LEAVE_INSPECT,
        "automatic_transitions": {k: list(v) for k, v in AUTOMATIC_TRANSITIONS.items()},
        "objective_checkpoints": list(OBJECTIVE_CHECKPOINTS),
        "state_byte_cap": STATE_BYTE_CAP,
        "recent_files_bound": RECENT_FILES_BOUND,
        "checkpoint_bound": CHECKPOINT_BOUND,
        "receipt_rule": "valid only for the exact tree digest the visible check ran against",
        "semantic_fields": "none; nothing here requires interpreting what tool output means",
        "hidden_data": "the final verifier and reference fixes are outside this path by construction",
        "contract_sha256": contract_sha256(),
    }
