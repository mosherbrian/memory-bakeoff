"""`interference-v1`: a ruler for what happens as the store fills with near-misses.

Round 2 asked what these systems remember. Round 3 asks a harder question: **what
happens when the store contains many plausible distractors and competing
memories?** Retrieval quality is not a property of a store alone; it is a property
of a store at a given density of things that look like the answer.

This fixture is frozen before any product sees it, and it is built to the four
rules Round 2 paid for:

1. **Every failure class is proved reachable with synthetic controls first.** A
   class that cannot fire reports a zero that means nothing. `controls()` drives
   each one deliberately, and a test asserts all five fire and all five stay
   silent on a correct answer.
2. **Scope and configuration are bound fairly from the start.** Round 2 spent five
   generations discovering that three adapters were never given a scope to
   honour. Here every observation carries both, and the contract requires the
   adapter to bind them on write and query.
3. **Retrieval and reader layers stay apart.** Every case is answerable by a
   store: no case asks for a judgement, and no case can only be passed by
   returning nothing.
4. **No pooled score.** `score_case` returns mechanisms, not a mark, and
   `assert_no_pooled_accuracy` refuses any summary that reports accuracy at scale
   before the mechanisms are decomposed.

**Scale is the independent variable.** Every load level is generated from the
*same semantic core* — the same topic, the same entities, the same wording family
— so the only thing that changes between levels is how many near-misses sit
between the query and the answer. A level that changed the vocabulary as well
would confound density with difficulty.

**Five mechanisms, and the first two are the pair that matters.**

- `TRUE_FORGETTING` — the current fact is absent and the window was **not** filled
  by same-core competitors. The store lost it.
- `DISTRACTOR_DISPLACEMENT` — the current fact is absent and the window is
  **saturated with same-core distractors**. The store did not lose it; the
  competitors crowded it out.

Those two look identical in any pooled count and have completely different fixes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

FIXTURE_VERSION = "interference-v1"
SCORER_VERSION = "interference-scorer-v1"

# Load levels: same semantic core, only the count of near-misses changes.
LOAD_LEVELS = (0, 4, 16, 64)

TRUE_FORGETTING = "true_forgetting"
DISTRACTOR_DISPLACEMENT = "distractor_displacement"
STALE_VERSION_INTERFERENCE = "stale_version_interference"
CROSS_SCOPE_CONTAMINATION = "cross_scope_contamination"
RETRIEVAL_WINDOW_EFFECT = "retrieval_window_effect"

MECHANISMS = (TRUE_FORGETTING, DISTRACTOR_DISPLACEMENT, STALE_VERSION_INTERFERENCE,
              CROSS_SCOPE_CONTAMINATION, RETRIEVAL_WINDOW_EFFECT)


@dataclass(frozen=True)
class Observation:
    id: str
    text: str
    scope: str
    configuration: str
    role: str          # current | superseded | distractor | foreign
    core: str          # the semantic core it was generated from


@dataclass(frozen=True)
class Case:
    id: str
    query: str
    core: str
    scope: str
    configuration: str
    load: int
    expected: tuple[str, ...]
    prohibited_stale: tuple[str, ...] = ()
    prohibited_foreign: tuple[str, ...] = ()


@dataclass(frozen=True)
class Fixture:
    observations: tuple[Observation, ...]
    cases: tuple[Case, ...]

    def by_id(self) -> dict[str, Observation]:
        return {o.id: o for o in self.observations}

    def distractors_for(self, core: str, scope: str, configuration: str) -> set[str]:
        return {o.id for o in self.observations
                if o.core == core and o.scope == scope
                and o.configuration == configuration and o.role == "distractor"}


# One semantic core, stated once, so every level is generated from it.
CORE = {
    "id": "throughput:atlas",
    "subject": "Atlas",
    "query": "Atlas measured throughput",
    "current": "Atlas measured 41 t/s after the cache fix.",
    "superseded": "Atlas measured 27 t/s.",
    # Distractors share the subject, the metric and the sentence shape. They are
    # plausible answers to the same query and wrong ones.
    "distractor_template": "Atlas run {n} measured {value} t/s on the {label} bench.",
    "labels": ("staging", "canary", "shadow", "replay", "soak", "smoke", "burn-in",
               "regression"),
}
FOREIGN_SCOPE = "repo:borealis"
FOREIGN_CONFIGURATION = "B2"


def build_fixture(levels: Sequence[int] = LOAD_LEVELS) -> Fixture:
    """One core, one scope, one configuration, and N same-core distractors."""
    observations: list[Observation] = []
    cases: list[Case] = []
    core, scope, configuration = CORE["id"], "server:atlas", "A1"

    observations.append(Observation("I000", CORE["current"], scope, configuration,
                                    "current", core))
    observations.append(Observation("I001", CORE["superseded"], scope, configuration,
                                    "superseded", core))
    # A foreign record: same core wording, different scope AND configuration.
    observations.append(Observation("I002", CORE["current"].replace("Atlas", "Borealis"),
                                    FOREIGN_SCOPE, FOREIGN_CONFIGURATION, "foreign",
                                    core))

    biggest = max(levels)
    for n in range(biggest):
        label = CORE["labels"][n % len(CORE["labels"])]
        observations.append(Observation(
            f"D{n:03d}",
            CORE["distractor_template"].format(n=n, value=20 + (n % 17), label=label),
            scope, configuration, "distractor", core))

    for level in levels:
        cases.append(Case(f"IQ{level:03d}", CORE["query"], core, scope, configuration,
                          level, expected=("I000",), prohibited_stale=("I001",),
                          prohibited_foreign=("I002",)))
    return Fixture(tuple(observations), tuple(cases))


def visible_ids(fixture: Fixture, case: Case) -> tuple[str, ...]:
    """What the store holds for this case: the core plus exactly `load` distractors."""
    core_ids = [o.id for o in fixture.observations if o.role != "distractor"]
    distractors = [o.id for o in fixture.observations if o.role == "distractor"]
    return tuple(core_ids + distractors[:case.load])


TARGET_ABSENT_UNATTRIBUTED = "target_absent_attribution_not_demonstrable"


def score_case(fixture: Fixture, case: Case, returned: Sequence[str],
               limit: int, *, window_expressible: bool = True) -> dict[str, Any]:
    """Mechanisms, never a mark. Rank and provenance are preserved on the way out.

    `window_expressible=False` is for an engine whose retrieval budget is not a
    result count (Gen96: hindsight expresses `max_tokens` and no limit). For those,
    a returned count equal to the harness limit would describe the harness's
    truncation, not the engine, so `saturated` is not computed and the forgetting /
    displacement split is recorded as `TARGET_ABSENT_UNATTRIBUTED` rather than
    guessed.
    """
    returned = list(returned)
    by_id = fixture.by_id()
    got_expected = [i for i in case.expected if i in returned]
    stale = [i for i in case.prohibited_stale if i in returned]
    foreign = [i for i in case.prohibited_foreign if i in returned]
    distractors = sorted(fixture.distractors_for(case.core, case.scope,
                                                 case.configuration) & set(returned))
    mechanisms: list[str] = []

    if not got_expected:
        if not window_expressible:
            # Gen96: no result-count window, so saturation is the harness's state.
            mechanisms.append(TARGET_ABSENT_UNATTRIBUTED)
        else:
            saturated = len(returned) >= limit
            # The pair that a pooled count would merge.
            if saturated and distractors:
                mechanisms.append(DISTRACTOR_DISPLACEMENT)
            else:
                mechanisms.append(TRUE_FORGETTING)
    if stale:
        mechanisms.append(STALE_VERSION_INTERFERENCE)
    if foreign:
        mechanisms.append(CROSS_SCOPE_CONTAMINATION)
    if got_expected and (stale or foreign):
        expected_rank = min(returned.index(i) for i in got_expected) + 1
        worst = min(returned.index(i) for i in stale + foreign) + 1
        if expected_rank < worst:
            mechanisms.append(RETRIEVAL_WINDOW_EFFECT)

    return {
        "case": case.id,
        "load": case.load,
        "returned": returned,
        "ranks": {i: returned.index(i) + 1 for i in returned if i in by_id},
        "expected_rank": (min(returned.index(i) for i in got_expected) + 1
                          if got_expected else None),
        "distractors_returned": distractors,
        "window_saturated": (len(returned) >= limit) if window_expressible else None,
        "window_expressible": window_expressible,
        "target_present": bool(got_expected),
        "mechanisms": tuple(mechanisms),
        "clean": mechanisms == [],
    }


def controls(fixture: Fixture, limit: int = 5) -> dict[str, Any]:
    """Drive every mechanism deliberately, before any product sees the fixture."""
    case = next(c for c in fixture.cases if c.load == max(LOAD_LEVELS))
    distractors = sorted(fixture.distractors_for(case.core, case.scope,
                                                 case.configuration))[:limit]
    return {
        "clean": score_case(fixture, case, ["I000"], limit),
        TRUE_FORGETTING: score_case(fixture, case, ["D000"], limit),
        DISTRACTOR_DISPLACEMENT: score_case(fixture, case, distractors, limit),
        STALE_VERSION_INTERFERENCE: score_case(fixture, case, ["I000", "I001"], limit),
        CROSS_SCOPE_CONTAMINATION: score_case(fixture, case, ["I000", "I002"], limit),
        # The window effect must fire when the current fact outranks the stale one,
        # and stay silent when it does not - otherwise it is not measuring rank.
        RETRIEVAL_WINDOW_EFFECT: score_case(fixture, case, ["I000", "D000", "I001"],
                                            limit),
        "window_effect_silent_when_stale_outranks": score_case(
            fixture, case, ["I001", "I000"], limit),
        # Displacement must NOT be charged when the window had room to spare.
        "not_displacement_when_window_has_room": score_case(
            fixture, case, ["D000", "D001"], limit),
    }


POOLED_TERMS = ("accuracy at scale", "overall accuracy", "aggregate score",
                "pooled score", "mean accuracy", "score at scale")


def assert_no_pooled_accuracy(statement: str) -> None:
    """Refuse an 'accuracy at scale' number before the mechanisms are decomposed."""
    lowered = statement.lower()
    found = sorted(term for term in POOLED_TERMS if term in lowered)
    if found:
        raise ValueError(
            f"no pooled accuracy before decomposition; found {found}. Round 2 spent "
            "five generations proving that a pooled count hides the mechanism.")


def contract() -> dict[str, Any]:
    return {
        "fixture_version": FIXTURE_VERSION,
        "scorer_version": SCORER_VERSION,
        "question": "what happens when the store contains many plausible "
                    "distractors and competing memories?",
        "independent_variable": "distractor count, generated from ONE semantic core "
                                "so density is the only thing that changes",
        "load_levels": list(LOAD_LEVELS),
        "mechanisms": list(MECHANISMS),
        "the_pair_that_matters": {
            TRUE_FORGETTING: "the current fact is absent and the window was NOT "
                             "filled by same-core competitors",
            DISTRACTOR_DISPLACEMENT: "the current fact is absent and the window is "
                                     "saturated with same-core distractors",
            "why": "identical in any pooled count, and completely different fixes",
        },
        "rules_carried_from_round_2": {
            "reachability_first": "every class is driven by a synthetic control "
                                  "before any product sees the fixture",
            "fair_bindings": "every observation carries a scope and a configuration; "
                             "the adapter must bind both on write and query",
            "layers_apart": "no case asks for a judgement, and none can only be "
                            "passed by returning nothing",
            "no_pooled_score": "score_case returns mechanisms; "
                               "assert_no_pooled_accuracy refuses a scale score",
        },
        "per_case_rank_and_provenance_preserved": True,
        "frozen_before_any_engine_run": True,
    }


ORDER_SENSITIVE_RESOLVERS = "the ingest order is part of the fixture, not an "\
                            "incidental detail; a resolver that returns an order "\
                            "must have that order preserved all the way to the write"


def assert_ingest_order_preserved(resolved: Sequence[str],
                                  written: Sequence[str]) -> None:
    """The records must be WRITTEN in the order the resolver returned them.

    Gen104: `observations_for` took `set(resolver(...))` and then iterated the
    fixture, which silently discarded the resolver's sequence. Gen102 therefore
    ran the v2 order while reporting itself as v3. The set was right and the
    sequence was not, and nothing checked the sequence.
    """
    if list(resolved) != list(written):
        raise ValueError(
            "ingest order was not preserved: resolver returned "
            f"{list(resolved)[:4]}... but records were written "
            f"{list(written)[:4]}... - " + ORDER_SENSITIVE_RESOLVERS)


def assert_hits_map_to_live_identity(hits: Sequence[str],
                                     live_ids: Sequence[str],
                                     mapping: Mapping[str, str]) -> None:
    """Every raw search hit must resolve to a live stored identity.

    A hit that maps to nothing is a provenance break; a hit that maps to a
    retired row means search and the store disagree. Either way the run is not
    reporting the engine.
    """
    unmapped = [h for h in hits if h not in mapping]
    if unmapped:
        raise ValueError(f"search hits resolve to no stored identity: {unmapped}")
    not_live = [h for h in hits if h not in set(live_ids)]
    if not_live:
        raise ValueError(
            f"search hits are not live in the store: {not_live}; search and the "
            "store disagree, so the result is not about the engine")


def ordered_observations(fixture, case, resolver) -> list:
    """The records a case ingests, IN THE RESOLVER'S ORDER.

    Gen104/105: four separate sites had each written this as
    `set(resolver(...))` plus a loop over `fixture.observations`, which
    discards the resolver's sequence. It was harmless while resolver order
    happened to match construction order (v1, v2) and silently wrong the
    moment v3 reordered ingestion on purpose. One helper, so no site can
    re-derive it wrongly again.
    """
    by_id = {o.id: o for o in fixture.observations}
    return [by_id[i] for i in resolver(fixture, case) if i in by_id]
