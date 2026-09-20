#!/usr/bin/env python3
"""S4-13(a) — M4 replay/calibration on the frozen verified outcome bundle.

Implements SPEC-OUTCOME-PROTOCOL.md §5.3 on team/outcome-bundle-scale-20260915
(286 events, Cairn PASS, no score import):

  §5.3.2 replay test — every event replayed through the M4 counting harness is
  counted exactly once, attributed to the right class, with the spec's
  repeated-instruction de-dup applied (repeat groups, not raw events).
  §5.3.1 calibration — class counts, confidence distribution, quoted-speech
  distribution, high-confidence banding under a DECLARED rule grounded in the
  spec's own pilot precision estimates, dedup reduction.

Fail-closed: the bundle sha256 must equal the frozen value or nothing runs.
Self-test: synthetic fixtures (duplicate id, RI group, tampered class) must be
caught by the harness before the real bundle is consumed.

Usage: m4_replay.py [--out calibration.json]
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TEAM = Path("/var/home/bmosher/memory-bake-off/team")
BUNDLE = TEAM / "outcome-bundle-scale-20260915" / "events.jsonl"
FROZEN_BUNDLE_SHA = "88f875e7a7eb94663033d4a0dc684537486266ea3d51099ad945394f50095d10"

# DECLARED high-confidence band (S4-13a; grounded in SPEC §3 M4's pilot
# estimates, since the v1 detector's own confidence field is flat 0.0 —
# see finding F1 in the receipt):
#   negation, actually           -> pilot ≈100%
#   env_fact_correction          -> pilot ≈5/7 with quoted third-party speech
#                                   the residual noise -> NOT quoted_speech
#   wrong                        -> pilot facts ≈85–90% -> in band
#   repeated_instruction         -> counted post-dedup at group level, in band
#                                   (de-dup is the spec's own anti-gaming rule)
HIGH_CONF_CLASSES = {"negation", "actually", "wrong"}
HIGH_CONF_RULE = ("class in {negation, actually, wrong}; env_fact_correction "
                  "only if NOT quoted_speech; repeated_instruction post-dedup "
                  "per group")


def is_high_conf(e):
    if e["class"] in HIGH_CONF_CLASSES:
        return True
    if e["class"] == "env_fact_correction":
        return not e["quoted_speech"]
    return False


def replay(events):
    """M4 counting harness. Returns (counts, findings).

    counts: raw per-class, high-conf per-class, RI dedup (groups), and the
    exactly-once total. findings: harness-level violations (must be empty)."""
    findings = []
    seen_ids = {}
    for e in events:
        eid = e["event_id"]
        if eid in seen_ids:
            findings.append(f"duplicate event_id: {eid[:16]}…")
        seen_ids[eid] = seen_ids.get(eid, 0) + 1

    raw = Counter(e["class"] for e in events)
    high = Counter(e["class"] for e in events if is_high_conf(e))

    ri = [e for e in events if e["class"] == "repeated_instruction"]
    groups = {}
    for e in ri:
        gid = e.get("repeat_group_id")
        if not gid:
            findings.append(f"RI event without repeat_group_id: {e['event_id'][:16]}…")
            continue
        g = groups.setdefault(gid, {"n": 0, "prefix_hashes": set()})
        g["n"] += 1
        g["prefix_hashes"].add(e.get("normalized_prefix_hash"))
    for gid, g in groups.items():
        if len(g["prefix_hashes"]) != 1:
            findings.append(f"RI group {gid[:12]}… has {len(g['prefix_hashes'])} distinct prefix hashes")

    counts = {
        "n_events": len(events),
        "n_unique_event_ids": len(seen_ids),
        "raw_by_class": dict(sorted(raw.items())),
        "high_conf_by_class": dict(sorted(high.items())),
        "ri_groups": len(groups),
        "ri_events": len(ri),
        "ri_group_sizes": sorted((g["n"] for g in groups.values()), reverse=True),
        "high_conf_total": sum(high.values()) + len(groups),
    }
    return counts, findings


def selftest():
    """§5.3.2 harness test on synthetic fixtures. Returns findings list."""
    base = {
        "schema_version": 1, "detector_version": "test", "subtype": None,
        "turn_index": 0, "timestamp_bucket": "2026-09-13T00",
        "project_pseudonym": "p", "source_session_pseudonym": "s",
        "confidence": 0.0, "correction_of_prior_same_fact": False,
        "evidence_span_length": 0, "exclusion_filters_applied": [],
        "extraction_run": "test",
    }
    ok = lambda i, c, **kw: {**base, "event_id": f"id{i}", "class": c, **kw}
    fixtures = [
        ok(1, "negation"),
        ok(2, "env_fact_correction", quoted_speech=True),   # out of band
        ok(3, "env_fact_correction", quoted_speech=False),  # in band
        ok(4, "repeated_instruction", repeat_group_id="g1", normalized_prefix_hash="h1"),
        ok(5, "repeated_instruction", repeat_group_id="g1", normalized_prefix_hash="h1"),
        ok(6, "repeated_instruction", repeat_group_id="g1", normalized_prefix_hash="h1"),
    ]
    counts, findings = replay(fixtures)
    if counts["raw_by_class"] != {"env_fact_correction": 2, "negation": 1,
                                  "repeated_instruction": 3}:
        findings.append(f"selftest: raw recount wrong: {counts['raw_by_class']}")
    if counts["high_conf_by_class"] != {"env_fact_correction": 1, "negation": 1}:
        findings.append(f"selftest: high-conf band wrong: {counts['high_conf_by_class']}")
    if counts["high_conf_total"] != 3:  # negation + env(non-quoted) + 1 RI group
        findings.append(f"selftest: high_conf_total wrong: {counts['high_conf_total']}")
    if counts["ri_groups"] != 1 or counts["ri_events"] != 3:
        findings.append("selftest: RI dedup wrong")

    dup = fixtures + [dict(fixtures[0])]
    dup_counts, dup_findings = replay(dup)
    if dup_counts["n_unique_event_ids"] != 6 or not any("duplicate" in f for f in dup_findings):
        findings.append("selftest: duplicate id not caught")

    tampered = [dict(fixtures[0], **{"class": "actually"})]
    t_counts, _ = replay(tampered)
    if t_counts["raw_by_class"] != {"actually": 1}:
        findings.append("selftest: class attribution not driven by event content")
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(TEAM / "s4-13-outcome" / "calibration.json"))
    args = ap.parse_args()

    sha = hashlib.sha256(BUNDLE.read_bytes()).hexdigest()
    if sha != FROZEN_BUNDLE_SHA:
        sys.exit(f"FATAL: bundle sha {sha} != frozen {FROZEN_BUNDLE_SHA}")

    st = selftest()
    if st:
        sys.exit("FATAL: harness self-test failed:\n" + "\n".join(st))

    events = [json.loads(l) for l in BUNDLE.open() if l.strip()]
    counts, findings = replay(events)
    gate = json.loads((BUNDLE.parent / "gate-receipt.json").read_text())
    if not gate.get("gate_pass"):
        sys.exit("FATAL: bundle gate-receipt is not PASS")

    conf_dist = dict(Counter(e["confidence"] for e in events))
    quoted_by_class = dict(Counter(e["class"] for e in events if e["quoted_speech"]))
    buckets = sorted(e["timestamp_bucket"] for e in events)
    out = {
        "row": "S4-13", "part": "(a) M4 replay/calibration",
        "bundle": str(BUNDLE), "bundle_sha256": sha,
        "gate_pass": gate["gate_pass"], "gate_findings": gate["gate_findings"],
        "excluded_class_counts": gate["excluded_class_counts"],
        "detector_version": sorted({e["detector_version"] for e in events}),
        "extraction_run": sorted({e["extraction_run"] for e in events}),
        "high_conf_rule": HIGH_CONF_RULE,
        "replay_counts": counts,
        "calibration": {
            "confidence_distribution": {str(k): v for k, v in sorted(conf_dist.items())},
            "quoted_speech_by_class": quoted_by_class,
            "quoted_speech_total": sum(quoted_by_class.values()),
            "distinct_projects": len({e["project_pseudonym"] for e in events}),
            "bucket_first": buckets[0], "bucket_last": buckets[-1],
            "distinct_buckets": len(set(buckets)),
            "precision_beside_count_pilot": {
                "source": "team/TRANSCRIPT-MINING-PILOT.md via SPEC §3 M4",
                "negation": "~1.00", "actually": "~1.00",
                "env_fact_correction": "~5/7 (quoted third-party speech = residual noise)",
                "wrong/facts": "~0.85-0.90",
            },
        },
        "harness_findings": findings,
        "selftest": "PASS (6 fixtures: exactly-once, RI dedup 3->1, band edges, duplicate catch, class attribution)",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps(out, indent=1, sort_keys=True))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
