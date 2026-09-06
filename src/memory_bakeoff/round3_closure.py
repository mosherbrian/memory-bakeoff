"""`round3-closure-v1`: the Round 3 source registry, and the guards that keep it honest.

Every conclusion carried into the final readout is recorded here with the
generation that produced it, the configuration it holds under, and - the part
that matters most after Gen105 - **what class of evidence still backs it**.

Three evidence classes, and the distinction is not cosmetic:

- `MANIFEST_VERIFIED` - the artefact is under `immutable-evidence-v1` and its
  sha256 is recorded and checkable.
- `COMMITTED_REPORT` - the aggregate is in a committed report and reproduces on
  re-run, but the underlying cells are not manifested.
- `LEGACY_UNMANIFESTED` - the artefact predates the evidence contract and its
  provenance cannot be proven. Gen105's re-runs overwrote the pre-correction
  Gen102 cells, so no old-versus-new cell comparison exists. **Nothing here is
  reconstructed and no manifest is back-dated over it.**

Mechanism kinds are never summed. `EXPLICIT_LINEAGE` (an operator names two
records), `STATE_TRANSITION` (an operator asks for a state change) and
`PRODUCT_DECIDES` (the product acts on its own rule) answer different
questions; a single "supersession score" would be a category error, and
`assert_no_pooled_mechanism_score` raises on the attempt.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "round3-closure-v1"

MANIFEST_VERIFIED = "MANIFEST_VERIFIED"
COMMITTED_REPORT = "COMMITTED_REPORT"
LEGACY_UNMANIFESTED = "LEGACY_UNMANIFESTED"
EVIDENCE_CLASSES = (MANIFEST_VERIFIED, COMMITTED_REPORT, LEGACY_UNMANIFESTED)

EXPLICIT_LINEAGE = "EXPLICIT_LINEAGE"
STATE_TRANSITION = "STATE_TRANSITION"
PRODUCT_DECIDES = "PRODUCT_DECIDES"
MECHANISM_KINDS = (EXPLICIT_LINEAGE, STATE_TRANSITION, PRODUCT_DECIDES)

# --- what Round 3 established -------------------------------------------------
REGISTRY: tuple[dict[str, Any], ...] = (
    {
        "id": "stale-version-interference-replicates",
        "claim": "Every engine co-returns the superseded record alongside the "
                 "current one, at every load, in every core.",
        "source_generation": 99,
        "corroborates": 97,
        "measure": "192 of 192 (4 cores x 4 loads x 3 repetitions x 4 engines)",
        "fixture": "interference-v2",
        "replication": "REPLICATED_ACROSS_CORES",
        "mechanism_kind": None,
        "artifact": "research/PI_REPLICATION_RUN_GEN99.md",
        "evidence": COMMITTED_REPORT,
        "survives": True,
    },
    {
        "id": "perseus-rank-decline-is-fixture-specific",
        "claim": "Perseus losing the target at 64 distractors did NOT reproduce "
                 "in the other cores.",
        "source_generation": 99,
        "corroborates": 97,
        "measure": "Gen98 Q1 verdict",
        "fixture": "interference-v2",
        "replication": "FIXTURE_SPECIFIC",
        "mechanism_kind": None,
        "artifact": "research/PI_REPLICATION_RUN_GEN99.md",
        "evidence": COMMITTED_REPORT,
        "survives": True,
    },
    {
        "id": "engine-shapes-hold-partially",
        "claim": "The other three engines hold their Gen97 shapes in some cores "
                 "and not others; agentmemory holds in two of four.",
        "source_generation": 99,
        "measure": "Gen98 Q3 verdict",
        "fixture": "interference-v2",
        "replication": "PARTIAL_REPLICATION",
        "mechanism_kind": None,
        "artifact": "research/PI_REPLICATION_RUN_GEN99.md",
        "evidence": COMMITTED_REPORT,
        "survives": True,
    },
    {
        "id": "no-engine-lacks-a-supersession-surface",
        "claim": "Three engines were never ASKED to express supersession; one "
                 "does it automatically. No engine lacks a surface.",
        "source_generation": 100,
        "measure": "3 SURFACE_PRESENT_BUT_UNUSED, 1 ALREADY_EXERCISED, "
                   "0 NO_USABLE_SUPERSESSION_SURFACE",
        "fixture": None,
        "mechanism_kind": None,
        "artifact": "research/PI_SUPERSESSION_SURFACE_GEN100.md",
        "evidence": COMMITTED_REPORT,
        "survives": True,
    },
    {
        "id": "perseus-explicit-lineage-works",
        "claim": "Explicit lineage removes stale co-return completely and loses "
                 "no current record.",
        "source_generation": 105,
        "measure": "stale removed 48/48 cells; current lost 0/48; no mechanisms "
                   "scored; rank rises in 41/48 as the stale record leaves the window",
        "fixture": "interference-v3",
        "configuration": "pinned Gen96 retrieval; Gen101 binding, from_key=OLD",
        "mechanism_kind": EXPLICIT_LINEAGE,
        "artifact": "ROUND3_SUPERSESSION_RESULT.md",
        "evidence": LEGACY_UNMANIFESTED,
        "survives": True,
    },
    {
        "id": "hindsight-invalidation-is-recall-identical",
        "claim": "update_memory(state='invalidated') is accepted and recall is "
                 "unchanged - not one of 48 paired cells differs.",
        "source_generation": 105,
        "measure": "stale removed 0/48; identical mechanisms, target_present and "
                   "ranks in every paired cell",
        "fixture": "interference-v3",
        "configuration": "pinned Gen96 retrieval; token budget, not a top-k window",
        "mechanism_kind": STATE_TRANSITION,
        "artifact": "ROUND3_SUPERSESSION_RESULT.md",
        "evidence": LEGACY_UNMANIFESTED,
        "survives": True,
        "note": "An accepted API call is an operation, not proof of an internal "
                "state change. Whether the store changed is NOT established; "
                "that recall is unchanged IS. Same shape as Gen70's query_timestamp.",
    },
    {
        "id": "agentmemory-suppression-is-lexical",
        "claim": "Current truth is kept everywhere; stale suppression fires only "
                 "where the product's lexical threshold is met.",
        "source_generation": 104,
        "measure": "current kept 48/48; stale removed 12/48, all in oncall:kestrel",
        "fixture": "interference-v3",
        "configuration": "unpaired by design - the mechanism is automatic, so an "
                         "OFF arm is a configuration the product does not offer",
        "mechanism_kind": PRODUCT_DECIDES,
        "artifact": "GEN104_RESULT.md",
        "evidence": LEGACY_UNMANIFESTED,
        "survives": True,
    },
    {
        "id": "mem0-arm-unavailable-in-pinned-profile",
        "claim": "infer=True routes through mem0's LLM extractor; the pinned "
                 "profile is deliberately no-LLM.",
        "source_generation": 102,
        "measure": "NOT_AVAILABLE_IN_PINNED_PROFILE - measured, and the runner "
                   "refuses the arm with that reason",
        "fixture": "interference-v3",
        "mechanism_kind": PRODUCT_DECIDES,
        "artifact": "ROUND3_SUPERSESSION_RESULT.md",
        "evidence": COMMITTED_REPORT,
        "survives": True,
        "note": "An unavailable configuration, NOT a failed product score.",
    },
    {
        "id": "ingest-order-blast-radius",
        "claim": "The ingest-order defect could only bite where resolver order "
                 "differs from fixture-construction order.",
        "source_generation": 104,
        "measure": "interference-v1 0/4 cases changed; v2 0/16; v3 16/16",
        "fixture": None,
        "mechanism_kind": None,
        "artifact": "GEN104_RESULT.md",
        "evidence": COMMITTED_REPORT,
        "survives": True,
        "note": "This is why Gen97 and Gen99 stand. It retracts only v3 work.",
    },
)

# --- what was retracted, and by whom -----------------------------------------
RETRACTIONS: tuple[dict[str, Any], ...] = (
    {"claim": "Gen85's reader-order effect", "retracted_by": 85,
     "reason": "a CITE parse defect scored three inline replies as UNPARSED; the "
               "whole attempt was quarantined and the contract version bumped"},
    {"claim": "Gen100's explanation of agentmemory's kestrel behaviour",
     "retracted_by": 102,
     "reason": "the v3 repair was predicted to fix it and did not; the account "
               "predicted the v2 outcome by coincidence, not by mechanism"},
    {"claim": "Gen102's agentmemory result (current record lost in kestrel at "
              "every load)", "retracted_by": 104,
     "reason": "a harness defect, not product behaviour - the current record is "
               "present in 48/48 on the corrected ingest order"},
    {"claim": "Gen103's named suspect (the provenance mapping)",
     "retracted_by": 104,
     "reason": "the mapping was sound; the defect was ingest ORDER. Naming a "
               "likely area is still a guess"},
)

SUPERSESSIONS: tuple[dict[str, Any], ...] = (
    {"superseded": "research/PI_SUPERSESSION_ABLATION_GEN102.md",
     "by": "ROUND3_SUPERSESSION_RESULT.md", "at_generation": 106,
     "reason": "computed from a run whose ingest order was wrong",
     "preserved": True},
)

LIMITATIONS: tuple[dict[str, Any], ...] = (
    {"id": "cell-level-diff-irrecoverable",
     "statement": "Gen105 re-ran corrected arms into the directory the original "
                  "run had used, so the pre-correction Gen102 cell-level "
                  "artefacts were destroyed. Aggregates reproduce exactly; no "
                  "old-versus-new cell diff is recoverable.",
     "not_reconstructed": True, "no_backdated_manifest": True},
    {"id": "supersession-arms-are-legacy-unmanifested",
     "statement": "The Gen104/105 arms were written before immutable-evidence-v1 "
                  "existed, to an unmanifested legacy directory. They are "
                  "COMMITTED_REPORT-grade at best, never MANIFEST_VERIFIED.",
     "not_reconstructed": True, "no_backdated_manifest": True},
    {"id": "hindsight-internal-state-unknown",
     "statement": "Hindsight accepted the invalidation call. Whether its stored "
                  "state changed is not established - only that recall did not.",
     "not_reconstructed": True, "no_backdated_manifest": True},
)

NOT_ESTABLISHED: tuple[str, ...] = (
    "No cross-engine ranking. The engines were never scored against each other "
    "on a common ruler in Round 3, and the budgets differ by design.",
    "No supersession score. Three mechanism kinds are not commensurable.",
    "Nothing about semantic supersession. agentmemory's rule is LEXICAL; the "
    "fixtures never tested paraphrase.",
    "Nothing about these engines outside the pinned Gen96 profiles.",
)

ROUND3_STATUS = "CLOSED"
NEXT_LINE_RECOMMENDATION = {
    "recommendation": "Take the retrieval-layer work no further. The next "
                      "justified line is the READER layer: whether a model "
                      "given a stale-and-current pair actually answers from the "
                      "current one.",
    "why": "Round 3's one general result is that every engine co-returns stale "
           "records (192/192), and only explicit lineage removes them. Whether "
           "that co-return actually harms an answer is untested - Gen85 tried "
           "and was quarantined for a parse defect, so the question is open and "
           "the fixture work already exists.",
    "eligible_but_not_opened": ["P1 SKILL.state / structured operational state",
                                "P2 observational semantic state"],
    "explicitly_not_opened_here": True,
}


# --- guards -------------------------------------------------------------------
def assert_no_pooled_mechanism_score(payload: Any) -> None:
    """Three mechanism kinds may never be reduced to one number.

    STRUCTURAL, not a prose search. The first version scanned the whole payload
    for the phrase "supersession score" and fired on this module's own
    NOT_ESTABLISHED line saying there is no supersession score - the Gen97 and
    Gen100 mistake for the third time. A pooled score would be a numeric FIELD,
    so that is what is checked: no key may name a score, and no single entry may
    carry an aggregate spanning more than one mechanism kind. Prose is free to
    discuss the thing it must not do.
    """
    def walk(node: Any, path: str = "", seen: frozenset = frozenset()) -> None:
        if isinstance(node, Mapping):
            kinds = seen | {v for k, v in node.items()
                            if k == "mechanism_kind" and v in MECHANISM_KINDS}
            for key, value in node.items():
                where = f"{path}.{key}" if path else str(key)
                if "score" in str(key).lower():
                    raise ValueError(
                        f"{where}: a field named as a score pools mechanism "
                        "kinds; EXPLICIT_LINEAGE, STATE_TRANSITION and "
                        "PRODUCT_DECIDES are not commensurable")
                if isinstance(value, (int, float)) and not isinstance(value, bool) \
                        and len(kinds) > 1:
                    raise ValueError(
                        f"{where}: numeric aggregate spans {sorted(kinds)}")
                walk(value, where, kinds)
        elif isinstance(node, (list, tuple)):
            for i, item in enumerate(node):
                walk(item, f"{path}[{i}]", seen)

    walk(payload)


def assert_gen102_is_superseded(payload: Mapping[str, Any]) -> None:
    """Gen102 is preserved history, never the canonical account."""
    entries = payload.get("supersessions") or []
    if not any(e.get("superseded", "").endswith("PI_SUPERSESSION_ABLATION_GEN102.md")
               and e.get("preserved") for e in entries):
        raise ValueError("Gen102 must be recorded as superseded AND preserved")


def assert_legacy_not_called_verified(entries: Iterable[Mapping[str, Any]]) -> None:
    """The Gen104/105 arms are not manifest-verified and must not be labelled so."""
    for entry in entries:
        if entry.get("source_generation") in (104, 105) and \
                entry.get("evidence") == MANIFEST_VERIFIED:
            raise ValueError(
                f"{entry['id']}: Gen104/105 evidence predates immutable-evidence-v1 "
                "and cannot be MANIFEST_VERIFIED")


def assert_v1_v2_not_retracted(payload: Mapping[str, Any]) -> None:
    """The blast radius retracts v3 work only. Gen97 and Gen99 stand."""
    for entry in payload.get("retractions", ()):
        for generation in (97, 99):
            if f"gen{generation}" in str(entry.get("claim", "")).lower():
                raise ValueError(
                    f"Gen{generation} cannot be retracted by a v3-only defect: "
                    "measured 0/4 (v1) and 0/16 (v2) cases changed")


def closure_payload() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "round": 3,
        "status": ROUND3_STATUS,
        "source_registry": list(REGISTRY),
        "retractions": list(RETRACTIONS),
        "supersessions": list(SUPERSESSIONS),
        "limitations": list(LIMITATIONS),
        "not_established": list(NOT_ESTABLISHED),
        "next_line": NEXT_LINE_RECOMMENDATION,
        "evidence_class_counts": {
            klass: sum(1 for e in REGISTRY if e["evidence"] == klass)
            for klass in EVIDENCE_CLASSES
        },
    }
