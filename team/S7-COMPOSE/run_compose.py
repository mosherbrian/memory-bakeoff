#!/usr/bin/env python3
"""S7-2 runner: compose attempt — bm25 retrieval behind pi-lcm's abstention
gate (queue row S7-2, kiln-flash 2026-09-17).

Emits the interface S7-2G's gate (check.py, authored 2026-09-17 13:44 from the
row text alone) declares:

  declaration.json  pre-run declaration: frozen prior files by sha256,
                    bm25_variant ("prior" — justified by S7-1's verdict),
                    the quoted S7-1 verdict, and the rule
                    {complementary_if_gain_at_least: margin}
  results.jsonl     run-order rows {ts, arm, case_id, retrieved_ids,
                    declaration_sha256}; components first (bm25 x10,
                    pi_lcm_toollevel_sel x10), then the compose arm x10
  verdict.json      recomputed prior + re-run scores, the two-by-two overlap
                    table, and the verdict the declared rule gives

Compose semantics (the gate verifies it, nothing else counts): per case,
retrieve nothing where pi-lcm retrieved nothing, else exactly the bm25 ids.
S7-1's verdict (artifact-refuted: the prefilter fixed no abstention and
regressed a retrieve case) forces bm25_variant "prior" — composing on the
prefilter would compose on a refuted configuration. $0, local, no LLM, no
score import.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = Path("/home/bmosher/memory-bake-off/team")   # absolute: no caller-tree dependence
REPO = Path("/home/bmosher/memory-bake-off/implementer/repo")
S6 = TEAM / "S6-SELECTIVITY"
S71 = TEAM / "S7-BM25-PREFILTER"
for p in (str(TEAM / "s4-14-crossengine-rerun"), str(TEAM / "s4-12-crossengine"),
          str(REPO / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from run_crossengine import RECORD_TS  # the S4-12/S4-14 fixed stamp
from run_s4_14 import PiLcmToolLevelProvider  # noqa: E402
from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.providers.bm25 import BM25Provider  # noqa: E402

# ---- pins ----
PRIOR_CORPUS_SHA = "5a8668f73383ea1acc4806a31df9240cc0eb9186a7be69385a8f23e8be2024be"
PRIOR_MANIFEST_SHA = "d2d189128088f6b938e3c53e583026525446bf27ee6c098bc4526a099ab49561"
PRIOR_RESULTS_SHA = "5f3f14fc2f9b609b9153a8fbe8a3cba33aa8bcbc39689e561e6828af436196ab"
S71_RESULTS_SHA = None  # bound live from S7-1's results.jsonl before use
MARGIN = 0.10           # one case's worth of mean movement on a 10-case corpus
S71_VERDICT = None      # read live from S7-1's verdict.json and quoted exactly
ENGINE_TOPK = {"pi_lcm_toollevel_sel": 5}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def die(msg: str) -> None:
    print(f"FATAL: {msg}", flush=True)
    raise SystemExit(1)


def f1(helpful: set, got: set) -> float:
    if not helpful:
        return 0.0 if got else 1.0
    tp = len(helpful & got)
    return 2 * tp / (len(helpful) + len(got)) if tp else 0.0


def correct(expect: str, helpful: set, got) -> bool:
    return not got if expect == "abstain" else helpful <= set(got)


def score(cases, helpful, got):
    return {
        "mean_f1": sum(f1(helpful[c], set(got[c])) for c in cases) / len(cases),
        "retrieve_correct": sum(1 for c in cases if helpful[c]
                                and helpful[c] <= set(got[c])),
        "abstain_correct": sum(1 for c in cases
                               if not helpful[c] and not got[c]),
    }


def records_for(case):
    return [MemoryRecord(id=r["id"], text=r["text"], timestamp=RECORD_TS,
                         session_id=f"sess-{case['case_id']}") for r in case["store"]]


def query_for(case):
    return QueryCase(id=case["case_id"], category=case["expect"], query=case["query"],
                     relevant_ids=(), prohibited_ids=())


def ids_from(result, text_to_id):
    out = []
    for it in result.items:
        rid = it.record_id if getattr(it, "record_id", None) else text_to_id.get(it.text)
        out.append(rid if rid else it.text)
    return out


def main() -> int:
    global S71_RESULTS_SHA, S71_VERDICT
    # ---- dependency + prior pins, verified live, before anything runs ----
    try:
        S71_VERDICT = json.loads((S71 / "verdict.json").read_text())["verdict"]
    except Exception as e:
        die(f"S7-1 verdict unreadable: {e}")
    if S71_VERDICT not in ("artifact-confirmed", "artifact-refuted"):
        die(f"S7-1 verdict {S71_VERDICT!r} is not a landed verdict")
    S71_RESULTS_SHA = sha(S71 / "results.jsonl")
    for name, want in (("corpus.jsonl", PRIOR_CORPUS_SHA),
                       ("manifest.json", PRIOR_MANIFEST_SHA),
                       ("results.jsonl", PRIOR_RESULTS_SHA)):
        if sha(S6 / name) != want:
            die(f"prior artifact {name} does not match its pinned sha")
    prior_rows = [json.loads(l) for l in (S6 / "results.jsonl").read_text().splitlines()
                  if l.strip()]
    prior = {"bm25": {}, "pi_lcm_toollevel_sel": {}}
    for r in prior_rows:
        if r["arm"] in prior:
            prior[r["arm"]][r["case_id"]] = r["retrieved_ids"]
    cases = [json.loads(l) for l in (S6 / "corpus.jsonl").read_text().splitlines()
             if l.strip()]
    helpful = json.loads((S6 / "manifest.json").read_text())["helpful"]

    # ---- declaration first: byte-final before ANY retrieval ----
    bm25_variant = "prefilter" if S71_VERDICT == "artifact-confirmed" else "prior"
    declaration = {
        "declared_at": now(),
        "corpus_sha256": PRIOR_CORPUS_SHA,
        "manifest_sha256": PRIOR_MANIFEST_SHA,
        "bm25_variant": bm25_variant,
        "s7_1_verdict": S71_VERDICT,
        "rule": {"complementary_if_gain_at_least": MARGIN,
                 "note": "margin 0.10 = one case's worth of mean set-F1 "
                         "movement on the 10-case corpus; less than that is "
                         "noise, not complementarity; fixed before the run"},
        "compose_semantics": "per case: retrieve nothing where "
                             "pi_lcm_toollevel_sel retrieved nothing, else "
                             "exactly the ids the bm25 arm retrieved; the gate "
                             "reads 'pi-lcm fired' as 'retrieved at least one "
                             "id', the only signal the prior schema holds",
        "variant_justification": (
            "S7-1's verdict is artifact-refuted (its prefilter fixed no "
            "abstention and regressed sel-003), so composing on the prefilter "
            "would compose on a refuted configuration; the unfiltered prior "
            "bm25 arm is the component, and pi-lcm's gate owns abstention — "
            "the S7-1 finding sharpens the division of labour: bm25 ranks, "
            "the gate decides whether to retrieve at all"),
        "prior_measurement": {
            "source": "team/S6-SELECTIVITY/results.jsonl (arms bm25 and "
                      "pi_lcm_toollevel_sel; sha256 "
                      "5f3f14fc2f9b609b9153a8fbe8a3cba33aa8bcbc39689e561e6828af"
                      "436196ab)",
            "bm25_mean_setf1": 0.5, "bm25_retrieve_correct": 5,
            "bm25_abstain_correct": 0,
            "pi_lcm_mean_setf1": 0.6, "pi_lcm_retrieve_correct": 1,
            "pi_lcm_abstain_correct": 5,
        },
        "dependency": "team/S7-BM25-PREFILTER (row S7-1) results.jsonl sha256 "
                      "bound at run time; verdict quoted from its verdict.json",
        "arms_in_order": ["bm25", "pi_lcm_toollevel_sel", "compose"],
        "expectation": "pre-registered before the run: pi-lcm's gate opens on "
                       "1 of 5 retrieve cases and on no abstain case, so the "
                       "compose inherits pi-lcm's correctness profile exactly "
                       "(mean 0.600, retrieve_correct 1, abstain_correct 5); "
                       "gain over the better single arm 0.000 < margin 0.10; "
                       "verdict not-complementary — the construction discards "
                       "bm25's retrieve-case coverage instead of combining it",
    }
    (HERE / "declaration.json").write_text(json.dumps(declaration, indent=1) + "\n")
    dsha = sha(HERE / "declaration.json")
    print(f"declaration written at {declaration['declared_at']} sha {dsha[:12]}...")

    # ---- the run: components first, then the composition ----
    rows = []

    def add(arm, case, ids):
        rows.append({"ts": now(), "arm": arm, "case_id": case["case_id"],
                     "retrieved_ids": ids, "declaration_sha256": dsha})

    text_to_id = {c["case_id"]: {r["text"]: r["id"] for r in c["store"]}
                  for c in cases}

    got_bm25 = {}
    eng = BM25Provider()
    for c in cases:
        eng.ingest(records_for(c))
        got_bm25[c["case_id"]] = [it.record_id
                                  for it in eng.retrieve(query_for(c), top_k=1).items]
        add("bm25", c, got_bm25[c["case_id"]])

    got_pi = {}
    engine = PiLcmToolLevelProvider()
    for c in cases:
        engine.reset()
        engine.ingest(records_for(c))
        res = engine.retrieve(query_for(c), top_k=ENGINE_TOPK["pi_lcm_toollevel_sel"])
        got_pi[c["case_id"]] = ids_from(res, text_to_id[c["case_id"]])
        add("pi_lcm_toollevel_sel", c, got_pi[c["case_id"]])
    engine.close()

    got_compose = {c["case_id"]: list(got_bm25[c["case_id"]]) if got_pi[c["case_id"]] else []
                   for c in cases}
    for c in cases:
        add("compose", c, got_compose[c["case_id"]])

    (HERE / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))

    # ---- verdict from the frozen rule, recomputed the way the gate does ----
    ids = {c["case_id"] for c in cases}
    hset = {k: set(v) for k, v in helpful.items()}
    prior_score = {"bm25": score(ids, hset, prior["bm25"]),
                   "pi_lcm": score(ids, hset, prior["pi_lcm_toollevel_sel"])}
    rerun_score = {"bm25": score(ids, hset, got_bm25),
                   "pi_lcm": score(ids, hset, got_pi),
                   "compose": score(ids, hset, got_compose)}
    expect_map = {c["case_id"]: c["expect"] for c in cases}
    got_by_arm = {"bm25": got_bm25, "pi_lcm_toollevel_sel": got_pi}
    ok = {a: {c for c in ids if correct(expect_map[c], hset[c], got_by_arm[a][c])}
          for a in ("bm25", "pi_lcm_toollevel_sel")}
    overlap = {"both": len(ok["bm25"] & ok["pi_lcm_toollevel_sel"]),
               "only_bm25": len(ok["bm25"] - ok["pi_lcm_toollevel_sel"]),
               "only_pi_lcm": len(ok["pi_lcm_toollevel_sel"] - ok["bm25"]),
               "neither": len(ids - ok["bm25"] - ok["pi_lcm_toollevel_sel"])}
    drift_bm25 = sorted(c for c in ids
                        if set(got_bm25[c]) != set(prior["bm25"][c]))
    drift_pi = sorted(c for c in ids
                      if set(got_pi[c]) != set(prior["pi_lcm_toollevel_sel"][c]))
    gain = (rerun_score["compose"]["mean_f1"]
            - max(rerun_score["bm25"]["mean_f1"], rerun_score["pi_lcm"]["mean_f1"]))
    complementary = gain >= MARGIN - 1e-9
    verdict = {
        "verdict": "complementary" if complementary else "not-complementary",
        "finding": "",   # filled below
        "feeds": "roadmap R-PF, Decision Gate F option B — the compose evidence "
                 "the S6-3 map says the build decision stays gated behind",
        "prior": {"source": "team/S6-SELECTIVITY/results.jsonl (arms bm25, "
                            "pi_lcm_toollevel_sel; sha256 "
                            "5f3f14fc2f9b609b9153a8fbe8a3cba33aa8bcbc39689e561e6828af436196ab)",
                  "bm25": {k: (round(v, 6) if k == "mean_f1" else v)
                           for k, v in prior_score["bm25"].items()},
                  "pi_lcm": {k: (round(v, 6) if k == "mean_f1" else v)
                             for k, v in prior_score["pi_lcm"].items()}},
        "rerun": {a: {k: (round(v, 6) if k == "mean_f1" else v)
                      for k, v in rerun_score[a].items()}
                  for a in ("bm25", "pi_lcm", "compose")},
        "overlap": overlap,
        "guard": ("both components reproduced their reference retrievals per "
                  "case on 10/10 cases (bm25 vs the prior bm25 arm; pi-lcm vs "
                  "the prior pi_lcm_toollevel_sel arm), so the compose result "
                  "is the composition's and not harness drift"
                  if not drift_bm25 and not drift_pi else
                  f"DRIFT: bm25 differs on {drift_bm25 or 'none'}, pi-lcm on "
                  f"{drift_pi or 'none'}; no conclusion is valid"),
        "s7_1_dependency": f"quoted s7_1_verdict {S71_VERDICT!r} from "
                           f"team/S7-BM25-PREFILTER/verdict.json (results sha "
                           f"{S71_RESULTS_SHA[:12]}...); bm25_variant "
                           f"{bm25_variant!r} follows from it",
        "expectation_registered_before_run": declaration["expectation"],
        "expectation_met": (abs(rerun_score["compose"]["mean_f1"] - 0.6) < 0.0006
                            and not complementary),
    }
    if drift_bm25 or drift_pi:
        verdict["finding"] = (
            "a component did not reproduce its reference retrieval, so this "
            "run supports no conclusion about the composition")
    elif complementary:
        verdict["finding"] = (
            f"the gate-owning compose gains {gain:+.3f} mean set-F1 over the "
            f"stronger single arm (margin {MARGIN}) on this corpus: the arms' "
            "strengths combine rather than substitute, which is the evidence "
            "Decision Gate F option B needed to keep a compose path open")
    else:
        verdict["finding"] = (
            f"the gate-owning compose gains {gain:+.3f} mean set-F1 over the "
            f"stronger single arm (margin {MARGIN}): pi-lcm's gate opens on "
            "only 1 of 5 retrieve cases and the construction discards bm25's "
            "coverage on the other 4, so on this corpus the compose is exactly "
            "pi-lcm's correctness profile with bm25's abstention failures "
            "suppressed — evidence for Decision Gate F option B in the "
            "negative: this compose construction does not justify building a "
            "state layer; a union-style construction (gate opens OR bm25 "
            "confident) is a different, separately-declared configuration")
    (HERE / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")

    for k in sorted(hset):
        expect = expect_map[k]
        print(f"{k} [{expect:8s}] bm25={got_bm25[k] or ['-']} "
              f"pi={got_pi[k] or ['-']} compose={got_compose[k] or ['-']}")
    for a in ("bm25", "pi_lcm", "compose"):
        print(f"{a:8s}: {rerun_score[a]}")
    print(f"overlap: {overlap}  gain {gain:+.3f}  verdict: {verdict['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
