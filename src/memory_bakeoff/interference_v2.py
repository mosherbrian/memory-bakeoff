"""`interference-v2`: the same experiment, in several independent neighbourhoods.

Gen97 produced four clean curves in **one** semantic neighbourhood: Perseus's
target slid down the ranking until 64 distractors pushed it out, the other three
held their rank, stale-version interference appeared everywhere, and hindsight
returned essentially the whole bank.

Every one of those could be a property of that neighbourhood rather than of the
engines. This fixture is the replication: **several independent semantic cores**,
each carrying the same structure, so a pattern can be seen to recur - or seen to
be a quirk of one vocabulary.

**What is held identical inside every core.** Four load levels (0/4/16/64), the
same current-versus-superseded structure, the same scope and configuration
isolation with a foreign record differing on both axes, and the same retrieval
policy. The only thing that changes between cores is **the subject and its
wording**, and that changes solely as a replication factor.

**Cores are never pooled.** `assert_no_core_pooling` raises on any summary that
averages across them, because the whole point is whether a result recurs, not
what it averages to. A pattern present in one core is `FIXTURE_SPECIFIC` and is
recorded as such.

**The replication questions are declared here, before the fixture is run**, and
hashed with it. Deciding afterwards which pattern counts as replicated is how a
fishing expedition is dressed up as a finding.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from memory_bakeoff.interference import (Case, Fixture, LOAD_LEVELS, MECHANISMS,
                                         Observation, score_case, visible_ids)

FIXTURE_VERSION = "interference-v2"
SCORER_VERSION = "interference-scorer-v1"      # unchanged; only the fixture grows

GENERAL = "REPLICATED_ACROSS_CORES"
PARTIAL = "PARTIAL_REPLICATION"
FIXTURE_SPECIFIC = "FIXTURE_SPECIFIC"
NOT_APPLICABLE = "NOT_APPLICABLE"

# Four independent neighbourhoods. Different subject, different metric, different
# sentence family - identical structure.
CORES = (
    {"id": "throughput:atlas", "subject": "Atlas", "unit": "t/s",
     "current": "Atlas measured 41 t/s after the cache fix.",
     "superseded": "Atlas measured 27 t/s.",
     "query": "Atlas measured throughput",
     "distractor": "Atlas run {n} measured {value} t/s on the {label} bench.",
     "labels": ("staging", "canary", "shadow", "replay", "soak", "smoke",
                "burn-in", "regression"),
     "scope": "server:atlas", "configuration": "A1"},
    {"id": "branch:vega", "subject": "Vega", "unit": "branch",
     "current": "Vega ships from branch release/vega-4.x.",
     "superseded": "Vega ships from branch release/vega-3.x.",
     "query": "Vega release branch",
     "distractor": "Vega topic branch {n} was cut from release/vega-{value}.x "
                   "for the {label} track.",
     "labels": ("hotfix", "backport", "spike", "docs", "infra", "vendor",
                "locale", "telemetry"),
     "scope": "repo:vega", "configuration": "V1"},
    {"id": "oncall:kestrel", "subject": "Kestrel", "unit": "rota",
     "current": "Kestrel escalations route to the platform rota.",
     "superseded": "Kestrel escalations route to the network rota.",
     "query": "Kestrel escalation routing",
     "distractor": "Kestrel incident {n} was handled by the {label} rota in "
                   "week {value}.",
     "labels": ("storage", "database", "edge", "identity", "billing", "search",
                "media", "queue"),
     "scope": "service:kestrel", "configuration": "K1"},
    {"id": "budget:solstice", "subject": "Solstice", "unit": "GiB",
     "current": "Solstice is provisioned with 512 GiB after the resize.",
     "superseded": "Solstice is provisioned with 256 GiB.",
     "query": "Solstice provisioned capacity",
     "distractor": "Solstice pool {n} reserved {value} GiB for the {label} tier.",
     "labels": ("archive", "scratch", "cache", "index", "spill", "staging",
                "backup", "replica"),
     "scope": "cluster:solstice", "configuration": "S1"},
)

FOREIGN_SUFFIX = "-foreign"

# Declared BEFORE the fixture is run, and hashed with it.
REPLICATION_QUESTIONS = {
    "Q1_perseus_rank_declines_with_density": {
        "question": "does perseus's target rank decline with load in every core?",
        "gen97_observation": "rank 2 -> 3/4 -> 5 -> absent, in one core",
        "replicated_if": "the rank is monotonically non-improving with load in "
                         "every core, and the target is lost at the top level in "
                         "every core",
        "fixture_specific_if": "it holds in one core only",
    },
    "Q2_stale_interference_recurs": {
        "question": "does stale-version interference appear across cores and loads?",
        "gen97_observation": "48 of 48 observations, one core",
        "replicated_if": "it appears at every load level of every core, for every "
                         "engine",
        "fixture_specific_if": "any core is free of it",
    },
    "Q3_other_engines_hold_their_shape": {
        "question": "do mem0, agentmemory and hindsight keep their Gen97 curves?",
        "gen97_observation": "mem0 flat at rank 2; agentmemory flat at rank 1; "
                             "hindsight flat at rank 2 with unbounded volume",
        "replicated_if": "each engine's rank is constant across loads in every "
                         "core, at the rank Gen97 recorded",
        "fixture_specific_if": "the shape holds in some cores and not others",
    },
}


def build_fixture(cores: Sequence[Mapping[str, Any]] = CORES,
                  levels: Sequence[int] = LOAD_LEVELS) -> Fixture:
    """One structure, N neighbourhoods. Ids are namespaced by core."""
    observations: list[Observation] = []
    cases: list[Case] = []
    biggest = max(levels)
    for index, core in enumerate(cores):
        tag = f"C{index}"
        core_id, scope, configuration = core["id"], core["scope"], core["configuration"]
        observations.append(Observation(f"{tag}-CUR", core["current"], scope,
                                        configuration, "current", core_id))
        observations.append(Observation(f"{tag}-SUP", core["superseded"], scope,
                                        configuration, "superseded", core_id))
        observations.append(Observation(
            f"{tag}-FOR", core["current"].replace(core["subject"], "Umbra"),
            scope + FOREIGN_SUFFIX, configuration + FOREIGN_SUFFIX, "foreign", core_id))
        for n in range(biggest):
            label = core["labels"][n % len(core["labels"])]
            observations.append(Observation(
                f"{tag}-D{n:03d}",
                core["distractor"].format(n=n, value=20 + (n % 17), label=label),
                scope, configuration, "distractor", core_id))
        for level in levels:
            cases.append(Case(f"{tag}-IQ{level:03d}", core["query"], core_id, scope,
                              configuration, level,
                              expected=(f"{tag}-CUR",),
                              prohibited_stale=(f"{tag}-SUP",),
                              prohibited_foreign=(f"{tag}-FOR",)))
    return Fixture(tuple(observations), tuple(cases))


def visible_ids(fixture: Fixture, case: Case) -> tuple[str, ...]:
    """What the store holds for this case: THIS core's records only.

    The v1 helper takes every non-distractor record plus the first `load`
    distractors globally, which across several cores would ingest another
    neighbourhood's records - and cross-core bleed would make the whole
    replication uninterpretable. A test caught it here; this is the core-aware
    version and the only one v2 uses.
    """
    core = [o.id for o in fixture.observations
            if o.core == case.core and o.role != "distractor"]
    distractors = [o.id for o in fixture.observations
                   if o.core == case.core and o.role == "distractor"]
    return tuple(core + distractors[:case.load])


def core_of(case: Case) -> str:
    return case.core


def cases_for_core(fixture: Fixture, core_id: str) -> tuple[Case, ...]:
    return tuple(c for c in fixture.cases if c.core == core_id)


def replication_verdict(per_core: Mapping[str, bool]) -> str:
    """A pattern is general only if it holds in every core."""
    if not per_core:
        return NOT_APPLICABLE
    held = [core for core, value in per_core.items() if value]
    if len(held) == len(per_core):
        return GENERAL
    if len(held) <= 1:
        return FIXTURE_SPECIFIC
    return PARTIAL


# Averaging phrasings only. The bare phrase "across cores" is ordinary
# descriptive prose - Gen98's own frozen question asks whether a pattern recurs
# "across cores and loads" - and flagging it caught the contract rather than a
# pooled number. The guard targets the ACT of averaging, not the concept.
POOLING_TERMS = ("all cores combined", "pooled across", "core mean",
                 "mean across cores", "averaged across cores",
                 "average across cores", "overall across cores",
                 "combined across cores")


def assert_no_core_pooling(statement: str) -> None:
    """Cores replicate a result; they do not average into one."""
    lowered = statement.lower()
    found = sorted(term for term in POOLING_TERMS if term in lowered)
    if found:
        raise ValueError(
            f"cores are a replication factor, not samples to average; found {found}. "
            "A pattern either recurs in each core or it is fixture-specific.")


def contract() -> dict[str, Any]:
    return {
        "fixture_version": FIXTURE_VERSION,
        "scorer_version": SCORER_VERSION,
        "cores": [{"id": c["id"], "subject": c["subject"], "scope": c["scope"],
                   "configuration": c["configuration"], "query": c["query"]}
                  for c in CORES],
        "load_levels": list(LOAD_LEVELS),
        "held_identical_within_every_core": [
            "four load levels", "current-versus-superseded structure",
            "a foreign record differing on BOTH scope and configuration",
            "the same retrieval policy"],
        "varies_between_cores": "subject and wording only, as a replication factor",
        "mechanisms": list(MECHANISMS),
        "replication_questions": REPLICATION_QUESTIONS,
        "questions_declared_before_any_run": True,
        "verdicts": {GENERAL: "holds in every core",
                     PARTIAL: "holds in some cores and not others",
                     FIXTURE_SPECIFIC: "holds in one core only - a property of that "
                                       "neighbourhood, not of the engine"},
        "no_core_pooling": "cores are never averaged; assert_no_core_pooling raises",
        "frozen_before_any_engine_run": True,
    }


def contract_sha256() -> str:
    return hashlib.sha256(
        json.dumps(contract(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
