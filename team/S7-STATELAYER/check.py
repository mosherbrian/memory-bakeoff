#!/usr/bin/env python3
"""Gate for QUEUE row S7-3 (false supersession: pi-lcm native store against a
trivial mark-superseded-on-newer-write layer, under stress distractors).

plumb-fable, row S7-3G, 2026-09-17. Written FROM ROW S7-3's TEXT ALONE, while
`team/S7-STATELAYER/` did not exist, and without opening the stress machinery
the row says to reuse. The interface below is declared by the gate, not fitted
to a document; every finding names what it wants.

This gate is an INSTRUMENT. It trusts no number in the artifact: it recounts
every rate from the per-trial receipts, and takes each trial's kind from the
frozen trial list, never from the receipt that reports on it.

The trap this gate is built round: a layer that NEVER supersedes scores a
perfect 0% false supersession. So the trial list must also hold real updates,
two control arms must show the instrument separates, and the verdict rule must
charge the layer for the updates it misses.

Declared interface (ROOT = team/S7-STATELAYER, REPO = the repository root)
  declaration.json  {declared_at (ISO), distractor_shape (names agentmemory),
                    trials_sha256, thin_layer: {path (inside ROOT), sha256},
                    rule: {layer_helps_if_rate_drop_at_least: m, 0 < m <= 1,
                           layer_max_missed_update_rate: u, 0 <= u < 1}}
  trials.jsonl      one trial per line: {trial_id, kind: "distractor" |
                    "update"}. distractor = a newer write that must NOT
                    supersede the original; update = one that must.
  receipts.jsonl    one receipt per line, IN RUN ORDER: {ts (ISO), arm,
                    trial_id, superseded (bool: the original was treated as
                    superseded after the newer write), declaration_sha256}.
                    Arms `never-supersede`, `always-supersede` (controls),
                    `pi-lcm-native`, `thin-layer`.
  verdict.json      {verdict: "layer-helps" | "layer-does-not-help", finding,
                    feeds (names roadmap R-PF, Decision Gate F),
                    prior_pi_lcm (states that none exists),
                    comparison: {system: "agentmemory", false_superseded: 418,
                                 trials: 450, source (a file under REPO)},
                    arms: {"pi-lcm-native": A, "thin-layer": A}}
                    A = {false_superseded, distractor_trials, missed_updates,
                         update_trials, false_supersession_rate}

What the row turns on (marker in brackets)
  (a) Measured, with receipts. Every arm has one receipt per trial
      [ARM-MISSING] [ARM-INCOMPLETE]; the list holds at least 30 distractor
      and 10 update trials [TOO-FEW-TRIALS] [NO-UPDATE-TRIALS], so a rate set
      beside 418/450 is not made of five trials and a never-supersede layer
      cannot hide. The controls ran first [CONTROLS-NOT-FIRST] and did what
      their names say [CONTROL-ARM-WRONG].
  (b) Declared before the run. declared_at precedes every receipt
      [DECLARED-AFTER-RECEIPTS]; each receipt embeds the sha256 of the
      declaration bytes [RECEIPTS-NOT-BOUND]; the declaration pins the trial
      list [TRIALS-NOT-FROZEN] and the layer source [LAYER-NOT-FROZEN], so
      neither moved once numbers were seen; the distractor shape is named
      [SHAPE-NOT-DECLARED]; the verdict rule is fixed [RULE-UNDECLARED].
  (c) The layer is TRIVIAL. The roadmap bans building a state layer before
      its deciding property is measured, so the thin layer is a probe: its
      source is inside ROOT [LAYER-MISSING] and has at most 80 code lines
      [LAYER-NOT-TRIVIAL].
  (d) One number, honestly placed. verdict.json reports both arms as recounted
      [NUMBERS-DISAGREE]; holds the verdict the rule gives: layer-helps if and
      only if the false-supersession rate drops by at least m AND the layer
      misses at most u of the real updates [VERDICT-CONTRADICTS-RULE]; gives a
      finding [VERDICT-NO-FINDING]; names the decision it feeds
      [GATE-F-NOT-NAMED]; states that no prior pi-lcm measurement exists
      [PRIOR-NOT-STATED]; and quotes the protected comparison point exactly,
      agentmemory 418/450 [PROTECTED-POINT-ALTERED], from a file that exists
      [PROTECTED-POINT-UNSOURCED]. `layer-does-not-help` is a PASS: Gate F
      asked for the number, not for a win.
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [VERDICT-INVALID]

Limits, stated on purpose: `superseded` and the timestamps are self-reported,
and a hash chain can be rebuilt by someone who sets out to. The gate cannot
tell that the distractors truly have the agentmemory shape, that the arm named
pi-lcm-native drove the real pi-lcm store, or that the run was local and $0.
418/450 came from another harness: it is a comparison point, not a ranking.
Those stay with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S7-3 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--repo DIR]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("declaration.json", "trials.jsonl", "receipts.jsonl", "verdict.json")
NEVER, ALWAYS = "never-supersede", "always-supersede"
NATIVE, THIN = "pi-lcm-native", "thin-layer"
ARMS = (NEVER, ALWAYS, NATIVE, THIN)
KINDS = ("distractor", "update")
VERDICTS = ("layer-helps", "layer-does-not-help")
COUNTS = ("false_superseded", "distractor_trials", "missed_updates",
          "update_trials")
PROTECTED = {"system": "agentmemory", "false_superseded": 418, "trials": 450}
MIN_DISTRACTOR, MIN_UPDATE, MAX_LAYER_LINES = 30, 10, 80
NO_PRIOR = re.compile(r"none exists?|no prior|no previous|never (been )?measured"
                      r"|first measurement", re.I)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ts(v):
    if not isinstance(v, str):
        return None
    try:
        t = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _load(path: Path, lines: bool = False):
    text = path.read_text(encoding="utf-8", errors="replace")
    if lines:
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    return json.loads(text)


def _count(kind: dict, sup: dict) -> dict:
    """One arm, recounted. kind: trial -> kind. sup: trial -> superseded."""
    d = [t for t, k in kind.items() if k == "distractor"]
    u = [t for t, k in kind.items() if k == "update"]
    false = sum(1 for t in d if sup[t])
    return {"false_superseded": false, "distractor_trials": len(d),
            "missed_updates": sum(1 for t in u if not sup[t]),
            "update_trials": len(u), "false_supersession_rate": false / len(d)}


def _fmt(a: dict) -> str:
    return (f"false supersession {a['false_superseded']}/"
            f"{a['distractor_trials']} ({a['false_supersession_rate']:.3f}), "
            f"missed updates {a['missed_updates']}/{a['update_trials']}")


def _schema(decl, trials, receipts, verdict) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    if not isinstance(decl, dict):
        return [("SCHEMA", "declaration.json must be an object")]
    if _ts(decl.get("declared_at")) is None:
        f.append(("SCHEMA", "declaration.json needs declared_at (ISO time)"))
    if not isinstance(decl.get("trials_sha256"), str):
        f.append(("SCHEMA", "declaration.json needs trials_sha256"))
    if "agentmemory" not in str(decl.get("distractor_shape", "")).lower():
        f.append(("SHAPE-NOT-DECLARED", "declaration.json needs "
                  "distractor_shape, naming the agentmemory-class shape the "
                  "trials reuse"))
    layer = decl.get("thin_layer")
    if not (isinstance(layer, dict) and isinstance(layer.get("path"), str)
            and layer["path"].strip() and isinstance(layer.get("sha256"), str)):
        f.append(("SCHEMA", "declaration.json needs thin_layer: {path, sha256}"))
    rule = decl.get("rule") if isinstance(decl.get("rule"), dict) else {}
    m = rule.get("layer_helps_if_rate_drop_at_least")
    u = rule.get("layer_max_missed_update_rate")
    if not (_num(m) and 0 < m <= 1 and _num(u) and 0 <= u < 1):
        f.append(("RULE-UNDECLARED", "declaration.json needs rule: "
                  "{layer_helps_if_rate_drop_at_least: m, 0 < m <= 1, "
                  "layer_max_missed_update_rate: u, 0 <= u < 1}, fixed before "
                  "the run"))

    ok = isinstance(trials, list) and trials and all(
        isinstance(t, dict) and isinstance(t.get("trial_id"), str)
        and t.get("kind") in KINDS for t in trials)
    if not ok or len({t["trial_id"] for t in trials}) != len(trials):
        f.append(("SCHEMA", "trials.jsonl needs one {trial_id, kind: "
                  "distractor | update} per line, trial_id unique"))

    if not isinstance(receipts, list) or not receipts:
        f.append(("SCHEMA", "receipts.jsonl has no rows"))
    else:
        for i, r in enumerate(receipts, 1):
            if not (isinstance(r, dict) and _ts(r.get("ts"))
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
                  "sentence that Decision Gate F can act on"))
    if "R-PF" not in str(verdict.get("feeds", "")):
        f.append(("GATE-F-NOT-NAMED", "verdict.json needs feeds, naming roadmap "
                  "R-PF (Decision Gate F)"))
    if not NO_PRIOR.search(str(verdict.get("prior_pi_lcm", ""))):
        f.append(("PRIOR-NOT-STATED", "verdict.json needs prior_pi_lcm, stating "
                  "in words that no false-supersession measurement of pi-lcm "
                  "exists (`none exists`)"))
    arms = verdict.get("arms")
    if not (isinstance(arms, dict) and all(
            isinstance(arms.get(a), dict)
            and all(_int(arms[a].get(k)) for k in COUNTS)
            and _num(arms[a].get("false_supersession_rate"))
            for a in (NATIVE, THIN))):
        f.append(("SCHEMA", f"verdict.json needs arms: {{{NATIVE}, {THIN}}}, "
                  f"each {{{', '.join(COUNTS)}, false_supersession_rate}}"))
    if not isinstance(verdict.get("comparison"), dict):
        f.append(("SCHEMA", "verdict.json needs comparison: {system, "
                  "false_superseded, trials, source}"))
    return f


def check(root: Path, repo: Path) -> tuple[list[tuple[str, str]], str]:
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        decl = _load(root / "declaration.json")
        trials = _load(root / "trials.jsonl", lines=True)
        receipts = _load(root / "receipts.jsonl", lines=True)
        verdict = _load(root / "verdict.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f = _schema(decl, trials, receipts, verdict)
    if f:
        return f, ""

    # (b) declared before the run; trial list and layer frozen
    sha = _sha(root / "declaration.json")
    unbound = sum(1 for r in receipts if r["declaration_sha256"] != sha)
    if unbound:
        f.append(("RECEIPTS-NOT-BOUND", f"{unbound} of {len(receipts)} receipts "
                  f"do not carry the sha256 of declaration.json as it stands "
                  f"({sha[:12]}): the declaration changed after the run, or "
                  f"the run never read it"))
    first = min(_ts(r["ts"]) for r in receipts)
    if _ts(decl["declared_at"]) >= first:
        f.append(("DECLARED-AFTER-RECEIPTS", f"declared_at {decl['declared_at']}"
                  f" is not before the first receipt {first.isoformat()}"))
    if decl["trials_sha256"] != _sha(root / "trials.jsonl"):
        f.append(("TRIALS-NOT-FROZEN", "trials_sha256 is not the sha256 of "
                  "trials.jsonl: the trial list, or a trial's kind, changed "
                  "after it was declared"))

    # (c) the layer is a probe, not a build
    layer = (root / decl["thin_layer"]["path"]).resolve()
    if not layer.is_file() or root.resolve() not in layer.parents:
        f.append(("LAYER-MISSING", f"thin_layer.path "
                  f"{decl['thin_layer']['path']!r} must be a file inside "
                  f"{root.name}/"))
    else:
        if _sha(layer) != decl["thin_layer"]["sha256"]:
            f.append(("LAYER-NOT-FROZEN", "thin_layer.sha256 is not the sha256 "
                      "of the layer source: the layer changed after it was "
                      "declared"))
        code = [l for l in layer.read_text(encoding="utf-8", errors="replace")
                .splitlines() if l.strip()
                and not l.strip().startswith(("#", "//"))]
        if len(code) > MAX_LAYER_LINES:
            f.append(("LAYER-NOT-TRIVIAL", f"the thin layer has {len(code)} "
                      f"code lines; the gate allows {MAX_LAYER_LINES}. Past "
                      f"that it is a state layer being built before its "
                      f"deciding property is measured, which the roadmap bans"))

    # (a) measured, with receipts, on an instrument shown to separate
    kind = {t["trial_id"]: t["kind"] for t in trials}
    n = Counter(kind.values())
    if n["update"] == 0:
        f.append(("NO-UPDATE-TRIALS", "trials.jsonl has no `update` trials: a "
                  "layer that never supersedes would score a perfect 0%"))
    elif n["update"] < MIN_UPDATE or n["distractor"] < MIN_DISTRACTOR:
        f.append(("TOO-FEW-TRIALS", f"trials.jsonl has {n['distractor']} "
                  f"distractor and {n['update']} update trials; the gate needs "
                  f"at least {MIN_DISTRACTOR} and {MIN_UPDATE}"))
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
                  f"can read both ends"))
    order = [r["arm"] for r in receipts]
    last_control = max(i for i, a in enumerate(order) if a in (NEVER, ALWAYS))
    if last_control > min(i for i, a in enumerate(order) if a in (NATIVE, THIN)):
        f.append(("CONTROLS-NOT-FIRST", "every control receipt must come "
                  f"before the first `{NATIVE}` or `{THIN}` receipt"))

    # (d) one number, honestly placed
    real = {a: _count(kind, sup[a]) for a in (NATIVE, THIN)}
    for a in (NATIVE, THIN):
        said = verdict["arms"][a]
        if any(said[k] != real[a][k] for k in COUNTS) or abs(
                said["false_supersession_rate"]
                - real[a]["false_supersession_rate"]) >= 0.0006:
            f.append(("NUMBERS-DISAGREE", f"verdict.json arms.{a} does not "
                      f"match the receipts as recounted: {_fmt(real[a])}"))
    rule = decl["rule"]
    drop = (real[NATIVE]["false_supersession_rate"]
            - real[THIN]["false_supersession_rate"])
    missed = real[THIN]["missed_updates"] / real[THIN]["update_trials"]
    helps = (drop >= rule["layer_helps_if_rate_drop_at_least"] - 1e-9
             and missed <= rule["layer_max_missed_update_rate"] + 1e-9)
    rightful = VERDICTS[0] if helps else VERDICTS[1]
    if verdict["verdict"] != rightful:
        f.append(("VERDICT-CONTRADICTS-RULE", f"the false-supersession rate "
                  f"drops by {drop:+.3f} (rule: at least "
                  f"{rule['layer_helps_if_rate_drop_at_least']}) and the layer "
                  f"misses {missed:.3f} of real updates (rule: at most "
                  f"{rule['layer_max_missed_update_rate']}): the verdict must "
                  f"be {rightful}"))
    comp = verdict["comparison"]
    if any(comp.get(k) != v for k, v in PROTECTED.items()):
        f.append(("PROTECTED-POINT-ALTERED", "verdict.json comparison must "
                  "quote the protected point exactly: system agentmemory, "
                  "false_superseded 418, trials 450"))
    src = comp.get("source")
    if not (isinstance(src, str) and src.strip() and (repo / src).is_file()):
        f.append(("PROTECTED-POINT-UNSOURCED", f"verdict.json comparison.source "
                  f"{src!r} must be a file under {repo}"))
    return f, (f"{rightful}; {NATIVE} {_fmt(real[NATIVE])}; "
               f"{THIN} {_fmt(real[THIN])}")


def run(root: Path, repo: Path) -> int:
    findings, summary = check(root, repo)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S7-3 gate findings: {len(findings)}")
        return 1
    print(f"S7-3 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_T0 = datetime(2026, 9, 18, 17, 0, tzinfo=timezone.utc)
_D = [f"d{i:02d}" for i in range(30)]
_U = [f"u{i:02d}" for i in range(10)]
_LAYER = ("# mark-superseded-on-newer-write, and nothing else\n"
          "def write(store, key, value):\n"
          "    for old in store.get(key, []):\n"
          "        old['superseded'] = True\n"
          "    store.setdefault(key, []).append({'value': value})\n")


def _a(false, missed):
    return {"false_superseded": false, "distractor_trials": 30,
            "missed_updates": missed, "update_trials": 10,
            "false_supersession_rate": false / 30}


def _fixture(helps: bool = True) -> dict:
    """native false-supersedes 24/30. The layer: 3/30 with 1/10 updates missed
    (helps), or 24/30 as well (the honest negative)."""
    thin_false = 3 if helps else 24
    return {
        "decl": {"declared_at": _T0.isoformat(),
                 "distractor_shape": "agentmemory-class stress distractors",
                 "trials_sha256": "AUTO",
                 "thin_layer": {"path": "thin_layer.py", "sha256": "AUTO"},
                 "rule": {"layer_helps_if_rate_drop_at_least": 0.2,
                          "layer_max_missed_update_rate": 0.2}},
        "trials": [{"trial_id": t, "kind": "distractor"} for t in _D]
        + [{"trial_id": t, "kind": "update"} for t in _U],
        # arm -> the trials on which the original was treated as superseded
        "sup": {NEVER: set(), ALWAYS: set(_D + _U),
                NATIVE: set(_D[:24] + _U),
                THIN: set(_D[:thin_false] + _U[1:])},
        "order": list(ARMS), "layer": _LAYER, "raw": {}, "after_run": None,
        "source": "results/agentmemory_stress/summary.md",
        "verdict": {
            "verdict": VERDICTS[0 if helps else 1],
            "finding": "the native store false-supersedes under stress "
                       "distractors and a trivial layer removes most of it."
            if helps else
            "a trivial layer false-supersedes as often as the native store, "
            "so a thin state layer does not close Gate F.",
            "feeds": "roadmap R-PF, Decision Gate F",
            "prior_pi_lcm": "none exists; this is the first measurement",
            "comparison": dict(PROTECTED,
                               source="results/agentmemory_stress/summary.md"),
            "arms": {NATIVE: _a(24, 0), THIN: _a(thin_false, 1)}},
    }


def _write(td: Path, fx: dict) -> tuple[Path, Path]:
    repo = td / "repo"
    root = repo / "team" / "S7-STATELAYER"
    root.mkdir(parents=True)
    src = repo / fx["source"]
    src.parent.mkdir(parents=True)
    src.write_text("agentmemory 418/450 false supersession\n")
    (root / "thin_layer.py").write_text(fx["layer"])
    (root / "trials.jsonl").write_text(
        "".join(json.dumps(t) + "\n" for t in fx["trials"]))
    decl = fx["decl"]
    if decl.get("trials_sha256") == "AUTO":
        decl["trials_sha256"] = _sha(root / "trials.jsonl")
    if isinstance(decl.get("thin_layer"), dict) \
            and decl["thin_layer"].get("sha256") == "AUTO":
        decl["thin_layer"]["sha256"] = _sha(root / "thin_layer.py")
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
    (root / "receipts.jsonl").write_text("".join(out + fx.get("extra", [])))
    (root / "verdict.json").write_text(json.dumps(fx["verdict"]))
    if fx["after_run"]:
        fx["after_run"](root, decl)
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, repo


def _after_rule(root, decl):  # the bar lowered once the numbers were seen
    decl["rule"]["layer_helps_if_rate_drop_at_least"] = 0.1
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))


def _after_relabel(root, decl):  # an awkward distractor relabelled an update
    p = root / "trials.jsonl"
    p.write_text(p.read_text().replace(
        '{"trial_id": "d29", "kind": "distractor"}',
        '{"trial_id": "d29", "kind": "update"}'))


def _after_layer(root, decl):  # the layer tuned after the run
    (root / "thin_layer.py").write_text(_LAYER + "# tuned\nTHRESHOLD = 0.7\n")


def _m_late(fx): fx["decl"]["declared_at"] = (_T0 + timedelta(hours=1)).isoformat()
def _m_rule_moved(fx): fx["after_run"] = _after_rule
def _m_relabel(fx): fx["after_run"] = _after_relabel
def _m_layer_tuned(fx): fx["after_run"] = _after_layer
def _m_noshape(fx): fx["decl"]["distractor_shape"] = "hard cases"
def _m_norule(fx): del fx["decl"]["rule"]
def _m_halfrule(fx): del fx["decl"]["rule"]["layer_max_missed_update_rate"]
def _m_layer_gone(fx): fx["decl"]["thin_layer"]["path"] = "../../src/state.py"
def _m_layer_big(fx): fx["layer"] = _LAYER + "x = 1\n" * 100
def _m_noarm(fx): fx["order"] = [NEVER, ALWAYS, NATIVE]
def _m_nocontrols(fx): fx["order"] = [NATIVE, THIN]
def _m_order(fx): fx["order"] = [NATIVE, THIN, NEVER, ALWAYS]
def _m_control(fx): fx["sup"][ALWAYS] = set(_D)
def _m_numbers(fx): fx["verdict"]["arms"][THIN]["false_superseded"] = 1
def _m_rate(fx): fx["verdict"]["arms"][NATIVE]["false_supersession_rate"] = 0.5
def _m_flip(fx): fx["verdict"]["verdict"] = VERDICTS[1]
def _m_maybe(fx): fx["verdict"]["verdict"] = "promising"
def _m_nofinding(fx): fx["verdict"]["finding"] = ""
def _m_nofeeds(fx): del fx["verdict"]["feeds"]
def _m_noprior(fx): fx["verdict"]["prior_pi_lcm"] = "see earlier runs"
def _m_protected(fx): fx["verdict"]["comparison"]["false_superseded"] = 408
def _m_unsourced(fx): fx["verdict"]["comparison"]["source"] = "results/nope.md"
def _m_badjson(fx): fx["raw"]["verdict.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["receipts.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["trials.jsonl"] = None


def _m_few(fx):  # numbers kept consistent, so only the floor can object
    fx["trials"] = fx["trials"][:5] + fx["trials"][30:]
    for arm, false in ((NATIVE, 5), (THIN, 3)):
        fx["verdict"]["arms"][arm].update(false_superseded=false,
                                          distractor_trials=5,
                                          false_supersession_rate=false / 5)


def _m_short(fx):
    fx["raw"]["receipts.jsonl"] = "DROP-LAST"


def _m_no_updates(fx):  # the trap: no real updates in the list at all
    fx["trials"] = fx["trials"][:30]


def _m_never_layer(fx):  # the trap: a layer that never supersedes claims a win
    fx["sup"][THIN] = set()
    fx["verdict"]["arms"][THIN] = _a(0, 10)


def _m_receipts(fx):  # every file exists and says nothing
    fx["raw"] = {n: "{}\n" for n in FILES}


def _m_claimed_win(fx):  # honest negative data, a win written over it
    fx.update(copy.deepcopy(_fixture(helps=False)), verdict=fx["verdict"])


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "declared after the run": (_m_late, {"DECLARED-AFTER-RECEIPTS"}),
    "rule moved after the run": (_m_rule_moved, {"RECEIPTS-NOT-BOUND"}),
    "trial relabelled after the run": (_m_relabel, {"TRIALS-NOT-FROZEN",
                                                    "TOO-FEW-TRIALS",
                                                    "NUMBERS-DISAGREE"}),
    "layer tuned after the run": (_m_layer_tuned, {"LAYER-NOT-FROZEN"}),
    "shape not named": (_m_noshape, {"SHAPE-NOT-DECLARED"}),
    "no verdict rule": (_m_norule, {"RULE-UNDECLARED"}),
    "rule without the missed-update guard": (_m_halfrule, {"RULE-UNDECLARED"}),
    "layer outside the directory": (_m_layer_gone, {"LAYER-MISSING"}),
    "layer is a build, not a probe": (_m_layer_big, {"LAYER-NOT-TRIVIAL"}),
    "five distractor trials": (_m_few, {"TOO-FEW-TRIALS"}),
    "no update trials": (_m_no_updates, {"NO-UPDATE-TRIALS"}),
    "layer arm missing": (_m_noarm, {"ARM-MISSING"}),
    "no control arms": (_m_nocontrols, {"ARM-MISSING"}),
    "a receipt dropped": (_m_short, {"ARM-INCOMPLETE"}),
    "controls after the engines": (_m_order, {"CONTROLS-NOT-FIRST"}),
    "control arm wrong": (_m_control, {"CONTROL-ARM-WRONG"}),
    "counts wrong": (_m_numbers, {"NUMBERS-DISAGREE"}),
    "rate wrong": (_m_rate, {"NUMBERS-DISAGREE"}),
    "verdict against the rule": (_m_flip, {"VERDICT-CONTRADICTS-RULE"}),
    "never-supersede layer claims a win": (_m_never_layer,
                                           {"VERDICT-CONTRADICTS-RULE"}),
    "win claimed over negative data": (_m_claimed_win,
                                       {"NUMBERS-DISAGREE",
                                        "VERDICT-CONTRADICTS-RULE"}),
    "verdict not in vocabulary": (_m_maybe, {"VERDICT-INVALID"}),
    "verdict without finding": (_m_nofinding, {"VERDICT-NO-FINDING"}),
    "decision not named": (_m_nofeeds, {"GATE-F-NOT-NAMED"}),
    "prior not stated": (_m_noprior, {"PRIOR-NOT-STATED"}),
    "protected point altered": (_m_protected, {"PROTECTED-POINT-ALTERED"}),
    "protected point unsourced": (_m_unsourced, {"PROTECTED-POINT-UNSOURCED"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile receipts": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want):
        with tempfile.TemporaryDirectory() as td:
            drop = fx["raw"].pop("receipts.jsonl", None) \
                if fx["raw"].get("receipts.jsonl") == "DROP-LAST" else None
            root, repo = _write(Path(td), fx)
            if drop:
                p = root / "receipts.jsonl"
                p.write_text("".join(p.read_text().splitlines(True)[:-1]))
            r = subprocess.run([sys.executable, __file__, str(root), "--repo",
                                str(repo)], capture_output=True, text=True,
                               timeout=60)
        text = r.stdout + r.stderr
        got = set(marker.findall(text))
        if "Traceback (most recent call last)" in text:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got
                               or "gate findings" in text):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not want(got)
                                   or "S7-3 gate findings: " not in text):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming, layer helps", _fixture(True), None)
    case("conforming, honestly does not help", _fixture(False), None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: len(got) >= 3 and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, lambda got, want=want: got == want)

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (2 conforming fixtures accepted, one of them an "
          f"honest negative; a receipts-only directory and {len(_MUTANTS)} "
          f"mutants each rejected by exactly their own markers, a "
          f"never-supersede layer among them; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S7-3")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--repo", default=str(HERE.parent.parent))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.root), Path(a.repo))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S7-3 gate findings: 1")
        raise SystemExit(1)
