"""Gen43 prototype runtime: history, artifacts, state patches, composer.

Everything here obeys `contract.py`. Nothing here talks to a model, a network
or Pi itself; the Pi binding is a thin extension that calls into this.

The load-bearing separations:

* **History** is append-only and hash-chained. Removing something from active
  state never removes it from history, and a tampered event is detectable.
* **State** is the latest validated revision only. Every accepted patch is
  itself an event, so prior revisions are reconstructible from history.
* **Artifacts** outrank both. A completion receipt records the digest the file
  had when it was validated; if the file changes, the receipt stops validating
  and control refuses to stay done.
* **The composer** builds the live context from immutable instructions, the
  current state, the latest observation and only the history explicitly asked
  for. The full transcript is never replayed.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from memory_bakeoff.pi_state_control.contract import (
    ArtifactError,
    BOUNDED_FIELDS,
    ControlError,
    GATED_PHASES,
    HistoryError,
    PATCH_OPS,
    REQUIRED_FIELDS,
    STATE_FIELDS,
    TRANSITIONS,
    StateError,
    canonical,
    digest,
    file_digest,
    initial_state,
    legal_transition,
    state_bytes,
    validate_state,
)

GENESIS = "0" * 64


# --- lossless history --------------------------------------------------------


class History:
    """Append-only, hash-chained event log kept out of the live context."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._events: list[dict[str, Any]] = []
        if self.path.exists():
            self._events = [json.loads(line) for line in self.path.read_text().splitlines() if line]

    def append(self, event_type: str, payload: Any) -> dict[str, Any]:
        prev = self._events[-1]["digest"] if self._events else GENESIS
        seq = len(self._events)
        event = {
            "seq": seq,
            "id": f"e{seq:06d}",
            "type": event_type,
            "payload": payload,
            "prev_digest": prev,
        }
        event["digest"] = digest({k: event[k] for k in ("seq", "id", "type", "payload", "prev_digest")})
        with self.path.open("a") as handle:
            handle.write(canonical(event) + "\n")
        self._events.append(event)
        return event

    def get(self, event_id: str) -> dict[str, Any]:
        for event in self._events:
            if event["id"] == event_id:
                return event
        raise HistoryError(f"no history event {event_id!r}")

    def range(self, first: str, last: str) -> list[dict[str, Any]]:
        start, end = self.get(first)["seq"], self.get(last)["seq"]
        if end < start:
            raise HistoryError(f"range {first}..{last} runs backwards")
        return self._events[start : end + 1]

    def search(self, needle: str) -> list[dict[str, Any]]:
        """Exact substring search. Semantic retrieval is out of scope for Gen43."""
        return [e for e in self._events if needle in canonical(e["payload"])]

    def verify_chain(self) -> None:
        prev = GENESIS
        for event in self._events:
            expected = digest({k: event[k] for k in ("seq", "id", "type", "payload", "prev_digest")})
            if event["prev_digest"] != prev:
                raise HistoryError(f"{event['id']}: chain broken at prev_digest")
            if event["digest"] != expected:
                raise HistoryError(f"{event['id']}: content does not match its digest")
            prev = event["digest"]

    @property
    def events(self) -> list[dict[str, Any]]:
        return list(self._events)

    def bytes_total(self) -> int:
        return sum(len(canonical(e).encode()) for e in self._events)

    def head_digest(self) -> str:
        return self._events[-1]["digest"] if self._events else GENESIS


# --- artifacts ---------------------------------------------------------------


@dataclass
class ArtifactRef:
    """What state is allowed to hold: a pointer plus the digest it trusted."""

    path: str
    digest: str
    kind: str
    passed: bool
    validated_at_event: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "digest": self.digest,
            "kind": self.kind,
            "passed": self.passed,
            "validated_at_event": self.validated_at_event,
        }


def revalidate(ref: Mapping[str, Any], root: Path) -> tuple[bool, str]:
    """Is the artifact still what it was when the receipt was written?"""
    target = root / ref["path"]
    if not target.exists():
        return False, "artifact missing"
    now = file_digest(target)
    if now != ref["digest"]:
        return False, f"digest changed: {ref['digest'][:12]} -> {now[:12]}"
    if not ref.get("passed"):
        return False, "receipt records a failed check"
    return True, "valid"


# --- the prototype -----------------------------------------------------------

IMMUTABLE_INSTRUCTIONS = (
    "You are working under an executable control layer. Move only along legal "
    "transitions. Do not claim completion; earn it with a validated artifact."
)


@dataclass
class StepMetrics:
    step: int
    event_id: str
    history_events: int
    history_bytes: int
    state_bytes: int
    observation_bytes: int
    composed_context_bytes: int
    retrieved_from_history_bytes: int
    tool_output_bytes_history_only: int
    patches_accepted: int
    patches_rejected: int
    transitions_accepted: int
    transitions_rejected: int


@dataclass
class Prototype:
    """One run's control, state, history and artifact authority."""

    root: Path
    goal: str = ""
    state: dict[str, Any] = field(default_factory=dict)
    revision: int = 0
    metrics: list[StepMetrics] = field(default_factory=list)
    counters: dict[str, int] = field(default_factory=lambda: {
        "patches_accepted": 0, "patches_rejected": 0,
        "transitions_accepted": 0, "transitions_rejected": 0,
        "history_only_tool_bytes": 0, "retrieved_bytes": 0,
    })

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.history = History(self.root / "history.ndjson")
        self.state_path = self.root / "state.json"
        if self.state_path.exists():
            saved = json.loads(self.state_path.read_text())
            self.state, self.revision = saved["state"], saved["revision"]
            self.counters.update(saved.get("counters", {}))
            validate_state(self.state)
        elif self.goal:
            self.state = initial_state(self.goal)
            self.revision = 0
            self._persist()
            self.history.append("run_start", {"goal": self.goal, "state_digest": self.state_digest()})

    # --- persistence ---------------------------------------------------------

    def _persist(self) -> None:
        self.state_path.write_text(
            canonical({"state": self.state, "revision": self.revision, "counters": self.counters})
        )

    def tally(self, event_type: str) -> int:
        """Counts come from the log, so a restart cannot quietly reset them."""
        return sum(1 for event in self.history.events if event["type"] == event_type)

    def state_digest(self) -> str:
        return digest({"state": self.state, "revision": self.revision})

    @classmethod
    def restore(cls, root: Path) -> "Prototype":
        """Rebuild from persisted evidence only. No in-memory objects survive."""
        root = Path(root)
        if not (root / "state.json").exists():
            raise StateError(f"no persisted state at {root}")
        restored = cls(root=root)
        restored.history.verify_chain()
        return restored

    # --- state patches -------------------------------------------------------

    def apply_patch(self, patch: Mapping[str, Any]) -> dict[str, Any]:
        """Validated transaction. Rejected patches are recorded, never silent."""
        try:
            self._check_patch(patch)
            candidate = self._with_ops(patch["ops"])
            archived = self._enforce_bounds(candidate)
            validate_state(candidate)
        except StateError as exc:
            self.counters["patches_rejected"] += 1
            return self.history.append(
                "state_patch_rejected", {"patch": dict(patch), "reason": str(exc)}
            )
        self.state = candidate
        self.revision += 1
        self.counters["patches_accepted"] += 1
        self._persist()
        return self.history.append(
            "state_patch_accepted",
            {
                "ops": list(patch["ops"]),
                "revision": self.revision,
                "state_digest": self.state_digest(),
                "archived_to_history": archived,
            },
        )

    def _check_patch(self, patch: Mapping[str, Any]) -> None:
        if set(patch) - {"base_revision", "ops"}:
            raise StateError(f"patch carries unexpected keys: {sorted(set(patch) - {'base_revision', 'ops'})}")
        if patch.get("base_revision") != self.revision:
            raise StateError(f"stale patch: base {patch.get('base_revision')} != {self.revision}")
        ops = patch.get("ops")
        if not isinstance(ops, list) or not ops:
            raise StateError("patch carries no operations")
        for op in ops:
            if op.get("op") not in PATCH_OPS:
                raise StateError(f"unknown op {op.get('op')!r}")
            if op.get("field") not in STATE_FIELDS:
                raise StateError(f"unknown field {op.get('field')!r}")
            if op["field"] == "phase":
                raise StateError("phase changes go through the control layer, not a patch")

    def _with_ops(self, ops: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        candidate = json.loads(canonical(self.state))
        for op in ops:
            field_name, kind, value = op["field"], op["op"], op.get("value")
            expected = STATE_FIELDS[field_name][0]
            if kind == "set":
                if not isinstance(value, expected):
                    raise StateError(
                        f"{field_name!r} takes {expected.__name__}, got {type(value).__name__}"
                    )
                candidate[field_name] = value
            elif kind == "append":
                if expected is not list:
                    raise StateError(f"{field_name!r} is not a list")
                candidate[field_name] = candidate[field_name] + [value]
            elif kind == "remove":
                if expected is not list:
                    raise StateError(f"{field_name!r} is not a list")
                if value not in candidate[field_name]:
                    raise StateError(f"{value!r} is not in {field_name!r}")
                candidate[field_name] = [v for v in candidate[field_name] if v != value]
        for name in REQUIRED_FIELDS:
            if name not in candidate:
                raise StateError(f"patch would delete required field {name!r}")
        return candidate

    def _enforce_bounds(self, candidate: dict[str, Any]) -> list[dict[str, Any]]:
        """Archive overflow to history rather than letting state become the log."""
        archived: list[dict[str, Any]] = []
        for name, bound in BOUNDED_FIELDS.items():
            values = candidate.get(name) or []
            if len(values) <= bound:
                continue
            overflow, keep = values[: len(values) - bound], values[len(values) - bound :]
            event = self.history.append("state_overflow_archived", {"field": name, "entries": overflow})
            candidate[name] = keep
            archived.append({"field": name, "count": len(overflow), "event_id": event["id"]})
        return archived

    # --- control -------------------------------------------------------------

    def transition(self, target: str, receipt: Mapping[str, Any] | None = None) -> dict[str, Any]:
        current = self.state["phase"]
        if not legal_transition(current, target):
            self.counters["transitions_rejected"] += 1
            return self.history.append(
                "transition_rejected",
                {"from": current, "to": target, "reason": "illegal transition"},
            )
        gate = GATED_PHASES.get(target)
        if gate:
            ok, why = self._gate_satisfied(gate, receipt)
            if not ok:
                self.counters["transitions_rejected"] += 1
                return self.history.append(
                    "transition_rejected", {"from": current, "to": target, "reason": why}
                )
        self.state["phase"] = target
        self.revision += 1
        self.counters["transitions_accepted"] += 1
        self._persist()
        return self.history.append(
            "transition_accepted",
            {"from": current, "to": target, "revision": self.revision,
             "state_digest": self.state_digest()},
        )

    def _gate_satisfied(self, kind: str, receipt: Mapping[str, Any] | None) -> tuple[bool, str]:
        refs = [r for r in self.state["validated_artifact_refs"] if r.get("kind") == kind]
        if receipt is not None:
            refs = [receipt]
        if not refs:
            return False, f"no {kind} in state; completion cannot be asserted"
        for ref in refs:
            ok, why = revalidate(ref, self.root)
            if not ok:
                return False, f"{kind} {ref['path']}: {why}"
        return True, "ok"

    def record_receipt(self, path: str, kind: str, passed: bool) -> ArtifactRef:
        """Take the digest now, so a later mutation is detectable."""
        target = self.root / path
        if not target.exists():
            raise ArtifactError(f"artifact {path} does not exist")
        event = self.history.append(
            "artifact_validated",
            {"path": path, "kind": kind, "passed": passed, "digest": file_digest(target)},
        )
        return ArtifactRef(path, file_digest(target), kind, passed, event["id"])

    def artifact_status(self) -> list[dict[str, Any]]:
        out = []
        for ref in self.state["validated_artifact_refs"]:
            ok, why = revalidate(ref, self.root)
            out.append({"path": ref["path"], "kind": ref["kind"], "valid": ok, "reason": why})
        return out

    # --- observations and composition ---------------------------------------

    def observe(self, tool: str, output: str, keep_in_context: bool = True) -> dict[str, Any]:
        """Tool output always lands in history; only some of it stays live."""
        event = self.history.append("tool_result", {"tool": tool, "output": output})
        if keep_in_context:
            self.last_observation = {"event_id": event["id"], "tool": tool, "output": output}
        else:
            self.counters["history_only_tool_bytes"] += len(output.encode())
            self._persist()
            self.last_observation = {
                "event_id": event["id"], "tool": tool,
                "output": f"[{len(output)} chars retained in history as {event['id']}]",
            }
        return event

    def recall(self, event_id: str) -> dict[str, Any]:
        """Pull one historical event back on demand. It does not become sticky."""
        event = self.history.get(event_id)
        self.counters["retrieved_bytes"] += len(canonical(event["payload"]).encode())
        self._persist()
        self.history.append("history_recalled", {"event_id": event_id})
        return event

    def compose(self, requested: Iterable[str] = ()) -> dict[str, Any]:
        """The deterministic live context. The transcript is never replayed."""
        recalled = [self.history.get(event_id) for event_id in requested]
        observation = getattr(self, "last_observation", None)
        context = {
            "instructions": IMMUTABLE_INSTRUCTIONS,
            "control": {
                "phase": self.state["phase"],
                "legal_next": list(TRANSITIONS[self.state["phase"]]),
                "gates": dict(GATED_PHASES),
            },
            "state": self.state,
            "observation": observation,
            "recalled": [{"id": e["id"], "type": e["type"], "payload": e["payload"]} for e in recalled],
        }
        return context

    def record_step(self, step: int, event_id: str, requested: Sequence[str] = ()) -> StepMetrics:
        context = self.compose(requested)
        observation = context["observation"] or {}
        metrics = StepMetrics(
            step=step,
            event_id=event_id,
            history_events=len(self.history.events),
            history_bytes=self.history.bytes_total(),
            state_bytes=state_bytes(self.state),
            observation_bytes=len(canonical(observation).encode()),
            composed_context_bytes=len(canonical(context).encode()),
            retrieved_from_history_bytes=self.counters["retrieved_bytes"],
            tool_output_bytes_history_only=self.counters["history_only_tool_bytes"],
            patches_accepted=self.tally("state_patch_accepted"),
            patches_rejected=self.tally("state_patch_rejected"),
            transitions_accepted=self.tally("transition_accepted"),
            transitions_rejected=self.tally("transition_rejected"),
        )
        self.metrics.append(metrics)
        return metrics
