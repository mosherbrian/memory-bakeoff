#!/usr/bin/env python3
"""Gate for QUEUE row S11-3 (pi-lcm NATIVE supersession on broader histories:
more distractor families, longer streams, the native arm only, old beside new).

plumb-fable, row S11-3G, 2026-09-18. Written FROM ROW S11-3's TEXT ALONE, while
`team/S10-PI-LCM-HIST/` held nothing. Read for this gate: the board row; of the
verified prior (team/S7-STATELAYER) only its gate, its key names and its
declared parameters. The interface below is declared by the gate, not fitted to
a document; every finding names what it wants.

This gate is an INSTRUMENT. It trusts no number in the artifact: it recounts
the native arm from the per-trial receipts with the S7-3 gate's own `_count`
(so old and new are counted by the same code), and takes each trial's kind and
family from the frozen trial list, never from the receipt that reports on it.

The trap this gate is built round: the row says a NULL is itself evidence. A
null is cheap to fake. A store that never supersedes scores 0 false
supersessions; a corpus no broader than the prior's repeats the prior's null;
an instrument that cannot read a supersession reports none. So the null counts
only when the corpus is broader as declared, real updates were superseded,
and two control arms show the instrument reads both ends.

Declared interface (ROOT = team/S10-PI-LCM-HIST)
  declaration.json  {declared_at (ISO), distractor_shape (names agentmemory),
                    trials_sha256, generator: {path (inside ROOT), sha256},
                    broader: {distractor_families: [name, ...],
                              stream_length_min: n}}
                    No key that names a layer.
  trials.jsonl      one trial per line: {trial_id, kind: "distractor" |
                    "update", family (distractors: a declared family),
                    stream: [{id, ...}, ...]}. stream = every write of the
                    trial in order, the original and the newer write included.
  receipts.jsonl    one receipt per line, IN RUN ORDER: {ts (ISO), arm,
                    trial_id, superseded (bool: the original was treated as
                    superseded at the end of the stream), declaration_sha256}.
                    Arms `never-supersede`, `always-supersede` (controls),
                    `pi-lcm-native`. No other arm.
  verdict.json      {verdict: "native-null" | "native-failure", finding,
                    feeds (names roadmap R-PF), changes_state_layer_answer
                    (bool), native: A, per_family: {family: {false_superseded,
                    distractor_trials}}, false_supersession_trials: [trial_id],
                    missed_update_trials: [trial_id],
                    prior: {source (names S7-STATELAYER/verdict.json),
                            native: the prior's four pi-lcm-native counts}}
                    A = {false_superseded, distractor_trials, missed_updates,
                         update_trials, false_supersession_rate}

What the row turns on (marker in brackets)
  (a) BROADER, AS DECLARED. At least two distractor families are declared
      [FAMILIES-NOT-BROADER]; every distractor carries a declared family
      [FAMILY-UNDECLARED]; every declared family holds at least 8 distractors
      [FAMILY-THIN], so a family is not a label on one trial. Streams are
      longer than the prior's two writes: stream_length_min >= 3 and every
      trial's stream reaches it [STREAM-NOT-LONGER]. There are more distractor
      trials than the prior's and no fewer updates [NOT-BROADER]. The shape is
      the documented agentmemory one [SHAPE-NOT-DECLARED].
  (b) DECLARED BEFORE THE RUN, UNFITTED. declared_at precedes every receipt
      [DECLARED-AFTER-RECEIPTS]; each receipt embeds the sha256 of the
      declaration bytes [RECEIPTS-NOT-BOUND]; the declaration pins the trial
      list [TRIALS-NOT-FROZEN] and the generator that made it mechanically
      [GENERATOR-MISSING] [GENERATOR-NOT-FROZEN], so no awkward trial was
      dropped or relabelled once numbers were seen.
  (c) NATIVE ARM ONLY, NO LAYER CODE. No arm beside the two controls and
      `pi-lcm-native` [LAYER-ARM-PRESENT]; no layer key in the declaration, no
      code file named for a layer and none that imports one inside ROOT
      [LAYER-CODE-PRESENT]. The answer page wants native-failure evidence
      BEFORE any layer talk.
  (d) MEASURED, ON AN INSTRUMENT THAT SEPARATES. Every arm has one receipt per
      trial [ARM-MISSING] [ARM-INCOMPLETE]; the controls ran first
      [CONTROLS-NOT-FIRST] and did what their names say [CONTROL-ARM-WRONG].
  (e) ANY NATIVE FAILURE IS REPORTED. verdict.json holds the native counts and
      the per-family counts as recounted [NUMBERS-DISAGREE]; names exactly the
      trials falsely superseded and the updates missed [FAILURES-NOT-REPORTED];
      says native-failure if and only if there is one
      [VERDICT-CONTRADICTS-RECEIPTS]; and says the state-layer answer changes
      if and only if there is one [ANSWER-IMPACT-WRONG]. `native-null` is a
      PASS: the Gate F record asked for the evidence, not for a failure.
  (f) OLD BESIDE NEW. verdict.json prior names the prior's verdict.json
      [PRIOR-NOT-CITED] and quotes its pi-lcm-native counts exactly
      [PRIOR-MISQUOTED]. It gives a finding [VERDICT-NO-FINDING] and names the
      decision it feeds [GATE-F-NOT-NAMED].
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [VERDICT-INVALID]
         [PRIOR-UNREADABLE] [S7-GATE-UNREADABLE]

Limits, stated on purpose: `superseded` and the timestamps are self-reported,
and a hash chain can be rebuilt by someone who sets out to. The gate does not
run the generator, so it cannot tell that trials.jsonl is its output, that the
families truly differ in shape, that the arm named pi-lcm-native drove the real
pinned store, or that the run was local and $0. A null here is a null on THIS
declared corpus. Those stay with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S11-3 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--prior DIR] [--s7-gate FILE]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "S7-STATELAYER"
FILES = ("declaration.json", "trials.jsonl", "receipts.jsonl", "verdict.json")
NEVER, ALWAYS, NATIVE = "never-supersede", "always-supersede", "pi-lcm-native"
ARMS = (NEVER, ALWAYS, NATIVE)
KINDS = ("distractor", "update")
VERDICTS = ("native-null", "native-failure")
COUNTS = ("false_superseded", "distractor_trials", "missed_updates",
          "update_trials")
PRIOR_STREAM = 2  # the prior's trials hold two writes: `original`, `newer`
MIN_FAMILIES, MIN_PER_FAMILY = 2, 8
CODE = (".py", ".js", ".ts", ".sh")
IMPORTS_LAYER = re.compile(r"^\s*(?:from|import)\s+\S*layer", re.I | re.M)


def _gate(path: Path):
    spec = importlib.util.spec_from_file_location("_s7_3_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fmt(a: dict) -> str:
    return (f"false supersession {a['false_superseded']}/"
            f"{a['distractor_trials']}, missed updates "
            f"{a['missed_updates']}/{a['update_trials']}")


def _schema(g, decl, trials, receipts, verdict) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    if not isinstance(decl, dict):
        return [("SCHEMA", "declaration.json must be an object")]
    if g._ts(decl.get("declared_at")) is None:
        f.append(("SCHEMA", "declaration.json needs declared_at (ISO time)"))
    if not isinstance(decl.get("trials_sha256"), str):
        f.append(("SCHEMA", "declaration.json needs trials_sha256"))
    if "agentmemory" not in str(decl.get("distractor_shape", "")).lower():
        f.append(("SHAPE-NOT-DECLARED", "declaration.json needs "
                  "distractor_shape, naming the documented agentmemory shape "
                  "the trial generation extends"))
    gen = decl.get("generator")
    if not (isinstance(gen, dict) and isinstance(gen.get("path"), str)
            and gen["path"].strip() and isinstance(gen.get("sha256"), str)):
        f.append(("SCHEMA", "declaration.json needs generator: {path, sha256}"))
    b = decl.get("broader")
    if not (isinstance(b, dict) and isinstance(b.get("distractor_families"), list)
            and all(isinstance(x, str) and x.strip()
                    for x in b["distractor_families"])
            and g._int(b.get("stream_length_min"))):
        f.append(("SCHEMA", "declaration.json needs broader: "
                  "{distractor_families: [name, ...], stream_length_min: n}"))

    ok = isinstance(trials, list) and trials and all(
        isinstance(t, dict) and isinstance(t.get("trial_id"), str)
        and t.get("kind") in KINDS and isinstance(t.get("stream"), list)
        and all(isinstance(w, dict) and isinstance(w.get("id"), str)
                for w in t["stream"])
        and len({w["id"] for w in t["stream"]}) == len(t["stream"])
        and (t["kind"] == "update" or isinstance(t.get("family"), str))
        for t in trials)
    if not ok or len({t["trial_id"] for t in trials}) != len(trials):
        f.append(("SCHEMA", "trials.jsonl needs one {trial_id, kind: distractor "
                  "| update, family (on distractors), stream: [{id, ...}]} per "
                  "line; trial_id unique, write ids unique in a stream"))

    if not isinstance(receipts, list) or not receipts:
        f.append(("SCHEMA", "receipts.jsonl has no rows"))
    else:
        for i, r in enumerate(receipts, 1):
            if not (isinstance(r, dict) and g._ts(r.get("ts"))
                    and isinstance(r.get("arm"), str)
                    and isinstance(r.get("trial_id"), str)
                    and isinstance(r.get("superseded"), bool)
                    and isinstance(r.get("declaration_sha256"), str)):
                f.append(("SCHEMA", f"receipts.jsonl row {i} needs ts, arm, "
                          "trial_id, superseded (true or false), "
                          "declaration_sha256"))
                break

    if not isinstance(verdict, dict):
        return f + [("SCHEMA", "verdict.json must be an object")]
    if verdict.get("verdict") not in VERDICTS:
        f.append(("VERDICT-INVALID", f"verdict.json verdict must be one of "
                  f"{' / '.join(VERDICTS)}"))
    if not isinstance(verdict.get("finding"), str) \
            or len(verdict["finding"].strip()) < 20:
        f.append(("VERDICT-NO-FINDING", "verdict.json needs finding: one "
                  "sentence the Gate F record can hold"))
    if "R-PF" not in str(verdict.get("feeds", "")):
        f.append(("GATE-F-NOT-NAMED", "verdict.json needs feeds, naming roadmap "
                  "R-PF (the Gate F evidence base)"))
    nat, fam = verdict.get("native"), verdict.get("per_family")
    if not (isinstance(nat, dict) and all(g._int(nat.get(k)) for k in COUNTS)
            and g._num(nat.get("false_supersession_rate"))):
        f.append(("SCHEMA", f"verdict.json needs native: {{{', '.join(COUNTS)}, "
                  f"false_supersession_rate}}"))
    if not (isinstance(fam, dict) and all(isinstance(c, dict)
                                          for c in fam.values())):
        f.append(("SCHEMA", "verdict.json needs per_family: {family: "
                  "{false_superseded, distractor_trials}}"))
    for k in ("false_supersession_trials", "missed_update_trials"):
        if not isinstance(verdict.get(k), list):
            f.append(("SCHEMA", f"verdict.json needs {k}: [trial_id, ...] "
                      f"(an empty list when there are none)"))
    if not isinstance(verdict.get("changes_state_layer_answer"), bool):
        f.append(("SCHEMA", "verdict.json needs changes_state_layer_answer "
                  "(true or false)"))
    if not isinstance(verdict.get("prior"), dict):
        f.append(("SCHEMA", "verdict.json needs prior: {source, native}"))
    return f


def _layer_code(root: Path, decl: dict) -> list[str]:
    hits = [f"declaration.json key `{k}`" for k in decl if "layer" in k.lower()]
    for p in sorted(root.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts \
                or p.suffix not in CODE or p.resolve() == Path(__file__).resolve():
            continue
        if "layer" in p.name.lower():
            hits.append(p.name)
        elif IMPORTS_LAYER.search(p.read_text(encoding="utf-8", errors="replace")):
            hits.append(f"{p.name} imports a layer")
    return hits


def check(root: Path, prior: Path, s7_gate: Path) -> tuple[list, str]:
    try:
        g = _gate(s7_gate)
        g._count, g._load, g._sha, g._ts, g._int, g._num
    except Exception as e:
        return [("S7-GATE-UNREADABLE", f"{s7_gate}: {type(e).__name__}: {e}")], ""
    try:
        old = g._load(prior / "verdict.json")["arms"][NATIVE]
        old = {k: old[k] for k in COUNTS}
        if not all(g._int(v) for v in old.values()):
            raise ValueError("the prior's native counts are not integers")
    except Exception as e:
        return [("PRIOR-UNREADABLE", f"{prior}: {type(e).__name__}: {e}")], ""

    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        decl = g._load(root / "declaration.json")
        trials = g._load(root / "trials.jsonl", lines=True)
        receipts = g._load(root / "receipts.jsonl", lines=True)
        verdict = g._load(root / "verdict.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f = _schema(g, decl, trials, receipts, verdict)
    if f:
        return f, ""

    # (b) declared before the run, unfitted
    sha = g._sha(root / "declaration.json")
    unbound = sum(1 for r in receipts if r["declaration_sha256"] != sha)
    if unbound:
        f.append(("RECEIPTS-NOT-BOUND", f"{unbound} of {len(receipts)} receipts "
                  f"do not carry the sha256 of declaration.json as it stands "
                  f"({sha[:12]}): the declaration changed after the run, or "
                  f"the run never read it"))
    first = min(g._ts(r["ts"]) for r in receipts)
    if g._ts(decl["declared_at"]) >= first:
        f.append(("DECLARED-AFTER-RECEIPTS", f"declared_at {decl['declared_at']}"
                  f" is not before the first receipt {first.isoformat()}"))
    if decl["trials_sha256"] != g._sha(root / "trials.jsonl"):
        f.append(("TRIALS-NOT-FROZEN", "trials_sha256 is not the sha256 of "
                  "trials.jsonl: the trial list changed after it was declared"))
    gen = (root / decl["generator"]["path"]).resolve()
    if not gen.is_file() or root.resolve() not in gen.parents:
        f.append(("GENERATOR-MISSING", f"generator.path "
                  f"{decl['generator']['path']!r} must be a file inside "
                  f"{root.name}/: the row extends the trial generation "
                  f"MECHANICALLY"))
    elif g._sha(gen) != decl["generator"]["sha256"]:
        f.append(("GENERATOR-NOT-FROZEN", "generator.sha256 is not the sha256 of "
                  "the generator source: it changed after it was declared"))

    # (a) broader, as declared
    kind = {t["trial_id"]: t["kind"] for t in trials}
    n = Counter(kind.values())
    families = decl["broader"]["distractor_families"]
    if len(set(families)) < MIN_FAMILIES:
        f.append(("FAMILIES-NOT-BROADER", f"broader.distractor_families names "
                  f"{len(set(families))}; the prior had one shape, and the row "
                  f"wants MORE distractor families (at least {MIN_FAMILIES})"))
    per = Counter(t["family"] for t in trials if t["kind"] == "distractor")
    stray = sorted(set(per) - set(families))
    if stray:
        f.append(("FAMILY-UNDECLARED", f"distractor trials carry families not "
                  f"declared before the run: {', '.join(stray[:5])}"))
    thin = [x for x in families if per[x] < MIN_PER_FAMILY]
    if thin:
        f.append(("FAMILY-THIN", f"each declared family needs at least "
                  f"{MIN_PER_FAMILY} distractor trials; short: "
                  + ", ".join(f"{x} ({per[x]})" for x in thin)))
    smin = decl["broader"]["stream_length_min"]
    short = [t["trial_id"] for t in trials if len(t["stream"]) < max(
        smin, PRIOR_STREAM + 1)]
    if smin <= PRIOR_STREAM or short:
        f.append(("STREAM-NOT-LONGER", f"the prior's streams hold "
                  f"{PRIOR_STREAM} writes; stream_length_min must be at least "
                  f"{PRIOR_STREAM + 1} (declared {smin}) and every trial's "
                  f"stream must reach it ({len(short)} do not"
                  f"{': ' + ', '.join(short[:5]) if short else ''})"))
    if n["distractor"] <= old["distractor_trials"] \
            or n["update"] < old["update_trials"] or not n["update"]:
        f.append(("NOT-BROADER", f"trials.jsonl has {n['distractor']} distractor "
                  f"and {n['update']} update trials; broader than the prior "
                  f"means more than {old['distractor_trials']} distractors and "
                  f"at least {max(old['update_trials'], 1)} updates. Without "
                  f"real updates a store that never supersedes scores a null"))

    # (c) native arm only, no layer code
    extra = sorted({r["arm"] for r in receipts} - set(ARMS))
    if extra:
        f.append(("LAYER-ARM-PRESENT", f"receipts.jsonl holds arms beside the "
                  f"controls and `{NATIVE}`: {', '.join(extra[:5])}. The row "
                  f"runs the NATIVE arm only"))
    layer = _layer_code(root, decl)
    if layer:
        f.append(("LAYER-CODE-PRESENT", f"no layer code in this row: "
                  f"{'; '.join(layer[:5])}"))

    # (d) measured, on an instrument shown to separate
    sup: dict[str, dict] = {}
    for arm in ARMS:
        mine = [r for r in receipts if r["arm"] == arm]
        if not mine:
            f.append(("ARM-MISSING", f"receipts.jsonl has no `{arm}` receipts"))
            continue
        seen = Counter(r["trial_id"] for r in mine)
        if set(seen) != set(kind) or max(seen.values()) > 1:
            f.append(("ARM-INCOMPLETE", f"`{arm}` must hold each of the "
                      f"{len(kind)} trials exactly once"))
            continue
        sup[arm] = {r["trial_id"]: r["superseded"] for r in mine}
    if len(sup) < len(ARMS) or not n["update"] or not n["distractor"]:
        return f, ""
    if any(sup[NEVER].values()) or not all(sup[ALWAYS].values()):
        f.append(("CONTROL-ARM-WRONG", f"`{NEVER}` must supersede on no trial "
                  f"and `{ALWAYS}` on every trial: they show the instrument "
                  f"can read both ends, which is what makes a null evidence"))
    order = [r["arm"] for r in receipts]
    if max(i for i, a in enumerate(order) if a in (NEVER, ALWAYS)) \
            > order.index(NATIVE):
        f.append(("CONTROLS-NOT-FIRST", f"every control receipt must come "
                  f"before the first `{NATIVE}` receipt"))

    # (e) any native failure is reported
    real = g._count(kind, sup[NATIVE])
    false = sorted(t["trial_id"] for t in trials
                   if t["kind"] == "distractor" and sup[NATIVE][t["trial_id"]])
    missed = sorted(t for t, k in kind.items()
                    if k == "update" and not sup[NATIVE][t])
    fam_real = {x: {"false_superseded": sum(
        1 for t in trials if t.get("family") == x and t["trial_id"] in false),
        "distractor_trials": per[x]} for x in families}
    said = verdict["native"]
    fam_said = {x: {k: c.get(k) for k in ("false_superseded",
                                          "distractor_trials")}
                for x, c in verdict["per_family"].items()}
    if any(said[k] != real[k] for k in COUNTS) or abs(
            said["false_supersession_rate"]
            - real["false_supersession_rate"]) >= 0.0006 or fam_said != fam_real:
        f.append(("NUMBERS-DISAGREE", f"verdict.json native / per_family do not "
                  f"match the receipts as recounted: {_fmt(real)}; per family "
                  f"{ {x: (c['false_superseded'], c['distractor_trials']) for x, c in fam_real.items()} }"))
    if sorted(map(str, verdict["false_supersession_trials"])) != false \
            or sorted(map(str, verdict["missed_update_trials"])) != missed:
        f.append(("FAILURES-NOT-REPORTED", f"verdict.json must name exactly the "
                  f"trials the native arm got wrong: false_supersession_trials "
                  f"{false[:5]}{'...' if len(false) > 5 else ''} "
                  f"({len(false)}), missed_update_trials {missed[:5]}"
                  f"{'...' if len(missed) > 5 else ''} ({len(missed)})"))
    failed = bool(false or missed)
    rightful = VERDICTS[1] if failed else VERDICTS[0]
    if verdict["verdict"] != rightful:
        f.append(("VERDICT-CONTRADICTS-RECEIPTS", f"recounted: {_fmt(real)}; "
                  f"the verdict must be {rightful}"))
    if verdict["changes_state_layer_answer"] != failed:
        f.append(("ANSWER-IMPACT-WRONG", f"changes_state_layer_answer must be "
                  f"{str(failed).lower()}: a native failure changes the "
                  f"state-layer answer, a null does not"))

    # (f) old beside new
    p = verdict["prior"]
    if f"{prior.name}/verdict.json" not in str(p.get("source", "")):
        f.append(("PRIOR-NOT-CITED", f"verdict.json prior.source must name "
                  f"{prior.name}/verdict.json"))
    quoted = p.get("native") if isinstance(p.get("native"), dict) else {}
    if {k: quoted.get(k) for k in COUNTS} != old:
        f.append(("PRIOR-MISQUOTED", f"verdict.json prior.native must quote the "
                  f"prior's {NATIVE} counts exactly: {old}"))
    return f, (f"{rightful}; {NATIVE} {_fmt(real)} on {len(set(families))} "
               f"families, streams of at least {smin}; prior {_fmt(old)}")


def run(root: Path, prior: Path, s7_gate: Path) -> int:
    findings, summary = check(root, prior, s7_gate)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S11-3 gate findings: {len(findings)}")
        return 1
    print(f"S11-3 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_T0 = datetime(2026, 9, 19, 17, 0, tzinfo=timezone.utc)
_FAMS = ("same-template-other-scope", "near-duplicate-value", "renamed-entity")
_D = [f"d{i:02d}" for i in range(36)]  # 12 per family, in family order
_U = [f"u{i:02d}" for i in range(12)]
_OLD = {"false_superseded": 0, "distractor_trials": 32, "missed_updates": 0,
        "update_trials": 12}
_GEN = "# extends the S7-3 generation mechanically\nFAMILIES = 3\nSTREAM = 4\n"


def _trial(tid: str, kind: str, fam: str | None, n: int = 4) -> dict:
    t = {"trial_id": tid, "kind": kind,
         "stream": [{"id": f"{tid}-w{j}", "text": f"write {j}"} for j in range(n)]}
    if fam:
        t["family"] = fam
    return t


def _fixture(fails: bool = False) -> dict:
    """The null: no distractor superseded, all 12 updates superseded. The
    failure: 2 of family two falsely superseded and 1 update missed."""
    false, missed = (_D[12:14], _U[:1]) if fails else ([], [])
    return {
        "decl": {"declared_at": _T0.isoformat(),
                 "distractor_shape": "the documented agentmemory 92.9% shape, "
                                     "extended mechanically",
                 "trials_sha256": "AUTO",
                 "generator": {"path": "gen_trials.py", "sha256": "AUTO"},
                 "broader": {"distractor_families": list(_FAMS),
                             "stream_length_min": 4}},
        "trials": [_trial(t, "distractor", _FAMS[i // 12])
                   for i, t in enumerate(_D)]
        + [_trial(t, "update", None) for t in _U],
        # arm -> the trials on which the original was treated as superseded
        "sup": {NEVER: set(), ALWAYS: set(_D + _U),
                NATIVE: set(false) | (set(_U) - set(missed)),
                "thin-layer": set(_U)},
        "order": list(ARMS), "files": {"gen_trials.py": _GEN}, "raw": {},
        "after_run": None, "prior_native": dict(_OLD),
        "verdict": {
            "verdict": VERDICTS[1 if fails else 0],
            "finding": "the native store falsely supersedes in one broader "
                       "family and misses an update." if fails else
                       "no native false supersession and no missed update on "
                       "the declared broader corpus.",
            "feeds": "roadmap R-PF, the Gate F evidence base",
            "changes_state_layer_answer": fails,
            "native": dict(false_superseded=len(false), distractor_trials=36,
                           missed_updates=len(missed), update_trials=12,
                           false_supersession_rate=len(false) / 36),
            "per_family": {x: {"false_superseded": len(false) if i == 1 else 0,
                               "distractor_trials": 12}
                           for i, x in enumerate(_FAMS)},
            "false_supersession_trials": list(false),
            "missed_update_trials": list(missed),
            "prior": {"source": "team/S7-STATELAYER/verdict.json",
                      "native": dict(_OLD)}},
    }


def _write(td: Path, fx: dict) -> tuple[Path, Path]:
    prior = td / "team" / "S7-STATELAYER"
    root = td / "team" / "S10-PI-LCM-HIST"
    prior.mkdir(parents=True)
    root.mkdir()
    (prior / "verdict.json").write_text(json.dumps(
        {"arms": {NATIVE: dict(fx["prior_native"], false_supersession_rate=0.0)}}))
    for name, text in fx["files"].items():
        (root / name).write_text(text)
    (root / "trials.jsonl").write_text(
        "".join(json.dumps(t) + "\n" for t in fx["trials"]))
    decl = fx["decl"]
    if decl.get("trials_sha256") == "AUTO":
        decl["trials_sha256"] = _sha(root / "trials.jsonl")
    if isinstance(decl.get("generator"), dict) \
            and decl["generator"].get("sha256") == "AUTO":
        decl["generator"]["sha256"] = _sha(root / "gen_trials.py")
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    sha = _sha(root / "declaration.json")
    out, i = [], 0
    for arm in fx["order"]:
        for t in fx["trials"]:
            i += 1
            out.append(json.dumps({
                "ts": (_T0 + timedelta(seconds=i)).isoformat(), "arm": arm,
                "trial_id": t["trial_id"],
                "superseded": t["trial_id"] in fx["sup"][arm],
                "declaration_sha256": sha}) + "\n")
    if fx.get("drop_last"):
        out = out[:-1]
    (root / "receipts.jsonl").write_text("".join(out))
    (root / "verdict.json").write_text(json.dumps(fx["verdict"]))
    if fx["after_run"]:
        fx["after_run"](root, decl)
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, prior


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _after_decl(root, decl):  # the declared breadth edited once numbers were seen
    decl["broader"]["stream_length_min"] = 3
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))


def _after_trials(root, decl):  # an awkward stream rewritten after the run
    p = root / "trials.jsonl"
    p.write_text(p.read_text().replace("write 3", "write three", 1))


def _after_gen(root, decl):  # the generator tuned after the run
    (root / "gen_trials.py").write_text(_GEN + "SKIP = ['d13']\n")


def _refit(fx, per: dict, false: int = 0):
    """Keep verdict.json honest about a reshaped trial list, so only the
    breadth check can object."""
    d = sum(per.values())
    fx["verdict"]["native"].update(distractor_trials=d,
                                   false_supersession_rate=false / d)
    fx["verdict"]["per_family"] = {x: {"false_superseded": 0,
                                       "distractor_trials": c}
                                   for x, c in per.items()}


def _m_late(fx): fx["decl"]["declared_at"] = (_T0 + timedelta(hours=1)).isoformat()
def _m_decl_moved(fx): fx["after_run"] = _after_decl
def _m_trials_moved(fx): fx["after_run"] = _after_trials
def _m_gen_tuned(fx): fx["after_run"] = _after_gen
def _m_gen_gone(fx): fx["decl"]["generator"]["path"] = "../../src/gen.py"
def _m_noshape(fx): fx["decl"]["distractor_shape"] = "hard cases"
def _m_two_writes(fx): fx["decl"]["broader"]["stream_length_min"] = 2
def _m_layer_arm(fx): fx["order"] = [*ARMS, "thin-layer"]
def _m_layer_file(fx): fx["files"]["thin_layer.py"] = "def write(s, k, v): pass\n"
def _m_layer_import(fx): fx["files"]["run.py"] = "import json\nfrom state_layer import mark\n"
def _m_layer_key(fx): fx["decl"]["thin_layer"] = {"path": "x.py", "sha256": "0"}
def _m_nocontrols(fx): fx["order"] = [NATIVE]
def _m_nonative(fx): fx["order"] = [NEVER, ALWAYS]
def _m_order(fx): fx["order"] = [NATIVE, NEVER, ALWAYS]
def _m_control(fx): fx["sup"][ALWAYS] = set(_D)
def _m_short(fx): fx["drop_last"] = True
def _m_numbers(fx): fx["verdict"]["native"]["update_trials"] = 14
def _m_family_numbers(fx): fx["verdict"]["per_family"][_FAMS[0]]["distractor_trials"] = 13
def _m_maybe(fx): fx["verdict"]["verdict"] = "mostly-null"
def _m_nofinding(fx): fx["verdict"]["finding"] = "ok"
def _m_nofeeds(fx): del fx["verdict"]["feeds"]
def _m_uncited(fx): fx["verdict"]["prior"]["source"] = "sprint 7"
def _m_misquoted(fx): fx["verdict"]["prior"]["native"]["distractor_trials"] = 36
def _m_noprior(fx): del fx["verdict"]["prior"]
def _m_badjson(fx): fx["raw"]["verdict.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["receipts.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["trials.jsonl"] = None
def _m_null_impact(fx): fx["verdict"]["changes_state_layer_answer"] = True


def _m_one_family(fx):
    for t in fx["trials"]:
        if t["kind"] == "distractor":
            t["family"] = _FAMS[0]
    fx["decl"]["broader"]["distractor_families"] = [_FAMS[0]]
    _refit(fx, {_FAMS[0]: 36})


def _m_family_label(fx):  # three families declared, the third a label on 2 trials
    for t in fx["trials"][26:36]:
        t["family"] = _FAMS[0]
    _refit(fx, {_FAMS[0]: 22, _FAMS[1]: 12, _FAMS[2]: 2})


def _m_family_stray(fx):
    fx["trials"][0]["family"] = "found-while-running"
    _refit(fx, {_FAMS[0]: 11, _FAMS[1]: 12, _FAMS[2]: 12})
    fx["verdict"]["native"].update(distractor_trials=36)


def _m_one_short_stream(fx): fx["trials"][5] = _trial("d05", "distractor", _FAMS[0], 2)


def _m_prior_size(fx):  # 30 distractors: not more than the prior's 32
    fx["trials"] = [t for t in fx["trials"] if t["trial_id"] not in
                    {"d10", "d11", "d22", "d23", "d34", "d35"}]
    _refit(fx, {x: 10 for x in _FAMS})


def _m_no_updates(fx):  # the trap: a null with nothing that should supersede
    fx["trials"] = fx["trials"][:36]


def _m_never_native(fx):  # the trap: a store that never supersedes claims a null
    fx["sup"][NATIVE] = set()


def _m_hidden(fx):  # failure data, a null written over it
    fx.update(copy.deepcopy(_fixture(fails=True)), verdict=fx["verdict"])


def _m_unnamed(fx):  # failure counted, the failing trials not named
    fx.update(copy.deepcopy(_fixture(fails=True)))
    fx["verdict"]["false_supersession_trials"] = []


def _m_fail_called_null(fx):
    fx.update(copy.deepcopy(_fixture(fails=True)))
    fx["verdict"]["verdict"] = VERDICTS[0]


def _m_fail_no_impact(fx):
    fx.update(copy.deepcopy(_fixture(fails=True)))
    fx["verdict"]["changes_state_layer_answer"] = False


def _m_receipts(fx):  # every file exists and says nothing
    fx["raw"] = {n: "{}\n" for n in FILES}


_HIDDEN = {"NUMBERS-DISAGREE", "FAILURES-NOT-REPORTED",
           "VERDICT-CONTRADICTS-RECEIPTS", "ANSWER-IMPACT-WRONG"}
# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "declared after the run": (_m_late, {"DECLARED-AFTER-RECEIPTS"}),
    "declaration edited after the run": (_m_decl_moved, {"RECEIPTS-NOT-BOUND"}),
    "a stream rewritten after the run": (_m_trials_moved, {"TRIALS-NOT-FROZEN"}),
    "generator tuned after the run": (_m_gen_tuned, {"GENERATOR-NOT-FROZEN"}),
    "generator outside the directory": (_m_gen_gone, {"GENERATOR-MISSING"}),
    "shape not named": (_m_noshape, {"SHAPE-NOT-DECLARED"}),
    "one distractor family, as the prior": (_m_one_family,
                                            {"FAMILIES-NOT-BROADER"}),
    "a family that is a label on two trials": (_m_family_label, {"FAMILY-THIN"}),
    "a family found while running": (_m_family_stray, {"FAMILY-UNDECLARED"}),
    "streams of two writes, as the prior": (_m_two_writes, {"STREAM-NOT-LONGER"}),
    "one stream shorter than declared": (_m_one_short_stream,
                                         {"STREAM-NOT-LONGER"}),
    "no more distractors than the prior": (_m_prior_size, {"NOT-BROADER"}),
    "no update trials": (_m_no_updates, {"NOT-BROADER"}),
    "a layer arm was run": (_m_layer_arm, {"LAYER-ARM-PRESENT"}),
    "a layer file in the directory": (_m_layer_file, {"LAYER-CODE-PRESENT"}),
    "the runner imports a layer": (_m_layer_import, {"LAYER-CODE-PRESENT"}),
    "a layer pinned in the declaration": (_m_layer_key, {"LAYER-CODE-PRESENT"}),
    "no control arms": (_m_nocontrols, {"ARM-MISSING"}),
    "native arm missing": (_m_nonative, {"ARM-MISSING"}),
    "a receipt dropped": (_m_short, {"ARM-INCOMPLETE"}),
    "controls after the native arm": (_m_order, {"CONTROLS-NOT-FIRST"}),
    "control arm wrong": (_m_control, {"CONTROL-ARM-WRONG"}),
    "counts wrong": (_m_numbers, {"NUMBERS-DISAGREE"}),
    "family counts wrong": (_m_family_numbers, {"NUMBERS-DISAGREE"}),
    "never-superseding store claims a null": (_m_never_native, _HIDDEN),
    "a null written over failure data": (_m_hidden, _HIDDEN),
    "failing trials not named": (_m_unnamed, {"FAILURES-NOT-REPORTED"}),
    "a failure called a null": (_m_fail_called_null,
                                {"VERDICT-CONTRADICTS-RECEIPTS"}),
    "a failure that changes nothing": (_m_fail_no_impact,
                                       {"ANSWER-IMPACT-WRONG"}),
    "a null that changes the answer": (_m_null_impact, {"ANSWER-IMPACT-WRONG"}),
    "verdict not in vocabulary": (_m_maybe, {"VERDICT-INVALID"}),
    "verdict without finding": (_m_nofinding, {"VERDICT-NO-FINDING"}),
    "decision not named": (_m_nofeeds, {"GATE-F-NOT-NAMED"}),
    "prior not named": (_m_uncited, {"PRIOR-NOT-CITED"}),
    "prior misquoted": (_m_misquoted, {"PRIOR-MISQUOTED"}),
    "no old beside new": (_m_noprior, {"SCHEMA"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile receipts": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest(s7_gate: Path) -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want, gate=s7_gate, prior=None):
        with tempfile.TemporaryDirectory() as td:
            root, p_root = _write(Path(td), fx)
            r = subprocess.run([sys.executable, __file__, str(root), "--prior",
                                str(prior or p_root), "--s7-gate", str(gate)],
                               capture_output=True, text=True, timeout=60)
        text = r.stdout + r.stderr
        got = set(marker.findall(text))
        if "Traceback (most recent call last)" in text:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got
                               or "gate findings" in text):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not want(got)
                                   or "S11-3 gate findings: " not in text):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming, a null", _fixture(False), None)
    case("conforming, an honest native failure", _fixture(True), None)
    hollow = _fixture()
    _m_receipts(hollow)
    case("all files present, no substance", hollow,
         lambda got: len(got) >= 3 and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, lambda got, want=want: got == want)
    case("S7-3 gate missing", _fixture(), lambda got: got == {"S7-GATE-UNREADABLE"},
         gate=Path("/nonexistent/check.py"))
    case("prior missing", _fixture(), lambda got: got == {"PRIOR-UNREADABLE"},
         prior=Path("/nonexistent/S7-STATELAYER"))

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (2 conforming fixtures accepted, one a null and one "
          f"an honest native failure; a files-only directory, a missing S7-3 "
          f"gate, a missing prior and {len(_MUTANTS)} mutants each rejected by "
          f"exactly their own markers - a never-superseding store claiming a "
          f"null, a corpus no broader than the prior's and a layer arm among "
          f"them; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S11-3")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--prior", default=str(PRIOR))
    ap.add_argument("--s7-gate", default=str(PRIOR / "check.py"))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest(Path(a.s7_gate))
    return run(Path(a.root), Path(a.prior), Path(a.s7_gate))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S11-3 gate findings: 1")
        raise SystemExit(1)
