#!/usr/bin/env python3
"""S11-3 trial generator: the S7-3 generation extended mechanically.

Declared before the run (queue row S11-3, kiln-flash 2026-09-19): more
distractor families than the prior's one, longer streams than the prior's two
writes, the documented agentmemory near-neighbor shape, unfitted. Deterministic:
re-running this file rewrites trials.jsonl byte-identically (no clock, no seed,
no environment reads) - the verifier executes it against the frozen sha.

Breadth, declared here and in declaration.json before any receipt:
  3 distractor families x 11 trials = 33 distractors (prior: one shape, 32),
  13 update trials (prior: 12),
  every stream holds 4 writes (prior: 2: original, newer).

The three families are three near-neighbor relations on the S7-3 template
machinery (same 4 fact-type templates, same 8 scopes, same query form). The
original w0 is always a plain S7-3 fact: build(s, v1), query "s <object>".
Ground truth per family - near-neighbor writes are DIFFERENT FACTS, never
successors of the original, so the original must NOT be displaced:

  mailbox-rename  the near-neighbor writes name a renamed mail target of the
                  same service: subject token s -> "s-mailbox" in the text.
  ledger-amend    the near-neighbor writes are a second ledger line of the
                  same service: the object is the companion migration/rollout/
                  quota/retry line (redis->postgres, canary->blue-green,
                  synthetic->load-test, import->export).
  roster-drift    the near-neighbor writes name a joint roster of two
                  services: subject token s -> "s-sB" (sB = next scope).

Update trials carry no family: same scope, same object, value ladder over
later timestamps - genuinely newer states of the same fact, the original MUST
be displaced (else a never-superseding store scores a null; the controls show
the instrument reads both ends).

Write clocks (fixed, increasing, the prior's convention): w0 2026-08-01,
w1 2026-08-10, w2 2026-08-20, w3 2026-09-01.

Usage: python3 gen_trials.py [OUT_PATH]   (default: trials.jsonl next to this
file; writes nothing else)
"""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

SCOPES = ["delta", "fjord", "archive", "search", "reporter", "mailer",
          "catalog", "badge"]
TEMPLATES = [
    ("redis migration",
     lambda s, v, d: f"the {s} service completed the redis migration to version {v} on {d}"
     if d else f"the {s} service completed the redis migration to version {v}",
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
FAMILIES = ("mailbox-rename", "ledger-amend", "roster-drift")
OBJECT2 = {"redis migration": "postgres migration",
           "canary rollout": "blue-green rollout",
           "synthetic traffic quota": "load-test quota",
           "import utility retries": "export utility retries"}
WRITE_DATES = ("2026-08-01", "2026-08-10", "2026-08-20", "2026-09-01")

# family x 11 (s, template) combos: 3 scopes x 4 templates, last dropped.
COMBOS = [(s, TEMPLATES[i]) for i in range(4) for s in SCOPES[:3]][:-1]
# 13 update combos: the full 12 the prior used, plus one.
UPD_COMBOS = [(s, TEMPLATES[i]) for i in range(4) for s in SCOPES[:3]] \
    + [(SCOPES[3], TEMPLATES[0])]


def _ladder(v1: str) -> list:
    """Three near-neighbor values mechanically derived from the original's:
    the prior's newer value v2, the prior's other value, and v1+3 (distinct
    from v1, v2 and the other value for every template in TEMPLATES)."""
    return [str(int(v1) + 1), str(int(v1) - 2), str(int(v1) + 3)]


def _rename(text: str, s: str) -> str:
    return text.replace(f"the {s} ", f"the {s}-mailbox ", 1)


def _secondline(text: str, ft: str) -> str:
    return text.replace(ft, OBJECT2[ft], 1)


def _roster(text: str, s: str) -> str:
    sB = next(x for x in SCOPES if x != s)
    return text.replace(f"the {s} ", f"the {s}-{sB} ", 1)


def _jaccard(a: str, b: str) -> float:
    ta, tb = set(a.lower().split()), set(b.lower().split())
    return round(len(ta & tb) / len(ta | tb), 3)


def _near_text(family: str, s: str, ft: str, build, value: str) -> str:
    t = build(s, value, None)
    if family == "mailbox-rename":
        return _rename(t, s)
    if family == "ledger-amend":
        return _secondline(t, ft)
    if family == "roster-drift":
        return _roster(t, s)
    raise ValueError(f"undeclared family {family!r}")


def build_trials() -> list:
    trials = []
    for family in FAMILIES:
        for n, (s, (ft, build, query, v1, v2, v_other)) in enumerate(COMBOS):
            tid = f"dis-{family.split('-')[0]}{n:02d}-{s}"
            o_text = build(s, v1[0], v1[1])
            ladders = _ladder(v1[0])
            stream = [{"id": f"{tid}-w0", "text": o_text, "ts": WRITE_DATES[0],
                       "role": "original", "scope": s, "fact_type": ft}]
            for j, value in enumerate(ladders, 1):
                stream.append({"id": f"{tid}-w{j}",
                               "text": _near_text(family, s, ft, build, value),
                               "ts": WRITE_DATES[j], "role": "near-neighbor",
                               "scope": s, "fact_type": ft})
            trials.append({
                "trial_id": tid, "kind": "distractor", "family": family,
                "scope": s, "fact_type": ft, "query": query(s),
                "jaccard": [_jaccard(o_text, w["text"]) for w in stream[1:]],
                "stream": stream,
            })
    for n, (s, (ft, build, query, v1, v2, v_other)) in enumerate(UPD_COMBOS):
        tid = f"upd-{s}-{ft.split()[0]}"
        extras = [str(x) for x in (int(v1[0]) + 1, int(v1[0]) + 2,
                                   int(v1[0]) + 3, int(v1[0]) + 4)
                  if str(x) != v2[0]][:2]
        values = [v1[0], v2[0], *extras]
        dates = [(v1[1] if j == 0 else WRITE_DATES[j]) for j in range(4)]
        stream = []
        for j, (value, d) in enumerate(zip(values, dates)):
            stream.append({"id": f"{tid}-w{j}", "text": build(s, value, d),
                           "ts": WRITE_DATES[j],
                           "role": "original" if j == 0 else "newer",
                           "scope": s, "fact_type": ft})
        o_text = stream[0]["text"]
        trials.append({
            "trial_id": tid, "kind": "update",
            "scope": s, "fact_type": ft, "query": query(s),
            "jaccard": [_jaccard(o_text, w["text"]) for w in stream[1:]],
            "stream": stream,
        })
    return trials


def serialize(trials: list) -> str:
    return "".join(json.dumps(t) + "\n" for t in trials)


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "trials.jsonl"
    trials = build_trials()
    n_dis = sum(1 for t in trials if t["kind"] == "distractor")
    per = {f: sum(1 for t in trials if t.get("family") == f)
           for f in FAMILIES}
    n_upd = sum(1 for t in trials if t["kind"] == "update")
    if set(per.values()) != {11} or n_dis != 33 or n_upd != 13:
        print(f"FATAL: breadth wrong: {per}, {n_dis} distractors, "
              f"{n_upd} updates", file=sys.stderr)
        return 1
    if any(len(t["stream"]) != 4 for t in trials):
        print("FATAL: a stream does not hold 4 writes", file=sys.stderr)
        return 1
    out.write_text(serialize(trials))
    print(f"{out}: {n_dis} distractors {per}, {n_upd} updates, "
          f"streams of 4 writes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
