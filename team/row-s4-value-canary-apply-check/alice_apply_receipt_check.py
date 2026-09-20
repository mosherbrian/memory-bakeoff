#!/usr/bin/env python3
"""Alice second-seat check of Assay's S4 value-canary APPLY RECEIPT.

Independent of `value_canary_apply_check.py` (Assay's): this driver
  A. re-hashes the live bases, the sealed guarded files and both diffs and
     compares them to the apply receipt and to the rev-2 note;
  B. applies each diff to a temp copy and compares bytes to the sealed guarded
     file (the receipt's own claim);
  C. probes the rev-2 detector/redaction semantics on synthetic entries, incl.
     the uppercase boundary Alice raised against rev 1 and the user/non-user
     `draft_id`-word asymmetry.

Read-only over the source trees; writes only under a temp dir. No packet text.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

IMPL = Path("/var/home/bmosher/memory-bake-off/implementer")
REPO = IMPL / "repo"
DSH2 = IMPL / "repo-glm-dsh2"
HERE = Path(__file__).resolve().parent
VC = DSH2 / "scripts" / "verify-20260913-assay-s4-value-canary"

JOBS = {
    "builder": {
        "diff": VC / "s4-value-canary-builder.diff",
        "root": REPO,
        "rel": "scripts/experiment_20260911_trial/build_s4_packets.py",
        "guarded": VC / "guarded" / "build_s4_packets.py",
        "canonical": VC / "canonical" / "build_s4_packets.py",
    },
    "scanner": {
        "diff": VC / "s4-value-canary-scanner.diff",
        "root": DSH2,
        "rel": "scripts/verify-20260912-assay-row1/packet_leak_scan.py",
        "guarded": VC / "guarded" / "packet_leak_scan.py",
        "canonical": VC / "canonical" / "packet_leak_scan.py",
    },
}

# Expected from the apply receipt / rev-2 note (prefixes as published).
RECEIPT_LIVE = {
    "builder": "6616c48e00e54722d111419eac6bf0c1fd7457161979e664ab3f2f046e08bdbb",
    "scanner": "1fc8e6c9af8e53803a80c7926ee6fc018ba3cb38ed6332f4f89fd1c552d1bb71",
}
RECEIPT_GUARDED = {
    "builder": "568face44b9e9d96e19e5011aa91e03ce5f217c5862a071e57e281294fd5caf4",
    "scanner": "33aa07cf13d9cce8abf730a7f6196ffaa66634cab2351677523c1b45f501d0f9",
}
NOTE_REV2_DIFF_PREFIX = {"builder": "ba907167", "scanner": "7498e3a4"}
NOTE_REV1_DIFF_PREFIX = {"builder": "557cb5bb", "scanner": "60c7c14e"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    out = {"apply_receipt_reproduction": {}, "boundary": {}, "findings": []}

    # ---- A/B: hashes + temp apply ----
    for name, j in JOBS.items():
        live = j["root"] / j["rel"]
        row = {
            "live_sha256": sha(live),
            "canonical_sha256": sha(j["canonical"]),
            "guarded_sha256": sha(j["guarded"]),
            "diff_sha256": sha(j["diff"]),
            "live_matches_receipt": sha(live) == RECEIPT_LIVE[name],
            "canonical_matches_live": sha(j["canonical"]) == sha(live),
            "guarded_matches_receipt": sha(j["guarded"]) == RECEIPT_GUARDED[name],
            "diff_is_rev2": sha(j["diff"]).startswith(NOTE_REV2_DIFF_PREFIX[name]),
            "diff_is_rev1": sha(j["diff"]).startswith(NOTE_REV1_DIFF_PREFIX[name]),
        }
        cp = subprocess.run(["git", "apply", "--check", str(j["diff"])],
                            cwd=str(j["root"]), capture_output=True, text=True)
        row["apply_check_rc"] = cp.returncode
        with tempfile.TemporaryDirectory(prefix="alice-apply-") as td:
            t = Path(td)
            (t / j["rel"]).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(live, t / j["rel"])
            subprocess.run(["git", "init", "-q"], cwd=str(t), check=True)
            ap = subprocess.run(["git", "apply", str(j["diff"])], cwd=str(t),
                                capture_output=True, text=True)
            row["temp_apply_rc"] = ap.returncode
            row["temp_applied_equals_guarded"] = (
                ap.returncode == 0 and sha(t / j["rel"]) == sha(j["guarded"]))
        out["apply_receipt_reproduction"][name] = row

    # ---- C: semantics on synthetic packets ----
    canon_sc = load_module(JOBS["scanner"]["canonical"], "canon_scanner")
    guard_sc = load_module(JOBS["scanner"]["guarded"], "guard_scanner")
    canon_bd = load_module(JOBS["builder"]["canonical"], "canon_builder")
    guard_bd = load_module(JOBS["builder"]["guarded"], "guard_builder")

    cases = {
        # name: (role, text)
        "nonuser_value_lower": ("assistant", "leak draft-abc123 value"),
        "nonuser_value_upper": ("assistant", "leak draft-ABC123 value"),
        "nonuser_word_only": ("assistant", "the word draft_id appears"),
        "user_value_upper": ("user", "my note draft-ABC123 value"),
        "user_word_only": ("user", "the word draft_id appears"),
        "clean_nonuser": ("assistant", "nothing sensitive"),
        "redacted_nonuser": ("assistant", None),  # marker set below
    }

    def entry(role: str, text):
        if text is None:
            return {"message": {"role": role, "content": "[memory activity: redacted]"},
                    "marker": True}
        return {"message": {"role": role, "content": text}}

    with tempfile.TemporaryDirectory(prefix="alice-boundary-") as td:
        t = Path(td)
        for cname, (role, text) in cases.items():
            e = entry(role, text)
            pkt = {"entries": [e]}
            p = t / f"turn-{cname}.json"
            p.write_text(json.dumps(pkt))
            can = canon_sc.scan_packet(p)
            gua = guard_sc.scan_packet(p)
            out["boundary"][cname] = {
                "role": role,
                "canonical_flagged": bool(can),
                "guarded_flagged": bool(gua),
                "canonical_redacts_memory_traffic": (
                    canon_bd.is_memory_traffic(e) if role != "user" else None),
                "guarded_redacts_memory_traffic": (
                    guard_bd.is_memory_traffic(e) if role != "user" else None),
                "guarded_redacts_draft_secret": guard_bd.user_entry_has_draft_secret(e),
            }

    # ---- findings (judgement, kept explicit) ----
    for name, j in JOBS.items():
        if not out["apply_receipt_reproduction"][name]["diff_is_rev2"]:
            out["findings"].append(f"{name}: on-disk diff is not the published rev-2 hash")
        if not out["apply_receipt_reproduction"][name]["temp_applied_equals_guarded"]:
            out["findings"].append(f"{name}: applied bytes != sealed guarded file")

    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
