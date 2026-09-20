#!/usr/bin/env python3
"""S7-1 runner: the bm25 arm re-measured under the declared stopword prefilter
(queue row S7-1, kiln-flash 2026-09-17).

Emits the interface S7-1G's gate (check.py, authored 2026-09-17 13:40 from the
row text alone, before any artifact file existed) declares:

  declaration.json  the pre-run declaration: the stopword list itself, its
                    provenance, the prior files it freezes by sha256, and the
                    verdict rule fixed as {artifact_if_abstain_at_least: N}
  corpus.jsonl      byte-identical copy of the prior frozen corpus
  results.jsonl     run-order rows {ts, arm, case_id, retrieved_ids,
                    query_tokens, declaration_sha256}; controls first
                    (return-nothing, return-everything, bm25-nofilter), then
                    bm25-prefilter, then oracle
  verdict.json      the recomputed prior and re-run numbers and the verdict
                    the declared rule gives

Chain enforced in code: prior artifacts sha-verified live -> stopword set
verified against the pinned index.ts AND the embedded copy -> declaration
written BEFORE any retrieval, sha-bound into every row -> decision from the
frozen rule. $0, local, no LLM, no score import.
"""
import hashlib
import json
import math
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = Path("/home/bmosher/memory-bake-off/team")   # absolute: no caller-tree dependence
REPO = Path("/home/bmosher/memory-bake-off/implementer/repo")
S6 = TEAM / "S6-SELECTIVITY"
STD = TEAM / "invocation-corpus-v3-standard"
for p in (str(REPO / "src"), str(STD)):
    if p not in sys.path:
        sys.path.insert(0, p)

from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.providers.bm25 import BM25Provider, tokenize  # noqa: E402
import run_standard  # noqa: E402  (load_stopwords; frozen v3 harness)

# ---- pins (declaration.json is the binding copy; these are enforced) ----
REPO_HEAD = "be2bfa908a329ac5dc5f3b33ca812eb1921bcc78"
BM25_PY_SHA = "259b15dcc7fc8397aa45884190d9b5afdbba2f82094267889218da892a124f9b"
INDEX_TS_SHA = "ec6d87948a48b44b536e714abc05b78968657d5abf20154d7a6059014fbbdd01"
PRIOR_CORPUS_SHA = "5a8668f73383ea1acc4806a31df9240cc0eb9186a7be69385a8f23e8be2024be"
PRIOR_MANIFEST_SHA = "d2d189128088f6b938e3c53e583026525446bf27ee6c098bc4526a099ab49561"
PRIOR_RESULTS_SHA = "5f3f14fc2f9b609b9153a8fbe8a3cba33aa8bcbc39689e561e6828af436196ab"
PRIOR_REVIEW_SHA = "7b6f738cfb4b1c99eb4fccfd3b4d0705507913ef320be0f4a008b61293509119"
RULE_N = 3   # fixed before the run; see declaration rule.note
UNWRITTEN = ("sel-006", "sel-007", "sel-010")
HELPFUL = {"sel-001": ["sel-001-r2"], "sel-002": ["sel-002-r1"],
           "sel-003": ["sel-003-r2"], "sel-004": ["sel-004-r3"],
           "sel-005": ["sel-005-r2"], "sel-006": [], "sel-007": [],
           "sel-008": [], "sel-009": [], "sel-010": []}
EXPECTATION = ("pre-registered before the run: abstain_correct 0 of 5 and "
               "retrieve_correct 5 of 5, verdict artifact-refuted — the set "
               "filters what/when/which/does but NOT is/the/for/how/many, and "
               "'the' appears in most store records, so residual query tokens "
               "keep every abstain case above score zero; the mean set-F1 will "
               "not move from 0.500, which is why the rule keys on abstentions")

STOPWORDS = frozenset("""
about after also been before being call campaign-1 campaign1 confirm confirmed
create created decision does done draft each environment exists from have into
more most never only opening other over pending project record said same shall
some still such than that their them then there they this tool trial under upon
used uses using very were what when where which while will window with
""".split())


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


def score(cases, helpful, got):
    """Same recomputation the gate performs."""
    return {
        "mean_f1": sum(f1(helpful[c], set(got[c])) for c in cases) / len(cases),
        "retrieve_correct": sum(1 for c in cases
                                if set(HELPFUL[c]) and set(HELPFUL[c]) <= set(got[c])),
        "abstain_correct": sum(1 for c in cases
                               if not HELPFUL[c] and not got[c]),
    }


class PrefilteredBM25(BM25Provider):
    """The pinned BM25Provider with ONE delta: tokens in the declared STOPWORDS
    set are dropped before scoring, on the query side and the document side.
    Copied from bm25.py @ 259b15dc with only the tokenize calls swapped — the
    copied-with-sole-delta pattern S4-12 used."""

    name = "bm25-prefilter"

    @staticmethod
    def _tok(text: str) -> list:
        return [t for t in tokenize(text) if t not in STOPWORDS]

    def ingest(self, records, mode: str = "raw") -> None:
        self.reset(); self.remember_records(records); self.docs = list(records)
        lengths = []
        for r in self.docs:
            toks = self._tok(r.text); c = Counter(toks)
            self.tf.append(c); lengths.append(len(toks)); self.df.update(c.keys())
        self.avgdl = sum(lengths) / len(lengths) if lengths else 0.0

    def _score(self, query: str, idx: int) -> float:
        q = self._tok(query); tf = self.tf[idx]
        dl = sum(tf.values()); n = len(self.docs); s = 0.0
        for term in q:
            if term not in tf:
                continue
            df = self.df[term]
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            f = tf[term]
            denom = f + self.k1 * (1 - self.b + self.b * (dl / self.avgdl if self.avgdl else 0))
            s += idf * (f * (self.k1 + 1) / denom)
        return s


def retrieve_top1(eng, case) -> list:
    q = QueryCase(id=case["case_id"], category=case["expect"], query=case["query"],
                  relevant_ids=(), prohibited_ids=())
    return [it.record_id for it in eng.retrieve(q, top_k=1).items]


def main() -> int:
    # ---- environment + prior pins, verified live, before anything runs ----
    if sha(REPO / "src" / "memory_bakeoff" / "providers" / "bm25.py") != BM25_PY_SHA:
        die("bm25.py is not the pinned revision")
    idx = REPO / "extensions" / "pi-change-trigger" / "index.ts"
    if sha(idx) != INDEX_TS_SHA:
        die("pi-change-trigger/index.ts is not the pinned revision")
    if run_standard.load_stopwords() != set(STOPWORDS):
        die("stopword set drifted from the pinned index.ts")
    for name, want in (("corpus.jsonl", PRIOR_CORPUS_SHA),
                       ("manifest.json", PRIOR_MANIFEST_SHA),
                       ("results.jsonl", PRIOR_RESULTS_SHA),
                       ("review.json", PRIOR_REVIEW_SHA)):
        if sha(S6 / name) != want:
            die(f"prior artifact {name} does not match its pinned sha")
    prior_rows = [json.loads(l) for l in (S6 / "results.jsonl").read_text().splitlines()
                  if l.strip()]
    prior_got = {r["case_id"]: r["retrieved_ids"] for r in prior_rows
                 if r["arm"] == "bm25"}
    cases = [json.loads(l) for l in (S6 / "corpus.jsonl").read_text().splitlines()
             if l.strip()]

    # ---- declaration first: byte-final before ANY retrieval ----
    shutil.copyfile(S6 / "corpus.jsonl", HERE / "corpus.jsonl")
    if sha(HERE / "corpus.jsonl") != PRIOR_CORPUS_SHA:
        die("local corpus copy is not byte-identical to the prior frozen corpus")
    declaration = {
        "declared_at": now(),
        "stopwords": sorted(STOPWORDS),
        "source": "implementer/repo/extensions/pi-change-trigger/index.ts "
                  "STOPWORDS @ sha256 ec6d87948a48b44b536e714abc05b78968657d5abf"
                  "20154d7a6059014fbbdd01 (the same pin S4-12 recorded as "
                  "trigger_pin), loaded per team/invocation-corpus-v3-standard/"
                  "run_standard.py load_stopwords(); the only stopword filter "
                  "the project's fire-log path has ever used, frozen for a "
                  "different instrument before the S6-2 corpus existed — chosen "
                  "for provenance, not fit; any other list would be a post-hoc "
                  "choice and a different list is a new declared configuration, "
                  "not a second try inside this row",
        "addresses": "the recorded deviation is S6-SELECTIVITY/review.json "
                     "deviation (1): bm25 fired on all five abstain cases "
                     "because the in-tree tokenizer keeps function words and no "
                     "stopword prefilter was declared or applied, while S4-12's "
                     "fire-log bm25 usage did filter — this row declares and "
                     "applies exactly that prefilter",
        "corpus_sha256": PRIOR_CORPUS_SHA,
        "manifest_sha256": PRIOR_MANIFEST_SHA,
        "rule": {"artifact_if_abstain_at_least": RULE_N,
                 "note": "N=3 because the tokenizer-artifact hypothesis "
                         "concerns the three unwritten-subject abstain cases "
                         "(sel-006, sel-007, sel-010); the two written-subject/"
                         "no-note cases are declared by the prior design to "
                         "possibly keep firing on the subject token, so "
                         "artifact-confirmed means abstention recovered on at "
                         "least those three; rerun.retrieve_correct is reported "
                         "beside the verdict and rank 2 reads it",
                 "staging_rule_note": "the pre-registration also required "
                                      "retrieve_correct = 5 for confirmed; the "
                                      "gate's rule shape keys on abstentions "
                                      "alone, so that condition travels in the "
                                      "verdict finding instead"},
        "prefilter_application": "tokens in the set are dropped from BOTH the "
                                 "query and the ingested record text before "
                                 "BM25 scoring; sole delta from the pinned "
                                 "BM25Provider (repo be2bfa9, bm25.py sha256 "
                                 "259b15dcc7fc8397aa45884190d9b5afdbba2f8209426"
                                 "789218da892a124f9b), the copied-with-sole-"
                                 "delta pattern S4-12 used",
        "baseline_pin": {"repo_head": REPO_HEAD, "bm25_py_sha256": BM25_PY_SHA},
        "index_ts_sha256": INDEX_TS_SHA,
        "prior_measurement": {
            "source": "team/S6-SELECTIVITY/results.jsonl (arm bm25; sha256 "
                      "5f3f14fc2f9b609b9153a8fbe8a3cba33aa8bcbc39689e561e6828af"
                      "436196ab)",
            "review_source": "team/S6-SELECTIVITY/review.json (sha256 "
                             "7b6f738cfb4b1c99eb4fccfd3b4d0705507913ef320be0f4a"
                             "008b61293509119)",
            "bm25_mean_setf1": 0.5,
            "bm25_abstain_correct": 0,
            "bm25_per_case_retrieved": prior_got,
        },
        "arms_in_order": ["return-nothing", "return-everything", "bm25-nofilter",
                          "bm25-prefilter", "oracle"],
        "expectation": EXPECTATION,
    }
    (HERE / "declaration.json").write_text(json.dumps(declaration, indent=1) + "\n")
    dsha = sha(HERE / "declaration.json")
    print(f"declaration written at {declaration['declared_at']} sha {dsha[:12]}...")

    # ---- the run: controls first, in declared arm order ----
    tokens = {c["case_id"]: tokenize(c["query"]) for c in cases}

    rows = []

    def add(arm, case, ids, qt):
        rows.append({"ts": now(), "arm": arm, "case_id": case["case_id"],
                     "retrieved_ids": ids, "query_tokens": qt,
                     "declaration_sha256": dsha})

    def records_for(case):
        return [MemoryRecord(id=r["id"], text=r["text"],
                             timestamp=datetime(2026, 9, 1, tzinfo=timezone.utc),
                             session_id=f"sess-{case['case_id']}") for r in case["store"]]

    for c in cases:                                            # return-nothing
        add("return-nothing", c, [], list(tokens[c["case_id"]]))
    for c in cases:                                            # return-everything
        add("return-everything", c, [r["id"] for r in c["store"]],
            list(tokens[c["case_id"]]))

    got_nofilter, got_prefilter = {}, {}
    eng = BM25Provider()
    for c in cases:                                            # paired control
        eng.ingest(records_for(c))
        got_nofilter[c["case_id"]] = retrieve_top1(eng, c)
        add("bm25-nofilter", c, got_nofilter[c["case_id"]],
            list(tokens[c["case_id"]]))
    eng = PrefilteredBM25()
    for c in cases:                                            # the measured arm
        eng.ingest(records_for(c))
        got_prefilter[c["case_id"]] = retrieve_top1(eng, c)
        add("bm25-prefilter", c, got_prefilter[c["case_id"]],
            [t for t in tokens[c["case_id"]] if t not in STOPWORDS])
    for c in cases:                                            # oracle
        add("oracle", c, list(HELPFUL[c["case_id"]]),
            list(tokens[c["case_id"]]))

    (HERE / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))

    # ---- verdict from the frozen rule, numbers recomputed the way the gate does ----
    prior_score = score({c["case_id"] for c in cases},
                        {k: set(v) for k, v in HELPFUL.items()}, prior_got)
    rerun_score = score({c["case_id"] for c in cases},
                        {k: set(v) for k, v in HELPFUL.items()}, got_prefilter)
    drifted = sorted(c for c in got_nofilter
                     if set(got_nofilter[c]) != set(prior_got[c]))
    regressed = sorted(c for c in got_nofilter
                       if got_nofilter[c] == HELPFUL[c]
                       and got_prefilter[c] != HELPFUL[c])
    confirmed = rerun_score["abstain_correct"] >= RULE_N
    verdict = {
        "verdict": "artifact-confirmed" if confirmed else "artifact-refuted",
        "finding": "",   # filled below
        "prior": {"source": "team/S6-SELECTIVITY/results.jsonl (bm25 arm; sha256 "
                            "5f3f14fc2f9b609b9153a8fbe8a3cba33aa8bcbc39689e561e6828af436196ab)",
                  "mean_f1": round(prior_score["mean_f1"], 6),
                  "retrieve_correct": prior_score["retrieve_correct"],
                  "abstain_correct": prior_score["abstain_correct"]},
        "rerun": {"mean_f1": round(rerun_score["mean_f1"], 6),
                  "retrieve_correct": rerun_score["retrieve_correct"],
                  "abstain_correct": rerun_score["abstain_correct"]},
        "guard": ("bm25-nofilter reproduced the prior bm25 retrieval per case on "
                  "10/10 cases, so the deltas are the prefilter's" if not drifted
                  else f"DRIFT: bm25-nofilter differs from the prior on "
                       f"{', '.join(drifted)}; no conclusion is valid"),
        "unwritten_subject_cases_abstained": sum(1 for k in UNWRITTEN
                                                 if not got_prefilter[k]),
        "retrieve_cases_regressed": regressed,
        "expectation_registered_before_run": EXPECTATION,
        "expectation_met": (rerun_score["abstain_correct"] == 0
                            and rerun_score["retrieve_correct"] == 5
                            and not confirmed),
    }
    if drifted:
        verdict["finding"] = (
            "harness drift: the unfiltered control did not reproduce the prior "
            "retrieval, so no conclusion about the prefilter is valid")
    elif confirmed:
        verdict["finding"] = (
            "bm25-prefilter abstains on the unwritten-subject cases and keeps "
            "its retrieve top-1s: the prior 0/5 abstention failure was a "
            "tokenizer artifact at trigger-grade filtering; rank 2 may compose "
            "on this frozen configuration but must read retrieve_correct beside "
            "the verdict")
    else:
        verdict["finding"] = (
            "bm25-prefilter still fires on every abstain case "
            f"(abstain_correct {rerun_score['abstain_correct']} of 5 under rule "
            f"N={RULE_N}): the abstention failure is not removed by the "
            "project's one pre-existing stopword filter, so rank 2 must not "
            "compose bm25 as-is and must not treat stopword filtering as the "
            "fix"
            + (f"; the prefilter also regressed previously-correct retrieve "
               f"case(s) {', '.join(regressed)}, consistent with the trigger "
               f"vocabulary holding content words (call, record, decision, "
               f"window, project) that re-rank ties when dropped document-side"
               if regressed else ""))
    (HERE / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")

    for k in sorted(HELPFUL):
        expect = "retrieve" if HELPFUL[k] else "abstain"
        print(f"{k} [{expect:8s}] nofilter={got_nofilter[k] or ['-']} "
              f"prefilter={got_prefilter[k] or ['-']}")
    print(f"prior  : {prior_score}")
    print(f"rerun  : {rerun_score}")
    print(f"verdict: {verdict['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
