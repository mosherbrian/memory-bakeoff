"""om-context-production-v2: typed citation contract over frozen Gen27/v1 captures.

v1 is exposed and frozen. This module changes only how a reader citation is
interpreted downstream; it never regenerates an answer, reruns the product, or
touches the v1 fixture, prompt, or scorer.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from . import om_context_production as v1

CONTRACT_VERSION = "om-context-production-v2"
SCORER_VERSION = "om-context-production-scorer-v2"

NATIVE_ID = re.compile(r"^[0-9a-f]{12}$")
CITATION_PREFIXES = {"obs-": "observation", "ref-": "reflection"}
ROLES = ("observation", "reflection")


def contract_sha256() -> str:
    payload = {
        "contract_version": CONTRACT_VERSION,
        "scorer_version": SCORER_VERSION,
        "inherits_fixture": v1.FIXTURE_VERSION,
        "inherits_fixture_sha256": v1.fixture_sha256(),
        "inherits_answer_rules_from": v1.SCORER_VERSION,
        "native_id_pattern": NATIVE_ID.pattern,
        "citation_prefixes": dict(CITATION_PREFIXES),
        "rules": {
            "typed_prefix_must_match_captured_role": True,
            "bare_id_accepted_only_when_roles_agree": True,
            "unknown_prefix_fails_closed": True,
            "unknown_or_malformed_id_fails_closed": True,
            "role_anchor_disagreement_fails_closed": True,
            "no_text_similarity_inference": True,
            "projection_must_reproduce_frozen_support": True,
        },
    }
    return hashlib.sha256(v1.canonical_json(payload).encode()).hexdigest()


def typed_projection(details: dict[str, Any], native_to_anchor: dict[str, str]) -> dict[str, dict[str, set[str]]]:
    """Roles and anchor support taken from one frozen `om.folded` record.

    OM re-emits a promoted observation as a same-id reflection, so an id can
    legitimately hold both roles. Roles are kept apart rather than collapsed.
    """
    observation: dict[str, set[str]] = {}
    for item in details.get("observations", []):
        oid = item.get("id")
        if isinstance(oid, str):
            observation[oid] = {native_to_anchor[x] for x in item.get("sourceEntryIds", []) if x in native_to_anchor}
    reflection: dict[str, set[str]] = {}
    for item in details.get("reflections", []):
        rid = item.get("id")
        deps = item.get("supportingObservationIds", [])
        if isinstance(rid, str):
            reflection[rid] = set().union(*(observation.get(d, set()) for d in deps)) if deps else set()
    return {"observation": observation, "reflection": reflection}


def reproduces_frozen_support(projection: dict[str, dict[str, set[str]]], frozen_support: dict[str, Any]) -> bool:
    """v1 collapsed both roles into one map, reflections last. Must still match."""
    merged = {k: sorted(v) for k, v in projection["observation"].items()}
    merged.update({k: sorted(v) for k, v in projection["reflection"].items()})
    return merged == {k: sorted(v) for k, v in frozen_support.items()}


def resolve_citation(citation: Any, projection: dict[str, dict[str, set[str]]]) -> tuple[frozenset[str] | None, str | None, str | None]:
    """Return (anchors, role, reason). A reason means the citation failed closed."""
    if not isinstance(citation, str) or not citation:
        return None, None, "malformed"
    role: str | None = None
    ident = citation
    for prefix, name in CITATION_PREFIXES.items():
        if citation.startswith(prefix):
            role, ident = name, citation[len(prefix):]
            break
    else:
        if "-" in citation:
            return None, None, "unknown_prefix"
    if not NATIVE_ID.match(ident):
        return None, None, "malformed_id"
    known = [name for name in ROLES if ident in projection[name]]
    if not known:
        return None, None, "unknown_id"
    if role is not None:
        if role not in known:
            return None, None, "type_mismatch"
        return frozenset(projection[role][ident]), role, None
    anchor_sets = {frozenset(projection[name][ident]) for name in known}
    if len(anchor_sets) != 1:
        return None, None, "ambiguous_role"
    return anchor_sets.pop(), "+".join(known), None


def grade_reader_v2(case: v1.ReaderCase, response: dict[str, Any], projection: dict[str, dict[str, set[str]]]) -> dict[str, Any]:
    """Answer rules are inherited from v1 unchanged; only citation resolution differs."""
    answer = str(response.get("answer", "")).lower()
    citations = tuple(response.get("citations", ()))
    resolved: set[str] = set()
    invalid: list[dict[str, str]] = []
    roles: dict[str, str] = {}
    for citation in citations:
        anchors, role, reason = resolve_citation(citation, projection)
        if reason is not None:
            invalid.append({"citation": str(citation), "reason": reason})
            continue
        resolved |= set(anchors)
        roles[citation] = str(role)
    required = ("unknown",) if case.unknown else tuple(x.lower() for x in case.accepted_terms)
    missing = [term for term in required if term not in answer]
    prohibited_hits = [term for term in (x.lower() for x in case.prohibited_terms) if term in answer]
    unsupported = bool(case.support_anchor_ids) and not (set(case.support_anchor_ids) & resolved)
    return {
        "case_id": case.id,
        "pass": not missing and not prohibited_hits and not invalid and not unsupported,
        "missing_required": missing,
        "prohibited_hits": prohibited_hits,
        "invalid_citations": invalid,
        "cited_anchor_ids": sorted(resolved),
        "citation_roles": roles,
        "unsupported_citation": unsupported,
    }


def responses_fingerprint(details: list[dict[str, Any]]) -> str:
    """Identity of the exact stored responses a regrade consumed."""
    payload = [
        {
            "case_id": item["grade"]["case_id"],
            "answer": item["response"]["answer"],
            "citations": list(item["response"]["citations"]),
        }
        for item in details
    ]
    return hashlib.sha256(v1.canonical_json(payload).encode()).hexdigest()


def projection_fingerprint(projection: dict[str, dict[str, set[str]]]) -> str:
    payload = {name: {k: sorted(v) for k, v in projection[name].items()} for name in ROLES}
    return hashlib.sha256(v1.canonical_json(payload).encode()).hexdigest()


def regrade(details: list[dict[str, Any]], projection: dict[str, dict[str, set[str]]]) -> dict[str, Any]:
    """Regrade exact stored reader responses. Never calls a model or the product."""
    cases = {case.id: case for case in v1.CASES}
    graded = []
    for item in details:
        case = cases[item["grade"]["case_id"]]
        graded.append({"grade": grade_reader_v2(case, item["response"], projection), "response": item["response"]})
    passed = sum(1 for g in graded if g["grade"]["pass"])
    return {
        "case_count": len(graded),
        "passed": passed,
        "pass_rate": passed / len(graded) if graded else 0.0,
        "details": graded,
    }
