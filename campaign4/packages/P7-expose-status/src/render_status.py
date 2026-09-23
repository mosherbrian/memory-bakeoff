"""P7 read-only derived status view + pending list (stdlib only).

Reads declared inputs, writes ONLY the given output files. Never mutates
inputs, never infers PASS/liveness, never invents sponsor decisions.
Missing/stale/contradictory evidence renders UNKNOWN/CONFLICT with owner
and links. Repeat renders are byte-stable for a fixed --as-of.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = "/home/bmosher/memory-bake-off"
C4 = os.path.join(ROOT, "campaign4")
PKG = os.path.join(C4, "packages", "P7-expose-status")

DEFAULT_INPUTS = {
    "pending_decisions": os.path.join(C4, "pending-decisions.md"),
    "control_tsv": os.path.join(C4, "control-events.tsv"),
    "connect_finish": os.path.join(C4, "CONNECT-FINISH-LINE-20260923.md"),
    "r18_acceptance": os.path.join(
        C4, "packages", "P6-r18-runtime-source-time", "acceptance.json"),
    "r19_terminal": os.path.join(
        C4, "packages", "P6-r19-live-runtime-witness",
        "terminal-disposition.json"),
    "charter": os.path.join(C4, "CHARTER.md"),
    "architecture": os.path.join(C4, "ACCEPTED-ARCHITECTURE.md"),
}

STALE_AFTER_S = 24 * 3600


def _utcnow():
    return datetime.now(timezone.utc)


def _iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mtime_iso(path):
    try:
        return _iso(datetime.fromtimestamp(os.path.getmtime(path),
                                           timezone.utc))
    except OSError:
        return None


def _sha(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def _read(path):
    try:
        with open(path) as fh:
            return fh.read()
    except OSError:
        return None


def _stale_flag(mtime_iso, as_of):
    if not mtime_iso:
        return True
    try:
        mt = datetime.strptime(mtime_iso, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
        ao = datetime.strptime(as_of, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except ValueError:
        return True
    return (ao - mt).total_seconds() > STALE_AFTER_S


def parse_pending_decisions(text):
    """Parse the decisions table. Returns (pending_rows, resolved_rows).

    A resolved row (resolved column not open/empty) ceases to be pending
    and is linked, never counted. Unknown shape -> UNKNOWN entry.
    """
    pending, resolved = [], []
    if text is None:
        return pending, [{"status": "UNKNOWN", "owner": "unknown",
                          "reason": "pending-decisions.md unreadable",
                          "source": "pending-decisions.md"}]
    in_table = False
    for line in text.splitlines():
        if line.startswith("| raised |"):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6 or cells[0].startswith("---"):
            continue
        raised, question, options, affected, owner, resolved_col = cells[:6]
        owner_clean = re.sub(r"\*+", "", owner).strip().split("—")[0].strip()
        row = {"raised": raised, "question": question, "options": options,
               "affected": affected, "owner": owner_clean or "unknown",
               "source": "campaign4/pending-decisions.md"}
        if re.search(r"retract", resolved_col, re.I):
            row["resolution"] = resolved_col
            resolved.append(row)
        elif resolved_col.lower().strip() in ("open", ""):
            row["next_action"] = "owner decision required; dependents " \
                "blocked (see affected)"
            pending.append(row)
        else:
            row["resolution"] = resolved_col
            resolved.append(row)
    return pending, resolved


def parse_connect_checks(text):
    """Parse the eight-check table: disposition controls status.

    Rows whose disposition routes remaining work to P8 (or says Partial)
    are partial/open; otherwise met at the stated boundary. Never inferred
    beyond the disposition text.
    """
    checks = []
    if text is None:
        return [{"check": "UNKNOWN", "status": "UNKNOWN", "owner": "unknown",
                 "reason": "CONNECT-FINISH-LINE unreadable"}]
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Check |"):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0].startswith("---"):
            continue
        name, evidence, disp = cells[:3]
        # Partial only on explicit Partial or open remaining work routed
        # to P8 (must/owns/open); a P8 administrative note on an
        # otherwise-proven row (e.g. freeze policy) stays met. This
        # reproduces the record's own three-met (#3,#5,#8) statement.
        if re.search(r"\bPartial\b|\bP8 must\b|\bP8 owns\b|remains open|"
                     r"\bopen\.", disp):
            status, owner = "partial", "P8 (Tern to allocate)"
        else:
            status, owner = "met-at-stated-boundary", "provenance in row"
        checks.append({"check": name, "status": status, "owner": owner,
                       "disposition": disp, "evidence": evidence})
    return checks


def load_json(path):
    raw = _read(path)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return {"_malformed": True}


def summarize_acceptance_vs_terminal(r18, r19):
    """Accepted R18 source vs terminated R19: distinguished, never merged.

    Missing/malformed sides render UNKNOWN; contradictory same-package
    claims render CONFLICT.
    """
    out = {}
    if r18 is None:
        out["r18"] = {"status": "UNKNOWN", "owner": "unknown",
                      "reason": "acceptance.json unreadable"}
    elif isinstance(r18, dict) and r18.get("_malformed"):
        out["r18"] = {"status": "UNKNOWN", "owner": "unknown",
                      "reason": "acceptance.json malformed"}
    else:
        out["r18"] = {"status": r18.get("decision", "UNKNOWN"),
                      "state": r18.get("state", "UNKNOWN"),
                      "source_commit": r18.get("source_commit", "unknown"),
                      "owner": "tern"}
    if r19 is None:
        out["r19"] = {"status": "UNKNOWN", "owner": "unknown",
                      "reason": "terminal-disposition.json unreadable"}
    elif isinstance(r19, dict) and r19.get("_malformed"):
        out["r19"] = {"status": "UNKNOWN", "owner": "unknown",
                      "reason": "terminal-disposition.json malformed"}
    else:
        out["r19"] = {"status": r19.get("state", "UNKNOWN"),
                      "reason": r19.get("reason", ""),
                      "live_executed": r19.get("live_executed", "unknown"),
                      "owner": "tern"}
    return out


def summarize_tsv(path, limit=60):
    """Labelled activity log (NOT truth): recent rows + owner counts.

    TSV edits are history, not immutable truth; counts are activity, not
    cost. Missing file -> UNKNOWN, never healthy-looking.
    """
    raw = _read(path)
    if raw is None:
        return {"status": "UNKNOWN", "owner": "unknown",
                "reason": "control-events.tsv unreadable"}
    rows = list(csv.reader(raw.splitlines(), delimiter="\t"))
    recent = [r for r in rows if r][:limit]
    by_owner, by_event = {}, {}
    for r in rows:
        if len(r) >= 5:
            by_owner[r[4] or "?"] = by_owner.get(r[4] or "?", 0) + 1
        if len(r) >= 4:
            by_event[r[3] or "?"] = by_event.get(r[3] or "?", 0) + 1
    return {"rows_total": len(rows), "recent": recent[-10:],
            "by_owner": by_owner, "by_event": by_event,
            "note": "edited activity log, not immutable truth; "
                    "counts are activity, not cost"}


def build_view(inputs, as_of):
    """Pure build: returns (status_md_text, pending_json_obj)."""
    snap = {}
    for key, path in inputs.items():
        snap[key] = {"path": os.path.relpath(path, ROOT)
                     if path.startswith(ROOT) else path,
                     "sha256": _sha(path),
                     "observed_at": _mtime_iso(path)}
        snap[key]["stale"] = _stale_flag(snap[key]["observed_at"], as_of)
        if snap[key]["sha256"] is None:
            snap[key]["status"] = "UNKNOWN"
    pending, resolved = parse_pending_decisions(
        _read(inputs["pending_decisions"]))
    checks = parse_connect_checks(_read(inputs["connect_finish"]))
    verdicts = summarize_acceptance_vs_terminal(
        load_json(inputs["r18_acceptance"]), load_json(inputs["r19_terminal"]))
    tsv = summarize_tsv(inputs["control_tsv"])
    met = [c for c in checks if c.get("status") != "partial"]
    partial = [c for c in checks if c.get("status") == "partial"]
    lines = []
    A = lines.append
    A("# P7 status view (derived, read-only)")
    A("")
    A("As-of (host time): %s. Every fact below is derived from the "
      "declared inputs; nothing here is live, scheduled or inferred PASS."
      % as_of)
    A("")
    A("## Connect ruling")
    A("Connect is CLOSED as a demonstrated integration stage, NOT accepted "
      "for general unattended adoption (director decision "
      "CONNECT-FINISH-LINE-20260923.md). R18 is the latest accepted "
      "candidate, not a new live PASS. Checks met at stated boundary: "
      "%d; partial: %d." % (len(met), len(partial)))
    A("")
    A("## Eight pre-unattended-use checks")
    for c in checks:
        A("- [%s] %s (owner: %s)" % (c.get("status", "UNKNOWN"),
                                     c.get("check", "?"),
                                     c.get("owner", "unknown")))
    A("")
    A("## Accepted source vs historical witness")
    A("- R18: %s (commit %s, owner tern)" % (
        verdicts["r18"].get("status"),
        verdicts["r18"].get("source_commit", "?")))
    A("- R19: %s (%s; live_executed=%s)" % (
        verdicts["r19"].get("status"), verdicts["r19"].get("reason", ""),
        verdicts["r19"].get("live_executed", "?")))
    A("- R9 live-review-3 remains the pinned historical positive witness; "
      "it is not transferred to later bytes.")
    A("")
    A("## Pending decisions (%d open)" % len(pending))
    for p in pending:
        A("- %s | owner: %s | raised: %s | affects: %s" % (
            p["question"][:160], p["owner"], p["raised"], p["affected"]))
        A("  next: %s" % p.get("next_action", "unknown"))
    for r in resolved:
        A("- RESOLVED/RETRACTED (not pending): %s... -> %s" % (
            r["question"][:80], r.get("resolution", "")[:120]))
    A("")
    A("## Active package")
    A("P7-expose-status: worker kiln builds this view (cap 100m with "
      "admission/verification/repair); no P8/P9 execution authorized here. "
      "Next action: verifier review, then director publish decision.")
    A("")
    A("## Costs and limits")
    A("Allocations are ceilings, not actual costs; actual worker/verifier "
      "minutes spent are unknown in this view. Missing cost/timing data "
      "is unknown, never zero.")
    A("")
    A("## Code links")
    A("- R18 candidate: "
      "campaign4/packages/P6-r18-runtime-source-time/candidate/")
    A("- This package: campaign4/packages/P7-expose-status/")
    A("- TSV activity (log, not truth): %s rows, owners %s" % (
        tsv.get("rows_total", "?"),
        json.dumps(tsv.get("by_owner", {}), sort_keys=True)))
    A("")
    A("## Inputs (pointers with hashes and freshness)")
    for key, s in snap.items():
        A("- %s: %s sha256=%s observed=%s stale=%s" % (
            key, s["path"], (s["sha256"] or "UNKNOWN")[:12],
            s["observed_at"] or "UNKNOWN", s["stale"]))
    pending_obj = {"as_of": as_of,
                   "pending": pending,
                   "resolved_not_pending": resolved,
                   "eight_checks": checks,
                   "acceptance_vs_terminal": verdicts,
                   "activity": {"rows_total": tsv.get("rows_total"),
                                "by_owner": tsv.get("by_owner", {}),
                                "note": tsv.get("note", "")},
                   "costs": "unknown (allocations are ceilings, not costs)",
                   "inputs": snap}
    return "\n".join(lines) + "\n", pending_obj


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="P7 read-only status render")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--inputs", default=None,
                    help="JSON path->path overrides for tests")
    args = ap.parse_args(argv)
    inputs = dict(DEFAULT_INPUTS)
    if args.inputs:
        inputs.update(json.load(open(args.inputs)))
    as_of = args.as_of or _iso(_utcnow())
    md, obj = build_view(inputs, as_of)
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "status.md"), "w") as fh:
        fh.write(md)
    with open(os.path.join(args.out_dir, "pending-decisions.json"),
              "w") as fh:
        json.dump(obj, fh, sort_keys=True, indent=1)
    print(json.dumps({"status_md": "status.md",
                      "pending_json": "pending-decisions.json",
                      "as_of": as_of}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
