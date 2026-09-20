#!/usr/bin/env python3
"""S4-13(b) — first matched-pair M1–M4 table over the S4-9 corrected window.

Descriptive first pass per SPEC-OUTCOME-PROTOCOL.md §3/§3.1/§7. Provenance is
pinned by the row's declared check: every number derives from the frozen
outcome bundle and the S4-9-declared window artifacts.

  M1  per-pair tokens/wall from the S4-9 frozen-input rerun (`run/pairs.json`,
      n=122): median + IQR of per-pair log-ratios, pooled and by family.
  M2  per-pair error counts, detectable kind "non-zero-exit command used as a
      task step" = toolResult records with isError=true, attributed to the
      in-progress turn by rebuilding turns with the S5 machinery itself
      (s5_pairing.build_turns_from_records). Other frozen M2 kinds
      (reverted edit, wrong-scope write, test/CI failure, broken build) are
      NOT detectable in this session shape — reported as absent, not zero.
  M3  NOT INSTRUMENTED this pass: needs record-state-at-start + delivered-
      level matching; fuzzy matching is exploratory_only by spec and is not
      invented here. The column is reported as structurally absent.
  M4  window-level counts from the frozen §5.1 bundle (part (a) harness
      bands), filtered to the declared window. Per-pair M4 attribution is
      impossible by construction (opaque pseudonyms over a different corpus),
      so M4 is a window-level column, never imputed into pairs.

Fail-closed pins: window file, INPUT-MANIFEST sha (S4-9 declaration),
pairs.json sha, bundle sha. Deterministic; re-running reproduces bytes.

Usage: m124_window_table.py
"""
import hashlib
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

TEAM = Path("/var/home/bmosher/memory-bake-off/team")
WINDOW_FILE = TEAM / "WINDOW-campaign-1.json"
BUNDLE = TEAM / "outcome-bundle-scale-20260915" / "events.jsonl"
FROZEN_BUNDLE_SHA = "88f875e7a7eb94663033d4a0dc684537486266ea3d51099ad945394f50095d10"
S5 = Path("/var/home/bmosher/acp-pi/s5-final-windowfix-20260916")
INPUT_MANIFEST = S5 / "frozen-input" / "INPUT-MANIFEST.json"
FROZEN_MANIFEST_SHA = "0f89ca5a0cda4b21b252db736f4b801b309f46db45f7e43932283303e04303ee"
PAIRS_JSON = S5 / "run" / "pairs.json"
FROZEN_PAIRS_SHA = "ce94487964887a596404c586d979efab36ee85761705cb593aba300d0b6d5f23"
SESSIONS = S5 / "frozen-input" / "sessions"
sys.path.insert(0, "/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2/scripts/experiment_20260912_s5")
import s5_pairing  # the S4-9 machinery itself; used read-only

OUT = TEAM / "s4-13-outcome"


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def med_iqr(vals):
    if not vals:
        return None
    v = sorted(vals)
    n = len(v)
    med = statistics.median(v)
    lo = v[max(0, int(0.25 * (n - 1)))]
    hi = v[min(n - 1, int(0.75 * (n - 1)))]
    return {"n": n, "median": round(med, 4), "iqr": [round(lo, 4), round(hi, 4)]}


def main():
    win = json.loads(WINDOW_FILE.read_text())
    w0 = datetime.fromisoformat(win["start_utc"].replace("Z", "+00:00"))
    w1 = datetime.fromisoformat(win["end_utc"].replace("Z", "+00:00"))

    findings = []
    if sha256(INPUT_MANIFEST) != FROZEN_MANIFEST_SHA:
        findings.append("INPUT-MANIFEST sha drifted from S4-9 declaration")
    if sha256(BUNDLE) != FROZEN_BUNDLE_SHA:
        findings.append("bundle sha drifted from frozen value")
    pairs_sha = sha256(PAIRS_JSON)

    data = json.loads(PAIRS_JSON.read_text())
    pairs = data["pairs"]
    if len(pairs) != 122:
        findings.append(f"expected 122 pairs, found {len(pairs)}")

    # --- M1: per-pair log-ratios ------------------------------------------
    for p in pairs:
        p["m1_token_logratio"] = round(math.log(p["mem_tokens"] / p["nomem_tokens"]), 4)
        p["m1_wall_logratio"] = round(math.log(p["mem_wall_s"] / p["nomem_wall_s"]), 4)
    m1_tokens_all = med_iqr([p["m1_token_logratio"] for p in pairs])
    m1_wall_all = med_iqr([p["m1_wall_logratio"] for p in pairs])
    by_family = defaultdict(list)
    for p in pairs:
        by_family[p["family"]].append(p)
    m1_by_family = {
        f: {"n": len(ps),
            "token_logratio": med_iqr([p["m1_token_logratio"] for p in ps]),
            "wall_logratio": med_iqr([p["m1_wall_logratio"] for p in ps])}
        for f, ps in sorted(by_family.items())}
    # cross-check vs S4-9 report medians (median of pct deltas)
    med_tok_pct = statistics.median(p["token_delta_pct"] for p in pairs)
    med_wall_pct = statistics.median(p["wall_delta_pct"] for p in pairs)

    # --- M2: rebuild turns from frozen sessions, count isError toolResults -
    tool_err = Counter()          # (session_id, turn_index) -> [err, total]
    n_turns_built = 0
    for f in sorted(SESSIONS.rglob("*.jsonl")):
        records = s5_pairing.load_session_file(str(f))
        sid = s5_pairing.session_meta(records).get("id") or f.stem
        turns = s5_pairing.build_turns_from_records(records, sid, str(f))
        n_turns_built += len(turns)
        # walk records again for toolResult attribution to in-progress turn
        idx = -1
        for rec in records:
            if not isinstance(rec, dict) or rec.get("type") != "message":
                continue
            msg = rec.get("message") or {}
            role = msg.get("role")
            if role == "user":
                idx += 1
            elif role == "toolResult" and 0 <= idx < len(turns):
                key = (sid, idx)
                e = tool_err.setdefault(key, [0, 0])
                e[1] += 1
                if msg.get("isError"):
                    e[0] += 1

    def turn_ref_err(ref):
        sid, i = ref.rsplit("#", 1)
        return tool_err.get((sid, int(i)), [0, 0])

    for p in pairs:
        me, mt = turn_ref_err(p["memory_turn"])
        ne, nt = turn_ref_err(p["nomem_turn"])
        p["m2_mem_errors"], p["m2_mem_toolcalls"] = me, mt
        p["m2_nomem_errors"], p["m2_nomem_toolcalls"] = ne, nt
    m2_mem_total = sum(p["m2_mem_errors"] for p in pairs)
    m2_nomem_total = sum(p["m2_nomem_errors"] for p in pairs)
    n_pairs_with_errors = sum(1 for p in pairs
                              if p["m2_mem_errors"] or p["m2_nomem_errors"])

    # --- M4: bundle events inside the declared window ----------------------
    evs = [json.loads(l) for l in BUNDLE.open() if l.strip()]
    in_win = []
    for e in evs:
        b = e["timestamp_bucket"]
        t = datetime.fromisoformat(b[:13] + ":00:00+00:00")  # hourly bucket
        if w0 <= t <= w1:
            in_win.append(e)
    m4 = {
        "note": ("window-level only: bundle pseudonyms are opaque and the "
                 "bundle corpus (claude-code projects) is disjoint from the "
                 "S5 trial lanes, so M4 cannot be attributed to pairs; "
                 "never imputed"),
        "n_events_in_window": len(in_win),
        "raw_by_class": dict(sorted(Counter(e["class"] for e in in_win).items())),
        "n_total_bundle_events": len(evs),
    }

    # --- table (§3.1 shape) ------------------------------------------------
    cols = ["pair", "family", "mem_tokens", "nomem_tokens", "m1_token_logratio",
            "mem_wall_s", "nomem_wall_s", "m1_wall_logratio",
            "m2_mem_errors", "m2_mem_toolcalls", "m2_nomem_errors",
            "m2_nomem_toolcalls", "m3_redundant_delivered",
            "m3_redundant_available_only", "provisional"]
    lines = ["| " + " | ".join(cols) + " |",
             "|" + "---|" * len(cols)]
    for p in pairs:
        lines.append("| " + " | ".join(str(p.get(c, "not_instrumented")) for c in cols) + " |")
    (OUT / "m124-window-table.md").write_text("\n".join(lines) + "\n")

    out = {
        "row": "S4-13", "part": "(b) first M1-M4 table over the corrected window",
        "descriptive_only": True,
        "window": {"file": str(WINDOW_FILE), "start_utc": win["start_utc"],
                   "end_utc": win["end_utc"]},
        "provenance": {
            "input_manifest_sha256": sha256(INPUT_MANIFEST),
            "pairs_json_sha256": pairs_sha,
            "bundle_sha256": sha256(BUNDLE),
            "rerun_summary_generated_at": data["meta"]["generated_at"],
        },
        "M1": {
            "token_logratio": m1_tokens_all, "wall_logratio": m1_wall_all,
            "median_token_delta_pct_crosscheck": round(med_tok_pct, 3),
            "median_wall_delta_pct_crosscheck": round(med_wall_pct, 3),
            "crosscheck_target_S4_9": {"tokens": 80.739, "wall": 149.233},
            "by_family": m1_by_family,
        },
        "M2": {
            "detectable_kind": "non-zero-exit command as a task step (toolResult isError)",
            "not_detectable_kinds": ["reverted/corrected edit", "wrong-scope write",
                                     "test/CI failure", "broken build left behind"],
            "mem_errors_total": m2_mem_total, "nomem_errors_total": m2_nomem_total,
            "pairs_with_any_error": n_pairs_with_errors,
            "turns_built": n_turns_built,
        },
        "M3": {"status": "not_instrumented_this_pass",
               "reason": ("needs record-state-at-start scan + delivered-level "
                          "matching; fuzzy matching is exploratory_only per "
                          "spec and was not invented")},
        "M4": m4,
        "harness_findings": findings,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (OUT / "m124-window-summary.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps(out, indent=1, sort_keys=True))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
