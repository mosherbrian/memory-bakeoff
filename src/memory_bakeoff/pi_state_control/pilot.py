"""Gen44 pilot contract: the frozen A/B design for the first live coding pilot.

Frozen before any live model exposure. Gen44 runs no model; this module states
what Gen45 is allowed to do and how it will be measured, so nothing can be
tuned once success rates are visible.

The treatment boundary, stated plainly: arm B is not "arm A with fewer bytes".
It replaces transcript replay with a composed view AND adds executable control,
bounded state, artifact-gated completion and the tools needed to drive them.
That whole bundle is the treatment. Attributing a difference to any single
piece of it is out of scope for a four-task pilot.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

PILOT_CONTRACT_VERSION = "pi-pilot-v1"
ORDER_SEED = 20260905

# --- arms --------------------------------------------------------------------

ARMS: dict[str, dict[str, Any]] = {
    "pi_default_v1": {
        "description": "stock Pi 0.73.0 history and context behaviour",
        "context_hook_installed": False,
        "pi_compaction": "enabled, Pi's own default",
        "state_control_tools": [],
        "history": "Pi's own session transcript",
    },
    "pi_state_control_v1": {
        "description": "Pi 0.73.0 plus the Gen43 state/control extension lineage",
        "context_hook_installed": True,
        "pi_compaction": "cancelled from the extension; history is externalized instead",
        "state_control_tools": ["propose_state_patch", "request_transition", "record_receipt"],
        "history": "lossless external NDJSON log, hash-chained, never replayed by default",
    },
}

TREATMENT_COMPONENTS = (
    "composed context replaces transcript replay",
    "executable phase transitions with a gated completion",
    "bounded validated structured state",
    "artifact receipts outrank state",
    "three extra tools that exist only to drive the above",
)

# --- arm B composition, frozen now -------------------------------------------

STATE_BYTE_CAP = 4096            # inherited from the Gen43 contract
RECENT_WINDOW_UNITS = 2          # complete interaction units, most recent first
RECENT_WINDOW_BYTE_CAP = 8192
LATEST_OBSERVATION_BYTE_CAP = 8192

COMPOSITION_ORDER = (
    "immutable_instructions",
    "control",
    "state",
    "recent_window",
    "latest_observation",
    "artifact_refs",
)

# Pi groups messages by role; an "interaction unit" here is deterministic and
# testable rather than a matter of judgement: one user message plus everything
# that follows it up to (not including) the next user message.
INTERACTION_UNIT_RULE = (
    "a unit starts at a user message and runs to the message before the next "
    "user message; a trailing partial unit counts as one unit; messages before "
    "the first user message belong to no unit and are never included"
)


def interaction_units(messages: list[dict]) -> list[list[dict]]:
    """Split a Pi-shaped message list into units by the rule above."""
    units: list[list[dict]] = []
    current: list[dict] | None = None
    for message in messages:
        if message.get("role") == "user":
            if current is not None:
                units.append(current)
            current = [message]
        elif current is not None:
            current.append(message)
    if current is not None:
        units.append(current)
    return units


def recent_window(messages: list[dict], units: int = RECENT_WINDOW_UNITS,
                  byte_cap: int = RECENT_WINDOW_BYTE_CAP) -> tuple[list[dict], int]:
    """The last `units` interaction units, in original order, under a byte cap.

    Overflow is dropped from the window only; the full text stays in the
    lossless history, which is the point of the design.
    """
    selected = [m for unit in interaction_units(messages)[-units:] for m in unit]
    kept: list[dict] = []
    used = 0
    for message in reversed(selected):
        size = len(canonical(message).encode())
        if used + size > byte_cap:
            break
        kept.append(message)
        used += size
    kept.reverse()
    return kept, used


# --- measurement definitions, frozen now -------------------------------------

PRIMARY_OUTCOME = "deterministic verifier pass or fail on the final repository state"

CO_PRIMARY_OUTCOMES = (
    "provider request bytes at every model call",
    "cumulative request bytes across the run",
    "max and median request bytes",
    "request bytes by turn index",
    "model calls",
    "tool calls",
)

# Frozen so they cannot be re-specified once results exist.
CHURN_DEFINITIONS = {
    "exact_repeated_tool_call": (
        "same tool name and canonicalized JSON arguments as any earlier call in "
        "the same run"
    ),
    "redundant_file_read": (
        "same path and byte/line range read again with no intervening write to "
        "that path in the run's own tool log"
    ),
    "redundant_verifier_invocation": (
        "same canonical verifier or test command repeated with no intervening "
        "repository mutation, judged by the worktree digest"
    ),
}

CONTROL_OUTCOMES_ARM_B = (
    "state patches accepted and rejected",
    "transitions accepted and rejected",
    "completion attempts blocked by the artifact gate",
    "state bytes per request",
    "history bytes and events accumulated",
    "bytes retained only in history",
    "artifact revalidation failures",
)

TERMINATION_CLASSES = {
    "valid_completion": "verifier passes and, in arm B, the gate also validates",
    "unearned_completion_attempt": "the model tried to finish while the verifier or receipt was invalid",
    "correctly_blocked": "arm B refused an unearned completion; a control success, not a task success",
    "abandoned_or_timeout": "the run ended without verifier success",
    "orchestration_failure": "the harness or extension failed; not a model result",
}

# Directional only. No numeric threshold is preregistered for four tasks.
HYPOTHESES = {
    "H1": "B materially reduces cumulative request bytes on longer or noisier runs",
    "H2": "B reduces the growth of request size with run length",
    "H3": "B does not reduce verifier success so far that the architecture is unusable",
    "H4": "exploratory: B may reduce repeated or redundant tool calls, or increase them",
    "H5": "the artifact gate prevents any naturally occurring unearned completion from counting",
    "H6": "a failure caused by missing older context is a result, not a reason to retune",
}

READING_RULES = (
    "four tasks and three repetitions is descriptive paired evidence, not a population estimate",
    "no global winner claim",
    "every run-level leaf is reported, including crashes and blocked runs",
    "wall clock stays outside the scientific digest",
)


# --- churn counting, implementing the frozen definitions ---------------------


def canonical_args(args: Any) -> str:
    return canonical(args)


def count_churn(tool_log: list[dict]) -> dict[str, Any]:
    """Apply the frozen churn definitions to one run's tool log.

    Each entry: {"tool", "args", optional "path", "range", "command",
    "mutates_repo": bool}. The counters are deliberately literal — a definition
    that needs interpretation at scoring time is a definition that can be bent.
    """
    seen_calls: set[tuple[str, str]] = set()
    reads: dict[tuple[str, str], int] = {}
    verifiers: dict[str, int] = {}
    written: dict[str, int] = {}
    repo_mutations = 0

    exact_repeats = 0
    redundant_reads = 0
    redundant_verifiers = 0
    detail: list[dict[str, Any]] = []

    for index, entry in enumerate(tool_log):
        key = (entry["tool"], canonical_args(entry.get("args", {})))
        if key in seen_calls:
            exact_repeats += 1
            detail.append({"index": index, "kind": "exact_repeated_tool_call", "tool": entry["tool"]})
        seen_calls.add(key)

        if entry.get("mutates_repo"):
            repo_mutations += 1
            if entry.get("path"):
                written[entry["path"]] = index

        if entry["tool"] == "read" and entry.get("path"):
            read_key = (entry["path"], entry.get("range", ""))
            previous = reads.get(read_key)
            if previous is not None and written.get(entry["path"], -1) < previous:
                redundant_reads += 1
                detail.append({"index": index, "kind": "redundant_file_read", "path": entry["path"]})
            reads[read_key] = index

        if entry.get("command"):
            previous = verifiers.get(entry["command"])
            if previous is not None and not any(
                other.get("mutates_repo") for other in tool_log[previous + 1 : index]
            ):
                redundant_verifiers += 1
                detail.append({"index": index, "kind": "redundant_verifier_invocation",
                               "command": entry["command"]})
            verifiers[entry["command"]] = index

    return {
        "tool_calls": len(tool_log),
        "exact_repeated_tool_calls": exact_repeats,
        "redundant_file_reads": redundant_reads,
        "redundant_verifier_invocations": redundant_verifiers,
        "repo_mutations": repo_mutations,
        "total_repeated_or_redundant": exact_repeats + redundant_reads + redundant_verifiers,
        "detail": detail,
    }


# --- run plan ----------------------------------------------------------------

TASK_IDS = ("T1", "T2", "T3", "T4")
REPETITIONS = 3


def run_order(seed: int = ORDER_SEED) -> list[dict[str, Any]]:
    """Counterbalanced, deterministic order for the 24 runs.

    Within each task and repetition the two arms are adjacent and their order
    alternates, so arm order cannot align with drift in the machine or the
    cache. The sequence of pairs is shuffled from the frozen seed.
    """
    pairs = [{"task": task, "repetition": rep} for task in TASK_IDS for rep in range(1, REPETITIONS + 1)]
    rng = random.Random(seed)
    rng.shuffle(pairs)
    order: list[dict[str, Any]] = []
    for index, pair in enumerate(pairs):
        arms = ["pi_default_v1", "pi_state_control_v1"]
        if index % 2:
            arms.reverse()
        for position, arm in enumerate(arms):
            order.append({
                "index": len(order) + 1,
                "task": pair["task"],
                "repetition": pair["repetition"],
                "arm": arm,
                "position_in_pair": position + 1,
            })
    return order


# --- helpers -----------------------------------------------------------------


def canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def digest(payload: Any) -> str:
    return hashlib.sha256(canonical(payload).encode()).hexdigest()


def contract_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def pilot_contract() -> dict[str, Any]:
    return {
        "contract_version": PILOT_CONTRACT_VERSION,
        "evidence_class": "architecture_pilot_design_no_score",
        "arms": ARMS,
        "treatment_components": list(TREATMENT_COMPONENTS),
        "composition": {
            "order": list(COMPOSITION_ORDER),
            "state_byte_cap": STATE_BYTE_CAP,
            "recent_window_units": RECENT_WINDOW_UNITS,
            "recent_window_byte_cap": RECENT_WINDOW_BYTE_CAP,
            "latest_observation_byte_cap": LATEST_OBSERVATION_BYTE_CAP,
            "interaction_unit_rule": INTERACTION_UNIT_RULE,
            "semantic_retrieval": "not available in this pilot",
        },
        "primary_outcome": PRIMARY_OUTCOME,
        "co_primary_outcomes": list(CO_PRIMARY_OUTCOMES),
        "churn_definitions": CHURN_DEFINITIONS,
        "control_outcomes_arm_b": list(CONTROL_OUTCOMES_ARM_B),
        "termination_classes": TERMINATION_CLASSES,
        "hypotheses": HYPOTHESES,
        "reading_rules": list(READING_RULES),
        "run_plan": {"tasks": list(TASK_IDS), "repetitions": REPETITIONS,
                     "runs": len(TASK_IDS) * REPETITIONS * 2, "execution": "serial, one at a time",
                     "order_seed": ORDER_SEED},
        "contract_sha256": contract_sha256(),
    }
