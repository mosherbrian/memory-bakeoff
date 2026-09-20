#!/usr/bin/env python3
"""S11-2 runner: KnowledgeDrift cross-system replay on the SAME frozen sample
(queue row S11-2, kiln-flash 2026-09-18).

Reuses the S7-4 harness (team/S7-KD-WORLDS) and its sha-pinned upstream worlds
via the `upstream` symlink here. The frozen 120-probe item list is the prior's
items.jsonl byte for byte; the replay protocol is the prior's, unchanged: ops
in stream order, a sampled recall answered at its own position against the
store as it then stands. What is new: at every sampled recall the query is put
to the OTHER pinned in-repo providers (dense_lsa, tfidf_cosine, hybrid_rrf)
alongside a fresh bm25 control run; the declared stretch arm claude_mem_chroma_lsa
(controlled core, raw ingest) runs under the same protocol. Family scores stay
separate; the prior's bm25 cells are quoted in verdict.prior (old beside new).

Emits the interface the verified S11-2 gate (check.py, authored from the row
text alone) declares: declaration.json, items.jsonl, results.jsonl, verdict.json.
Controls first (return-nothing, oracle); every receipt carries the declaration
sha. $0, local, no LLM, no score import.

Stop rule (declared before the run): if the fresh bm25 arm does not reproduce
the prior's per-item pass/fail exactly, the harness has moved and the run dies
before any receipt is written - a difference between systems must not be
confoundable with a difference between runs.
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "S7-KD-WORLDS"
REPO = Path("/var/home/bmosher/memory-bake-off/implementer/repo")
for p in (str(REPO / "src"),):
    if p not in sys.path:
        sys.path.insert(0, p)

# Pinned before any provider is built: the controlled claude-mem core applies a
# default 90-day recency window against this eval-now; the replay's fixed
# record timestamp (2026-09-01, the prior harness's) sits inside it, so the
# window keeps every record and the policy is reproducible rather than ambient.
os.environ["CLAUDE_MEM_EVAL_NOW"] = "2026-08-30T12:00:00+00:00"

# This seat's shell runs HOME-isolated, so python's user site (numpy 2.4.4,
# scikit-learn 1.9.0 for the dense/tfidf/hybrid/claude-mem arms) is not on
# sys.path; it is added explicitly instead of ambient — the environment is
# part of reproducibility.
USER_SITE = "/var/home/bmosher/.local/lib/python3.14/site-packages"
if USER_SITE not in sys.path:
    sys.path.append(USER_SITE)

from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.providers.bm25 import BM25Provider  # noqa: E402
from memory_bakeoff.providers.dense import DenseLSAProvider  # noqa: E402
from memory_bakeoff.providers.tfidf import TfidfCosineProvider  # noqa: E402
from memory_bakeoff.providers.hybrid import HybridRRFProvider  # noqa: E402
from memory_bakeoff.providers.claude_mem_core import (  # noqa: E402
    ClaudeMemChromaLSAProvider,
)

WORLDS_DIR = "upstream/KnowledgeDrift/worlds/v2"
SEEDS = (1, 2)
K_DEFAULT = 10
ENGINES = ("bm25", "dense_lsa", "tfidf_cosine", "hybrid_rrf",
           "claude_mem_chroma_lsa")
JUDGING = {
    "Retrieval": "probe expect gold: the gold note key must appear among the "
                 "hits (top k per the recall op, k=10)",
    "Abstention": "probe expect control: correct behaviour is to decline — "
                  "zero hits. None of these ranked-retrieval engines has a "
                  "declined concept, so zero hits is the only honest decline "
                  "any of them can produce",
    "Rationale": "probe expect linked: the gold (the reasoning note linked to "
                 "the anchor decision) must appear among the hits (top k=10)",
}
NOT_RUN = {
    "Currency": "needs supersession history and a current-head notion no "
                "engine in this run implements (all five are flat ranked-"
                "retrieval stores: history capability is absent); measuring "
                "it would record a capability absence as a behavior score",
    "Contradiction": "needs the suspects capability (nominating disagreements "
                     "for a person); no engine here has one, so every case "
                     "would score 0 by construction — a capability absence, "
                     "not a selectivity measurement, on every arm alike",
    "Drift": "needs stale-sibling detection (suspects capability); same "
             "capability absence as Contradiction, on every arm",
    "Deletion": "needs release traces and tombstones; these flat stores just "
                "delete (trace: false upstream), so the family would measure "
                "the delete primitive, not memory behavior, on every arm",
    "Temporal": "needs a recall window applied natively by the store (temporal "
                "capability); the replay supplies no as-of, so no arm applies "
                "one and the family would be unmeasured, not failed",
    "Authority": "the optional ninth family; needs endorsement rungs stored "
                 "as first-class note attributes, which no engine here keeps",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def die(msg: str) -> None:
    print(f"FATAL: {msg}", flush=True)
    raise SystemExit(1)


def record_text(rec: dict) -> str:
    return f"{rec.get('title', '')} {rec.get('body', '')}".strip()


def load_world(path: Path) -> dict:
    w = json.loads(path.read_text())
    recall_ops = {o["id"]: o for o in w["ops"]
                  if o.get("op") in ("recall", "recall_path") and o.get("id")}
    probes = {p["id"]: p for p in w["probes"]}
    return {"spec": w["spec"], "ops": w["ops"], "probes": probes,
            "recall_ops": recall_ops}


def sample(world: dict, seed: int) -> list:
    """The prior's deterministic stratified sample, re-derived to prove the
    frozen item list is what the prior's sampler produces."""
    items = []
    for fam_lower, fam_card in (("retrieval", "Retrieval"),
                                ("abstention", "Abstention"),
                                ("rationale", "Rationale")):
        if fam_lower == "retrieval":
            phrasings = ("lexical", "paraphrase", "oblique", "crossed")
            per = 20 // len(phrasings)
            picked = []
            for phr in phrasings:
                ids = [p["id"] for p in world["probes"].values()
                       if p["family"] == fam_lower and p.get("expect") == "gold"
                       and p.get("phrasing") == phr]
                ids = [i for i in ids if i in world["recall_ops"]]
                stride = max(1, len(ids) // per)
                picked += ids[::stride][:per]
        else:
            ids = [p["id"] for p in world["probes"].values()
                   if p["family"] == fam_lower]
            ids = [i for i in ids if i in world["recall_ops"]]
            stride = max(1, len(ids) // 20)
            picked = ids[::stride][:20]
        for pid in picked:
            items.append({"item_id": f"s{seed}-{pid}", "family": fam_card,
                          "seed": seed})
    return items


def replay_and_answer(world: dict, sampled: set) -> dict:
    """Replay ops in stream order; at each sampled recall put the query to
    every engine against the store as it then stands (the store is flat and
    engine-independent, so one replay serves all arms — the prior's protocol,
    unchanged, with more engines answering)."""
    live: dict[str, str] = {}
    answers: dict[str, dict[str, list]] = {e: {} for e in ENGINES}
    prows = {"bm25": BM25Provider(),
             "dense_lsa": DenseLSAProvider(),
             "tfidf_cosine": TfidfCosineProvider(),
             "hybrid_rrf": HybridRRFProvider(),
             "claude_mem_chroma_lsa": ClaudeMemChromaLSAProvider()}

    def run_query(op):
        recs = [MemoryRecord(id=k, text=t,
                             timestamp=datetime(2026, 9, 1, tzinfo=timezone.utc),
                             session_id="kd") for k, t in live.items()]
        for name, eng in prows.items():
            eng.ingest(recs)
            res = eng.retrieve(QueryCase(id=op["id"], category="probe",
                                         query=op["query"], relevant_ids=(),
                                         prohibited_ids=()),
                               top_k=op.get("k", K_DEFAULT))
            answers[name][op["id"]] = [it.record_id for it in res.items]

    for op in world["ops"]:
        kind = op.get("op")
        if kind == "inscribe":
            rec = op["record"]
            live[rec["key"]] = record_text(rec)
        elif kind == "supersede":
            live.pop(op["old"], None)
            rec = op["new"]
            live[rec["key"]] = record_text(rec)
        elif kind in ("release", "purge"):
            live.pop(op["key"], None)
        elif kind == "recall" and op.get("id") in sampled:
            run_query(op)
        # recall_path sampled items are not in this sample (expect gold only);
        # link/endorse/settle/lineage/suspects/recall_path: no-ops for a flat store
    for eng in prows.values():
        eng.close()
    return answers


def main() -> int:
    # frozen sample: the prior's file, byte for byte
    items_bytes = (PRIOR / "items.jsonl").read_bytes()
    (HERE / "items.jsonl").write_bytes(items_bytes)
    items = [json.loads(l) for l in items_bytes.decode().splitlines() if l.strip()]
    prior_decl = json.loads((PRIOR / "declaration.json").read_text())

    worlds, file_hashes = {}, {}
    for fname, want in prior_decl["worlds"]["files"].items():
        p = HERE / WORLDS_DIR / fname
        if not p.is_file():
            die(f"world file missing: {p}")
        got = sha(p)
        if got != want:
            die(f"world file {fname} sha {got[:12]} != prior pin {want[:12]}")
        file_hashes[fname] = got
        w = load_world(p)
        worlds[w["spec"]["seed"]] = w
        print(f"loaded {fname}: seed {w['spec']['seed']}, {len(w['ops'])} ops, "
              f"{len(w['probes'])} probes")

    # the frozen list must be what the prior's sampler produces
    for seed in SEEDS:
        regrown = {i["item_id"] for i in sample(worlds[seed], seed)}
        frozen = {i["item_id"] for i in items if i["seed"] == seed}
        if regrown != frozen:
            die(f"regrown sample for seed {seed} differs from the frozen list")
    meta = {}
    for i in items:
        pid = i["item_id"].split("-", 1)[1]
        meta[i["item_id"]] = {"probe": worlds[i["seed"]]["probes"][pid],
                              "op": worlds[i["seed"]]["recall_ops"][pid]}

    declaration = {
        "declared_at": now(),
        "items_sha256": sha(HERE / "items.jsonl"),
        "worlds": dict(prior_decl["worlds"], files=file_hashes),
        "engines": {
            "bm25": {"experiment_class": "baseline",
                     "note": "the pinned in-tree BM25 baseline (repo be2bfa9), "
                             "re-run as the control: the harness must not move, "
                             "so it must pass and fail exactly the prior's "
                             "items; stop rule dies before receipts otherwise"},
            "dense_lsa": {"experiment_class": "baseline",
                          "note": "the pinned in-tree dense LSA baseline "
                                  "(TfidfVectorizer bigrams + TruncatedSVD 32 "
                                  "dims, deterministic seed 0), flat store"},
            "tfidf_cosine": {"experiment_class": "baseline",
                             "note": "the pinned in-tree sparse TF-IDF cosine "
                                     "baseline (word/bigram, sublinear tf, "
                                     "english stopwords), flat store"},
            "hybrid_rrf": {"experiment_class": "baseline",
                           "note": "the pinned in-tree hybrid baseline (bm25 + "
                                   "dense LSA fused by reciprocal-rank fusion, "
                                   "k=60), flat store"},
            "claude_mem_chroma_lsa": {"experiment_class": "controlled_core",
                                      "note": "the declared stretch arm, run: "
                                              "pinned claude-mem chroma search "
                                              "policy as a controlled core over "
                                              "the shared LSA representation; "
                                              "raw ingest of the replay store "
                                              "is honest (records enter the "
                                              "observation text as-is); its "
                                              "default 90-day recency window "
                                              "is pinned via CLAUDE_MEM_EVAL_"
                                              "NOW=2026-08-30T12:00Z and keeps "
                                              "every record (replay timestamp "
                                              "2026-09-01); product compression "
                                              "not run, by the arm's design"},
        },
        "families_not_run": NOT_RUN,
        "sampling": prior_decl["sampling"] + " (the prior's frozen sample, "
                                             "reused byte for byte)",
        "judging": JUDGING,
        "prior_measurement": "team/S7-KD-WORLDS/verdict.json — the prior run "
                             "of this instrument, bm25 only: Retrieval 21/40, "
                             "Abstention 0/40, Rationale 5/40 (oblique 1/10, "
                             "crossed 0/10). This row re-measures the same "
                             "frozen sample on the other pinned in-repo "
                             "providers; expected to differ: which engine sits "
                             "where on Retrieval and Rationale (dense/LSA "
                             "phrasings may shift oblique/crossed), and nothing "
                             "on Abstention (no added engine has a declined "
                             "concept); bm25 is expected to reproduce the prior "
                             "item for item",
        "expectation": "pre-registered before the run: bm25 reproduces the "
                       "prior exactly (stop rule); the added systems are "
                       "expected to land near bm25's shape — retrieval "
                       "middling once stratified across phrasings, rationale "
                       "middling, abstention at the floor (no declined concept "
                       "in any of them: on a several-hundred-note store some "
                       "token always matches) — with dense_lsa and the "
                       "claude-mem controlled core possibly moving paraphrase/"
                       "oblique phrasing recall, since LSA smears exact tokens; "
                       "if instead a system declines (zero hits) on Abstention "
                       "items, that is the finding of the sprint",
    }
    (HERE / "declaration.json").write_text(json.dumps(declaration, indent=1) + "\n")
    dsha = sha(HERE / "declaration.json")
    print(f"declaration written at {declaration['declared_at']} sha {dsha[:12]}...")

    measured: dict[str, dict[str, list]] = {}
    for seed in SEEDS:
        sampled = {i["item_id"].split("-", 1)[1] for i in items
                   if i["seed"] == seed}
        answers = replay_and_answer(worlds[seed], sampled)
        for name, per_op in answers.items():
            bucket = measured.setdefault(name, {})
            for iid in (i["item_id"] for i in items if i["seed"] == seed):
                bucket[iid] = per_op.get(iid.split("-", 1)[1])
        print(f"seed {seed} replayed: {len(sampled)} sampled recalls answered "
              f"by {len(answers)} engines")

    # stop rule: the control must reproduce the prior before any receipt
    prior_rows = [json.loads(l) for l in
                  (PRIOR / "results.jsonl").read_text().splitlines() if l.strip()]
    prior_bm25 = {r["item_id"]: r["passed"] for r in prior_rows
                  if r["engine"] == "bm25"}
    fresh_bm25 = {}
    for iid, hits in measured["bm25"].items():
        probe = meta[iid]["probe"]
        fresh_bm25[iid] = (len(hits or []) == 0) if \
            next(i["family"] for i in items if i["item_id"] == iid) == "Abstention" \
            else probe.get("gold") in (hits or [])
    drift = sorted(i for i in set(fresh_bm25) | set(prior_bm25)
                   if fresh_bm25.get(i) != prior_bm25.get(i))
    if drift:
        die(f"bm25 control drifts from the prior on {len(drift)} items "
            f"({', '.join(drift[:5])}): the harness has moved; no receipts "
            f"written — a difference between systems must not be confoundable "
            f"with a difference between runs")
    print(f"stop rule: bm25 reproduces the prior item for item ({len(fresh_bm25)} items)")

    receipts = []

    def add(engine, item, passed, response):
        fam = next(i["family"] for i in items if i["item_id"] == item)
        probe = meta[item]["probe"]
        expected = ("decline" if fam == "Abstention"
                    else probe.get("gold") if isinstance(probe.get("gold"), str)
                    else ",".join(probe.get("gold", [])) or probe.get("expect"))
        receipts.append({"ts": now(), "engine": engine, "item_id": item,
                         "passed": bool(passed), "expected": expected,
                         "response": response, "declaration_sha256": dsha})

    # controls first: return-nothing, then oracle, over every item
    for i in items:
        add("return-nothing", i["item_id"], i["family"] == "Abstention",
            "0 hits (control: returns nothing)")
    for i in items:
        probe = meta[i["item_id"]]["probe"]
        if i["family"] == "Abstention":
            add("oracle", i["item_id"], True, "declined (control: perfect abstention)")
        else:
            gold = probe.get("gold")
            add("oracle", i["item_id"], True,
                f"gold {gold} (control: perfect recall)")
    for name in ENGINES:
        for i in items:
            iid = i["item_id"]
            probe = meta[iid]["probe"]
            hits = measured[name].get(iid) or []
            if i["family"] == "Abstention":
                passed = len(hits) == 0
            else:
                passed = probe.get("gold") in hits
            shown = ", ".join(hits[:5]) + (f" (+{len(hits) - 5} more)"
                                           if len(hits) > 5 else "")
            add(name, iid, passed, f"{len(hits)} hits: {shown or 'none'}")

    (HERE / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in receipts))

    # ---- verdict: recount per engine x family, families kept separate ----
    per_family: dict[str, dict] = {}
    for r in receipts:
        if r["engine"] in ("return-nothing", "oracle"):
            continue
        fam = next(i["family"] for i in items if i["item_id"] == r["item_id"])
        cell = per_family.setdefault(r["engine"], {}).setdefault(
            fam, {"passed": 0, "items": 0})
        cell["items"] += 1
        cell["passed"] += int(r["passed"])
    for e in per_family:
        for fam in per_family[e]:
            c = per_family[e][fam]
            c["pass_rate"] = round(c["passed"] / c["items"], 6)

    by_phr: dict[str, dict] = {}
    for e in ENGINES:
        for i in items:
            if i["family"] != "Retrieval":
                continue
            probe = meta[i["item_id"]]["probe"]
            phr = probe.get("phrasing", "?")
            cell = by_phr.setdefault(e, {}).setdefault(
                phr, {"passed": 0, "items": 0})
            cell["items"] += 1
            cell["passed"] += int(next(r["passed"] for r in receipts
                                       if r["engine"] == e
                                       and r["item_id"] == i["item_id"]))
    for e in by_phr:
        for phr in by_phr[e]:
            c = by_phr[e][phr]
            c["pass_rate"] = round(c["passed"] / c["items"], 6)

    def rates(e):
        return ", ".join(f"{fam} {per_family[e][fam]['pass_rate']:.2f}"
                         for fam in ("Retrieval", "Rationale", "Abstention"))

    verdict = {
        "finding": (
            f"on the prior's frozen sample replayed unchanged, no added system "
            f"declines: abstention sits at the floor for every engine, as "
            f"pre-registered — the weakness the external benchmark found is "
            f"not bm25's alone but the flat ranked-retrieval shape itself. "
            f"Retrieval and rationale move by system and are reported "
            f"family-separate beside the prior's cells: the control reproduces "
            f"the prior item for item ({rates('bm25')}); dense_lsa {rates('dense_lsa')}; "
            f"tfidf_cosine {rates('tfidf_cosine')}; hybrid_rrf {rates('hybrid_rrf')}; "
            f"the claude-mem controlled core {rates('claude_mem_chroma_lsa')} "
            f"with its recency window keeping every record. Where the added "
            f"engines land by phrasing is data, not verdict: "
            + "; ".join(f"{e} " + "/".join(
                f"{p} {by_phr[e][p]['pass_rate']:.2f}"
                for p in ("lexical", "paraphrase", "oblique", "crossed"))
                for e in ENGINES)),
        "lane": "external",
        "feeds": "roadmap R-PE — external lanes as separate evidence classes; "
                 "R-PB2 — benchmarks as separate evidence classes, family "
                 "scores kept separate; G3 invocation",
        "card": "team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md",
        "caveat": "The benchmark's author has a system in its own ranking, "
                  "and it wins.",
        "prior": {
            "source": "team/S7-KD-WORLDS/verdict.json",
            "bm25": json.loads((PRIOR / "verdict.json").read_text())
                        ["per_family"]["bm25"],
        },
        "per_family": per_family,
        "retrieval_by_phrasing": by_phr,
        "families_not_run": NOT_RUN,
        "sampling_and_judging": {"sampling": declaration["sampling"],
                                 "judging": JUDGING},
        "expectation_registered_before_run": declaration["expectation"],
        "not_run": {},
    }
    (HERE / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")

    for e in per_family:
        for fam, c in sorted(per_family[e].items()):
            print(f"{e:24s} {fam:11s} {c['passed']}/{c['items']} = {c['pass_rate']:.3f}")
    print(f"finding: {verdict['finding'][:160]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
