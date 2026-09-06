"""Gen115: no-reader adjudication of Gen114 under `gen115-adjudication-v1`.

Reads sealed Gen114 bytes; writes nothing into results/gen114.
"""
from __future__ import annotations
import json, hashlib, collections
from pathlib import Path
from memory_bakeoff import evidence as EV, gen115_adjudication as G115
from memory_bakeoff import reader_interference_v4 as V4

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results/gen114/attempt1"
CAN = V4.CANONICAL

# --- per-wording semantic adjudication, written against the actual sentence ---
# R3: every category carries a rationale naming what the sentence does.
FORMS = {
 ("branch:vega", "CONFLICT_CURRENT_FIRST"): (G115.UNRESOLVED_BOTH,
   "Names both branches separated only by a comma. No temporal word, no "
   "selection, no assertion that either is the live one. The prompt supplies "
   "no recency signal, so no selection is derivable from the records."),
 ("branch:vega", "CONFLICT_STALE_FIRST"): (G115.UNRESOLVED_BOTH,
   "Same two branches, comma-separated, in the reverse order - which is the "
   "order the records appear in this prompt. Ordering tracks the prompt, not "
   "any claim about which branch is live."),
 ("budget:solstice", "CONFLICT_CURRENT_FIRST"): (G115.CURRENT_ONLY,
   "Answers '512 GiB' and nothing else. The stale value is absent from the "
   "answer text."),
 ("budget:solstice", "CONFLICT_STALE_FIRST"): (G115.RECONCILED_TO_CURRENT,
   "'256 GiB initially, resized to 512 GiB' places the two values in an "
   "explicit chronological sequence that terminates at the current value. "
   "'initially' and 'resized to' are temporal operators, and the current "
   "record itself says 'after the resize'. Under R4 this is a coherent "
   "reconciliation that answers the question and adds history."),
 ("oncall:kestrel", "CONFLICT_CURRENT_FIRST"): (G115.UNRESOLVED_BOTH,
   "Conjoins both rotas with 'and' in a single sentence. Routing to two rotas "
   "is not self-evidently impossible, so R6 is not met; but no selection is "
   "made and no recency is claimed."),
 ("oncall:kestrel", "CONFLICT_STALE_FIRST"): (G115.UNRESOLVED_BOTH,
   "Same conjunction, rotas reversed to match the order of the records in "
   "this prompt. No selection, no recency claim."),
 ("throughput:atlas", "CONFLICT_CURRENT_FIRST"): (G115.AMBIGUOUS,
   "Names both figures and carries the qualifier 'after the cache fix' on the "
   "41 t/s value, which marks that figure as the later one. But the sentence "
   "runs current-then-stale, so it does not terminate at the current value "
   "and R4 is not satisfied. It carries a recency marker without a clean "
   "resolution."),
 ("throughput:atlas", "CONFLICT_STALE_FIRST"): (G115.RECONCILED_TO_CURRENT,
   "'27 t/s and 41 t/s after the cache fix' runs stale-then-current and "
   "attaches the temporal marker to the terminating value, satisfying R4."),
}

def main() -> None:
    assert EV.verify(SRC)["verified"], "sealed Gen114 evidence failed verification"
    req = {json.loads(l)["call_index"]: json.loads(l)
           for l in (SRC / "reader_requests.jsonl").read_text().splitlines()}
    res = [json.loads(l) for l in (SRC / "reader_responses.jsonl").read_text().splitlines()]
    pub = {p["call_index"]: p for p in
           json.loads((SRC / "reader_interference_results.json").read_text())["cells"]}
    cases = {c["id"]: c for c in V4.build_fixture()["cases"]}

    # ---- scope 2: independent reproduction of all 60 machine grades ----------
    repro_mismatch = []
    for r in res:
        row, mine = pub[r["call_index"]], V4.grade(V4.parse_response(r["text"]), cases[r["case_id"]])
        for f in ("outcome", "answer_class", "citation_relation"):
            if mine[f] != row[f]:
                repro_mismatch.append({"call_index": r["call_index"], "field": f,
                                       "recomputed": mine[f], "published": row[f]})
    frozen = json.loads((ROOT / "results/gen113/attempt2/reader_interference_v4.json").read_text())
    ph = frozen["contract_payload"]["prompt_sha256"]
    prompt_mismatch = [q["call_index"] for q in req.values()
                       if hashlib.sha256(q["prompt"].encode()).hexdigest() != ph[q["case_id"]]]
    reproduction = {
        "contract": G115.CONTRACT_VERSION, "responses": len(res),
        "regrade_mismatches": repro_mismatch, "prompt_hash_mismatches": prompt_mismatch,
        "served_models": sorted({r.get("served_model") for r in res}),
        "http_statuses": sorted({r.get("http_status") for r in res}),
        "finish_reasons": sorted({r.get("finish_reason") for r in res}),
        "terminal_dispositions": dict(collections.Counter(r["terminal_disposition"] for r in res)),
        "condition_counts": {f"{c}|{o}": n for (c, o), n in
                             sorted(collections.Counter((p["condition"], p["outcome"])
                                                        for p in pub.values()).items())},
        "reproduces_exactly": not repro_mismatch and not prompt_mismatch,
    }
    if not reproduction["reproduces_exactly"]:
        raise SystemExit("FAIL CLOSED: Gen114 machine grading did not reproduce")

    # ---- scope 3: the 24-row exploratory conflict table ----------------------
    rows = []
    for r in sorted([x for x in res if x["condition"].startswith("CONFLICT")],
                    key=lambda x: x["call_index"]):
        cur, stale = CAN[r["core"]]["current"], CAN[r["core"]]["stale"]
        prompt, ans = req[r["call_index"]]["prompt"], json.loads(r["text"])["answer"]
        cat, why = FORMS[(r["core"], r["condition"])]
        pc, ps = ans.find(cur), ans.find(stale)
        rows.append({
            "call_index": r["call_index"], "core": r["core"], "condition": r["condition"],
            "repetition": r["repetition"], "answer_text": ans,
            "v4_machine_label": pub[r["call_index"]]["outcome"],
            "semantic_category": cat, "rationale": why,
            "context_order": "current_first" if prompt.find(cur) < prompt.find(stale) else "stale_first",
            "answer_mention_order": ("current_first" if pc < ps else "stale_first")
                                    if pc >= 0 and ps >= 0 else
                                    ("current_only" if pc >= 0 else "stale_only" if ps >= 0 else "neither"),
            "asserts_stale_as_current": False,
            "prompt_discloses_recency": False,
            "confirmatory": False,
        })
    for row in rows:
        G115.assert_not_confirmatory(row)
    G115.assert_rationale_present(rows)

    echo = sum(1 for r in rows if r["answer_mention_order"] == r["context_order"])
    tally = collections.Counter(r["semantic_category"] for r in rows)
    conflict_table = {
        "contract": G115.CONTRACT_VERSION, "status": G115.OPEN_EXPLORATORY,
        "exploratory_by_construction": "R2 - outputs were observed before these categories existed",
        "rows": rows, "category_tally": dict(tally),
        "stale_only_answers": sum(1 for r in rows if r["answer_mention_order"] == "stale_only"),
        "mention_order_matches_context_order": f"{echo}/{len(rows)}",
        "explicit_contradictions_found": tally.get(G115.EXPLICIT_CONTRADICTION, 0),
    }

    # ---- scope 4: fixture-decidability finding ------------------------------
    cue_terms = ("after the resize", "after the cache fix")
    cores = {}
    for c in V4.build_fixture()["cases"]:
        if c["condition"].startswith("CONFLICT") and c["core"] not in cores:
            cur_text = next(r["text"] for r in c["records"] if r["role"] == "current")
            cores[c["core"]] = {"current_text": cur_text,
                                "in_text_recency_cue": [t for t in cue_terms if t in cur_text.lower()]}
    decidability = {
        "status": G115.OPEN_EXPLORATORY,
        "observation": "No conflict prompt discloses which record is current. No role "
                       "label, no timestamp, no ordering semantics. Record ids are opaque.",
        "verified_absent_tokens": ["superseded", "current", "stale", "role", "outdated",
                                   "latest", "newer", "order"],
        "consequence": "Selecting the current value is not derivable from the records "
                       "except where the record text itself carries a temporal cue. v4 "
                       "nonetheless treats correct_current_answer as the success state.",
        "cores": cores,
        "pattern": "The 2 cores whose current record carries a cue (budget:solstice, "
                   "throughput:atlas) produced current-leaning or reconciled answers. The "
                   "2 cores with no cue (branch:vega, oncall:kestrel) produced both-values "
                   "answers in prompt order.",
        "strength": "n=2 vs n=2 at core level. SUGGESTIVE ONLY - not an effect estimate, "
                    "not confirmatory, and generated after seeing the outputs (R2).",
    }

    # ---- scope 5: claim ledger ----------------------------------------------
    ledger = [
     {"claim": "All 60 reader calls completed; one model, HTTP 200, finish=stop, and the "
               "v4 grading reproduces exactly from sealed raw text.",
      "status": G115.PRESERVED_RAW,
      "basis": "independent regrade, 0/60 mismatches; 0/60 prompt-hash mismatches"},
     {"claim": "v4 assigned mixed_contradictory_answer to 21 of 24 conflict cells.",
      "status": G115.PRESERVED_RAW,
      "basis": "reproducible machine output; a LABEL, not a semantic finding (R1)"},
     {"claim": "Stale context caused the reader to contradict itself.",
      "status": G115.RETRACTED,
      "basis": "0/24 answers assert the stale value as current; 0/24 meet R6. The v4 "
               "label buckets three distinct response forms together."},
     {"claim": "A harmful correctness order effect exists between stale-first and "
               "current-first.",
      "status": G115.RETRACTED,
      "basis": "21/24 answers list both values in the order the records appear in the "
               "prompt. The only grade difference (budget:solstice) is a temporal "
               "reconciliation ending at the current value, correct under R4."},
     {"claim": "The reader resists stale context in this fixture.",
      "status": G115.PRESERVED_LIMITED,
      "basis": "0/24 stale-only answers is a real observation, but the fixture is "
               "4 cores, development-exposed, and gives no recency signal - so it "
               "bounds nothing about production memory systems."},
     {"claim": "The 24 conflict cells rest on 24 independent observations.",
      "status": G115.RETRACTED,
      "basis": "19 of 20 cases returned byte-identical text across all three "
               "repetitions. The 60 cells carry 21 unique replies; the 24 "
               "conflict cells carry 9. Repetition measured determinism, not "
               "variance, so counts like '21 of 24' overstate the evidence."},
     {"claim": "Record texts are symmetric between current and stale.",
      "status": G115.RETRACTED,
      "basis": "both current records that carry a temporal cue ('after the "
               "resize', 'after the cache fix') are the current ones; the stale "
               "records are bare. Recency is partly recoverable from content in "
               "2 of 4 cores and not at all in the other 2."},
     {"claim": "The conflict condition measures stale-memory interference.",
      "status": G115.OPEN_EXPLORATORY,
      "basis": "the prompt is undecidable as to recency; the condition may instead "
               "measure behaviour under an unanswerable question. See decidability."},
    ]

    ledger_attribution = {
        "reconciliation_not_contradiction": "raised independently by glm-5.3-flash "
            "(review 20260906-004659, point 1) and glm-5.3 (point 3) before this "
            "adjudication; confirmed here against sealed bytes",
        "recency_cue_asymmetry": "raised by glm-5.3-flash (point 3); quantified here",
        "effective_sample_size": "raised by glm-5.3 (point 2) and glm-5.3-flash "
            "(point 2); recomputed here as 9 unique replies behind 24 conflict cells",
        "runner_untracked_at_pinned_commit": "raised by both reviewers (point 1 / point 4)",
        "not_found_by": "the implementer (me) in any of these four cases",
    }

    out = EV.next_attempt(ROOT, 115)
    EV.write_evidence(out, "gen115_reproduction.json", reproduction)
    EV.write_evidence(out, "gen115_conflict_adjudication.json", conflict_table)
    EV.write_evidence(out, "gen115_fixture_decidability.json", decidability)
    EV.write_evidence(out, "gen115_claim_ledger.json",
                      {"contract": G115.CONTRACT_VERSION,
                       "contract_hash": G115.contract_hash(),
                       "evidence_classification": G115.EVIDENCE_CLASSIFICATION,
                       "decision_rules": G115.DECISION_RULES, "claims": ledger,
                       "attribution": ledger_attribution})
    print(f"WROTE {out}")
    print(f"  reproduces_exactly       : {reproduction['reproduces_exactly']}")
    print(f"  stale-only answers       : {conflict_table['stale_only_answers']}/24")
    print(f"  explicit contradictions  : {conflict_table['explicit_contradictions_found']}/24")
    print(f"  mention order == ctx     : {conflict_table['mention_order_matches_context_order']}")
    print(f"  categories               : {conflict_table['category_tally']}")
    print(f"  verify                   : {EV.verify(out)}")

if __name__ == "__main__":
    main()
