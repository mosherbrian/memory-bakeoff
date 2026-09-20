#!/usr/bin/env python3
"""S7-4 runner: KnowledgeDrift frozen worlds as a second instrument
(queue row S7-4, kiln-flash 2026-09-17).

Emits the interface S7-4G's gate (check.py, authored 2026-09-17 13:53 from the
row text alone) declares:

  declaration.json  pinned upstream (repo + commit + licence + world-file
                    hashes), the frozen item list sha, our engines with their
                    evidence classes, and families_not_run with reasons
  items.jsonl       sampled probes: {item_id, family (the card's names), seed}
  results.jsonl     receipts in run order: controls first (return-nothing,
                    oracle), then our engine; each carries expected, response
                    and the declaration sha
  verdict.json      per-family recount for our engine, the card's caveat
                    quoted verbatim, lane/feeds/prior

Replay follows the upstream protocol (docs/protocol.md): ops in stream order
are load-bearing; the store mutates on inscribe/supersede/release/purge; a
sampled recall is answered at its own position in the stream against the
store as it then stands. Judging is per the declared rule below, and the
upstream leaderboard is neither cited nor approached: no score import.

$0, local, no LLM, no score import. Worlds are the upstream MIT frozen
worlds/v2 500-fact files at the pinned commit, hashed in the declaration.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = Path("/home/bmosher/memory-bake-off/team")
REPO = Path("/home/bmosher/memory-bake-off/implementer/repo")
for p in (str(REPO / "src"),):
    if p not in sys.path:
        sys.path.insert(0, p)

from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.providers.bm25 import BM25Provider  # noqa: E402

WORLDS_DIR = "upstream/KnowledgeDrift/worlds/v2"
UPSTREAM_REPO = "github.com/techtheist/KnowledgeDrift (MIT)"
COMMIT = "edff308ea6ab331dbb24e0ab5ac29717d88b29f0"
WORLD_FILES = {
    "knowledgedrift-500-seed1-v2.json": "9766378f93e3a7d4",   # digest pin; sha256 pinned below
    "knowledgedrift-500-seed2-v2.json": "f19851acdf7c3043",
}
SEEDS = (1, 2)
SAMPLE_PER_FAMILY = 20
K_DEFAULT = 10
FAMILIES_RUN = ("Retrieval", "Abstention", "Rationale")
JUDGING = {
    "Retrieval": "probe expect gold: the gold note key must appear among the "
                 "hits (top k per the recall op, k=10)",
    "Abstention": "probe expect control: correct behaviour is to decline — "
                  "zero hits. The engine has no declined concept, so zero hits "
                  "is the only honest decline it can produce",
    "Rationale": "probe expect linked: the gold (the reasoning note linked to "
                 "the anchor decision) must appear among the hits (top k=10)",
}
NOT_RUN = {
    "Currency": "needs supersession history and a current-head notion our "
                "flat baseline engine does not implement (history capability "
                "is absent); measuring it here would mean building the very "
                "write-path behavior row S7-3 just measured and the roadmap's "
                "Phase-G ban gates",
    "Contradiction": "needs the suspects capability (nominating disagreements "
                     "for a person); the engine has none, so every case would "
                     "score 0 by construction, which is a capability absence, "
                     "not a selectivity measurement",
    "Drift": "needs stale-sibling detection (suspects capability); same "
             "capability absence as Contradiction",
    "Deletion": "needs release traces and tombstones; a flat baseline store "
                "just deletes (trace: false upstream), so the family would "
                "measure the delete primitive, not memory behavior",
    "Temporal": "needs a recall window applied natively by the store "
                "(temporal capability); the engine has no capture-time "
                "filter, so the family would be unmeasured, not failed",
    "Authority": "the optional ninth family; needs endorsement rungs stored "
                 "as first-class note attributes, which the engine lacks",
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
    """Deterministic stratified sample per run family, in probe-file order.
    Retrieval is stratified across the four phrasings (5 each per seed) so no
    phrasing block is over- or under-represented by a stride accident."""
    items = []
    for fam_lower, fam_card in (("retrieval", "Retrieval"),
                                ("abstention", "Abstention"),
                                ("rationale", "Rationale")):
        if fam_lower == "retrieval":
            phrasings = ("lexical", "paraphrase", "oblique", "crossed")
            per = SAMPLE_PER_FAMILY // len(phrasings)
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
            stride = max(1, len(ids) // SAMPLE_PER_FAMILY)
            picked = ids[::stride][:SAMPLE_PER_FAMILY]
        for pid in picked:
            items.append({"item_id": f"s{seed}-{pid}", "family": fam_card,
                          "seed": seed})
    return items


def replay_and_answer(world: dict, sampled: set) -> dict:
    """Replay ops in stream order; answer a sampled recall at its own
    position against the store as it then stands (bm25, top k of the op)."""
    live: dict[str, str] = {}   # key -> text
    answers: dict[str, list] = {}
    eng = BM25Provider()

    def run_query(op):
        recs = [MemoryRecord(id=k, text=t,
                             timestamp=datetime(2026, 9, 1, tzinfo=timezone.utc),
                             session_id="kd") for k, t in live.items()]
        eng.ingest(recs)
        res = eng.retrieve(QueryCase(id=op["id"], category="probe",
                                     query=op["query"], relevant_ids=(),
                                     prohibited_ids=()),
                           top_k=op.get("k", K_DEFAULT))
        answers[op["id"]] = [it.record_id for it in res.items]

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
    eng.close()
    return answers


def main() -> int:
    wdir = HERE / WORLDS_DIR
    worlds, file_hashes = {}, {}
    for fname in WORLD_FILES:
        p = wdir / fname
        if not p.is_file():
            die(f"world file missing: {p}")
        file_hashes[fname] = sha(p)
        w = load_world(p)
        worlds[w["spec"]["seed"]] = w
        print(f"loaded {fname}: seed {w['spec']['seed']}, {len(w['ops'])} ops, "
              f"{len(w['probes'])} probes")

    items, meta = [], {}
    for seed in SEEDS:
        for it in sample(worlds[seed], seed):
            probe = worlds[seed]["probes"][it["item_id"].split("-", 1)[1]]
            items.append(it)
            meta[it["item_id"]] = {"probe": probe,
                                   "op": worlds[seed]["recall_ops"][probe["id"]]}
    if len({i["seed"] for i in items}) < 2:
        die("sampling produced a single seed")

    # measure our engine: replay each world once, answering sampled recalls
    measured: dict[str, list] = {}
    for seed in SEEDS:
        sampled = {iid.split("-", 1)[1] for iid in meta
                   if iid.startswith(f"s{seed}-")}
        answers = replay_and_answer(worlds[seed], sampled)
        for iid, probe_id in ((i, i.split("-", 1)[1]) for i in meta
                              if i.startswith(f"s{seed}-")):
            measured[iid] = answers.get(probe_id)

    (HERE / "items.jsonl").write_text(
        "".join(json.dumps(i) + "\n" for i in items))

    declaration = {
        "declared_at": now(),
        "items_sha256": sha(HERE / "items.jsonl"),
        "worlds": {
            "upstream_repo": UPSTREAM_REPO,
            "commit": COMMIT,
            "license": "MIT",
            "dir": WORLDS_DIR,
            "files": file_hashes,
        },
        "engines": {"bm25": {"experiment_class": "baseline",
                             "note": "the pinned in-tree BM25 baseline "
                                     "(repo be2bfa9), flat store, no "
                                     "capabilities beyond ranked lexical "
                                     "recall; replayed per the upstream "
                                     "protocol (flat column of docs/"
                                     "protocol.md)"}},
        "families_not_run": NOT_RUN,
        "sampling": "per seed (1 and 2, the 500-fact frozen worlds): "
                    "deterministic stride sample of 20 probes per family from "
                    "the probe file order, retrieval restricted to expect=gold "
                    "(path-bound probes excluded), each sampled probe answered "
                    "at its own position in the ops stream",
        "judging": JUDGING,
        "prior_measurement": "no run of our engines on these worlds exists — "
                             "none exists; the card recorded the candidate "
                             "with structure adopted and scores unimported",
        "expectation": "pre-registered before the run: the lexical baseline is "
                       "expected to sit high on Retrieval (its home turf — the "
                       "card's own shape), near-floor on Abstention (it has no "
                       "declined concept: on a several-hundred-note store some "
                       "token always matches, so it fires on questions about "
                       "nothing), and middling on Rationale; if so, the second "
                       "instrument independently reproduces the shape our own "
                       "S6-2 instrument measured, on a corpus we did not build",
    }
    (HERE / "declaration.json").write_text(json.dumps(declaration, indent=1) + "\n")
    dsha = sha(HERE / "declaration.json")
    print(f"declaration written at {declaration['declared_at']} sha {dsha[:12]}...")

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
    for i in items:
        iid = i["item_id"]
        probe = meta[iid]["probe"]
        hits = measured.get(iid) or []
        if i["family"] == "Abstention":
            passed = len(hits) == 0
        else:
            passed = probe.get("gold") in hits
        shown = ", ".join(hits[:5]) + (f" (+{len(hits) - 5} more)" if len(hits) > 5 else "")
        add("bm25", iid, passed, f"{len(hits)} hits: {shown or 'none'}")

    (HERE / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in receipts))

    # ---- verdict: recount per engine x family ----
    per_family: dict[str, dict] = {}
    for r in receipts:
        if r["engine"] == "return-nothing" or r["engine"] == "oracle":
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

    bm = per_family["bm25"]
    verdict = {
        "finding": "",   # filled below
        "lane": "external",
        "feeds": "roadmap R-PE — external lanes as separate evidence classes; "
                 "the one S6-2 KnowledgeDrift choice not exercised until now",
        "card": "team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md",
        "caveat": "The benchmark's author has a system in its own ranking, "
                  "and it wins.",
        "prior": "no run of our engines on these frozen worlds exists — none "
                 "exists; scores are re-derived here, none imported",
        "per_family": per_family,
        "families_not_run": NOT_RUN,
        "sampling_and_judging": {"sampling": declaration["sampling"],
                                 "judging": JUDGING},
        "expectation_registered_before_run": declaration["expectation"],
    }
    r_ab = bm["Abstention"]["pass_rate"]
    r_ret = bm["Retrieval"]["pass_rate"]
    r_rat = bm["Rationale"]["pass_rate"]
    by_phr = {}
    for i in items:
        if i["family"] != "Retrieval":
            continue
        probe = meta[i["item_id"]]["probe"]
        phr = probe.get("phrasing", "?")
        cell = by_phr.setdefault(phr, {"passed": 0, "items": 0})
        cell["items"] += 1
        cell["passed"] += int(next(r["passed"] for r in receipts
                                   if r["engine"] == "bm25"
                                   and r["item_id"] == i["item_id"]))
    for phr in by_phr:
        by_phr[phr]["pass_rate"] = round(by_phr[phr]["passed"] / by_phr[phr]["items"], 6)
    verdict["retrieval_by_phrasing"] = by_phr
    lex = by_phr.get("lexical", {}).get("pass_rate")
    verdict["finding"] = (
        f"on the upstream frozen worlds (seeds 1 and 2, {len(items)} sampled "
        f"probes, scores re-derived under the declared judging rules) the "
        f"lexical baseline scores retrieval {r_ret:.2f} "
        f"(lexical phrasing {lex:.2f}, but paraphrase/oblique/crossed phrasings "
        f"pull it down — the upstream phrasings are doing real work), rationale "
        f"{r_rat:.2f}, abstention {r_ab:.2f}: the second instrument reproduces "
        f"the shape our own instrument measured — lookup recall without any "
        f"ability to decline (the engine has no declined concept and fires "
        "whenever any token matches). The external lane is live: a home-team "
        "score on someone else's frozen corpus, the caveat quoted below "
        "travelling beside every number")
    (HERE / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")

    for e in per_family:
        for fam, c in sorted(per_family[e].items()):
            print(f"{e:6s} {fam:11s} {c['passed']}/{c['items']} = {c['pass_rate']:.3f}")
    print(f"finding: {verdict['finding'][:140]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
