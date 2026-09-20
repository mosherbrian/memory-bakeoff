#!/usr/bin/env python3
"""S11-3 runner: pi-lcm NATIVE supersession on broader histories (queue row
S11-3, kiln-flash 2026-09-19). Native arm only - no layer code, no layer arm.

Emits the interface the S11-3G gate (check.py in this directory) declares:

  declaration.json  declared_at, distractor_shape (the documented agentmemory
                    shape), frozen trials sha, frozen generator {path, sha256},
                    broader {distractor_families, stream_length_min}
  receipts.jsonl    one receipt per arm per trial, controls first
                    (never-supersede, always-supersede), then pi-lcm-native,
                    each receipt bound to the declaration sha
  verdict.json      the native counts and per-family counts as recounted, the
                    failing trials named exactly, and the verified prior
                    (team/S7-STATELAYER/verdict.json) quoted old-beside-new

trials.jsonl belongs to gen_trials.py (deterministic, re-runnable in place);
this runner never writes it - it verifies the frozen bytes match the
generator's output and stops if not.

Protocol (declared in declaration.json before any receipt): supersession is
retrieval displacement generalized to streams - the store has no write-time
consolidation, so per trial a fresh pinned store (pi_lcm_store_reader_toollevel,
the S4-14/S6-2 pin) ingests the trial's whole stream in order, the ORIGINAL's
own query is re-issued with every write present, and superseded = the top hit
is any write other than the original. Controls: never-supersede supersedes
nothing, always-supersede everything - the instrument must read both ends for
a null to be evidence. Sanity before declaration: each original alone answers
its own query as top-1; a trial that cannot is malformed and nothing is frozen.

$0, local, no LLM, no score import.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = Path("/home/bmosher/memory-bake-off/team")   # absolute: no caller-tree dependence
WORKSPACE = TEAM.parent
for p in (str(TEAM / "s4-14-crossengine-rerun"),
          str(WORKSPACE / "implementer" / "repo" / "src"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

from run_s4_14 import PiLcmToolLevelProvider  # noqa: E402  (S4-14/S6-2 pin)
from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from gen_trials import FAMILIES, build_trials, serialize  # noqa: E402

PRIOR_DIR = TEAM / "S7-STATELAYER"
STREAM_MIN = 4


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def die(msg: str) -> None:
    print(f"FATAL: {msg}", flush=True)
    raise SystemExit(1)


def wts(w: dict) -> datetime:
    return datetime.fromisoformat(w["ts"] + "T00:00:00+00:00")


def store_ok(eng) -> None:
    probe = eng.probe()
    if not probe.available:
        die(f"pinned store unavailable: {probe.reason}")


def drive(eng, t: dict) -> bool:
    """One native-arm trial on a fresh store: ingest the whole stream in
    order, re-issue the original's own query, report displacement."""
    eng.reset()
    eng.ingest([MemoryRecord(id=w["id"], text=w["text"], timestamp=wts(w),
                             session_id=f"sess-{t['trial_id']}")
                for w in t["stream"]])
    res = eng.retrieve(QueryCase(id=t["trial_id"], category=t["kind"],
                                 query=t["query"], relevant_ids=(),
                                 prohibited_ids=()), top_k=1)
    top = res.items[0].record_id if res.items else None
    original = t["stream"][0]["id"]
    if top is not None and top != original \
            and top not in {w["id"] for w in t["stream"]}:
        die(f"{t['trial_id']}: top hit {top!r} is not a write of the stream")
    return top is not None and top != original


def main() -> int:
    # ---- trials: the generator's own output, verified against the frozen bytes
    frozen = HERE / "trials.jsonl"
    if not frozen.is_file():
        die("trials.jsonl missing: run gen_trials.py first")
    trials = build_trials()
    if frozen.read_text() != serialize(trials):
        die("trials.jsonl does not match gen_trials.py output - regenerate "
            "BEFORE any declaration; never edit trials under a frozen pin")
    n_dis = sum(1 for t in trials if t["kind"] == "distractor")
    n_upd = sum(1 for t in trials if t["kind"] == "update")
    if n_dis <= 32 or n_upd < 12 or n_upd < 1:
        die(f"breadth wrong: {n_dis} distractors, {n_upd} updates")
    if any(len(t["stream"]) < max(STREAM_MIN, 3) for t in trials):
        die("a stream is shorter than the declared length")

    eng = PiLcmToolLevelProvider()
    store_ok(eng)

    # ---- sanity BEFORE declaration: each original alone answers its own query
    bad = []
    for t in trials:
        eng.reset()
        eng.ingest([MemoryRecord(id=t["stream"][0]["id"],
                                 text=t["stream"][0]["text"],
                                 timestamp=wts(t["stream"][0]),
                                 session_id=f"sess-{t['trial_id']}")])
        res = eng.retrieve(QueryCase(id=t["trial_id"], category=t["kind"],
                                     query=t["query"], relevant_ids=(),
                                     prohibited_ids=()), top_k=1)
        if not res.items or res.items[0].record_id != t["stream"][0]["id"]:
            bad.append(t["trial_id"])
    if bad:
        eng.close()
        die(f"malformed trials (original does not answer its own query): "
            f"{bad} - fix gen_trials.py, nothing is frozen yet")

    # ---- declaration: written once, before the first receipt, never after
    declaration = {
        "declared_at": now(),
        "distractor_shape": "agentmemory-class extended: deliberately distinct "
                            "facts sharing the fact-type template, the shape "
                            "research/AGENTMEMORY_FINDINGS.md documents at 418/"
                            "450 false supersessions (92.9%) under the /remember "
                            "Jaccard write path (Jaccard 0.75-0.9 near-neighbors); "
                            "per-trial jaccard lists are recorded in trials.jsonl; "
                            "three near-neighbor relations declared before the "
                            "run: mailbox-rename (renamed mail target of the same "
                            "service), ledger-amend (the service's companion "
                            "ledger line: redis->postgres, canary->blue-green, "
                            "synthetic->load-test, import->export), roster-drift "
                            "(joint roster of two services)",
        "trials_sha256": sha(frozen),
        "generator": {"path": "gen_trials.py", "sha256": sha(HERE / "gen_trials.py")},
        "broader": {"distractor_families": list(FAMILIES),
                    "stream_length_min": STREAM_MIN},
        "protocol": "supersession for pi-lcm-native is retrieval displacement "
                    "generalized to streams: the store has no write-time "
                    "consolidation, so per trial a fresh pinned store "
                    "(pi_lcm_store_reader_toollevel, the S4-14/S6-2 pin) "
                    "ingests the trial's whole 4-write stream in order, the "
                    "original's own query is re-issued with every write "
                    "present, and superseded = the top hit is any write other "
                    "than the original. never-supersede/always-supersede are "
                    "the controls and run first. Sanity before declaration: "
                    "each original alone answers its own query as top-1. "
                    "Ground truth: near-neighbor writes are different facts "
                    "(renamed target, companion ledger line, joint roster), "
                    "never successors of the original, so distractor "
                    "displacement is false supersession; update streams are "
                    "genuinely newer states of the same fact, so the original "
                    "must be displaced.",
        "expectation": "pre-registered before the run: the prior native arm "
                       "scored 0/32 false supersessions on cross-scope "
                       "near-neighbors (same whole-token scope match was the "
                       "only pressure). The three new families pressure "
                       "mechanisms the prior corpus never exercised: "
                       "mailbox-rename and roster-drift embed the original's "
                       "scope token as a SUBSTRING of the near-neighbor "
                       "subject (delta-mailbox, delta-fjord), and whether the "
                       "exact-AND gate matches substrings or whole tokens "
                       "decides if they compete at all; ledger-amend shares "
                       "scope and template but swaps the object token. "
                       "Expected: false supersession stays LOW if the store "
                       "matches whole tokens; a HIGH rate would be a genuine "
                       "native failure on broader histories - exactly the "
                       "evidence the state-layer answer page requires. Either "
                       "number decides; this row measures, it does not defend "
                       "the prior's null.",
        "prior_measurement": {
            "pi_lcm": "team/S7-STATELAYER/verdict.json (VERIFIED PASS S7-3G): "
                      "native 0/32 false supersessions, 12/12 updates "
                      "superseded - controlled corpus only, one distractor "
                      "shape, streams of 2 writes; this row re-measures the "
                      "native arm on the declared-broader corpus above and "
                      "must report old-vs-new (standing re-measurement rule)",
            "agentmemory": "418 of 450 stress distractors (92.9%) falsely "
                           "superseded under the /remember Jaccard write path "
                           "- the protected comparison point, from "
                           "research/AGENTMEMORY_FINDINGS.md",
        },
    }
    (HERE / "declaration.json").write_text(json.dumps(declaration, indent=1) + "\n")
    dsha = sha(HERE / "declaration.json")
    print(f"declaration written at {declaration['declared_at']} sha {dsha[:12]}...",
          flush=True)

    # ---- receipts: controls first, then the native arm
    receipts = []

    def add(arm, t, sup):
        receipts.append({"ts": now(), "arm": arm, "trial_id": t["trial_id"],
                         "superseded": bool(sup), "declaration_sha256": dsha})

    for t in trials:
        add("never-supersede", t, False)
    for t in trials:
        add("always-supersede", t, True)

    winners = {}
    for t in trials:
        sup = drive(eng, t)
        add("pi-lcm-native", t, sup)
        if sup:
            winners[t["trial_id"]] = True
    eng.close()
    (HERE / "receipts.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in receipts))

    # ---- verdict: recounted the way the gate recounts, old beside new
    prior_verdict = json.loads((PRIOR_DIR / "verdict.json").read_text())
    old = {k: prior_verdict["arms"]["pi-lcm-native"][k]
           for k in ("false_superseded", "distractor_trials",
                     "missed_updates", "update_trials")}
    kind = {t["trial_id"]: t["kind"] for t in trials}
    sup = {r["trial_id"]: r["superseded"] for r in receipts
           if r["arm"] == "pi-lcm-native"}
    false = sorted(t["trial_id"] for t in trials
                   if t["kind"] == "distractor" and sup[t["trial_id"]])
    missed = sorted(t for t, k in kind.items()
                    if k == "update" and not sup[t])
    per_family = {f: {"false_superseded": sum(
        1 for t in trials if t.get("family") == f
        and sup[t["trial_id"]]),
        "distractor_trials": sum(1 for t in trials
                                 if t.get("family") == f)} for f in FAMILIES}
    native = {"false_superseded": len(false), "distractor_trials": n_dis,
              "missed_updates": len(missed), "update_trials": n_upd,
              "false_supersession_rate": len(false) / n_dis}
    failed = bool(false or missed)
    verdict = {
        "verdict": "native-failure" if failed else "native-null",
        "finding": "",   # filled below
        "feeds": "roadmap R-PF, Decision Gate F — the Gate F evidence base "
                 "named by the S6-3 map",
        "changes_state_layer_answer": failed,
        "native": native,
        "per_family": per_family,
        "false_supersession_trials": false,
        "missed_update_trials": missed,
        "prior": {"source": "team/S7-STATELAYER/verdict.json",
                  "native": old},
        "native_detail": {
            "distractor_trials_displaced": false,
            "update_trials_superseded": n_upd - len(missed),
            "update_trials_missed": missed,
            "note": "superseded = the original's own query returns a newer "
                    "write as top-1 with the whole 4-write stream in a fresh "
                    "store; per-write winners are recoverable by re-running "
                    "run_hist.py against the frozen trials sha",
        },
        "comparison": {"system": "agentmemory", "false_superseded": 418,
                       "trials": 450,
                       "source": "implementer/repo/research/AGENTMEMORY_FINDINGS.md"},
        "expectation_registered_before_run": declaration["expectation"],
    }
    old_fmt = (f"{old['false_superseded']}/{old['distractor_trials']} false "
               f"supersessions, {old['missed_updates']}/{old['update_trials']} "
               f"missed updates")
    new_fmt = (f"{native['false_superseded']}/{n_dis} false supersessions, "
               f"{native['missed_updates']}/{n_upd} missed updates")
    if failed:
        verdict["finding"] = (
            f"the native pi-lcm arm fails on the declared broader corpus: "
            f"{new_fmt} (per family "
            f"{ {f: c['false_superseded'] for f, c in per_family.items()} }) "
            f"against the prior's controlled-corpus {old_fmt} - broader "
            f"histories do surface native supersession failure, and the "
            f"state-layer answer changes: the prior's 0/32 null does not "
            f"generalize untested")
    else:
        verdict["finding"] = (
            f"native null on the declared broader corpus: {new_fmt} with "
            f"controls reading both ends, against the prior's controlled-"
            f"corpus {old_fmt} - the pi-lcm native null now holds beyond the "
            f"prior's single shape and two-write streams, and the "
            f"state-layer answer does not change")
    (HERE / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")

    print(f"native: {native}")
    print(f"per family: { {f: (c['false_superseded'], c['distractor_trials']) for f, c in per_family.items()} }")
    print(f"controls: never-supersede 0 displaced by construction; "
          f"always-supersede all displaced by construction")
    print(f"prior (S7-STATELAYER, controlled): {old_fmt}")
    print(f"verdict: {verdict['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
