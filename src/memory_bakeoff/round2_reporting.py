"""round2-reporting-v1: a fail-closed reporting layer for the Round-2 ledger.

Built after Gen33 exposed that Gen31's lifecycle numbers were never measured:
three SQL queries failed silently and returned plausible empty answers, and a
lifecycle-only failure class was read from the case-level stream, where it can
never appear. Both produced zeros that looked like measurements.

The rules here exist so neither can recur:

* measurement is tri-state - PRESENT, MEASURED_ZERO or UNMEASURED - and a
  missing key, absent stream or failed parse becomes UNMEASURED, never 0;
* every failure class declares the scorer stream it may legally come from, and
  asking the wrong stream raises;
* every count is rebuilt from leaf evidence and reconciled against the stored
  aggregate, with any mismatch fatal and named.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping

from .longitudinal import (FailureClass, LifecycleDisposition, LifecycleEvidence,
                           build_longitudinal_fixture, canonical_json, fixture_sha256,
                           score_lifecycle_state, score_longitudinal_case, scorer_contract_sha256)

CONTRACT_VERSION = "round2-reporting-v1"
EXPECTED_CASES = 20
EXPECTED_CHECKPOINTS = 9
EXPECTED_REPETITIONS = 3


class Stream(StrEnum):
    CASE = "case_scorer"
    LIFECYCLE = "lifecycle_scorer"
    PRODUCT_EVENT = "product_lifecycle_event"
    DIAGNOSTIC = "capability_diagnostic"


class Status(StrEnum):
    PRESENT = "present"
    MEASURED_ZERO = "measured_zero"
    UNMEASURED = "unmeasured"
    UNSUPPORTED = "unsupported"


class ReportingError(RuntimeError):
    """Any integrity failure. Never caught and converted into a default."""


@dataclass(frozen=True)
class Measurement:
    """A count that knows whether it was measured. Never collapses to int."""

    status: Status
    count: int | None = None
    note: str = ""

    @staticmethod
    def measured(count: int, note: str = "") -> "Measurement":
        return Measurement(Status.PRESENT if count else Status.MEASURED_ZERO, count, note)

    @staticmethod
    def unmeasured(note: str) -> "Measurement":
        return Measurement(Status.UNMEASURED, None, note)

    @staticmethod
    def unsupported(note: str) -> "Measurement":
        return Measurement(Status.UNSUPPORTED, None, note)

    def value_or_raise(self) -> int:
        if self.count is None:
            raise ReportingError(f"measurement is {self.status}: {self.note or 'no evidence'}")
        return self.count

    def payload(self) -> dict[str, Any]:
        return {"status": str(self.status), "count": self.count, "note": self.note}


# Canonical registry: every class declares where it may legally come from.
# false_supersession is lifecycle-only; that is the rule Gen31 violated.
_LIFECYCLE_ONLY = {FailureClass.FALSE_SUPERSESSION}
_CASE_CLASSES = {c for c in FailureClass if c not in _LIFECYCLE_ONLY}

REGISTRY: dict[str, dict[str, Any]] = {}
for _c in FailureClass:
    lifecycle_only = _c in _LIFECYCLE_ONLY
    REGISTRY[str(_c)] = {
        "canonical_name": str(_c),
        "legal_streams": [str(Stream.LIFECYCLE)] if lifecycle_only else [str(Stream.CASE), str(Stream.LIFECYCLE)],
        "primary_stream": str(Stream.LIFECYCLE) if lifecycle_only else str(Stream.CASE),
        "zero_meaningful_only_after_stream_validated": True,
        "independently_checkable_against_product_events": lifecycle_only,
        "publication_category": "lifecycle" if lifecycle_only else "case",
    }


def legal_stream(failure_class: str, stream: Stream) -> None:
    entry = REGISTRY.get(failure_class)
    if entry is None:
        raise ReportingError(f"unknown failure class {failure_class!r}; the registry is closed")
    if str(stream) not in entry["legal_streams"]:
        raise ReportingError(
            f"{failure_class} may not be sourced from {stream}; legal streams are {entry['legal_streams']}. "
            "Reading a lifecycle-only class from case totals is the Gen31 defect."
        )


def contract_payload() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "fixture_sha256": fixture_sha256(),
        "scorer_contract_sha256": scorer_contract_sha256(),
        "expected": {"cases": EXPECTED_CASES, "checkpoints": EXPECTED_CHECKPOINTS,
                     "repetitions": EXPECTED_REPETITIONS},
        "streams": [str(s) for s in Stream],
        "statuses": [str(s) for s in Status],
        "registry": REGISTRY,
        "rules": {
            "tri_state_measurement": "missing evidence is UNMEASURED, never integer zero",
            "no_default_zero": "evidence-critical reads never use .get(key, 0)",
            "leaf_rebuild": "counts are rebuilt from cases[].failure_classes and replayed lifecycle state",
            "summaries_are_verification_targets": "stored summary.json is compared against, never read as input",
            "mismatch_is_fatal": "a stored aggregate disagreeing with leaf evidence raises, naming engine/rep/class",
            "helpers_raise": "no helper converts an exception into '', [], {}, 0 or False",
        },
    }


def contract_sha256() -> str:
    return hashlib.sha256(canonical_json(contract_payload()).encode()).hexdigest()


def load_json(path: Path) -> Any:
    """Raise on anything unreadable. Never returns a default."""
    if not path.exists():
        raise ReportingError(f"required evidence file is missing: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ReportingError(f"evidence file is not valid JSON: {path}: {exc}") from exc


def require(mapping: Mapping[str, Any], key: str, where: str) -> Any:
    if key not in mapping:
        raise ReportingError(f"required key {key!r} missing from {where}")
    return mapping[key]


def validate_repetition(evidence: Mapping[str, Any], where: str) -> None:
    cases = require(evidence, "cases", where)
    if len(cases) != EXPECTED_CASES:
        raise ReportingError(f"{where}: expected {EXPECTED_CASES} cases, found {len(cases)}")
    ids = [require(c, "case_id", f"{where} case") for c in cases]
    if len(set(ids)) != len(ids):
        raise ReportingError(f"{where}: duplicate case_id in evidence")
    fixture = build_longitudinal_fixture()
    known = {c.id for c in fixture.cases}
    unknown = sorted(set(ids) - known)
    if unknown:
        raise ReportingError(f"{where}: unknown case ids {unknown}")
    for case in cases:
        for name in require(case, "failure_classes", f"{where} case {case['case_id']}"):
            legal_stream(name, Stream.CASE)
    lifecycle = require(evidence, "lifecycle", where)
    if len(lifecycle) != EXPECTED_CHECKPOINTS:
        raise ReportingError(f"{where}: expected {EXPECTED_CHECKPOINTS} checkpoints, found {len(lifecycle)}")
    for checkpoint, entries in lifecycle.items():
        if not entries:
            raise ReportingError(f"{where}: checkpoint {checkpoint} has empty lifecycle evidence")
        for entry in entries:
            for field in ("canonical_id", "active_current", "historically_recoverable"):
                require(entry, field, f"{where} lifecycle {checkpoint}")


def rebuild_case_totals(evidence: Mapping[str, Any]) -> dict[str, Measurement]:
    counts: dict[str, int] = {name: 0 for name in REGISTRY if str(Stream.CASE) in REGISTRY[name]["legal_streams"]}
    for case in evidence["cases"]:
        for name in case["failure_classes"]:
            legal_stream(name, Stream.CASE)
            counts[name] = counts.get(name, 0) + 1
    return {name: Measurement.measured(count) for name, count in counts.items()}


def replay_lifecycle(evidence: Mapping[str, Any]) -> dict[str, Measurement]:
    """Recompute lifecycle failures by calling the FROZEN scorer on leaf state."""
    fixture = build_longitudinal_fixture()
    counts: dict[str, int] = {name: 0 for name in REGISTRY}
    for checkpoint, entries in evidence["lifecycle"].items():
        observed = [
            LifecycleEvidence(
                canonical_id=entry["canonical_id"],
                active_current=entry["active_current"],
                historically_recoverable=entry["historically_recoverable"],
                disposition=LifecycleDisposition(entry.get("disposition", "unknown")),
            )
            for entry in entries
        ]
        for name in score_lifecycle_state(fixture, checkpoint, observed).failure_classes:
            legal_stream(name, Stream.LIFECYCLE)
            counts[name] = counts.get(name, 0) + 1
    return {name: Measurement.measured(count) for name, count in counts.items()}


def reconcile(stored: Mapping[str, Any] | None, rebuilt: Mapping[str, Measurement],
              where: str, stream: Stream) -> list[str]:
    """Compare a stored aggregate against leaf-derived truth. Mismatch is fatal."""
    if stored is None:
        return [f"{where}: no stored {stream} aggregate to verify against"]
    problems = []
    for name, measurement in rebuilt.items():
        if measurement.count is None:
            continue
        if name in stored and stored[name] != measurement.count:
            problems.append(f"{where}: {stream} {name} stored={stored[name]} recomputed={measurement.count}")
        if name not in stored and measurement.count:
            problems.append(f"{where}: {stream} {name} recomputed={measurement.count} but absent from stored totals")
    if problems:
        raise ReportingError("stored aggregate disagrees with leaf evidence -> " + "; ".join(problems))
    return []
