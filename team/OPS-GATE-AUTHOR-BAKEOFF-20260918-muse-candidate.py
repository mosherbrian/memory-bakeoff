import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


ROW_PRIOR_REL = "team/S7-STATELAYER/verdict.json"
SPEC_NAME = "spec.json"
TRIALS_NAME = "trials.jsonl"
VERDICT_NAME = "verdict.json"


class Finding(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(f"FINDING {code}: {detail}")


def _read_text(p: Path):
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        raise Finding("READ_ERROR", f"{p} unreadable: {e}")


def _load_json(p: Path, code):
    t = _read_text(p)
    try:
        o = json.loads(t)
    except Exception as e:
        raise Finding(code, f"{p} is not valid JSON: {e}")
    return o, t


def _check_prior(prior_path: Path, findings: list):
    if not prior_path.is_file():
        findings.append(
            f"FINDING MISSING_PRIOR: row-declared {ROW_PRIOR_REL} not found at {prior_path}"
        )
        return None, ""
    try:
        obj, raw = _load_json(prior_path, "BAD_PRIOR_JSON")
    except Finding as f:
        findings.append(str(f))
        return None, ""
    low = raw.lower()
    has_slash_old = "0/32" in raw
    has_slash_upd = "12/12" in raw
    has_concepts = ("false" in low and "supersession" in low) or ("false" in low and "update" in low)
    if not has_concepts:
        findings.append(
            "FINDING PRIOR_NOT_CONTROLLED: row-declared team/S7-STATELAYER/verdict.json does not report false-supersession/update concepts"
        )
    elif not (has_slash_old and has_slash_upd):
        # lenient numeric fallback: look for 32 and 12 near relevant keys
        has32 = bool(re.search(r"32", raw))
        has12 = bool(re.search(r"12", raw))
        if not (has32 and has12):
            findings.append(
                "FINDING PRIOR_NOT_CONTROLLED: prior verdict does not contain controlled-corpus baseline 0/32 false supersession and 12/12 updates"
            )
    return obj, raw


def _get_alias(d: dict, keys, default=None):
    if not isinstance(d, dict):
        return default
    lowmap = {str(k).lower(): k for k in d.keys()}
    for k in keys:
        if k.lower() in lowmap:
            return d[lowmap[k.lower()]]
    return default


def _check_spec(art: Path, findings: list):
    p = art / SPEC_NAME
    if not p.is_file():
        findings.append(f"FINDING MISSING_SPEC: {SPEC_NAME} not found in {art}")
        return None, ""
    try:
        obj, raw = _load_json(p, "BAD_SPEC_JSON")
    except Finding as f:
        findings.append(str(f))
        return None, ""
    low = raw.lower()
    if "s7-3" not in low and "s7_3" not in low:
        findings.append("FINDING SPEC_NOT_S73_BASE: spec must declare mechanical extension of S7-3 trial generation")
    v = _get_alias(obj, ["declared_before_run", "declared-before-run", "predeclared"], None)
    if v is not True:
        findings.append("FINDING SPEC_NOT_DECLARED_BEFORE_RUN: spec must set declared_before_run=true (declared before the run)")
    fams = _get_alias(obj, ["distractor_families", "families", "distractorFamilies"], None)
    if not isinstance(fams, list) or len([x for x in fams if isinstance(x, str) and x.strip()]) < 3:
        findings.append("FINDING SPEC_NOT_BROADER_FAMILIES: spec must declare >=3 distractor families (more families than S7-3)")
    ext = _get_alias(obj, ["extends_s73", "extends-s73", "extendsS73"], None)
    added = _get_alias(obj, ["added_families", "addedFamilies", "added", "extension"], None)
    has_broader_word = "broader" in low or "extend" in low or "added" in low
    if not (ext is True or (isinstance(added, list) and len(added) > 0) or has_broader_word):
        findings.append("FINDING SPEC_NOT_BROADER_FAMILIES: spec must explicitly declare extension vs S7-3 (extends_s73/added_families)")
    # longer streams
    stream_obj = _get_alias(obj, ["stream", "streams", "stream_spec"], None)
    maxlen = None
    longer_flag = None
    if isinstance(stream_obj, dict):
        maxlen = _get_alias(stream_obj, ["max_len", "maxLen", "max_length", "max", "len_max", "longest"], None)
        longer_flag = _get_alias(stream_obj, ["longer_than_s73", "longerThanS73", "longer", "extended"], None)
    if maxlen is None:
        maxlen = _get_alias(obj, ["stream_max_len", "max_stream_len", "max_len", "stream_len_max", "longest_stream"], None)
    if longer_flag is None:
        longer_flag = _get_alias(obj, ["longer_than_s73", "longerThanS73"], None)
    try:
        maxlen_num = int(maxlen) if maxlen is not None else None
    except Exception:
        maxlen_num = None
    if maxlen_num is None or maxlen_num < 50:
        findings.append("FINDING SPEC_NOT_LONGER_STREAMS: spec must declare longer streams with numeric max_len>=50")
    if longer_flag is not True:
        findings.append("FINDING SPEC_NOT_LONGER_STREAMS: spec must set longer_than_s73=true")
    # 92.9% agentmemory shape
    if "92.9" not in raw or "agentmemory" not in low:
        findings.append("FINDING SPEC_NOT_AGENTMEMORY_SHAPE: spec must cite documented agentmemory 92.9% distractor shape")
    # unfitted
    unf = None
    fit = None
    if isinstance(obj, dict):
        unf = _get_alias(obj, ["unfitted"], None)
        fit = _get_alias(obj, ["fitted"], None)
        if isinstance(stream_obj, dict):
            pass
        shape = _get_alias(obj, ["distractor_shape", "distractorShape", "shape"], None)
        if isinstance(shape, dict):
            if unf is None:
                unf = _get_alias(shape, ["unfitted"], None)
            if fit is None:
                fit = _get_alias(shape, ["fitted"], None)
        if unf is None:
            # search raw for unfitted:true
            if re.search(r'"unfitted"\s*:\s*true', raw, re.I):
                unf = True
        if fit is None and re.search(r'"fitted"\s*:\s*true', raw, re.I):
            fit = True
    if unf is not True:
        findings.append("FINDING SPEC_NOT_UNFITTED: spec must declare distractor shape unfitted=true")
    if fit is True:
        findings.append("FINDING SPEC_NOT_UNFITTED: spec must not set fitted=true (row requires unfitted)")
    # native only, no layer
    arm = _get_alias(obj, ["arm", "arms", "native_arm_only"], None)
    if isinstance(obj, dict):
        nao = _get_alias(obj, ["native_arm_only", "nativeArmOnly", "native_only"], None)
        if nao is not True:
            # accept arm=="native" as alternative
            ok = False
            if isinstance(arm, str) and arm.lower() == "native":
                ok = True
            if isinstance(arm, list) and len(arm) == 1 and str(arm[0]).lower() == "native":
                ok = True
            if not ok:
                findings.append("FINDING SPEC_HAS_LAYER: spec must declare NATIVE arm only (native_arm_only=true / arm=native), no layer code")
    # layer active in spec?
    for k, val in (obj.items() if isinstance(obj, dict) else []):
        if "layer" in str(k).lower():
            if val is True or (isinstance(val, str) and val.lower() not in ("", "none", "false", "no", "native only", "native-only", "not run", "disabled")):
                if isinstance(val, (list, dict)) and len(val) == 0:
                    continue
                if isinstance(val, (int, float)) and val == 0:
                    continue
                if isinstance(val, str) and "no layer" in val.lower():
                    continue
                findings.append(f"FINDING SPEC_HAS_LAYER: spec key {k!r} indicates layer involvement; row requires NATIVE pi-lcm arm only")
                break
    return obj, raw


def _check_trials(art: Path, spec_obj, findings: list):
    p = art / TRIALS_NAME
    if not p.is_file():
        findings.append(f"FINDING MISSING_TRIALS: {TRIALS_NAME} not found in {art}")
        return []
    rows = []
    try:
        text = _read_text(p)
    except Finding as f:
        findings.append(str(f))
        return []
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        findings.append("FINDING BAD_TRIALS: trials file is empty; broader corpus requires executed trials")
        return []
    bad_lines = 0
    for i, l in enumerate(lines, 1):
        try:
            o = json.loads(l)
            rows.append(o)
        except Exception:
            bad_lines += 1
    if bad_lines:
        findings.append(f"FINDING BAD_TRIALS: {bad_lines}/{len(lines)} lines are not valid JSON")
        return rows
    if len(rows) < 20:
        findings.append(f"FINDING TRIALS_NOT_BROADER: only {len(rows)} trials; declared-broader corpus requires >=20")
    fams = set()
    maxlen = 0
    missing_fields = 0
    for r in rows:
        if not isinstance(r, dict):
            missing_fields += 1
            continue
        fam = _get_alias(r, ["distractor_family", "family", "distractorFamily"], None)
        sl = _get_alias(r, ["stream_len", "streamLen", "len", "length", "history_len", "n_steps"], None)
        if fam is None or sl is None:
            missing_fields += 1
            continue
        if isinstance(fam, str) and fam.strip():
            fams.add(fam.strip().lower())
        try:
            sln = int(sl)
            if sln > maxlen:
                maxlen = sln
        except Exception:
            missing_fields += 1
    if missing_fields:
        findings.append(f"FINDING BAD_TRIALS: {missing_fields}/{len(rows)} trials lack distractor_family/stream_len")
    if len(fams) < 3:
        findings.append(f"FINDING TRIALS_NOT_BROADER: only {len(fams)} distinct distractor families in trials; need >=3 for broader histories")
    if maxlen < 50:
        findings.append(f"FINDING TRIALS_NOT_BROADER: max stream_len {maxlen} <50; longer streams not evidenced")
    # cross-check vs spec families if available
    if isinstance(spec_obj, dict):
        sf = _get_alias(spec_obj, ["distractor_families", "families"], None)
        if isinstance(sf, list) and sf:
            sset = set(str(x).strip().lower() for x in sf if isinstance(x, str))
            if sset and len(fams & sset) < 2:
                findings.append("FINDING TRIALS_SHAPE_MISMATCH: trials families do not match spec-declared distractor families")
    return rows


def _extract_verdict_numbers(v: dict):
    false_n = _get_alias(v, ["native_false_supersessions", "false_supersessions", "false_supersession_count", "false_count", "n_false"], None)
    total_n = _get_alias(v, ["native_false_supersession_total", "n_trials", "total_trials", "n", "total", "num_trials"], None)
    upd_ok = _get_alias(v, ["native_updates_correct", "updates_correct", "updates_ok", "n_updates_correct"], None)
    upd_tot = _get_alias(v, ["native_updates_total", "updates_total", "n_updates_total", "updates"], None)
    missed = _get_alias(v, ["missed_updates", "missed", "n_missed"], None)
    return false_n, total_n, upd_ok, upd_tot, missed


def _check_verdict(art: Path, prior_raw: str, trial_rows: list, findings: list):
    p = art / VERDICT_NAME
    if not p.is_file():
        findings.append(f"FINDING MISSING_VERDICT: {VERDICT_NAME} not found in {art}")
        return None
    try:
        v, raw = _load_json(p, "BAD_VERDICT_JSON")
    except Finding as f:
        findings.append(str(f))
        return None
    if not isinstance(v, dict):
        findings.append("FINDING BAD_VERDICT_JSON: verdict root must be a JSON object")
        return None
    low = raw.lower()
    # native only
    arm = _get_alias(v, ["arm", "arms"], None)
    native_ok = False
    if isinstance(arm, str) and arm.lower() == "native":
        native_ok = True
    if isinstance(arm, list) and len(arm) == 1 and str(arm[0]).lower() == "native":
        native_ok = True
    if _get_alias(v, ["native_arm_only"], None) is True:
        native_ok = True
    if "native" in low and native_ok:
        pass
    else:
        # require explicit native declaration
        if not native_ok:
            findings.append("FINDING VERDICT_NOT_NATIVE_ONLY: verdict must declare native arm only (arm=native)")
    # layer presence with active meaning
    for k, val in v.items():
        if "layer" in str(k).lower():
            active = True
            if val is False or val == 0 or val == [] or val == {}:
                active = False
            elif isinstance(val, str) and val.lower() in ("", "none", "no", "false", "disabled", "not run", "native only", "native-only"):
                active = False
            elif isinstance(val, dict):
                # allow zeroed layer stats or explicit not-run marker
                s = json.dumps(val).lower()
                if ("not run" in s or "native only" in s or "no layer" in s):
                    active = False
                elif re.search(r'"(false|total|n_trials|count)"\s*:\s*[1-9]', s):
                    active = True
                elif val == {}:
                    active = False
                else:
                    # any layer dict with nonzero counts is active; empty/zero is ok
                    nums = re.findall(r":\s*(\d+)", s)
                    if nums and any(int(x) != 0 for x in nums):
                        active = True
                    else:
                        active = False
            if active:
                findings.append(f"FINDING VERDICT_HAS_LAYER: verdict key {k!r} indicates layer measurement; row requires NATIVE pi-lcm arm only, no layer code")
                break
    # numbers present
    false_n, total_n, upd_ok, upd_tot, missed = _extract_verdict_numbers(v)
    try:
        false_n_i = int(false_n) if false_n is not None else None
        total_n_i = int(total_n) if total_n is not None else None
        upd_ok_i = int(upd_ok) if upd_ok is not None else None
        upd_tot_i = int(upd_tot) if upd_tot is not None else None
    except Exception:
        findings.append("FINDING VERDICT_NEW_INCONSISTENT: verdict counts must be integers (false supersessions, trials, updates)")
        return v
    if None in (false_n_i, total_n_i, upd_ok_i, upd_tot_i):
        findings.append("FINDING VERDICT_NEW_INCONSISTENT: verdict must report native false-supersession count/total and update correct/total")
    else:
        if not (0 <= false_n_i <= total_n_i and total_n_i > 0):
            findings.append("FINDING VERDICT_NEW_INCONSISTENT: false-supersession count must satisfy 0<=false<=total, total>0")
        if not (0 <= upd_ok_i <= upd_tot_i and upd_tot_i > 0):
            findings.append("FINDING VERDICT_NEW_INCONSISTENT: updates must satisfy 0<=correct<=total, total>0")
        if missed is not None:
            try:
                m = int(missed)
                if m != (upd_tot_i - upd_ok_i):
                    findings.append("FINDING VERDICT_NEW_INCONSISTENT: missed_updates must equal updates_total-updates_correct")
            except Exception:
                findings.append("FINDING VERDICT_NEW_INCONSISTENT: missed_updates must be integer")
        if trial_rows and total_n_i != len(trial_rows):
            findings.append(f"FINDING VERDICT_NEW_INCONSISTENT: verdict total {total_n_i} != executed trials {len(trial_rows)}")
    # old_vs_new
    ovn = _get_alias(v, ["old_vs_new", "oldVsNew", "old-vs-new", "comparison"], None)
    if not isinstance(ovn, dict):
        findings.append("FINDING VERDICT_MISSING_OLD_VS_NEW: verdict must contain old_vs_new {old,new} vs team/S7-STATELAYER/verdict.json")
    else:
        old = _get_alias(ovn, ["old", "prior", "baseline", "s7"], None)
        new = _get_alias(ovn, ["new", "current", "remeasure", "s10", "s11"], None)
        if not isinstance(old, dict) or not isinstance(new, dict):
            findings.append("FINDING VERDICT_MISSING_OLD_VS_NEW: old_vs_new must have old{} and new{} objects")
        else:
            os_ = json.dumps(old)
            if "0/32" not in os_:
                # numeric fallback
                if not (re.search(r"\b0\b", os_) and re.search(r"\b32\b", os_)):
                    findings.append("FINDING VERDICT_OLD_MISMATCH: old_vs_new.old must restate prior 0/32 false supersession")
            if "12/12" not in os_:
                if not (re.search(r"\b12\b", os_)):
                    findings.append("FINDING VERDICT_OLD_MISMATCH: old_vs_new.old must restate prior 12/12 updates")
            if ROW_PRIOR_REL not in os_ and "s7-statelayer" not in os_.lower():
                findings.append("FINDING VERDICT_OLD_MISMATCH: old_vs_new.old must cite source team/S7-STATELAYER/verdict.json")
            ns = json.dumps(new)
            if false_n_i is not None and total_n_i is not None:
                exp = f"{false_n_i}/{total_n_i}"
                if exp not in ns and not (str(false_n_i) in ns and str(total_n_i) in ns):
                    findings.append("FINDING VERDICT_NEW_INCONSISTENT: old_vs_new.new must restate new false-supersession numbers")
            if upd_ok_i is not None and upd_tot_i is not None:
                exp2 = f"{upd_ok_i}/{upd_tot_i}"
                if exp2 not in ns and not (str(upd_ok_i) in ns and str(upd_tot_i) in ns):
                    findings.append("FINDING VERDICT_NEW_INCONSISTENT: old_vs_new.new must restate new update numbers")
    # outcome consistency: null vs native failure
    out = _get_alias(v, ["outcome", "result", "conclusion", "finding"], None)
    if out is None:
        findings.append("FINDING VERDICT_OUTCOME_MISMATCH: verdict must state outcome null_no_native_failure vs native_failure_found")
    elif isinstance(out, str):
        lo = out.lower()
        has_failure = False
        if false_n_i is not None and upd_ok_i is not None and upd_tot_i is not None:
            has_failure = (false_n_i > 0) or (upd_ok_i < upd_tot_i)
        if has_failure:
            if "native" not in lo or "fail" not in lo:
                findings.append("FINDING VERDICT_OUTCOME_MISMATCH: non-null native errors require outcome native_failure_found (changes state-layer answer)")
        else:
            if not (("null" in lo) or ("no" in lo and "fail" in lo) or ("gate" in lo and "f" in lo)):
                findings.append("FINDING VERDICT_OUTCOME_MISMATCH: null result must be recorded as null Gate-F evidence (null_no_native_failure)")
    # llm / cost / deps
    llm = _get_alias(v, ["llm_used", "llmUsed", "used_llm", "llm"], "ABSENT")
    if llm != False:
        # allow explicit false-like strings? require boolean false
        if not (isinstance(llm, str) and llm.lower() in ("false", "no", "none")):
            findings.append("FINDING VERDICT_LLM_COST_DEP: verdict must set llm_used=false ($0, local, no LLM)")
    cost = _get_alias(v, ["cost_usd", "cost", "costUsd", "dollars"], "ABSENT")
    if cost != "ABSENT":
        try:
            if float(cost) != 0.0:
                findings.append("FINDING VERDICT_LLM_COST_DEP: cost must be 0 ($0, local)")
        except Exception:
            findings.append("FINDING VERDICT_LLM_COST_DEP: cost_usd must be numeric 0")
    else:
        findings.append("FINDING VERDICT_LLM_COST_DEP: verdict must declare cost_usd=0")
    deps = _get_alias(v, ["depends_on", "dependsOn", "depends", "deps"], "ABSENT")
    if deps != "ABSENT":
        if not (isinstance(deps, list) and len(deps) == 0):
            findings.append("FINDING VERDICT_LLM_COST_DEP: depends_on must be [] (row: Depends on none)")
    else:
        findings.append("FINDING VERDICT_LLM_COST_DEP: verdict must declare depends_on=[]")
    return v


def _check_no_layer_code(art: Path, findings: list):
    pat = re.compile(r"state\s*[-_ ]?layer|layer\s*[-_ ]?arm|layer\s*[-_ ]?code|from\s+\S*layer|import\s+\S*layer", re.I)
    try:
        pys = [p for p in art.glob("*.py") if p.name != "check.py"]
    except Exception:
        return
    for py in pys:
        try:
            t = py.read_text(encoding="utf-8", errors="strict")
        except Exception:
            continue
        if pat.search(t):
            findings.append(f"FINDING LAYER_CODE_PRESENT: {py.name} contains layer code; row requires NATIVE pi-lcm arm only, no layer code")
            break


def check_artifact(art_dir: Path, prior_path: Path):
    findings: list = []
    try:
        _, prior_raw = _check_prior(prior_path, findings)
    except Exception:
        findings.append("FINDING PRIOR_NOT_CONTROLLED: prior verdict unreadable")
        prior_raw = ""
    try:
        spec_obj, _ = _check_spec(art_dir, findings)
    except Exception:
        findings.append("FINDING BAD_SPEC_JSON: spec unreadable")
        spec_obj = None
    try:
        rows = _check_trials(art_dir, spec_obj, findings)
    except Exception:
        findings.append("FINDING BAD_TRIALS: trials unreadable")
        rows = []
    try:
        _check_verdict(art_dir, prior_raw, rows, findings)
    except Exception:
        findings.append("FINDING BAD_VERDICT_JSON: verdict unreadable")
    try:
        _check_no_layer_code(art_dir, findings)
    except Exception:
        findings.append("FINDING LAYER_CODE_PRESENT: layer scan failed")
    # dedupe preserving order
    seen = set()
    out = []
    for f in findings:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def resolve_real_paths():
    art = Path(__file__).resolve().parent
    root = None
    probe = art
    for _ in range(7):
        if (probe / ROW_PRIOR_REL).is_file():
            root = probe
            break
        probe = probe.parent
    if root is None:
        # fallback: <root>/team/S10-PI-LCM-HIST/check.py layout
        try:
            cand = art.parents[2]
            if (cand / ROW_PRIOR_REL).is_file() or (cand / "team").is_dir():
                root = cand
            else:
                root = Path.cwd()
        except Exception:
            root = Path.cwd()
    prior = root / ROW_PRIOR_REL
    return art, prior


def _write_prior(root: Path):
    d = root / "team" / "S7-STATELAYER"
    d.mkdir(parents=True, exist_ok=True)
    prior = {
        "corpus": "controlled only",
        "native_false_supersession": "0/32",
        "native_updates": "12/12",
        "layer_false_supersession": "0/32",
        "layer_updates": "12/12",
    }
    (d / "verdict.json").write_text(json.dumps(prior, indent=2), encoding="utf-8")


def _write_conforming(art: Path):
    art.mkdir(parents=True, exist_ok=True)
    spec = {
        "base": "S7-3",
        "declared_before_run": True,
        "distractor_families": ["negation-flip", "temporal-shift", "entity-swap"],
        "added_families": ["temporal-shift", "entity-swap"],
        "extends_s73": True,
        "stream": {"max_len": 80, "min_len": 50, "longer_than_s73": True},
        "distractor_shape": {"name": "agentmemory 92.9% distractor shape", "unfitted": True, "fitted": False},
        "arm": "native",
        "native_arm_only": True,
        "llm_used": False,
        "cost_usd": 0,
    }
    (art / SPEC_NAME).write_text(json.dumps(spec, indent=2), encoding="utf-8")
    fams = ["negation-flip", "temporal-shift", "entity-swap"]
    with open(art / TRIALS_NAME, "w", encoding="utf-8") as fh:
        tid = 0
        for fam in fams:
            for k in range(8):
                tid += 1
                sl = 55 + ((tid * 7) % 26)
                fh.write(json.dumps({"id": tid, "distractor_family": fam, "stream_len": sl, "history": [0] * sl}) + "\n")
    verdict = {
        "row": "S11-3",
        "arm": "native",
        "native_arm_only": True,
        "n_trials": 24,
        "native_false_supersessions": 0,
        "native_false_supersession_total": 24,
        "native_updates_correct": 24,
        "native_updates_total": 24,
        "missed_updates": 0,
        "old_vs_new": {
            "old": {"false_supersession": "0/32", "updates": "12/12", "source": "team/S7-STATELAYER/verdict.json"},
            "new": {"false_supersession": "0/24", "updates": "24/24"},
        },
        "outcome": "null_no_native_failure: Gate F evidence, no native false supersession",
        "llm_used": False,
        "cost_usd": 0,
        "depends_on": [],
    }
    (art / VERDICT_NAME).write_text(json.dumps(verdict, indent=2), encoding="utf-8")


def _write_nonconforming(art: Path):
    art.mkdir(parents=True, exist_ok=True)
    spec = {
        "base": "S7-3",
        "declared_before_run": False,
        "distractor_families": ["negation-flip"],
        "stream": {"max_len": 20, "longer_than_s73": False},
        "distractor_shape": {"name": "custom fitted shape", "unfitted": False, "fitted": True},
        "arm": "layer",
        "native_arm_only": False,
    }
    (art / SPEC_NAME).write_text(json.dumps(spec, indent=2), encoding="utf-8")
    with open(art / TRIALS_NAME, "w", encoding="utf-8") as fh:
        for i in range(1, 6):
            fh.write(json.dumps({"id": i, "distractor_family": "negation-flip", "stream_len": 10}) + "\n")
    verdict = {
        "row": "S11-3",
        "arm": "layer",
        "n_trials": 5,
        "native_false_supersessions": 0,
        "native_false_supersession_total": 5,
        "native_updates_correct": 5,
        "native_updates_total": 5,
        "llm_used": True,
        "cost_usd": 5,
        "depends_on": ["S7-3"],
        "layer_arm": {"n_trials": 5},
    }
    (art / VERDICT_NAME).write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    (art / "run_layer.py").write_text("from state_layer import run\nlayer_arm.run()\n", encoding="utf-8")


def run_selftest():
    try:
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            r1 = Path(t1)
            _write_prior(r1)
            a1 = r1 / "team" / "S10-PI-LCM-HIST"
            _write_conforming(a1)
            f1 = check_artifact(a1, r1 / ROW_PRIOR_REL)
            r2 = Path(t2)
            _write_prior(r2)
            a2 = r2 / "team" / "S10-PI-LCM-HIST"
            _write_nonconforming(a2)
            f2 = check_artifact(a2, r2 / ROW_PRIOR_REL)
            ok_reject = len(f2) > 0
            ok_accept = len(f1) == 0
            if ok_reject and ok_accept:
                print("SELFTEST PASS: non-conforming rejected; conforming accepted")
                print(f"SELFTEST EVIDENCE reject={f2[0]}")
                return 0
            if not ok_reject:
                print("FINDING SELFTEST_NO_FAIL: deliberately non-conforming fixture was accepted; check cannot fail")
                return 1
            print(f"FINDING SELFTEST_FALSE_REJECT: minimal conforming fixture rejected: {f1[0] if f1 else 'unknown'}")
            for f in f1:
                print(f)
            return 1
    except Exception as e:
        print(f"FINDING SELFTEST_ERROR: selftest crashed: {e}")
        return 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.selftest:
            sys.exit(run_selftest())
        art, prior = resolve_real_paths()
        findings = check_artifact(art, prior)
        if not findings:
            print("OK: S11-3 native broader-history evidence clean")
            return 0
        for f in findings:
            print(f)
        return 1
    except SystemExit:
        raise
    except Exception as e:
        print(f"FINDING INTERNAL_ERROR: gate crashed without verdict: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
