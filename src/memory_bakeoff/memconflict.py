"""MemConflict external benchmark: what the benchmark means, frozen before any product touches it.

This module owns the contract only. It defines which released fields a memory
product may see, which belong to the scorer, where each question's history stops,
and which metric may be read from which stream. It runs no product, no reader and
no LLM.

Upstream scoring is audited here, not reimplemented. Where upstream turns a
missing measurement into a numeric zero, this module refuses to: an unmeasurable
metric is UNMEASURED and raises if read as a number.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping, Sequence

from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.round2_reporting import Measurement, ReportingError, Status

CONTRACT_VERSION = "memconflict-benchmark-v1"

UPSTREAM_REPO = "https://github.com/TaoZhen1110/MemConflict"
UPSTREAM_COMMIT = "ec51d5d36e87f7665d1337f3a88cbde95fc2a964"
DATASET_RELATIVE_PATH = "Data/Step4_4.jsonl"
DATASET_BLOB = "6dcbf9e536ea3e5d52f015ba75b15bdcd3377c94"
DATASET_SHA256 = "8ef9ec8589eccb86f63ab3a819a9180217405351a8d5846866721ea74babe092"

ROOT = Path(__file__).resolve().parents[2]
CHECKOUT = ROOT / "external/MemConflict"
DATASET = CHECKOUT / DATASET_RELATIVE_PATH

CONFLICT_TYPES = ("dynamic_conflict", "static_conflict", "conditional_conflict")

# Upstream Evaluation/eval_scoring.py at the pinned commit.
UPSTREAM_PRIMARY_TOP_K = 3
UPSTREAM_TOP_K_VALUES = (2, 3, 5)


class Stream(StrEnum):
    DATASET_VALIDATION = "dataset_validation"
    RETRIEVAL = "retrieval"
    ANSWER_READER = "answer_reader"
    PRODUCT_LIFECYCLE = "product_lifecycle"
    DIAGNOSTIC = "diagnostic"


class Lane(StrEnum):
    UPSTREAM_LLM_JUDGE = "upstream_llm_judge"
    UPSTREAM_RULE_FALLBACK = "upstream_rule_fallback"
    EXACT_PROVENANCE_WHITEBOX = "exact_provenance_whitebox"


LANES: dict[str, dict[str, Any]] = {
    str(Lane.UPSTREAM_LLM_JUDGE): {
        "description": "Upstream official path: an LLM judge scores answer metrics and decides the "
                       "white-box support rank by reading retrieved memory text.",
        "streams": [str(Stream.ANSWER_READER), str(Stream.RETRIEVAL)],
        "requires_reader": True,
        "status_without_reader": "requires_reader_authorization",
    },
    str(Lane.UPSTREAM_RULE_FALLBACK): {
        "description": "Upstream fallback when the judge is unavailable. Scores answer metrics by "
                       "string overlap and leaves every white-box metric at 0.0 without measuring it.",
        "streams": [str(Stream.ANSWER_READER)],
        "requires_reader": False,
        "white_box_is_measured": False,
    },
    str(Lane.EXACT_PROVENANCE_WHITEBOX): {
        "description": "Benchmark-owned lane. Compares the released session identifiers carried by "
                       "returned units against scorer-only gold support sessions. No text, no judge.",
        "streams": [str(Stream.RETRIEVAL)],
        "requires_reader": False,
    },
}

METRIC_STREAMS: dict[str, str] = {
    "exact_support_hit_at_k": str(Stream.RETRIEVAL),
    "exact_support_log_rank_at_k": str(Stream.RETRIEVAL),
    "exact_support_first_rank": str(Stream.RETRIEVAL),
    "dynamic_answer_accuracy": str(Stream.ANSWER_READER),
    "static_answer_accuracy": str(Stream.ANSWER_READER),
    "conditional_answer_accuracy": str(Stream.ANSWER_READER),
    "update_awareness_and_order_consistency_score": str(Stream.ANSWER_READER),
    "conflict_recognition_score": str(Stream.ANSWER_READER),
    "questions_total": str(Stream.DATASET_VALIDATION),
    "units_ingested": str(Stream.DATASET_VALIDATION),
    "boundary_violations": str(Stream.DIAGNOSTIC),
}


def legal_stream(metric: str, stream: Stream) -> None:
    expected = METRIC_STREAMS.get(metric)
    if expected is None:
        raise ReportingError(f"unknown metric {metric!r}; the MemConflict metric registry is closed")
    if expected != str(stream):
        raise ReportingError(
            f"{metric} may only be read from {expected}, not {stream}. "
            "Answer-level and retrieval-level evidence are different measurements."
        )


# --- field registry -------------------------------------------------------
# Public: what a memory product may legitimately see, in the order upstream
# presents it. Scorer-only: what exists solely to grade the answer.
PUBLIC_INPUT_FIELDS: dict[str, str] = {
    "ID": "persona identifier, needed to isolate one run per persona",
    "Fixed_Profile": "profile known before the interaction begins",
    "Dynamic_Profile": "initial profile state; later sessions update it in dialogue",
    "Preference_Profile": "initial preference state",
    "Personality": "persona colour, present before interaction",
    "Life_Goal": "persona colour, present before interaction",
    "Others_Profile": "third-party profiles the dialogue refers to",
    "Full_Session_Chain[].Session_ID": "chronological session identifier",
    "Full_Session_Chain[].Date": "session date, the only timestamp a product may stamp",
    "Full_Session_Chain[].Session_Dialogue": "the conversation itself; the ingestion surface",
}

SCORER_ONLY_FIELDS: dict[str, str] = {
    "Full_Session_Chain[].Session_Questions[].answer": "gold answer",
    "Full_Session_Chain[].Session_Questions[].conflict_type": "conflict label; upstream gives it to the scorer, not to the system",
    "Full_Session_Chain[].Session_Questions[].ability_target": "construction label",
    "Full_Session_Chain[].Session_Questions[].difficulty": "construction label",
    "Full_Session_Chain[].Updated_Attributes": "before/after truth for dynamic conflicts",
    "Full_Session_Chain[].Revealed_Attributes": "construction metadata for the initial reveal",
    "Full_Session_Chain[].Static_Conflict_Information": "conflict roles and truth values",
    "Full_Session_Chain[].Conditional_Conflict_Information": "rule identities, items and conditions",
    "Full_Session_Chain[].Others_Dynamic_Information": "third-party construction metadata",
    "Full_Session_Chain[].Question_Trigger_Types": "why this session carries questions",
    "Full_Session_Chain[].Event_Types": "construction labels",
    "Full_Session_Chain[].Session_Outline": "generator instruction for the dialogue",
    "Full_Session_Chain[].Session_Type": "construction label naming the session's role",
    "metadata": "generator seed",
    "token_cost": "generation cost accounting",
}

_SCORER_ONLY_KEYS = frozenset(
    path.split("].")[-1].split(".")[-1].replace("[]", "") for path in SCORER_ONLY_FIELDS
) | {"answer", "conflict_type", "ability_target", "difficulty", "Session_Questions"}

# The question text itself is public: upstream supplies it to the system.
PUBLIC_QUESTION_FIELDS = frozenset({"question", "question_id"})


@dataclass(frozen=True)
class Unit:
    """One ingestible dialogue turn, carrying only released identifiers."""
    persona_id: str
    session_id: int
    session_index: int
    turn_index: int
    message_index: int
    role: str
    text: str
    date: str

    @property
    def provenance_id(self) -> str:
        return f"{self.persona_id}|S{self.session_id}|T{self.turn_index}|M{self.message_index}"


@dataclass(frozen=True)
class Question:
    """The public half of a question. The gold answer is deliberately absent."""
    persona_id: str
    session_id: int
    session_index: int
    question_id: str
    text: str

    @property
    def key(self) -> str:
        return f"{self.persona_id}|S{self.session_id}|{self.question_id}"


@dataclass(frozen=True)
class Gold:
    """Scorer-only. Never hand this to a product."""
    key: str
    conflict_type: str
    answer: str
    support_sessions: frozenset[int] | None
    support_status: str
    support_reason: str


def load_personas(path: Path | None = None) -> list[dict]:
    target = path or DATASET
    if not target.exists():
        raise ReportingError(f"pinned MemConflict dataset missing: {target}")
    personas = []
    with target.open() as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                personas.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ReportingError(f"{target}: line {number} is not valid JSON: {exc}") from exc
    if not personas:
        raise ReportingError(f"{target}: parsed zero personas")
    return personas


def dataset_sha256(path: Path | None = None) -> str:
    target = path or DATASET
    if not target.exists():
        raise ReportingError(f"pinned MemConflict dataset missing: {target}")
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _classify_message(message: Any) -> tuple[str, str] | str:
    """Return (role, content) for a well-formed message, or an anomaly label.

    The released file contains a small number of malformed messages. They are
    excluded from ingestion and COUNTED; they are never dropped silently, because
    a quietly shrinking corpus is indistinguishable from a product that forgot.
    """
    if not isinstance(message, Mapping):
        return "message_is_not_an_object"
    role, content = message.get("role"), message.get("content")
    if isinstance(role, str) and isinstance(content, str) and content:
        return role, content
    if role is not None and content is None:
        return "missing_content"
    if content is not None and role is None:
        return "missing_role"
    return "role_and_content_absent"


def parse_dialogue(persona: Mapping[str, Any]) -> tuple[list["Unit"], list[dict]]:
    """Split every released dialogue message into ingestible units and counted anomalies."""
    units: list[Unit] = []
    anomalies: list[dict] = []
    for session_index, session in enumerate(persona["Full_Session_Chain"]):
        dialogue = session.get("Session_Dialogue") or {}
        for turn_name, messages in dialogue.items():
            match = re.fullmatch(r"dialogue_turn_(\d+)", turn_name)
            if match is None:
                raise ReportingError(f"unexpected dialogue turn key {turn_name!r}")
            turn_index = int(match.group(1))
            if not isinstance(messages, list):
                raise ReportingError(f"dialogue turn {turn_name} is not a list")
            for message_index, message in enumerate(messages, start=1):
                outcome = _classify_message(message)
                if isinstance(outcome, str):
                    anomalies.append({
                        "persona_id": persona["ID"], "session_id": session["Session_ID"],
                        "turn": turn_index, "message": message_index, "anomaly": outcome,
                        "released_keys": sorted(message) if isinstance(message, Mapping) else None,
                    })
                    continue
                role, text = outcome
                units.append(Unit(persona_id=persona["ID"], session_id=session["Session_ID"],
                                  session_index=session_index, turn_index=turn_index,
                                  message_index=message_index, role=role, text=text,
                                  date=session["Date"]))
    return units, anomalies


def ingestion_units(persona: Mapping[str, Any]) -> list[Unit]:
    """Every well-formed dialogue message, in released order, released identifiers only."""
    return parse_dialogue(persona)[0]


def dialogue_anomalies(persona: Mapping[str, Any]) -> list[dict]:
    return parse_dialogue(persona)[1]


def questions(persona: Mapping[str, Any]) -> list[Question]:
    out: list[Question] = []
    for session_index, session in enumerate(persona["Full_Session_Chain"]):
        for item in session.get("Session_Questions") or []:
            out.append(Question(persona_id=persona["ID"], session_id=session["Session_ID"],
                                session_index=session_index, question_id=item["question_id"],
                                text=item["question"]))
    return out


def allowed_session_indices(question: Question) -> range:
    """Upstream ingests session i, then asks session i's questions. The prefix is inclusive."""
    return range(0, question.session_index + 1)


def assert_within_boundary(question: Question, units: Sequence[Unit]) -> None:
    allowed = allowed_session_indices(question)
    future = sorted({u.session_index for u in units if u.session_index not in allowed})
    if future:
        raise ReportingError(
            f"{question.key}: units from future sessions {future} were offered; "
            f"the allowed prefix ends at session index {question.session_index}"
        )


def assert_public_only(payload: Any, where: str = "payload") -> None:
    """Refuse any scorer-only field on its way into a product."""
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in PUBLIC_QUESTION_FIELDS:
                continue
            if key in _SCORER_ONLY_KEYS:
                raise ReportingError(f"{where}: scorer-only field {key!r} may not reach a product")
            assert_public_only(value, f"{where}.{key}")
    elif isinstance(payload, (list, tuple)):
        for index, value in enumerate(payload):
            assert_public_only(value, f"{where}[{index}]")


# --- gold support, from released identifiers only -------------------------
def _rule_chain(persona: Mapping[str, Any]) -> dict[str, list[tuple[int, str]]]:
    chain: dict[str, list[tuple[int, str]]] = {}
    for session_index, session in enumerate(persona["Full_Session_Chain"]):
        for entry in session.get("Conditional_Conflict_Information") or []:
            rule_id = entry.get("Rule_ID")
            if rule_id:
                chain.setdefault(entry["Conflict_ID"], []).append((session_index, rule_id))
    for conflict_id in chain:
        chain[conflict_id].sort()
    return chain


def gold_for(persona: Mapping[str, Any], question: Question) -> Gold:
    """Map a question to the sessions holding its supporting evidence, or say it cannot be done."""
    session = persona["Full_Session_Chain"][question.session_index]
    item = next(q for q in session["Session_Questions"] if q["question_id"] == question.question_id)
    conflict_type = item["conflict_type"]
    answer = item["answer"]

    if conflict_type == "dynamic_conflict":
        if not (session.get("Updated_Attributes") or []):
            return Gold(question.key, conflict_type, answer, None, str(Status.UNMEASURED),
                        "dynamic question in a session with no released Updated_Attributes")
        return Gold(question.key, conflict_type, answer, frozenset({session["Session_ID"]}),
                    str(Status.PRESENT),
                    "the updated state is established by this session's own released update")

    if conflict_type == "static_conflict":
        point_b = [c for c in session.get("Static_Conflict_Information") or [] if c.get("Role") == "Point_B"]
        if len(point_b) != 1:
            return Gold(question.key, conflict_type, answer, None, str(Status.UNMEASURED),
                        f"{len(point_b)} Point_B entries in the question's session; the conflict is ambiguous")
        conflict_id = point_b[0]["Conflict_ID"]
        truth = [s["Session_ID"] for s in persona["Full_Session_Chain"]
                 for c in (s.get("Static_Conflict_Information") or [])
                 if c.get("Conflict_ID") == conflict_id and c.get("Role") == "Point_A"]
        if len(truth) != 1:
            return Gold(question.key, conflict_type, answer, None, str(Status.UNMEASURED),
                        f"conflict {conflict_id} has {len(truth)} Point_A sessions")
        return Gold(question.key, conflict_type, answer, frozenset(truth), str(Status.PRESENT),
                    f"truth for {conflict_id} was stated in the Point_A session")

    if conflict_type == "conditional_conflict":
        points = [c for c in session.get("Conditional_Conflict_Information") or [] if c.get("Rule_ID")]
        askers = [q for q in session["Session_Questions"] if q["conflict_type"] == "conditional_conflict"]
        if len(points) != 1 or len(askers) != 1:
            return Gold(question.key, conflict_type, answer, None, str(Status.UNMEASURED),
                        f"{len(askers)} conditional questions against {len(points)} released rules in this "
                        "session; which question addresses which rule is not determined by released identifiers")
        chain = _rule_chain(persona).get(points[0]["Conflict_ID"], [])
        position = [i for i, (_, rule_id) in enumerate(chain) if rule_id == points[0]["Rule_ID"]]
        if not position or position[0] == 0:
            return Gold(question.key, conflict_type, answer, None, str(Status.UNMEASURED),
                        "the rule established here has no released predecessor rule")
        predecessor_index = chain[position[0] - 1][0]
        return Gold(question.key, conflict_type, answer,
                    frozenset({persona["Full_Session_Chain"][predecessor_index]["Session_ID"]}),
                    str(Status.PRESENT),
                    f"the question addresses the predecessor rule {chain[position[0] - 1][1]}")

    raise ReportingError(f"unknown conflict_type {conflict_type!r}")


# --- exact-provenance metrics --------------------------------------------
def first_support_rank(returned: Sequence[Unit], gold: Gold) -> Measurement:
    """Rank of the first returned unit whose released session is a gold support session."""
    if gold.support_sessions is None:
        return Measurement.unmeasured(gold.support_reason)
    for rank, unit in enumerate(returned, start=1):
        if unit.session_id in gold.support_sessions:
            return Measurement.measured(rank)
    return Measurement(status=Status.MEASURED_ZERO, count=0,
                       note="no returned unit came from a gold support session")


def hit_at_k(rank: Measurement, k: int) -> Measurement:
    if rank.status is Status.UNMEASURED:
        return Measurement.unmeasured(rank.note)
    value = rank.count or 0
    return Measurement.measured(1 if 1 <= value <= k else 0)


def log_rank_at_k(rank: Measurement, k: int) -> float | None:
    """Upstream's shape: 1/log2(rank+1) inside K, zero outside, undefined when unmeasured."""
    if rank.status is Status.UNMEASURED:
        return None
    value = rank.count or 0
    if 1 <= value <= k:
        from math import log2
        return 1.0 / log2(float(value) + 1.0)
    return 0.0


# --- calibration ----------------------------------------------------------
def calibration_personas(persona_ids: Sequence[str], fraction: int = 5) -> list[str]:
    """Label-blind: every persona whose ID hash falls in one bucket of `fraction`."""
    chosen = [pid for pid in persona_ids
              if int(hashlib.sha256(pid.encode()).hexdigest(), 16) % fraction == 0]
    return sorted(chosen)


def contract_payload() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "upstream": {"repo": UPSTREAM_REPO, "commit": UPSTREAM_COMMIT,
                     "dataset_path": DATASET_RELATIVE_PATH, "dataset_blob": DATASET_BLOB,
                     "dataset_sha256": DATASET_SHA256},
        "public_input_fields": PUBLIC_INPUT_FIELDS,
        "scorer_only_fields": SCORER_ONLY_FIELDS,
        "ingestion_unit": "one dialogue message, identified by persona|session|turn|message",
        "chronology_rule": "upstream ingests session i then asks session i's questions; "
                           "the allowed prefix for a question is sessions 0..i inclusive",
        "query_contract": "the released question text only; no conflict label, no gold answer",
        "provenance_contract": "a returned unit carries released identifiers only and is credited "
                               "by session identity, never by text similarity",
        "top_k": {"primary": UPSTREAM_PRIMARY_TOP_K, "variants": list(UPSTREAM_TOP_K_VALUES)},
        "lanes": LANES,
        "metric_streams": METRIC_STREAMS,
        "missing_semantics": {
            "unmeasured": "no gold support could be derived from released identifiers",
            "measured_zero": "gold support exists and nothing returned matched it",
            "never": "a missing measurement is never reported as zero",
        },
    }


def contract_sha256() -> str:
    return hashlib.sha256(canonical_json(contract_payload()).encode()).hexdigest()
