"""Engine-independent point-in-time truth fixtures and oracle scoring.

This module is deliberately a harness-side ruler, not a provider adapter.  It
models what was known at a replay checkpoint separately from what later
evidence proves about an earlier event.  Future engines receive chronological
prefixes; the oracle is used only to validate this public synthetic fixture.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Iterable


UTC = timezone.utc


class Transition(StrEnum):
    ADD = "ADD"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    SUPERSEDE_CURRENT = "SUPERSEDE_CURRENT"
    CORRECTION = "CORRECTION"
    FAILED_ATTEMPT = "FAILED_ATTEMPT"
    SUCCESSFUL_ATTEMPT = "SUCCESSFUL_ATTEMPT"
    CONCURRENT_SCOPE = "CONCURRENT_SCOPE"
    RETRACTION = "RETRACTION"
    INVALIDATION = "INVALIDATION"


class TargetKind(StrEnum):
    CURRENT = "current_truth"
    SCOPE = "scope_truth"
    AS_OF = "as_of_event_truth"
    HISTORICAL_BELIEF = "historical_belief"
    CORRECTED_HISTORY = "corrected_historical_truth"
    RECOMMENDED_PROCEDURE = "recommended_procedure"
    NEGATIVE_UNKNOWN = "negative_unknown"
    LATE_HISTORY = "late_arriving_history"


class FailureClass(StrEnum):
    FUTURE_LEAKAGE = "future_leakage"
    STALE_PERSISTENCE = "stale_persistence"
    FALSE_PERSISTENCE = "false_persistence"
    HISTORY_ERASURE = "history_erasure"
    SCOPE_COLLAPSE = "scope_collapse"
    FALSE_SUPERSESSION = "false_supersession"
    CORRECTION_FAILURE = "correction_failure"
    BELIEF_TRUTH_CONFUSION = "belief_truth_confusion"
    FAILED_PROCEDURE_ADOPTION = "failed_procedure_adoption"
    LATE_HISTORY_CORRUPTION = "late_history_corruption"
    UNKNOWN_HALLUCINATION = "unknown_hallucination"


@dataclass(frozen=True)
class LongitudinalObservation:
    id: str
    assertion: str
    event_time: datetime
    effective_time: datetime
    reference_time: datetime
    ingestion_order: int
    ingestion_time: datetime
    scope: str
    configuration: str
    transition: Transition
    truth_key: str
    provenance: str = "synthetic_public"
    corrects_id: str | None = None
    procedure_outcome: str | None = None


@dataclass(frozen=True)
class Checkpoint:
    id: str
    ingestion_order: int
    description: str


@dataclass(frozen=True)
class LongitudinalCase:
    id: str
    checkpoint_id: str
    target_kind: TargetKind
    truth_key: str
    query: str
    as_of_event_time: datetime | None = None
    scope: str | None = None
    configuration: str | None = None
    prohibited_ids: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class LongitudinalFixture:
    observations: tuple[LongitudinalObservation, ...]
    checkpoints: tuple[Checkpoint, ...]
    cases: tuple[LongitudinalCase, ...]

    def prefix(self, checkpoint_id: str) -> tuple[LongitudinalObservation, ...]:
        checkpoint = next(c for c in self.checkpoints if c.id == checkpoint_id)
        return tuple(o for o in self.observations if o.ingestion_order <= checkpoint.ingestion_order)


@dataclass(frozen=True)
class LongitudinalScore:
    case_id: str
    expected_ids: tuple[str, ...]
    returned_ids: tuple[str, ...]
    failure_classes: tuple[str, ...]


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=UTC)


def build_longitudinal_fixture() -> LongitudinalFixture:
    """Small, publication-safe corpus with corrections and late-arriving history."""
    O = LongitudinalObservation
    observations = (
        O("L001", "Nimbus on Forge with C1 measured 21 tokens/s.", _dt("2026-01-10T09:00:00"), _dt("2026-01-10T09:00:00"), _dt("2026-01-10T09:00:00"), 1, _dt("2026-01-10T09:01:00"), "server:forge", "C1", Transition.ADD, "throughput:forge:C1"),
        O("L002", "Nimbus on Forge with C2 measured 29 tokens/s.", _dt("2026-01-12T09:00:00"), _dt("2026-01-12T09:00:00"), _dt("2026-01-12T09:00:00"), 2, _dt("2026-01-12T09:01:00"), "server:forge", "C2", Transition.CONFIG_CHANGE, "throughput:forge:C2"),
        # Learned later, but corrects the Jan 10 C1 event rather than becoming a new C1 run.
        O("L003", "Later audit corrected Forge/C1: the valid measurement was 24 tokens/s, not 21.", _dt("2026-01-20T09:00:00"), _dt("2026-01-10T09:00:00"), _dt("2026-01-20T09:00:00"), 3, _dt("2026-01-20T09:01:00"), "server:forge", "C1", Transition.CORRECTION, "throughput:forge:C1", corrects_id="L001"),
        O("L004", "Nimbus on Anvil with C2 measured 33 tokens/s.", _dt("2026-01-22T09:00:00"), _dt("2026-01-22T09:00:00"), _dt("2026-01-22T09:00:00"), 4, _dt("2026-01-22T09:01:00"), "server:anvil", "C2", Transition.CONCURRENT_SCOPE, "throughput:anvil:C2"),
        O("L005", "The first Forge/C2 reproduction procedure omitted the warmup and failed.", _dt("2026-01-23T09:00:00"), _dt("2026-01-23T09:00:00"), _dt("2026-01-23T09:00:00"), 5, _dt("2026-01-23T09:01:00"), "server:forge", "C2", Transition.FAILED_ATTEMPT, "procedure:forge:C2", procedure_outcome="failure"),
        O("L006", "The Forge/C2 reproduction succeeded after a warmup and fixed batch size.", _dt("2026-01-24T09:00:00"), _dt("2026-01-24T09:00:00"), _dt("2026-01-24T09:00:00"), 6, _dt("2026-01-24T09:01:00"), "server:forge", "C2", Transition.SUCCESSFUL_ATTEMPT, "procedure:forge:C2", procedure_outcome="success"),
        O("L007", "Repo Aurora's release branch was release/aurora-1.x.", _dt("2026-02-01T09:00:00"), _dt("2026-02-01T09:00:00"), _dt("2026-02-01T09:00:00"), 7, _dt("2026-02-01T09:01:00"), "repo:aurora", "main", Transition.ADD, "branch:aurora"),
        O("L008", "Repo Aurora moved its release branch to release/aurora-2.x.", _dt("2026-02-10T09:00:00"), _dt("2026-02-10T09:00:00"), _dt("2026-02-10T09:00:00"), 8, _dt("2026-02-10T09:01:00"), "repo:aurora", "main", Transition.SUPERSEDE_CURRENT, "branch:aurora", corrects_id="L007"),
        # This is an old event discovered after the branch change; it must not replace the current branch.
        O("L009", "Recovered CI log: on 2026-02-05 Aurora still built release/aurora-1.x.", _dt("2026-02-05T12:00:00"), _dt("2026-02-05T12:00:00"), _dt("2026-02-15T09:00:00"), 9, _dt("2026-02-15T09:01:00"), "repo:aurora", "main", Transition.ADD, "branch-history:aurora"),
    )
    checkpoints = (
        Checkpoint("CP1", 1, "after initial Forge/C1 observation"),
        Checkpoint("CP2", 2, "after Forge/C2 configuration change"),
        Checkpoint("CP3", 3, "after late correction of Forge/C1"),
        Checkpoint("CP4", 4, "after concurrent Anvil/C2 observation"),
        Checkpoint("CP6", 6, "after failed then successful procedure"),
        Checkpoint("CP8", 8, "after Aurora branch supersession"),
        Checkpoint("CP9", 9, "after late-arriving old Aurora history"),
    )
    C = LongitudinalCase
    cases = (
        C("LQ01", "CP1", TargetKind.CURRENT, "throughput:forge:C1", "What was Forge/C1 throughput?"),
        C("LQ02", "CP2", TargetKind.CURRENT, "throughput:forge:C2", "What is Forge/C2 throughput?", prohibited_ids=("L001",)),
        C("LQ03", "CP2", TargetKind.SCOPE, "throughput:forge:C1", "What remains true for Forge/C1?", prohibited_ids=("L002",)),
        C("LQ04", "CP3", TargetKind.HISTORICAL_BELIEF, "throughput:forge:C1", "At CP1, what did we reasonably believe about Forge/C1?", as_of_event_time=_dt("2026-01-10T10:00:00")),
        C("LQ05", "CP3", TargetKind.CORRECTED_HISTORY, "throughput:forge:C1", "What do we now know was true for Forge/C1 on Jan 10?", as_of_event_time=_dt("2026-01-10T10:00:00"), prohibited_ids=("L001",)),
        C("LQ06", "CP4", TargetKind.SCOPE, "throughput:forge:C2", "What is Forge/C2 throughput, not Anvil/C2?", prohibited_ids=("L004",)),
        C("LQ07", "CP6", TargetKind.RECOMMENDED_PROCEDURE, "procedure:forge:C2", "Which Forge/C2 reproduction procedure should be recommended?", prohibited_ids=("L005",)),
        C("LQ08", "CP8", TargetKind.CURRENT, "branch:aurora", "What is Aurora's current release branch?", prohibited_ids=("L007",)),
        C("LQ09", "CP9", TargetKind.LATE_HISTORY, "branch-history:aurora", "What branch was used by Aurora on Feb 5?"),
        C("LQ10", "CP2", TargetKind.NEGATIVE_UNKNOWN, "unknown:oncall", "Who was on call for Nimbus on Jan 12?"),
    )
    return LongitudinalFixture(observations, checkpoints, cases)


def oracle_expected_ids(fixture: LongitudinalFixture, case: LongitudinalCase) -> tuple[str, ...]:
    """Return fixture truth at one checkpoint; never use this as a contestant."""
    visible = [o for o in fixture.prefix(case.checkpoint_id) if o.truth_key == case.truth_key]
    if case.target_kind is TargetKind.NEGATIVE_UNKNOWN:
        return ()
    if case.target_kind is TargetKind.RECOMMENDED_PROCEDURE:
        return tuple(o.id for o in visible if o.procedure_outcome == "success")
    if case.target_kind is TargetKind.HISTORICAL_BELIEF:
        # Belief excludes later corrections even when evaluated after their ingestion.
        eligible = [o for o in visible if o.transition is not Transition.CORRECTION and (case.as_of_event_time is None or o.event_time <= case.as_of_event_time)]
        return (max(eligible, key=lambda o: o.event_time).id,) if eligible else ()
    if case.target_kind is TargetKind.CORRECTED_HISTORY:
        originals = [o for o in visible if o.transition is not Transition.CORRECTION and (case.as_of_event_time is None or o.effective_time <= case.as_of_event_time)]
        if not originals:
            return ()
        original = max(originals, key=lambda o: o.event_time)
        corrections = [o for o in visible if o.transition is Transition.CORRECTION and o.corrects_id == original.id]
        return ((max(corrections, key=lambda o: o.ingestion_order).id,) if corrections else (original.id,))
    eligible = [o for o in visible if o.transition not in (Transition.CORRECTION, Transition.FAILED_ATTEMPT, Transition.SUCCESSFUL_ATTEMPT)]
    if case.target_kind is TargetKind.AS_OF and case.as_of_event_time:
        eligible = [o for o in eligible if o.event_time <= case.as_of_event_time]
    return (max(eligible, key=lambda o: (o.effective_time, o.ingestion_order)).id,) if eligible else ()


def score_longitudinal_case(fixture: LongitudinalFixture, case: LongitudinalCase, returned_ids: Iterable[str]) -> LongitudinalScore:
    returned = tuple(returned_ids)
    expected = oracle_expected_ids(fixture, case)
    visible_ids = {o.id for o in fixture.prefix(case.checkpoint_id)}
    failures: set[str] = set()
    if any(r not in visible_ids for r in returned):
        failures.add(FailureClass.FUTURE_LEAKAGE)
    if expected and not set(expected).intersection(returned):
        if case.target_kind in (TargetKind.HISTORICAL_BELIEF, TargetKind.AS_OF, TargetKind.LATE_HISTORY):
            failures.add(FailureClass.HISTORY_ERASURE)
        else:
            failures.add("missing_required_truth")
        if case.target_kind is TargetKind.CORRECTED_HISTORY:
            failures.add(FailureClass.CORRECTION_FAILURE)
        if case.target_kind is TargetKind.RECOMMENDED_PROCEDURE:
            failures.add(FailureClass.FAILED_PROCEDURE_ADOPTION)
    if not expected and returned:
        failures.add(FailureClass.UNKNOWN_HALLUCINATION)
    if set(returned).intersection(case.prohibited_ids):
        if case.target_kind is TargetKind.SCOPE:
            failures.add(FailureClass.SCOPE_COLLAPSE)
        elif case.target_kind is TargetKind.HISTORICAL_BELIEF:
            failures.add(FailureClass.BELIEF_TRUTH_CONFUSION)
        elif case.target_kind is TargetKind.RECOMMENDED_PROCEDURE:
            failures.add(FailureClass.FAILED_PROCEDURE_ADOPTION)
        elif case.target_kind is TargetKind.CORRECTED_HISTORY:
            failures.add(FailureClass.FALSE_PERSISTENCE)
        else:
            failures.add(FailureClass.STALE_PERSISTENCE)
    if case.target_kind is TargetKind.CURRENT and "L009" in returned:
        failures.add(FailureClass.LATE_HISTORY_CORRUPTION)
    return LongitudinalScore(case.id, expected, returned, tuple(sorted(str(failure) for failure in failures)))


def aggregate_failure_classes(scores: Iterable[LongitudinalScore]) -> dict[str, int]:
    """Count named failure modes without collapsing them to a single score."""
    counts = {str(kind): 0 for kind in FailureClass}
    for score in scores:
        for failure in score.failure_classes:
            if failure in counts:
                counts[failure] += 1
    return counts
