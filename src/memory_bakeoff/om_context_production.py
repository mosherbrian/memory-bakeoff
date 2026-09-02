"""Frozen Gen27 context-production fixture and model-independent grader.

Only :func:`public_turns` is permitted on the live Pi/OM ingestion path.  The
reader cases and answer contract are deliberately separate from that path.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Iterable

FIXTURE_VERSION = "om-context-production-v1"
SCORER_VERSION = "om-context-production-scorer-v1"


@dataclass(frozen=True)
class Anchor:
    id: str
    text: str
    required_terms: tuple[str, ...]


@dataclass(frozen=True)
class ReaderCase:
    id: str
    question: str
    accepted_terms: tuple[str, ...]
    prohibited_terms: tuple[str, ...] = ()
    unknown: bool = False
    support_anchor_ids: tuple[str, ...] = ()


# These are fictional ordinary engineering notes, not labels supplied to Pi.
ANCHORS: tuple[Anchor, ...] = (
    Anchor("A01", "For the Lantern service, the active packaging profile is ember.", ("ember",)),
    Anchor("A02", "The desktop relay uses a 12-second retry delay; the worker relay uses a 47-second retry delay.", ("12-second", "47-second")),
    Anchor("A03", "The first Lantern p95 measurement was 840 ms.", ("840",)),
    Anchor("A04", "A deployment without draining the queue failed and must not be used as the rollout procedure.", ("without draining", "failed")),
    Anchor("A05", "A temporary environment override named BRIDGE_RELAXED_ACK was enabled while investigating a flaky check.", ("BRIDGE_RELAXED_ACK",)),
    Anchor("A06", "The prior client location was lib/lantern/generated/client.ts.", ("lib/lantern/generated/client.ts",)),
    Anchor("A07", "An archived build note says the release train used wren-1 on 2026-05-11.", ("wren-1", "2026-05-11")),
    Anchor("A08", "The Lantern service changed its active packaging profile from ember to quartz.", ("quartz", "ember")),
    Anchor("A09", "A corrected benchmark says the Lantern p95 was 760 ms, not 840 ms.", ("760", "840")),
    Anchor("A10", "The supported rollout is: drain the queue, deploy, then verify one clean relay handshake.", ("drain", "verify", "handshake")),
    Anchor("A11", "The BRIDGE_RELAXED_ACK workaround was rolled back; it must not be enabled now.", ("rolled back", "BRIDGE_RELAXED_ACK")),
    Anchor("A12", "The old client location lib/lantern/generated/client.ts was invalidated as a stale generated artifact.", ("invalidated", "lib/lantern/generated/client.ts")),
    Anchor("A13", "The current client location is api/lantern/v3/relay_client.ts.", ("api/lantern/v3/relay_client.ts",)),
    Anchor("A14", "The current release train is wren-2; the archived wren-1 note is historical only.", ("wren-2", "historical")),
    Anchor("A15", "The mobile relay keeps a 29-second retry delay, independently of the desktop and worker relays.", ("29-second",)),
    Anchor("A16", "A later audit confirmed that wren-1 was only the 2026-05-11 historical state and did not change the current wren-2 selection.", ("wren-1", "wren-2")),
)

CASES: tuple[ReaderCase, ...] = (
    ReaderCase("Q01", "What packaging profile is active for Lantern now?", ("quartz",), ("ember",), support_anchor_ids=("A08",)),
    ReaderCase("Q02", "What retry delays apply to the desktop and worker relays?", ("12", "47"), support_anchor_ids=("A02",)),
    ReaderCase("Q03", "What is the corrected Lantern p95?", ("760",), ("840",), support_anchor_ids=("A09",)),
    ReaderCase("Q04", "What rollout procedure should be recommended?", ("drain", "deploy", "verify"), ("without draining",), support_anchor_ids=("A10",)),
    ReaderCase("Q05", "Should BRIDGE_RELAXED_ACK be enabled now?", ("no", "rolled back"), ("yes",), support_anchor_ids=("A11",)),
    ReaderCase("Q06", "What is the current Lantern client location?", ("api/lantern/v3/relay_client.ts",), ("lib/lantern/generated/client.ts",), support_anchor_ids=("A13",)),
    ReaderCase("Q07", "What release train was used on 2026-05-11?", ("wren-1",), support_anchor_ids=("A07", "A16")),
    ReaderCase("Q08", "What release train is current now?", ("wren-2",), ("wren-1",), support_anchor_ids=("A14", "A16")),
    ReaderCase("Q09", "What retry delay applies to the mobile relay?", ("29",), ("12", "47"), support_anchor_ids=("A15",)),
    ReaderCase("Q10", "Was the no-drain deployment attempt successful?", ("no", "failed"), ("successful",), support_anchor_ids=("A04",)),
    ReaderCase("Q11", "Who is the Lantern incident commander?", ("UNKNOWN",), unknown=True),
    ReaderCase("Q12", "What is the Lantern production region?", ("UNKNOWN",), unknown=True),
)


def filler_turn(index: int) -> str:
    """Deterministic realistic filler with no anchor vocabulary or answer terms."""
    label = chr(65 + (index - 1) % 26) + chr(65 + ((index - 1) // 26) % 26)
    patch = "\n".join(
        f"+ const frame_{label}_{chr(65 + (n - 1) % 26)} = mergePacket(source_{chr(65 + (n - 1) % 26)}, {{ lane: stable, retry: bounded }});"
        for n in range(1, 76)
    )
    log = "\n".join(
        f"[review-ci] shard={chr(65 + (n - 1) % 26)} cache={'hit' if n%4 else 'miss'} status=ok"
        for n in range(1, 61)
    )
    return f"Review packet {label}: routine refactor and build output. Reply briefly.\n\nPatch:\n{patch}\n\nBuild log:\n{log}\n\nRoutine formatting only."


def public_turns() -> tuple[tuple[str, str | None], ...]:
    """The sole product-facing fixture surface: text plus local anchor mapping."""
    anchors = iter(ANCHORS)
    turns: list[tuple[str, str | None]] = []
    # 40 turns.  Anchors are early/mid, with thirteen complete filler turns
    # after A16 before context capture.
    for number in range(1, 41):
        if number in {3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33}:
            anchor = next(anchors)
            turns.append((f"Engineering status update:\n{anchor.text}\n\nPlease acknowledge this update in one sentence.", anchor.id))
        else:
            turns.append((filler_turn(number), None))
    assert len(turns) == 40
    return tuple(turns)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fixture_payload() -> dict[str, Any]:
    return {"fixture_version": FIXTURE_VERSION, "anchors": [asdict(x) for x in ANCHORS], "cases": [asdict(x) for x in CASES], "turns": [text for text, _ in public_turns()]}


def fixture_sha256() -> str:
    return hashlib.sha256(canonical_json(fixture_payload()).encode()).hexdigest()


def scorer_contract_sha256() -> str:
    payload = {"scorer_version": SCORER_VERSION, "case_fields": list(ReaderCase.__dataclass_fields__), "rules": {"reader_gets_rendered_context_only": True, "unknown_requires_unknown": True, "prohibited_fails": True, "citation_must_map_to_support": True}}
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()


def assert_lexical_isolation() -> None:
    filler = "\n".join(text for text, anchor in public_turns() if anchor is None).lower()
    forbidden = {term.lower() for anchor in ANCHORS for term in anchor.required_terms}
    forbidden |= {case.question.lower() for case in CASES}
    forbidden |= {term.lower() for case in CASES for term in case.accepted_terms + case.prohibited_terms}
    leaks = sorted(token for token in forbidden if token and token in filler)
    if leaks:
        raise ValueError(f"fixture filler leaks anchor/case vocabulary: {leaks}")


def folded_entries(entries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [entry for entry in entries if entry.get("type") == "compaction" and entry.get("details", {}).get("type") == "om.folded"]


def projection_support(compaction: dict[str, Any], native_to_anchor: dict[str, str]) -> dict[str, set[str]]:
    """Map visible OM observations/reflections through native entry IDs."""
    details = compaction.get("details", {})
    support: dict[str, set[str]] = {}
    for item in details.get("observations", []):
        oid = item.get("id")
        source_ids = item.get("sourceEntryIds", [])
        if isinstance(oid, str):
            support[oid] = {native_to_anchor[x] for x in source_ids if x in native_to_anchor}
    for item in details.get("reflections", []):
        rid = item.get("id")
        deps = item.get("supportingObservationIds", [])
        if isinstance(rid, str):
            support[rid] = set().union(*(support.get(dep, set()) for dep in deps)) if deps else set()
    return support


def rendered_context(compaction: dict[str, Any]) -> str:
    value = compaction.get("summary")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("om.folded record lacks a rendered summary")
    return value


def parse_reader_response(content: str) -> dict[str, Any]:
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("reader did not return JSON") from exc
    if not isinstance(value, dict) or not isinstance(value.get("answer"), str) or not isinstance(value.get("citations"), list) or not all(isinstance(x, str) for x in value["citations"]):
        raise ValueError("reader JSON schema invalid")
    return value


def grade_reader(case: ReaderCase, response: dict[str, Any], support: dict[str, set[str]]) -> dict[str, Any]:
    answer = response["answer"].lower()
    citations = tuple(response["citations"])
    cited_anchor_ids = set().union(*(support.get(cid, set()) for cid in citations)) if citations else set()
    required = ("unknown",) if case.unknown else tuple(x.lower() for x in case.accepted_terms)
    prohibited = tuple(x.lower() for x in case.prohibited_terms)
    missing = [term for term in required if term not in answer]
    prohibited_hits = [term for term in prohibited if term in answer]
    invalid_citations = [cid for cid in citations if cid not in support]
    unsupported = bool(case.support_anchor_ids) and not (set(case.support_anchor_ids) & cited_anchor_ids)
    passed = not missing and not prohibited_hits and not invalid_citations and not unsupported
    return {"case_id": case.id, "pass": passed, "missing_required": missing, "prohibited_hits": prohibited_hits, "invalid_citations": invalid_citations, "cited_anchor_ids": sorted(cited_anchor_ids), "unsupported_citation": unsupported}


def reader_prompt(context: str, question: str) -> str:
    return ("Use only the rendered memory below. Return exactly JSON with string keys answer and citations; citations is an array of OM IDs such as obs-... or ref-.... "
            "If the memory does not establish the answer, answer UNKNOWN with an empty citations array.\n\n"
            f"RENDERED_MEMORY:\n{context}\n\nQUESTION:\n{question}")
