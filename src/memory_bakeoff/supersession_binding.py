"""`supersession-binding-gen101-v1`: one lifecycle variable, four engines, no deletions.

Gen100 found a native supersession mechanism on all four pinned engines and
established that three were never called. This freezes the **minimal** binding for
each — the smallest change that tells the engine one record replaces another, with
**nothing else moved**.

**Three kinds of mechanism, named rather than blurred.** They are not equivalent,
and reporting them as if they were would manufacture a comparison the interfaces
do not support:

- **`EXPLICIT_LINEAGE`** — the caller names both records and the relationship.
  Only perseus offers this.
- **`STATE_TRANSITION`** — the caller marks the old record's lifecycle state,
  leaving its content intact. hindsight's `update_memory(state="invalidated",
  reason=...)`.
- **`PRODUCT_DECIDES`** — the engine decides for itself, from the writes alone.
  mem0's `add(infer=True)` and agentmemory's write-time rule. The harness selects
  nothing.

**Nothing here deletes.** Deleting the superseded record would make every engine
look perfect and would measure our own delete call. Every binding leaves the old
record in the store; `assert_no_deletion` refuses any binding that names a
destructive operation, and a test drives it with one.

**agentmemory's binding is the empty change.** Its mechanism was already enabled
in Round 2 and stays exactly as it was — for that engine the only thing Gen101
moves is the fixture's ingest order, which is the point.
"""
from __future__ import annotations

from typing import Any, Mapping

CONTRACT_VERSION = "supersession-binding-gen101-v1"

EXPLICIT_LINEAGE = "EXPLICIT_LINEAGE"
STATE_TRANSITION = "STATE_TRANSITION"
PRODUCT_DECIDES = "PRODUCT_DECIDES"

DESTRUCTIVE = ("delete", "erase", "purge", "remove", "drop", "clear", "forget")

BINDINGS = {
    "perseus": {
        "kind": EXPLICIT_LINEAGE,
        "call": "perseus_vault_supersede",
        "arguments": {"from_category": "<current record's category>",
                      "from_key": "record-<current id>",
                      "to_category": "<superseded record's category>",
                      "to_key": "record-<superseded id>",
                      "relationship": "supersedes",
                      "reason": "benchmark: the later observation replaces the earlier"},
        "issued": "once, after both records are written",
        "old_record_retained": True,
        "effect": "the old entity's status becomes 'deprecated'; it is not removed",
        "one_variable": "the frozen Gen29 write path is unchanged; this is the only "
                        "added call",
    },
    "hindsight": {
        "kind": STATE_TRANSITION,
        "call": "memory.update_memory(bank_id, memory_id, state='invalidated', "
                "reason=...)",
        "arguments": {"bank_id": "<the case bank>",
                      "memory_id": "<the superseded observation>",
                      "state": "invalidated",
                      "reason": "benchmark: superseded by the later observation"},
        "issued": "once, after both records are written",
        "old_record_retained": True,
        "effect": "the observation's lifecycle state changes; its text is NOT "
                  "replaced and the record is not deleted",
        "one_variable": "retain and recall are unchanged; only the frozen "
                        "'lifecycle_calls: none' becomes this single call",
        "note": "the only states the pinned build accepts are 'valid' and "
                "'invalidated'; there is no 'supersedes' relationship to name, so "
                "this is a state transition and is labelled as one",
    },
    "mem0": {
        "kind": PRODUCT_DECIDES,
        "call": "Memory.add(..., infer=True)",
        "arguments": {"infer": True},
        "issued": "on every write; the engine decides whether a new statement "
                  "updates an earlier one",
        "old_record_retained": True,
        "effect": "mem0's own consolidation decides; the harness selects nothing "
                  "and issues no update or delete",
        "one_variable": "infer flips from False to True and nothing else moves",
        "note": "Memory.update exists and is NOT used: it would replace the old "
                "record's content, which is the harness deciding the outcome rather "
                "than the engine",
    },
    "agentmemory": {
        "kind": PRODUCT_DECIDES,
        "call": "unchanged - /agentmemory/remember with write-time supersession",
        "arguments": {},
        "issued": "automatically on write, exactly as in Round 2",
        "old_record_retained": True,
        "effect": "isLatest=false; the record stays in KV and leaves the search "
                  "index. Absence from search is not deletion",
        "one_variable": "NOTHING changes for this engine. Its mechanism was already "
                        "exercised; the only variable Gen101 moves for it is the "
                        "fixture's ingest order",
    },
}


def assert_no_deletion(engine: str, binding: Mapping[str, Any]) -> None:
    """Refuse any binding that would manufacture supersession by removing a record."""
    call = str(binding.get("call", "")).lower()
    named = sorted(term for term in DESTRUCTIVE if term in call)
    if named:
        raise ValueError(
            f"{engine}: a supersession binding must not call {named}. Deleting the "
            "superseded record would make every engine look perfect and would "
            "measure the harness's own delete call.")
    if not binding.get("old_record_retained"):
        raise ValueError(f"{engine}: the superseded record must remain in the store")


def kinds() -> dict[str, str]:
    return {engine: entry["kind"] for engine, entry in BINDINGS.items()}


def contract() -> dict[str, Any]:
    for engine, binding in BINDINGS.items():
        assert_no_deletion(engine, binding)
    return {
        "contract_version": CONTRACT_VERSION,
        "kinds": kinds(),
        "mechanism_kinds_are_not_equivalent": "explicit lineage, a state transition "
                                              "and a product decision are three "
                                              "different things; reporting them as "
                                              "one comparison would manufacture an "
                                              "equivalence the interfaces do not "
                                              "support",
        "bindings": BINDINGS,
        "nothing_deletes": "every binding leaves the superseded record in the store; "
                           "assert_no_deletion refuses one that does not",
        "agentmemory_binding_is_empty": "its mechanism was already exercised; the "
                                        "only variable moved for it is the fixture "
                                        "ingest order",
        "frozen_before_any_engine_run": True,
    }
