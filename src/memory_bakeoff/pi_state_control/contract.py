"""Gen43 prototype contract: control, state schema, artifact authority.

Frozen before the synthetic trace is measured. This module holds the rules;
`runtime.py` holds the machinery that obeys them.

    State tells the agent what to do now. Memory tells it what it has learned.
    History lets it reconstruct what happened. Artifacts establish what is true.
    Control defines what the agent is allowed to do next.

Control and state are deliberately separate here. State is a bounded record of
where the run is. Control is a transition table plus a completion gate, both
executable, so "done" is something the run has to earn from an artifact rather
than something it can assert in prose.

Evidence class: architecture_prototype_no_score.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

CONTRACT_VERSION = "pi-state-control-v1"
STATE_SCHEMA_VERSION = 1

# --- control -----------------------------------------------------------------

PHASES = ("inspect", "plan", "implement", "validate", "done", "blocked")

# Legal transitions. Backedges are deliberate: validation failure returns to
# implement, and a blocked run can be resumed rather than being a dead end.
TRANSITIONS: dict[str, tuple[str, ...]] = {
    "inspect": ("plan", "blocked"),
    "plan": ("implement", "inspect", "blocked"),
    "implement": ("validate", "plan", "blocked"),
    "validate": ("done", "implement", "blocked"),
    "done": (),
    "blocked": ("inspect", "plan", "implement", "validate"),
}

# Entering this phase requires a validated artifact receipt, not a claim.
GATED_PHASES = {"done": "validation_receipt"}


class ControlError(RuntimeError):
    """An illegal transition, or a gate that was not satisfied."""


class StateError(RuntimeError):
    """A patch that would leave the state invalid, stale or unbounded."""


class HistoryError(RuntimeError):
    """A history reference that does not exist, or a log that fails its chain."""


class ArtifactError(RuntimeError):
    """An artifact whose content no longer matches the digest state relies on."""


def legal_transition(current: str, target: str) -> bool:
    if current not in TRANSITIONS or target not in PHASES:
        return False
    return target in TRANSITIONS[current]


# --- state schema ------------------------------------------------------------

# field -> (python type, required, bound). A bound of None means unbounded by
# nature (scalars); an int bounds a list, and overflow is archived to history
# rather than dropped.
STATE_FIELDS: dict[str, tuple[type, bool, int | None]] = {
    "schema_version": (int, True, None),
    "phase": (str, True, None),
    "goal": (str, True, None),
    "active_files": (list, True, 6),
    "important_findings": (list, True, 8),
    "completed_checkpoints": (list, True, 6),
    "current_process_or_tool": (str, False, None),
    "next_actions": (list, True, 5),
    "open_questions": (list, False, 5),
    "blockers": (list, False, 4),
    "validated_artifact_refs": (list, True, 4),
    "last_observation_ref": (str, False, None),
}

REQUIRED_FIELDS = tuple(name for name, (_t, req, _b) in STATE_FIELDS.items() if req)
BOUNDED_FIELDS = {name: bound for name, (_t, _r, bound) in STATE_FIELDS.items() if bound}

# A guard, not a preference: if the active state ever grows past this it has
# stopped being state and become the transcript in JSON.
MAX_STATE_BYTES = 4096

PATCH_OPS = ("set", "append", "remove")


def initial_state(goal: str) -> dict[str, Any]:
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "phase": "inspect",
        "goal": goal,
        "active_files": [],
        "important_findings": [],
        "completed_checkpoints": [],
        "current_process_or_tool": "",
        "next_actions": [],
        "open_questions": [],
        "blockers": [],
        "validated_artifact_refs": [],
        "last_observation_ref": "",
    }


def validate_state(state: Mapping[str, Any]) -> None:
    unknown = sorted(set(state) - set(STATE_FIELDS))
    if unknown:
        raise StateError(f"state carries fields outside the schema: {unknown}")
    for name in REQUIRED_FIELDS:
        if name not in state:
            raise StateError(f"required state field {name!r} is missing")
    for name, value in state.items():
        expected = STATE_FIELDS[name][0]
        if not isinstance(value, expected):
            raise StateError(f"{name!r} is {type(value).__name__}, expected {expected.__name__}")
    if state["schema_version"] != STATE_SCHEMA_VERSION:
        raise StateError(f"state schema {state['schema_version']} != {STATE_SCHEMA_VERSION}")
    if state["phase"] not in PHASES:
        raise StateError(f"unknown phase {state['phase']!r}")
    size = state_bytes(state)
    if size > MAX_STATE_BYTES:
        raise StateError(f"active state is {size} bytes, over the {MAX_STATE_BYTES} bound")


def state_bytes(state: Mapping[str, Any]) -> int:
    return len(canonical(state).encode())


def canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def digest(payload: Any) -> str:
    return hashlib.sha256(canonical(payload).encode()).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def contract_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def contract_identity() -> dict[str, Any]:
    """What was frozen, so a later run can prove it measured the same rules."""
    return {
        "contract_version": CONTRACT_VERSION,
        "state_schema_version": STATE_SCHEMA_VERSION,
        "phases": list(PHASES),
        "transitions": {k: list(v) for k, v in TRANSITIONS.items()},
        "gated_phases": dict(GATED_PHASES),
        "state_fields": {
            name: {"type": t.__name__, "required": req, "bound": bound}
            for name, (t, req, bound) in STATE_FIELDS.items()
        },
        "max_state_bytes": MAX_STATE_BYTES,
        "patch_ops": list(PATCH_OPS),
        "contract_sha256": contract_sha256(),
    }
