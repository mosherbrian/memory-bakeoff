"""`correction-late-arrival-semantics-v1`: why a temporal answer was wrong.

Gen68 surfaced an anomaly nobody has explained. Perseus is the only engine that
can recover what was *believed* at a past moment - 6 of 6 - and the only one that
fails on history that *arrives* late. The other three are exactly the opposite.
That is too clean to be noise, and pooling it into one "temporal accuracy" score
would destroy the only interesting thing about it.

The fixture supports the distinction because it contains three different shapes
of revision:

- **a correction with a backdated effective time.** `L005` corrects `L001` on
  20 January about a measurement that was valid on the 10th. Its event time is
  later than its effective time, so a store that files it by when it arrived puts
  it in the wrong place on the timeline.
- **an invalidation chain.** `L012` is invalidated by `L013` and replaced by
  `L014`, all with aligned event and effective times. Nothing is backdated; the
  question is only whether the superseded version survives.
- **late-arriving history.** `L011` describes 5 February but is ingested tenth,
  after facts about the 10th. It is marked historical-only: it was never current.

Each asks a different question of the storage model, so each failure is
attributed to a mechanism rather than to a score:

`overwrote_prior_truth` - the superseded version is simply gone
`belief_truth_confusion` - the newer version answers a question about the older belief
`correction_not_applied` - the corrected value exists but the stale one is served
`late_arrival_not_integrated` - the backfilled fact is not retrievable at all
`late_arrival_misplaced` - it is retrievable but filed by arrival, not by when it happened

Nothing here runs an engine. It reads committed Gen68 per-case records.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "correction-late-arrival-semantics-v1"

OVERWROTE = "overwrote_prior_truth"
BELIEF_CONFUSION = "belief_truth_confusion"
NOT_APPLIED = "correction_not_applied"
NOT_INTEGRATED = "late_arrival_not_integrated"
MISPLACED = "late_arrival_misplaced"
CLEAN = "clean"

# Which revision shape each case exercises. Correction and invalidation are both
# "a later fact revises an earlier one", but only the correction is backdated.
CLUSTER = {
    "LQ04": "correction", "LQ05": "correction", "LQ06": "correction",
    "LQ07": "correction",
    "LQ18": "invalidation", "LQ19": "invalidation",
    "LQ13": "late_arrival", "LQ20": "late_arrival",
}
BACKDATED = {"correction"}


def mechanism(*, kind: str, expected: Iterable[str], prohibited: Iterable[str],
              returned: Iterable[str], cluster: str) -> dict[str, Any]:
    """Attribute one case's outcome to a storage mechanism, not a score."""
    expected, prohibited, returned = set(expected), set(prohibited), set(returned)
    got_expected = bool(expected & returned)
    got_prohibited = bool(prohibited & returned)

    if got_expected and not got_prohibited:
        return {"mechanism": CLEAN, "cluster": cluster,
                "why": "returned what the question asked for and nothing it forbade"}

    if cluster == "late_arrival":
        if got_prohibited and not got_expected:
            return {"mechanism": MISPLACED, "cluster": cluster,
                    "why": "answered with the fact that arrived later; the backfilled "
                           "observation is filed by arrival order, not by when it "
                           "actually happened"}
        if not got_expected:
            return {"mechanism": NOT_INTEGRATED, "cluster": cluster,
                    "why": "the backfilled observation was not retrievable at all"}
        return {"mechanism": MISPLACED, "cluster": cluster,
                "why": "returned the backfilled fact alongside a later one it should "
                       "have excluded"}

    if kind == "historical_belief":
        if got_prohibited:
            return {"mechanism": BELIEF_CONFUSION, "cluster": cluster,
                    "why": "answered a question about a past belief with the version "
                           "that superseded it"}
        return {"mechanism": OVERWROTE, "cluster": cluster,
                "why": "the superseded version was not returned and the newer one was "
                       "not offered either; the prior state appears to be gone"}

    # as_of / corrected-history: the revision itself is what should be served.
    if got_prohibited and not got_expected:
        return {"mechanism": NOT_APPLIED, "cluster": cluster,
                "why": "served the stale version; the revision exists but did not "
                       "take effect for this question"}
    if not got_expected:
        return {"mechanism": OVERWROTE, "cluster": cluster,
                "why": "neither the revision nor the original was returned"}
    return {"mechanism": NOT_APPLIED, "cluster": cluster,
            "why": "returned the revision together with the version it replaced"}


def decompose(records: Iterable[Mapping[str, Any]],
              cases: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Per-case mechanisms plus per-cluster tallies for one engine."""
    per_case, tallies = [], {}
    for record in records:
        case = cases.get(record["case_id"])
        if case is None or record["case_id"] not in CLUSTER:
            continue
        cluster = CLUSTER[record["case_id"]]
        verdict = mechanism(
            kind=case["target_kind"], expected=case["expected_ids"],
            prohibited=case["prohibited_ids"], returned=record["returned_ids"],
            cluster=cluster)
        per_case.append({"case_id": record["case_id"], "kind": case["target_kind"],
                         "returned": sorted(record["returned_ids"]), **verdict})
        bucket = tallies.setdefault(cluster, {})
        bucket[verdict["mechanism"]] = bucket.get(verdict["mechanism"], 0) + 1
    return {"per_case": per_case,
            "by_cluster": {k: dict(sorted(v.items())) for k, v in sorted(tallies.items())}}


def storage_reading(by_cluster: Mapping[str, Mapping[str, int]]) -> dict[str, Any]:
    """Does the pattern look like storage semantics, or like retrieval behaviour?

    Two discriminators, each tied to a clock:

    - **belief retention** - does a question about a past belief ever get answered
      with the version that superseded it? Any `belief_truth_confusion` means the
      superseded state is not addressable.
    - **late-arrival integration** - is a fact that arrived out of order
      retrievable at its own event time? `not_integrated` means it is absent
      entirely; `misplaced` means it is present but filed by arrival.

    An engine can fail these independently, and which one it fails says which
    clock it actually keeps. Requiring a whole cluster to be spotless would hide
    that, because both clusters also contain ordinary retrieval misses.
    """
    def count(cluster: str, name: str) -> int:
        return (by_cluster.get(cluster) or {}).get(name, 0)

    confusion = sum(count(cluster, BELIEF_CONFUSION)
                    for cluster in ("correction", "invalidation"))
    absent = count("late_arrival", NOT_INTEGRATED)
    misfiled = count("late_arrival", MISPLACED)
    retains_belief = confusion == 0
    integrates_late = absent == 0 and misfiled == 0

    if retains_belief and integrates_late:
        reading = "keeps both clocks: superseded belief stays addressable and "\
                  "backfilled facts land at their own event time"
    elif retains_belief:
        reading = "keeps belief history, but a fact that arrives out of order is "\
                  "not addressable at its own event time"
    elif integrates_late:
        reading = "files by event time, so backfill lands correctly, but the "\
                  "superseded version is not addressable"
    else:
        reading = "neither superseded belief nor out-of-order arrival is handled"

    return {"belief_truth_confusions": confusion,
            "late_arrival_not_integrated": absent,
            "late_arrival_misplaced": misfiled,
            "retains_superseded_belief": retains_belief,
            "integrates_late_arrival": integrates_late,
            "reading": reading,
            "caveat": "one fixture, one correction, one invalidation chain and one "
                      "backfilled fact; this names a pattern, it does not prove a "
                      "storage design"}


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "question": "is the Perseus-versus-others split distinct storage semantics or "
                    "just retrieval behaviour?",
        "clusters": {"correction": "later fact, BACKDATED effective time (L001->L005)",
                     "invalidation": "later fact, aligned times (L012->L013->L014)",
                     "late_arrival": "earlier fact ingested out of order (L011)"},
        "mechanisms": [OVERWROTE, BELIEF_CONFUSION, NOT_APPLIED, NOT_INTEGRATED,
                       MISPLACED, CLEAN],
        "not_pooled": "these are different questions of the storage model and must "
                      "not be averaged into one temporal-accuracy score",
        "reads_only": "committed Gen68 per-case records; no engine is run",
    }
