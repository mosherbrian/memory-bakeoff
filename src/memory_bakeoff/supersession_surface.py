"""`supersession-surface-gen100-v1`: is the universal stale co-return a defect, or a question nobody asked?

Gen99 measured stale-version interference in **192 of 192** observations. Before
that is called a ranking defect, one prior question has to be answered, and it is
the question this programme keeps finding decisive: **was the engine ever told
that one observation supersedes another?**

Round 2 spent five generations discovering that three adapters were never given a
scope to honour. The same shape is available here. So each pinned engine is
audited for a **native way to represent "this observation supersedes that one"** -
update, replace, invalidate, version lineage, temporal invalidation, or
equivalent - and the answer is one of three, never a guess:

- **`ALREADY_EXERCISED`** - the mechanism exists and the tested profile used it.
  A stale co-return here is a real product result.
- **`SURFACE_PRESENT_BUT_UNUSED`** - the mechanism exists and the frozen adapter
  deliberately did not call it. The stale co-return says nothing yet about the
  product's supersession behaviour.
- **`NO_USABLE_SUPERSESSION_SURFACE`** - nothing on the interface expresses it.

**Supersession is never manufactured by deleting old records in the harness.**
Deleting the superseded record would make every engine look perfect and measure
nothing but our own delete call. Where a native mechanism exists, the *engine*
performs the retirement; where none exists, that is the finding.
"""
from __future__ import annotations

from typing import Any, Mapping

CONTRACT_VERSION = "supersession-surface-gen100-v1"

ALREADY_EXERCISED = "ALREADY_EXERCISED"
PRESENT_BUT_UNUSED = "SURFACE_PRESENT_BUT_UNUSED"
NO_SURFACE = "NO_USABLE_SUPERSESSION_SURFACE"

SURFACES = {
    "perseus": {
        "mechanism": "perseus_vault_supersede",
        "description": "Create a 'supersedes' relationship from a new fact to an "
                       "old one, setting the old entity's status to 'deprecated'.",
        "parameters": ["from_category", "from_key", "to_category", "to_key",
                       "relationship", "reason", "valid_to_unix_ms"],
        "status": PRESENT_BUT_UNUSED,
        "evidence": "the tool exists on the pinned 2.23.2 MCP surface, and the "
                    "frozen Gen29 adapter contract states write_path = "
                    "'documented operator CLI write (NO supersede/update/delete/"
                    "maintenance)'",
        "explicit_lineage": True,
    },
    "mem0": {
        "mechanism": "Memory.update / Memory.delete, plus inference-time "
                     "consolidation via add(infer=True)",
        "description": "update replaces a memory's content; the inference path "
                       "decides for itself whether a new statement updates an old "
                       "one",
        "parameters": ["memory_id", "data"],
        "status": PRESENT_BUT_UNUSED,
        "evidence": "update/delete/history exist upstream; the frozen Gen32 "
                    "adapter pins infer=False and states lifecycle_calls = 'none; "
                    "no update, delete, reset or history rewrite is issued'",
        "explicit_lineage": False,
    },
    "hindsight": {
        "mechanism": "memory update_memory, clear_memory_observations, "
                     "get_observation_history; documents update_document / "
                     "delete_document; the curate endpoint",
        "description": "content replacement and observation history; no operation "
                       "names a supersedes relationship between two records",
        "parameters": ["bank_id", "memory_id", "document_id"],
        "status": PRESENT_BUT_UNUSED,
        "evidence": "those operations exist on the pinned 0.9.2 client, and the "
                    "frozen Gen31 adapter states lifecycle_calls = 'none; no "
                    "curate, invalidate, revert, update or delete call is issued'",
        "explicit_lineage": False,
    },
    "agentmemory": {
        "mechanism": "write-time supersession during /agentmemory/remember",
        "description": "on write, a new observation retires a near-duplicate "
                       "predecessor: isLatest=false, the record stays in KV and "
                       "leaves the search index",
        "parameters": ["automatic; the caller selects nothing"],
        "status": ALREADY_EXERCISED,
        "evidence": "the frozen Gen33 adapter states write_path = 'native "
                    "/agentmemory/remember with the product's own write-time "
                    "supersession ENABLED', and harness_lifecycle_calls = 'none; "
                    "the harness never selects what to retire'",
        "explicit_lineage": False,
        "rule": {"similarity": "lexical Jaccard over whitespace tokens longer "
                               "than two characters, case- and "
                               "punctuation-sensitive",
                 "threshold": 0.7,
                 "predecessors_per_write": 1,
                 "direction": "the NEW write retires the OLD near-duplicate"},
    },
}


def jaccard(left: str, right: str) -> float:
    """The pinned agentmemory rule, reimplemented to ask whether it can fire."""
    import re

    def tokens(text: str) -> set[str]:
        return {t for t in re.findall(r"[A-Za-z0-9/.\-]+", text) if len(t) > 2}

    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a | b) if (a | b) else 0.0


def can_agentmemory_supersede(current: str, superseded: str) -> dict[str, Any]:
    score = jaccard(current, superseded)
    threshold = SURFACES["agentmemory"]["rule"]["threshold"]
    return {"jaccard": round(score, 3), "threshold": threshold,
            "rule_can_fire": score > threshold}


def verdict() -> dict[str, Any]:
    statuses = {engine: entry["status"] for engine, entry in SURFACES.items()}
    unused = sorted(e for e, s in statuses.items() if s == PRESENT_BUT_UNUSED)
    return {
        "contract_version": CONTRACT_VERSION,
        "statuses": statuses,
        "no_engine_lacks_a_surface": all(s != NO_SURFACE for s in statuses.values()),
        "reading": f"{len(unused)} of 4 engines have a supersession mechanism the "
                   "frozen adapter deliberately did not call, and one exercises its "
                   "own automatically. The 192/192 stale co-return is therefore NOT "
                   "yet a ranking defect for the three unused ones - it is a "
                   "question that was never asked.",
        "agentmemory_exception": "agentmemory's mechanism WAS enabled, so its stale "
                                 "co-return is a real product observation - subject "
                                 "to whether its rule could fire on the data",
        "never_manufacture": "supersession is never simulated by deleting the old "
                             "record in the harness; that would measure our delete "
                             "call and nothing else",
        "no_engine_runs": True,
    }


def explains_gen99_kestrel(fixture, core_id: str, ingest_order: list[str]) -> dict[str, Any]:
    """Does agentmemory's own rule account for the Gen99 kestrel result?

    Gen99 found agentmemory returning ONLY the superseded record in the kestrel
    core, at zero distractors. If the rule can fire there and nowhere else, and
    the current record is written FIRST, then the later write retired the answer -
    a product rule meeting a harness ingest order, not a retrieval failure.
    """
    by_id = fixture.by_id()
    current = next(o for o in fixture.observations
                   if o.core == core_id and o.role == "current")
    superseded = next(o for o in fixture.observations
                      if o.core == core_id and o.role == "superseded")
    fires = can_agentmemory_supersede(current.text, superseded.text)
    positions = {i: ingest_order.index(i) for i in (current.id, superseded.id)
                 if i in ingest_order}
    current_written_first = (positions.get(current.id, 10**6)
                             < positions.get(superseded.id, 10**6))
    return {
        "core": core_id,
        **fires,
        "current_written_first": current_written_first,
        "retires": "the LATER write retires the earlier near-duplicate",
        "explains_absence": bool(fires["rule_can_fire"] and current_written_first),
        "why": "the current record is written first, the superseded record is "
               "written second and is a near-duplicate above threshold, so the "
               "product retires the CURRENT one - correct behaviour under its own "
               "recency rule, on an ingest order the harness chose",
        "harness_or_product": "BOTH: a real product rule meeting a fixture ordering "
                              "that is backwards from the world it models, where "
                              "the superseded fact is written first",
    }
