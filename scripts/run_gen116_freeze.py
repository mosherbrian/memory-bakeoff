"""Gen116: audit and freeze reader-interference-v5. Calls no model, no endpoint.

Every published number here is computed. Nothing is asserted.
"""
from __future__ import annotations
import hashlib, json, re, collections
from pathlib import Path
from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference_v5 as V5
from memory_bakeoff import reader_interference_v4 as V4

ROOT = Path(__file__).resolve().parents[1]
SCIENTIFIC_SOURCES = ("src/memory_bakeoff/reader_interference_v5.py",
                      "scripts/run_gen116_freeze.py",
                      "scripts/grade_gen116_v5.py",
                      "scripts/verify_gen116_contract.py")
# The four cores burned by Gen110-115, plus every value and answer string observed.
EXPOSED = ("branch:vega", "budget:solstice", "oncall:kestrel", "throughput:atlas",
           "vega", "solstice", "kestrel", "atlas", "release/vega", "gib", "t/s",
           "rota", "cache fix", "resize", "provisioned", "escalations", "throughput")


def fixture_audit() -> dict:
    fx = V5.build_fixture()
    cases = fx["cases"]
    faces = []          # every model-facing byte
    for c in cases:
        faces.append(V5.project_prompt(c))
    joined = " ".join(faces).casefold()

    reuse = sorted({t for t in EXPOSED if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", joined)})
    banned_prose = sorted({w for w in V5.BANNED_PROSE
                           if re.search(rf"(?<!\w){w}(?!\w)", joined)})
    # Role words are banned in RECORD content and ids, not in the frozen rule text,
    # which must name the fields. Scan record statements and ids only.
    rec_text = " ".join(f"{r['record_id']} {r['statement']}"
                        for c in cases for r in c["records"]).casefold()
    banned_role = sorted({w for w in V5.BANNED_ROLE
                          if re.search(rf"(?<!\w){w}(?!\w)", rec_text)})

    # Morphology / balance across the 12 cores.
    sym, longer2, larger2, digits = [], 0, 0, 0
    for core in V5.CORES:
        v = V5.canonical_values(core)
        sym.append({"core": core["key"], "v1": v[1], "v2": v[2],
                    "same_token_count": len(v[1].split()) == len(v[2].split()),
                    "len_delta": abs(len(v[1]) - len(v[2])),
                    "shares_head_noun": v[1].split()[0] == v[2].split()[0]})
        longer2 += len(v[2]) > len(v[1])
        larger2 += v[2] > v[1]
        digits += any(ch.isdigit() for ch in v[1] + v[2])

    # Opaque-id leakage: does the revision-2 id sort before the revision-1 id in a
    # way that tracks the role? A perfect 12/0 or 0/12 split would be a leak.
    id2_first = sum(1 for core in V5.CORES
                    if V5.record_id(core["key"], 2) < V5.record_id(core["key"], 1))
    # Does the revision-2 value appear first in context more often than chance?
    order2_first = sum(1 for c in cases if c["records"][0]["effective_revision"] == 2)

    return {
        "cores": len(V5.CORES), "cases": len(cases),
        "unique_case_ids": len({c["case_id"] for c in cases}),
        "unique_prompts": len({hashlib.sha256(p.encode()).hexdigest() for p in faces}),
        "reused_exposed_terms": reuse,
        "banned_progression_words_in_model_facing_text": banned_prose,
        "banned_role_words_in_records_or_ids": banned_role,
        "values_containing_digits": digits,
        "revision2_value_longer_count": f"{longer2}/12",
        "revision2_value_lexicographically_larger_count": f"{larger2}/12",
        "revision2_id_sorts_first_count": f"{id2_first}/12",
        "revision2_first_in_context_cases": f"{order2_first}/{len(cases)}",
        "conflict_order_counterbalanced": (
            sum(1 for c in cases if c["condition"] == "CONFLICT_CURRENT_FIRST") ==
            sum(1 for c in cases if c["condition"] == "CONFLICT_STALE_FIRST") == len(V5.CORES)),
        "symmetry": sym,
        "recency_derivable_only_from_frozen_fields": all(
            ("effective_revision" in p and "as_of_revision" in p) for p in faces),
    }


def ontology_audit() -> dict:
    rows = V5._ontology_table()
    classes = {r["answer_class"] for r in rows}
    # Mutual exclusivity: the classifier returns exactly one label per input, so
    # exclusivity is structural. Exhaustiveness is what must be proven.
    unreachable = [c for c in V5.ONTOLOGY if c not in classes]
    return {"ontology": list(V5.ONTOLOGY), "rows": len(rows),
            "classes_reached": sorted(classes), "unreachable_classes": unreachable,
            "exhaustive_over_declared_contract": not unreachable,
            "one_label_per_input": True,
            "note": ("RESOLVED with a null selection and no prior values is incoherent "
                     "rather than unparseable; it is labelled MALFORMED_RESPONSE and "
                     "that choice is recorded here rather than left implicit.")}


def legacy_projection() -> dict:
    """Gen114 replies through the v5 ontology. DEVELOPMENT ONLY, NON_CONFIRMATORY."""
    src = ROOT / "results/gen114/attempt1"
    assert EV.verify(src)["verified"]
    res = [json.loads(l) for l in (src / "reader_responses.jsonl").read_text().splitlines()]
    gen115 = json.loads((ROOT / "results/gen115/attempt4/gen115_conflict_adjudication.json").read_text())
    g115 = {r["call_index"]: r["semantic_category"] for r in gen115["rows"]}

    mapped = {}
    for r in res:
        if not r["condition"].startswith("CONFLICT"):
            continue
        cur, stale = V4.CANONICAL[r["core"]]["current"], V4.CANONICAL[r["core"]]["stale"]
        ans = json.loads(r["text"])["answer"]
        has_c, has_s = V5.value_present(ans, cur), V5.value_present(ans, stale)
        # The old contract had no disposition field, so the adapter reads the
        # free text. This is exactly why it cannot be confirmatory.
        if has_c and has_s:
            cls = V5.RECONCILED_CURRENT if re.search(r"\b(initially|resized)\b", ans, re.I) \
                  and ans.rstrip(".").endswith(cur) else V5.UNRESOLVED_BOTH
        elif has_c:
            cls = V5.CURRENT_ONLY
        elif has_s:
            cls = V5.STALE_ONLY
        else:
            cls = V5.MALFORMED
        mapped[r["call_index"]] = cls

    v5_tally = collections.Counter(mapped.values())
    g115_tally = collections.Counter(g115.values())
    agree = sum(1 for k in mapped if mapped[k] == g115.get(k))
    diffs = [{"call_index": k, "v5": mapped[k], "gen115": g115.get(k)}
             for k in sorted(mapped) if mapped[k] != g115.get(k)]
    return {
        "status": "NON_CONFIRMATORY",
        "why": ("the Gen114 corpus is development-exposed and its response contract "
                "had no disposition field, so this projection needs a text adapter "
                "and can never be evidence for v5"),
        "cells": len(mapped),
        "v5_tally": dict(v5_tally), "gen115_tally": dict(g115_tally),
        "identical_labels": f"{agree}/{len(mapped)}",
        "differences": diffs,
        "restores_retracted_v4_reading": False,
        "note": ("v5 has no AMBIGUOUS class, so the 3 Gen115 AMBIGUOUS cells cannot "
                 "map identically. That difference is reported, not engineered away."),
    }


def source_digests() -> dict:
    out = {}
    for rel in SCIENTIFIC_SOURCES:
        p = ROOT / rel
        out[rel] = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    return out


def main() -> None:
    payload = V5.contract_payload()
    payload_with_sources = {**payload, "source_sha256": source_digests()}
    csha = hashlib.sha256(json.dumps(payload_with_sources, sort_keys=True, default=str).encode()).hexdigest()

    fx_audit, on_audit, legacy = fixture_audit(), ontology_audit(), legacy_projection()
    hard_fail = (fx_audit["reused_exposed_terms"]
                 or fx_audit["banned_progression_words_in_model_facing_text"]
                 or fx_audit["banned_role_words_in_records_or_ids"]
                 or fx_audit["values_containing_digits"]
                 or fx_audit["unique_prompts"] != 60
                 or fx_audit["unique_case_ids"] != 60
                 or on_audit["unreachable_classes"])
    if hard_fail:
        raise SystemExit(f"FAIL CLOSED: fixture or ontology audit failed: "
                         f"{fx_audit['reused_exposed_terms']} "
                         f"{fx_audit['banned_progression_words_in_model_facing_text']} "
                         f"{fx_audit['banned_role_words_in_records_or_ids']} "
                         f"{on_audit['unreachable_classes']}")

    fixture = V5.build_fixture()
    out = EV.next_attempt(ROOT, 116)
    EV.write_evidence(out, "reader_interference_v5_contract.json",
                      {"contract": V5.CONTRACT_VERSION, "contract_sha256": csha,
                       "r1_decision": V5.R1_DECISION,
                       "source_sha256": source_digests(),
                       "exclusions": ["contract_sha256 itself"],
                       "runner": "scripts/run_gen116_freeze.py",
                       "grader": "scripts/grade_gen116_v5.py",
                       "verifier": "scripts/verify_gen116_contract.py"})
    EV.write_evidence(out, "reader_interference_v5_contract_payload.json", payload_with_sources)
    EV.write_evidence(out, "reader_interference_v5_schedule.json",
                      {"contract": V5.CONTRACT_VERSION, "independent_unit": "core",
                       "cores": len(V5.CORES), "cases": len(fixture["cases"]),
                       "unique_prompts": fx_audit["unique_prompts"],
                       "cases_are_not_observations": True, "cases": fixture["cases"]})
    EV.write_evidence(out, "reader_interference_v5_prompt_hashes.json", payload["prompt_sha256"])
    EV.write_evidence(out, "reader_interference_v5_decision_table.json",
                      {"parser": payload["parser_table"], "ontology": payload["ontology_table"],
                       "citation": payload["citation_table"],
                       "success_states": payload["success_states"],
                       "ontology_audit": on_audit})
    EV.write_evidence(out, "reader_interference_v5_integrity_audit.json", fx_audit)
    EV.write_evidence(out, "reader_interference_v5_legacy_development_projection.json", legacy)
    EV.write_evidence(out, "NON_EVIDENCE.json",
                      {"marker": "NON_EVIDENCE",
                       "reason": "Generation 116 froze a candidate protocol and produced no reader result",
                       "reader_calls": 0, "model_calls": 0, "endpoint_calls": 0, "gpu_calls": 0,
                       "may_not_be_upgraded_retrospectively": True})
    print(f"WROTE {out}")
    print(f"  contract_sha256      : {csha}")
    print(f"  cores / cases        : {fx_audit['cores']} / {fx_audit['cases']}")
    print(f"  unique prompts       : {fx_audit['unique_prompts']}")
    print(f"  exposed-term reuse   : {fx_audit['reused_exposed_terms'] or 'none'}")
    print(f"  banned prose / role  : {fx_audit['banned_progression_words_in_model_facing_text'] or 'none'}"
          f" / {fx_audit['banned_role_words_in_records_or_ids'] or 'none'}")
    print(f"  rev2 longer / larger : {fx_audit['revision2_value_longer_count']} / "
          f"{fx_audit['revision2_value_lexicographically_larger_count']}")
    print(f"  rev2 id sorts first  : {fx_audit['revision2_id_sorts_first_count']}")
    print(f"  ontology unreachable : {on_audit['unreachable_classes'] or 'none'}")
    print(f"  legacy projection    : {legacy['identical_labels']} identical, {len(legacy['differences'])} differ")
    print(f"  verify               : {EV.verify(out)}")


if __name__ == "__main__":
    main()
