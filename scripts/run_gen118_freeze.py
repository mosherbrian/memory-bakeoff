"""Gen118: audit and freeze reader-interference-v6. Calls no model, no endpoint.

The leak audit is stricter than Gen116's: it scans the complete MODEL-FACING
input against every string burned by v5, including record ids and the tokens of
canonical values, because reusing half a burned value is still reuse.

Every published number here is computed. Nothing is asserted.
"""
from __future__ import annotations
import hashlib, json, re, collections
from pathlib import Path
from memory_bakeoff import evidence as EV
from memory_bakeoff import reader_interference_v6 as V6
from memory_bakeoff import reader_interference_v4 as V4

ROOT = Path(__file__).resolve().parents[1]
# Every behaviour-bearing surface, including the FUTURE run path. Gen118 bound
# five files and omitted the runner, the request projection, the capture/seal
# path, the retry policy and the evidence-marker logic. A contract that does not
# bind what will run is not a freeze - the control plane said so and was right.
SCIENTIFIC_SOURCES = ("src/memory_bakeoff/reader_interference_v6.py",
                      "src/memory_bakeoff/evidence.py",
                      "tests/test_gen118_reader_v6.py",
                      "tests/test_gen119_run_apparatus.py",
                      "scripts/run_gen118_freeze.py",
                      "scripts/grade_gen118_v6.py",
                      "scripts/verify_gen118_contract.py",
                      "scripts/run_reader_v6.py",
                      # The 37 witnesses for F1-F3 - the defects this generation
                      # headlines - were the one unbound test file, so they could
                      # be weakened after the freeze without invalidating it.
                      # attempt9 exists BECAUSE contract-bound tests drifted,
                      # which makes the asymmetry worth closing. Found by glm-5.3.
                      "tests/test_gen120_evidence_closure.py")
# The four cores burned by Gen110-115, plus every value and answer string observed.
def _burned() -> tuple[str, ...]:
    """Everything v4 and v5 put in front of the reader. Derived, not typed."""
    from memory_bakeoff import reader_interference_v5 as V5
    out = {"branch:vega", "budget:solstice", "oncall:kestrel", "throughput:atlas",
           "vega", "solstice", "kestrel", "atlas", "rota", "gib", "t/s"}
    for c in V5.CORES:
        out.add(c["subject"].split()[1].casefold())
        for v in V5.canonical_values(c).values():
            out.add(v.casefold())
            out.update(w.casefold() for w in v.split())
    return tuple(sorted(out))


EXPOSED = _burned()


def fixture_audit() -> dict:
    fx = V6.build_fixture()
    cases = fx["cases"]
    faces = []          # every model-facing byte
    for c in cases:
        faces.append(V6.project_prompt(c))
    joined = " ".join(faces).casefold()

    reuse = sorted({t for t in EXPOSED if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", joined)})
    from memory_bakeoff import reader_interference_v5 as _V5
    v5_ids = {r["record_id"] for c in _V5.build_fixture()["cases"] for r in c["records"]}
    v6_ids = {r["record_id"] for c in cases for r in c["records"]}
    id_reuse = sorted(v5_ids & v6_ids)
    v5_prompts = {hashlib.sha256(_V5.project_prompt(c).encode()).hexdigest()
                  for c in _V5.build_fixture()["cases"]}
    v6_prompts = {hashlib.sha256(p.encode()).hexdigest() for p in faces}
    prompt_reuse = sorted(v5_prompts & v6_prompts)
    banned_prose = sorted({w for w in V6.BANNED_PROSE
                           if re.search(rf"(?<!\w){w}(?!\w)", joined)})
    # Role words are banned in RECORD content and ids, not in the frozen rule text,
    # which must name the fields. Scan record statements and ids only.
    rec_text = " ".join(f"{r['record_id']} {r['statement']}"
                        for c in cases for r in c["records"]).casefold()
    banned_role = sorted({w for w in V6.BANNED_ROLE
                          if re.search(rf"(?<!\w){w}(?!\w)", rec_text)})

    # Morphology / balance across the 12 cores.
    sym, longer2, larger2, digits = [], 0, 0, 0
    for core in V6.CORES:
        v = V6.canonical_values(core)
        sym.append({"core": core["key"], "v1": v[1], "v2": v[2],
                    "same_token_count": len(v[1].split()) == len(v[2].split()),
                    "len_delta": abs(len(v[1]) - len(v[2])),
                    "shares_head_noun": v[1].split()[0] == v[2].split()[0]})
        longer2 += len(v[2]) > len(v[1])
        larger2 += v[2] > v[1]
        digits += any(ch.isdigit() for ch in v[1] + v[2])

    # Opaque-id leakage: does the revision-2 id sort before the revision-1 id in a
    # way that tracks the role? A perfect 12/0 or 0/12 split would be a leak.
    id2_first = sum(1 for core in V6.CORES
                    if V6.record_id(core["key"], 2) < V6.record_id(core["key"], 1))
    # Does the revision-2 value appear first in context more often than chance?
    order2_first = sum(1 for c in cases if c["records"][0]["effective_revision"] == 2)

    return {
        "cores": len(V6.CORES), "cases": len(cases),
        "unique_case_ids": len({c["case_id"] for c in cases}),
        "unique_prompts": len({hashlib.sha256(p.encode()).hexdigest() for p in faces}),
        "reused_exposed_terms": reuse,
        "reused_record_ids": id_reuse,
        "reused_prompt_hashes": prompt_reuse,
        "verbatim_rule_in_every_prompt": all("copy the ENTIRE value phrase" in p for p in faces),
        "canonicalisation_declared": V6.CANONICALISATION,
        "banned_progression_words_in_model_facing_text": banned_prose,
        "banned_role_words_in_records_or_ids": banned_role,
        "values_containing_digits": digits,
        "revision2_value_longer_count": f"{longer2}/12",
        "revision2_value_lexicographically_larger_count": f"{larger2}/12",
        "revision2_id_sorts_first_count": f"{id2_first}/12",
        "revision2_first_in_context_cases": f"{order2_first}/{len(cases)}",
        "conflict_order_counterbalanced": (
            sum(1 for c in cases if c["condition"] == "CONFLICT_CURRENT_FIRST") ==
            sum(1 for c in cases if c["condition"] == "CONFLICT_STALE_FIRST") == len(V6.CORES)),
        "symmetry": sym,
        "recency_derivable_only_from_frozen_fields": all(
            ("effective_revision" in p and "as_of_revision" in p) for p in faces),
    }


def ontology_audit() -> dict:
    rows = V6._ontology_table()
    classes = {r["answer_class"] for r in rows}
    # Mutual exclusivity: the classifier returns exactly one label per input, so
    # exclusivity is structural. Exhaustiveness is what must be proven.
    unreachable = [c for c in V6.ONTOLOGY if c not in classes]
    return {"ontology": list(V6.ONTOLOGY), "rows": len(rows),
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
        has_c, has_s = V6.value_present(ans, cur), V6.value_present(ans, stale)
        # The old contract had no disposition field, so the adapter reads the
        # free text. This is exactly why it cannot be confirmatory.
        if has_c and has_s:
            cls = V6.RECONCILED_CURRENT if re.search(r"\b(initially|resized)\b", ans, re.I) \
                  and ans.rstrip(".").endswith(cur) else V6.UNRESOLVED_BOTH
        elif has_c:
            cls = V6.CURRENT_ONLY
        elif has_s:
            cls = V6.STALE_ONLY
        else:
            cls = V6.MALFORMED
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


def id_balance_ok(id_first: int, cores: int) -> bool:
    """EXACT, not within one.

    This gate used to read `abs(id_first - cores // 2) > 1`, so 7/12 - the precise
    imbalance attempt1 was superseded for, and the number every handoff since has
    described as "a hard gate that fails closed" - would have PASSED. Every
    published attempt was genuinely 6/12, so no artifact was ever wrong; the GATE
    was weaker than every claim made about it. A tolerance nobody asked for is how
    a declared invariant quietly becomes a preference. Found by glm-5.3 at Gen120.

    It is a named function so its test can call THE GATE. The first control
    asserted against a lambda reimplementing the same rule inside the test, which
    proves only that the test agrees with itself. Found by glm-5.3-flash.
    """
    return id_first == cores // 2


def main() -> None:
    payload = V6.contract_payload()
    payload_with_sources = {**payload, "source_sha256": source_digests()}
    csha = hashlib.sha256(json.dumps(payload_with_sources, sort_keys=True, default=str).encode()).hexdigest()

    fx_audit, on_audit, legacy = fixture_audit(), ontology_audit(), legacy_projection()
    # The Gen118 instruction required id ordering BALANCED across cores. The
    # first freeze reported 7/12 and shipped anyway, because reporting a number
    # is not gating on it. Sol caught that.
    # EVERY published balance invariant is gated, not just the one that was
    # caught. The freeze computed value-length balance, lexicographic balance and
    # the conflict-order counterbalance, PRINTED all three, and shipped on none of
    # them - so a future refreeze could have passed with 8/12 length balance while
    # the report said "balanced". That is the same "reporting a number is not
    # gating on it" failure Gen119 was named for, surviving inside the gate Gen120
    # had just repaired. Found by glm-5.3 at Gen120 round 4.
    cores = len(V6.CORES)
    balances = {
        "id_sorts_first": int(fx_audit["revision2_id_sorts_first_count"].split("/")[0]),
        "value_longer": int(fx_audit["revision2_value_longer_count"].split("/")[0]),
        "value_lexicographically_larger":
            int(fx_audit["revision2_value_lexicographically_larger_count"].split("/")[0]),
    }
    unbalanced = {k: v for k, v in balances.items() if not id_balance_ok(v, cores)}
    id_first = balances["id_sorts_first"]
    hard_fail = (unbalanced
                 or not fx_audit["conflict_order_counterbalanced"]
                 or fx_audit["reused_exposed_terms"] or fx_audit["reused_record_ids"]
                 or fx_audit["reused_prompt_hashes"]
                 or not fx_audit["verbatim_rule_in_every_prompt"]
                 or fx_audit["banned_progression_words_in_model_facing_text"]
                 or fx_audit["banned_role_words_in_records_or_ids"]
                 or fx_audit["values_containing_digits"]
                 or fx_audit["unique_prompts"] != 60
                 or fx_audit["unique_case_ids"] != 60
                 or on_audit["unreachable_classes"])
    if hard_fail:
        raise SystemExit(f"FAIL CLOSED: unbalanced={unbalanced or 'none'} "
                         f"counterbalanced={fx_audit['conflict_order_counterbalanced']} "
                         f"id_balance={fx_audit['revision2_id_sorts_first_count']} "
                         f"fixture or ontology audit failed: "
                         f"{fx_audit['reused_exposed_terms']} "
                         f"{fx_audit['banned_progression_words_in_model_facing_text']} "
                         f"{fx_audit['banned_role_words_in_records_or_ids']} "
                         f"{on_audit['unreachable_classes']}")

    fixture = V6.build_fixture()
    out = EV.next_attempt(ROOT, 118)
    EV.write_evidence(out, "reader_interference_v6_contract.json",
                      {"contract": V6.CONTRACT_VERSION, "contract_sha256": csha,
                       "r1_decision": V6.R1_DECISION,
                       "source_sha256": source_digests(),
                       "exclusions": ["contract_sha256 itself"],
                       "runner": "scripts/run_gen118_freeze.py",
                       "grader": "scripts/grade_gen118_v6.py",
                       "verifier": "scripts/verify_gen118_contract.py"})
    EV.write_evidence(out, "reader_interference_v6_contract_payload.json", payload_with_sources)
    EV.write_evidence(out, "reader_interference_v6_schedule.json",
                      {"contract": V6.CONTRACT_VERSION, "independent_unit": "core",
                       "cores": len(V6.CORES), "cases": len(fixture["cases"]),
                       "unique_prompts": fx_audit["unique_prompts"],
                       "cases_are_not_observations": True, "cases": fixture["cases"]})
    EV.write_evidence(out, "reader_interference_v6_prompt_hashes.json", payload["prompt_sha256"])
    EV.write_evidence(out, "reader_interference_v6_decision_table.json",
                      {"parser": payload["parser_table"], "ontology": payload["ontology_table"],
                       "citation": payload["citation_table"],
                       "success_states": payload["success_states"],
                       "ontology_audit": on_audit})
    EV.write_evidence(out, "reader_interference_v6_integrity_audit.json", fx_audit)
    EV.write_evidence(out, "reader_interference_v6_legacy_development_projection.json", legacy)
    EV.write_evidence(out, "NON_EVIDENCE.json",
                      {"marker": "NON_EVIDENCE",
                       "reason": "Generation 118 froze the v6 candidate protocol and produced no reader result",
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
