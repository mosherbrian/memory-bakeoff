#!/usr/bin/env python3
"""S7-3 runner: false supersession — pi-lcm native store vs a trivial
mark-superseded-on-newer-write layer, under agentmemory-class distractors
(queue row S7-3, kiln-flash 2026-09-17).

Emits the interface S7-3G's gate (check.py, authored 2026-09-17 13:48 from the
row text alone) declares:

  declaration.json  declared_at, distractor_shape (agentmemory-class), the
                    frozen trials list sha, the thin layer {path, sha256},
                    rule {layer_helps_if_rate_drop_at_least: m,
                    layer_max_missed_update_rate: u}
  trials.jsonl      one trial per line: {trial_id, kind, scope, fact_type,
                    query, original{id,text,ts}, newer{id,text,ts}, jaccard}
  receipts.jsonl    one receipt per arm per trial, controls first
                    (never-supersede, always-supersede), then pi-lcm-native
                    (the real pinned store reader + tool-level query behavior,
                    fresh store per trial), then thin-layer (the pinned layer's
                    own decide())
  verdict.json      both measured arms recounted, the protected comparison
                    point (agentmemory 418/450) quoted from the repo file it
                    came from, and the verdict the declared rule gives

Supersession semantics for pi-lcm-native: the store has no write-time
consolidation, so "the original was treated as superseded" is operationalized
as retrieval displacement — after both records are in the store, the
original's own query returns the newer write as its top hit. $0, local, no
LLM, no score import.
"""
import hashlib
import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = Path("/home/bmosher/memory-bake-off/team")   # absolute: no caller-tree dependence
WORKSPACE = TEAM.parent
for p in (str(TEAM / "s4-14-crossengine-rerun"), str(TEAM / "s4-12-crossengine"),
          str(WORKSPACE / "implementer" / "repo" / "src"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

from run_s4_14 import PiLcmToolLevelProvider  # noqa: E402  (S4-14/S6-2 pin)
from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from thin_layer import ThinLayer  # noqa: E402  (the probe this row measures)

RULE_M = 0.50   # the layer must at least halve the native false-supersession rate
RULE_U = 0.10   # and miss at most 10% of the real updates
T_ORIG = datetime(2026, 9, 1, tzinfo=timezone.utc)
T_NEW = datetime(2026, 9, 2, tzinfo=timezone.utc)
SCOPES = ["delta", "fjord", "archive", "search", "reporter", "mailer", "catalog", "badge"]
TEMPLATES = [
    ("redis migration",
     lambda s, v, d: f"the {s} service completed the redis migration to version {v} on {d}",
     lambda s: f"{s} redis migration",
     ("7", "2026-08-01"), ("8", "2026-09-01"), ("5", "2026-07-15")),
    ("canary rollout",
     lambda s, v, d: f"the {s} deploy runs its canary rollout at {v} percent traffic",
     lambda s: f"{s} canary rollout",
     ("5", None), ("25", None), ("10", None)),
    ("synthetic traffic quota",
     lambda s, v, d: f"the {s} synthetic traffic quota allows {v} requests per hour",
     lambda s: f"{s} synthetic traffic quota",
     ("1000", None), ("4000", None), ("2500", None)),
    ("import utility retries",
     lambda s, v, d: f"the {s} import utility retries failed batches {v} times before paging",
     lambda s: f"{s} import utility retries",
     ("3", None), ("5", None), ("2", None)),
]
PROTECTED = {"system": "agentmemory", "false_superseded": 418, "trials": 450,
             "source": "implementer/repo/research/AGENTMEMORY_FINDINGS.md"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def die(msg: str) -> None:
    print(f"FATAL: {msg}", flush=True)
    raise SystemExit(1)


def jaccard(a: str, b: str) -> float:
    ta, tb = set(a.lower().split()), set(b.lower().split())
    return len(ta & tb) / len(ta | tb)


def build_trials() -> list:
    """Deterministic agentmemory-class trial list: near-neighbor facts, same
    template, different scope (the shape research/AGENTMEMORY_FINDINGS.md
    documents at 418/450), plus same-key updates with a genuinely newer value."""
    trials = []
    for sA, (ft, build, query, v1, _, v_other) in itertools.product(SCOPES, TEMPLATES):
        sB = next(s for s in SCOPES if s != sA)
        o_text, n_text = build(sA, v1[0], v1[1]), build(sB, v_other[0], v_other[1])
        trials.append({
            "trial_id": f"dis-{sA}-{ft.replace(' ', '-')}", "kind": "distractor",
            "scope": sA, "fact_type": ft, "query": query(sA),
            "original": {"id": f"dis-{sA}-{ft.split()[0]}-orig", "text": o_text,
                         "ts": T_ORIG.isoformat(), "scope": sA, "fact_type": ft},
            "newer": {"id": f"dis-{sA}-{ft.split()[0]}-new", "text": n_text,
                      "ts": T_NEW.isoformat(), "scope": sB, "fact_type": ft},
            "jaccard": round(jaccard(o_text, n_text), 3),
        })
    for sA, (ft, build, query, v1, v2, _) in itertools.product(SCOPES[:3], TEMPLATES):
        o_text, n_text = build(sA, v1[0], v1[1]), build(sA, v2[0], v2[1])
        trials.append({
            "trial_id": f"upd-{sA}-{ft.replace(' ', '-')}", "kind": "update",
            "scope": sA, "fact_type": ft, "query": query(sA),
            "original": {"id": f"upd-{sA}-{ft.split()[0]}-orig", "text": o_text,
                         "ts": T_ORIG.isoformat(), "scope": sA, "fact_type": ft},
            "newer": {"id": f"upd-{sA}-{ft.split()[0]}-new", "text": n_text,
                      "ts": T_NEW.isoformat(), "scope": sA, "fact_type": ft},
            "jaccard": round(jaccard(o_text, n_text), 3),
        })
    return trials


def sanity_check(trials: list) -> None:
    """Pre-declaration instrument check: the original alone must answer its own
    query as top-1, else the trial is malformed and nothing may be frozen."""
    eng = PiLcmToolLevelProvider()
    bad = []
    for t in trials:
        eng.reset()
        eng.ingest([MemoryRecord(id=t["original"]["id"], text=t["original"]["text"],
                                 timestamp=T_ORIG, session_id=f"sess-{t['trial_id']}")])
        res = eng.retrieve(QueryCase(id=t["trial_id"], category=t["kind"],
                                     query=t["query"], relevant_ids=(),
                                     prohibited_ids=()), top_k=1)
        if not res.items or res.items[0].record_id != t["original"]["id"]:
            bad.append(t["trial_id"])
    eng.close()
    if bad:
        die(f"malformed trials (original does not answer its own query): {bad}")


def main() -> int:
    trials = build_trials()
    n_dis = sum(1 for t in trials if t["kind"] == "distractor")
    n_upd = sum(1 for t in trials if t["kind"] == "update")
    if n_dis < 30 or n_upd < 10:
        die(f"trial list too small: {n_dis} distractor, {n_upd} update")
    sanity_check(trials)

    layer_path = HERE / "thin_layer.py"
    if not layer_path.is_file():
        die("thin_layer.py missing from the artifact directory")
    code_lines = [l for l in layer_path.read_text().splitlines()
                  if l.strip() and not l.strip().startswith("#")]
    if len(code_lines) > 80:
        die(f"thin layer has {len(code_lines)} code lines; the probe must stay trivial")

    (HERE / "trials.jsonl").write_text(
        "".join(json.dumps(t) + "\n" for t in trials))

    declaration = {
        "declared_at": now(),
        "distractor_shape": "agentmemory-class: deliberately distinct facts "
                            "sharing the fact-type template but scoped to "
                            "different repos/services (a delta redis migration "
                            "vs a fjord redis migration, archive vs search "
                            "canary commands) — the near-neighbor pressure "
                            "shape research/AGENTMEMORY_FINDINGS.md documents "
                            "at 418/450 false supersessions (Jaccard 0.75-0.9); "
                            "per-trial jaccard is recorded in trials.jsonl",
        "trials_sha256": sha(HERE / "trials.jsonl"),
        "thin_layer": {"path": "thin_layer.py", "sha256": sha(layer_path)},
        "rule": {"layer_helps_if_rate_drop_at_least": RULE_M,
                 "layer_max_missed_update_rate": RULE_U,
                 "note": "m 0.50: a state layer earns existence only by at "
                         "least halving the native false-supersession rate; "
                         "u 0.10: while missing at most 1 of 12 real updates; "
                         "both fixed before the run"},
        "protocol": "supersession for pi-lcm-native is retrieval displacement: "
                    "the store has no write-time consolidation, so per trial a "
                    "fresh pinned store holds original+newer and the original's "
                    "own query is re-issued; superseded = the newer write is "
                    "the top hit. never-supersede/always-supersede are the "
                    "controls; thin-layer is the pinned layer's own decide(). "
                    "Sanity before declaration: each original alone answers "
                    "its own query as top-1.",
        "prior_measurement": {
            "pi_lcm": "no false-supersession measurement of pi-lcm exists — "
                      "none exists; stated per the standing re-measurement rule",
            "agentmemory": "418 of 450 stress distractors (92.9%) falsely "
                           "superseded under the /remember Jaccard write path — "
                           "the protected comparison point, from "
                           "research/AGENTMEMORY_FINDINGS.md",
        },
        "expectation": "pre-registered before the run: pi-lcm's exact-AND "
                       "gate matches distractors only through bounded "
                       "relaxation, so the native false-supersession rate is "
                       "expected LOW; if it is, the rate drop cannot clear "
                       "m and the verdict is layer-does-not-help — pi-lcm does "
                       "not have agentmemory's disease and a state layer adds "
                       "nothing. If native false-supersession is HIGH, the "
                       "trivial layer is expected to drop it to ~0 while "
                       "missing 0 updates (decide() is key equality) and the "
                       "verdict is layer-helps. Either number decides Gate F.",
    }
    (HERE / "declaration.json").write_text(json.dumps(declaration, indent=1) + "\n")
    dsha = sha(HERE / "declaration.json")
    print(f"declaration written at {declaration['declared_at']} sha {dsha[:12]}...")

    # ---- receipts: controls first, then the two measured arms ----
    receipts = []

    def add(arm, t, sup):
        receipts.append({"ts": now(), "arm": arm, "trial_id": t["trial_id"],
                         "superseded": bool(sup), "declaration_sha256": dsha})

    for t in trials:
        add("never-supersede", t, False)
    for t in trials:
        add("always-supersede", t, True)

    eng = PiLcmToolLevelProvider()
    for t in trials:
        eng.reset()
        eng.ingest([
            MemoryRecord(id=t["original"]["id"], text=t["original"]["text"],
                         timestamp=T_ORIG, session_id=f"sess-{t['trial_id']}"),
            MemoryRecord(id=t["newer"]["id"], text=t["newer"]["text"],
                         timestamp=T_NEW, session_id=f"sess-{t['trial_id']}"),
        ])
        res = eng.retrieve(QueryCase(id=t["trial_id"], category=t["kind"],
                                     query=t["query"], relevant_ids=(),
                                     prohibited_ids=()), top_k=1)
        add("pi-lcm-native", t,
            bool(res.items) and res.items[0].record_id == t["newer"]["id"])
    eng.close()

    layer = ThinLayer()
    for t in trials:
        add("thin-layer", t, layer.decide(t["original"], t["newer"]))

    (HERE / "receipts.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in receipts))

    # ---- verdict from the frozen rule, recounted the way the gate does ----
    kind = {t["trial_id"]: t["kind"] for t in trials}
    sup = {a: {} for a in ("never-supersede", "always-supersede",
                           "pi-lcm-native", "thin-layer")}
    for r in receipts:
        sup[r["arm"]][r["trial_id"]] = r["superseded"]

    def count(arm):
        d = [t for t, k in kind.items() if k == "distractor"]
        u = [t for t, k in kind.items() if k == "update"]
        false = sum(1 for t in d if sup[arm][t])
        return {"false_superseded": false, "distractor_trials": len(d),
                "missed_updates": sum(1 for t in u if not sup[arm][t]),
                "update_trials": len(u),
                "false_supersession_rate": round(false / len(d), 6)}

    native, thin = count("pi-lcm-native"), count("thin-layer")
    drop = native["false_supersession_rate"] - thin["false_supersession_rate"]
    missed_rate = thin["missed_updates"] / thin["update_trials"]
    helps = (drop >= RULE_M - 1e-9 and missed_rate <= RULE_U + 1e-9)
    native_native_displaced = [t["trial_id"] for t in trials
                               if t["kind"] == "distractor"
                               and sup["pi-lcm-native"][t["trial_id"]]]
    upd_caught_native = sum(1 for t in trials if t["kind"] == "update"
                            and sup["pi-lcm-native"][t["trial_id"]])
    verdict = {
        "verdict": "layer-helps" if helps else "layer-does-not-help",
        "finding": "",   # filled below
        "feeds": "roadmap R-PF, Decision Gate F — the one number the S6-3 map "
                 "names as deciding Gate F",
        "prior_pi_lcm": "no prior false-supersession measurement of pi-lcm "
                        "exists — none exists; this row is the first "
                        "measurement, per the standing re-measurement rule",
        "comparison": PROTECTED,
        "arms": {"pi-lcm-native": native, "thin-layer": thin},
        "controls": {"never-supersede": count("never-supersede"),
                     "always-supersede": count("always-supersede")},
        "native_detail": {
            "distractor_trials_displaced": native_native_displaced,
            "update_trials_superseded": upd_caught_native,
        },
        "rule_worked_out": {"rate_drop": round(drop, 6),
                            "thin_missed_update_rate": round(missed_rate, 6)},
        "expectation_registered_before_run": declaration["expectation"],
    }
    if helps:
        verdict["finding"] = (
            f"a {len(code_lines)}-code-line key-equality layer drops false "
            f"supersession from {native['false_superseded']}/{n_dis} to "
            f"{thin['false_superseded']}/{n_dis} while missing "
            f"{thin['missed_updates']}/{n_upd} real updates: the deciding "
            "property exists and is trivial, so Decision Gate F may treat a "
            "thin keyed state layer as sufficient — building more than this "
            "probe stays gated")
    else:
        verdict["finding"] = (
            f"the rate drop ({drop:+.3f}, rule needs {RULE_M}) or the layer's "
            f"missed updates ({missed_rate:.3f}, rule allows {RULE_U}) fails "
            f"the declared rule: native false supersession is "
            f"{native['false_superseded']}/{n_dis} and the trivial layer does "
            "not change the picture enough to earn a state layer — Decision "
            "Gate F gets its number, and option B loses this justification")
    (HERE / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")

    print(f"native: {native}")
    print(f"thin  : {thin}")
    print(f"drop {drop:+.3f} (m {RULE_M}), missed {missed_rate:.3f} (u {RULE_U})"
          f"  verdict: {verdict['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
