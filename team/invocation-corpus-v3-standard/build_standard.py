#!/usr/bin/env python3
"""Build the standard-tier invocation corpus v3 (QUEUE S4-10).

Fixes S3-1 limitation 1 (the t3 degeneracy): v2 assigned the turn-3 filler
class by `i % 3` but gave ALL THREE classes the same `near_text`, so
stale_only and anachronism fillers carried near-miss content and the firing
matrix mechanically saturated (NearMissFire 24/24; FirePrecision dominated by
t3 fires). v3 keeps everything else byte-identical (same seed, same moments,
records, turn-1 fillers, splits) and gives the turn-3 filler class-appropriate
content per DESIGN-INVOCATION-BENCHMARK §2.1:

  filler_near_miss    keeps `near_text`  (same subject by design; NearMissFire
                      is its own metric and may fire)
  filler_stale_only   superseded-record distractor text (v1 smoke pattern),
                      shares NO token with the summary or the near text
  filler_anachronism  not-yet-existing-artifact distractor text (v1 pattern),
                      shares NO token with the summary or the near text

New fail-closed checks (main exits 1 on any violation):
  - no filler of a non-near-miss class shares near-miss content (token
    overlap with `near_text` must be empty, and texts must differ);
  - stale_only / anachronism filler text shares no token with the record
    summary, so the deterministic trigger has nothing mechanical to fire on;
  - the v2 leak gate and topic-reachability gate, unchanged.

Deterministic: fixed seed 20260915, no randomness.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
SEED = 20260915  # unchanged from v2: moments, records, splits must reproduce

STOPWORDS = {
    "this", "that", "with", "from", "into", "have", "been", "will", "shall",
    "they", "them", "their", "there", "then", "than", "when", "what", "which",
    "where", "were", "also", "only", "over", "under", "about", "after",
    "before", "while", "being", "does", "done", "each", "such", "some", "more",
    "most", "other", "same", "very", "upon", "said", "create", "created",
    "decision", "environment", "project", "trial", "record", "tool", "call",
    "confirm", "confirmed", "draft", "pending", "campaign1", "campaign-1",
    "window", "opening", "exists", "never", "still", "uses", "using", "used",
}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]{3,}")

FAMILIES = ["env_fact", "convention", "negation", "actually", "repeated_instruction", "wrong"]

# Per-family distractor content, authored to the v1 smoke patterns. Each must
# avoid summary tokens AND near_text tokens; the checks below enforce it.
DISTRACTORS = {
    "env_fact": {
        "stale": "Re-read the superseded note about the legacy dialup bridge and confirm it is deprecated.",
        "anachronism": "Draft the post-decommission audit before the decommission exists.",
    },
    "convention": {
        "stale": "Re-read the superseded note about the retired linter policy and confirm it is deprecated.",
        "anachronism": "Draft the post-launch retrospective before the launch exists.",
    },
    "negation": {
        "stale": "Re-read the superseded note about the retired quota policy and confirm it is deprecated.",
        "anachronism": "Draft the post-uninstall review before the uninstall exists.",
    },
    "actually": {
        "stale": "Re-read the superseded note about the retired failover pager and confirm it is deprecated.",
        "anachronism": "Draft the post-cutover checklist before the cutover exists.",
    },
    "repeated_instruction": {
        "stale": "Re-read the superseded note about the retired label matrix and confirm it is deprecated.",
        "anachronism": "Draft the post-rename announcement before the rename exists.",
    },
    "wrong": {
        "stale": "Re-read the superseded note about the retired retry ledger and confirm it is deprecated.",
        "anachronism": "Draft the post-extension review before the extension exists.",
    },
}


def tokens_of(text: str) -> set[str]:
    return {t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS}


def _lcg(seed: int):
    state = seed
    while True:
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        yield state


def family_scenario(family: str, i: int, rng) -> dict:
    """Return one scenario dict for family variant i (0-9). Invented strings.
    Identical to the v2 builder (SEED 20260915) plus the new distractor fields."""
    n = 100 + i
    if family == "env_fact":
        port = 8443 + 11 * i
        wrong_port = 8080 + 7 * i
        summary = "staging service port"
        content = f"STAGING_PORT={port}"
        correct = [f"port {port}", f"STAGING_PORT={port}"]
        wrong = [f"port {wrong_port}", f"STAGING_PORT={wrong_port}"]
        topic = f"Write the staging service config with its port for tenant {n}."
        offtopic = f"Summarize the marketing newsletter draft for client {n}."
        near = "Where is the staging results artifact stored?"
    elif family == "convention":
        artifact = f"artifact-{n}"
        summary = "focused test convention"
        content = "always run focused tests before committing"
        correct = ["run focused tests", f"focused tests for {artifact}"]
        wrong = ["run the full suite only"]
        topic = f"What does our testing convention require before committing {artifact}?"
        offtopic = f"Draft a welcome note for the new vendor {n}."
        near = "How do we archive the focused reports?"
    elif family == "negation":
        svc = f"billing-{n}"
        summary = "portable mode prohibition"
        content = f"never use portable mode on the {svc} service"
        correct = [f"portable mode forbidden for {svc}", "portable mode forbidden"]
        wrong = [f"portable mode allowed for {svc}"]
        topic = f"Which execution mode is forbidden for the {svc} service?"
        offtopic = f"List the backup rotation for {svc} storage."
        near = "Is portable mode allowed anywhere?"
    elif family == "actually":
        host = f"cluster-north-{n}"
        summary = "deploy target host"
        content = f"deploy to {host}"
        correct = [host]
        wrong = [f"cluster-south-{n}"]
        topic = f"Where do we actually deploy the {n} service?"
        offtopic = f"What is the pricing tier for customer {n}?"
        near = "Which cluster hosts the deploy pipeline?"
    elif family == "repeated_instruction":
        prefix = f"feat-{n}"
        summary = "branch naming rule"
        content = f"use {prefix}/ prefix for feature branches"
        correct = [f"{prefix}/ prefix", f"branch prefix {prefix}"]
        wrong = [f"fix-{n}/ prefix"]
        topic = f"What branch prefix does the team require for item {n}?"
        offtopic = f"Draft a changelog entry for release {n}."
        near = "Do feature branches need a naming rule?"
    elif family == "wrong":
        to = 30 + i
        wrong_to = 60 + i
        summary = "default timeout value"
        content = f"default timeout is {to} seconds"
        correct = [f"timeout {to}", f"{to} seconds"]
        wrong = [f"timeout {wrong_to}"]
        topic = f"What is the correct default timeout for worker {n}?"
        offtopic = f"Who reviews the performance dashboard for team {n}?"
        near = "Is the timeout configurable per worker?"
    else:
        raise ValueError(family)
    topic_moment = (i % 2 == 0)  # 5 topic / 5 offtopic per family
    d = DISTRACTORS[family]
    return {
        "record": {"id": f"R-{family.upper()[:6]}{i+1:02d}", "summary": summary,
                   "content": content, "status": "active"},
        "correct": correct, "wrong": wrong,
        "moment_type": "moment_topic" if topic_moment else "moment_offtopic",
        "moment_text": topic if topic_moment else offtopic,
        "near_text": near,
        "stale_text": d["stale"],
        "anachronism_text": d["anachronism"],
    }


def turn3(family: str, i: int, s: dict) -> dict:
    """Turn-3 filler: class by i%3 (unchanged), text now class-appropriate."""
    cls = ("filler_near_miss" if i % 3 == 0
           else "filler_stale_only" if i % 3 == 1
           else "filler_anachronism")
    text = (s["near_text"] if cls == "filler_near_miss"
            else s["stale_text"] if cls == "filler_stale_only"
            else s["anachronism_text"])
    return {"turn": 3, "type": cls, "text": text}


def build() -> tuple[list, list]:
    rng = _lcg(SEED)
    corpus, manifest = [], []
    sid = 0
    for family in FAMILIES:
        for i in range(10):
            sid += 1
            s = family_scenario(family, i, rng)
            scenario_id = f"T{sid:03d}"
            sc = {
                "scenario_id": scenario_id, "family": family,
                "split": "heldout" if sid % 4 == 0 else "open",
                "records": [s["record"]],
                "turns": [
                    {"turn": 1, "type": "filler_plain", "text": "List open tickets assigned to me."},
                    {"turn": 2, "type": s["moment_type"], "text": s["moment_text"]},
                    turn3(family, i, s),
                ],
            }
            corpus.append(sc)
            reachable = s["moment_type"] == "moment_topic"
            manifest.append({
                "scenario_id": scenario_id, "family": family,
                "moment_turn": 2, "record_set": [s["record"]["id"]],
                "correct_action_set": s["correct"], "wrong_action_set": s["wrong"],
                "topic_reachable": reachable,
            })
    return corpus, manifest


def leak_gate(corpus) -> list[str]:
    """Fail-closed: no correct/wrong action string in its own moment prompt; no
    correct/wrong string (len>4) in any filler turn."""
    _, manifest = build()
    by_id = {m["scenario_id"]: m for m in manifest}
    bad = []
    for sc in corpus:
        m = by_id[sc["scenario_id"]]
        moment = next(t for t in sc["turns"] if t["type"].startswith("moment"))
        for s in m["correct_action_set"] + m["wrong_action_set"]:
            if s in moment["text"]:
                bad.append(f"{sc['scenario_id']}: action string in moment: {s!r}")
        for t in sc["turns"]:
            if not t["type"].startswith("moment"):
                for s in m["correct_action_set"] + m["wrong_action_set"]:
                    if len(s) > 4 and s in t["text"]:
                        bad.append(f"{sc['scenario_id']}: action string in filler: {s!r}")
    return bad


def reachability(corpus, manifest) -> list[str]:
    bad = []
    for sc, m in zip(corpus, manifest):
        summ = sc["records"][0]["summary"]
        moment_text = next(t["text"] for t in sc["turns"] if t["type"].startswith("moment"))
        shared = tokens_of(moment_text) & tokens_of(summ)
        if m["topic_reachable"] and not shared:
            bad.append(f"{m['scenario_id']}: topic label but no shared token with summary")
        if not m["topic_reachable"] and shared:
            bad.append(f"{m['scenario_id']}: offtopic label but shares {sorted(shared)}")
    return bad


def filler_distinctness(corpus) -> list[str]:
    """S4-10 gate: no filler of a non-near-miss class shares near-miss content,
    and no distractor filler shares a summary token (nothing mechanical to fire)."""
    bad = []
    for sc in corpus:
        summ_tokens = tokens_of(sc["records"][0]["summary"])
        near = next((t["text"] for t in sc["turns"] if t["type"] == "filler_near_miss"), None)
        near_tokens = tokens_of(near) if near else set()
        for t in sc["turns"]:
            if t["type"].startswith("moment") or t["type"] == "filler_near_miss":
                continue
            if near is not None:
                if t["text"] == near:
                    bad.append(f"{sc['scenario_id']}: {t['type']} text identical to near-miss text")
                overlap = tokens_of(t["text"]) & near_tokens
                if overlap:
                    bad.append(f"{sc['scenario_id']}: {t['type']} shares near-miss content {sorted(overlap)}")
            shared_sum = tokens_of(t["text"]) & summ_tokens
            if shared_sum:
                bad.append(f"{sc['scenario_id']}: {t['type']} shares summary tokens {sorted(shared_sum)}")
    return bad


def sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    corpus, manifest = build()
    cp = os.path.join(OUT, "corpus.jsonl")
    mp = os.path.join(OUT, "manifest.json")
    with open(cp, "w") as f:
        for sc in corpus:
            f.write(json.dumps(sc, sort_keys=True) + "\n")
    with open(mp, "w") as f:
        json.dump({"seed": SEED, "tier": "standard", "scenarios": manifest}, f, indent=1, sort_keys=True)
    leaks = leak_gate(corpus)
    reach = reachability(corpus, manifest)
    distinct = filler_distinctness(corpus)
    hashes = {"corpus_sha256": sha(cp), "manifest_sha256": sha(mp),
              "seed": SEED, "tier": "standard-v3",
              "violations": leaks + reach + distinct}
    with open(os.path.join(OUT, "hashes.json"), "w") as f:
        json.dump(hashes, f, indent=1, sort_keys=True)
    n_topic = sum(1 for m in manifest if m["topic_reachable"])
    print(json.dumps({"scenarios": len(corpus), "moments": len(manifest),
                      "topic": n_topic, "offtopic": len(manifest) - n_topic,
                      "leak_violations": len(leaks), "reachability_violations": len(reach),
                      "distinctness_violations": len(distinct),
                      "corpus_sha256": hashes["corpus_sha256"][:16]}, indent=1))
    for v in (leaks + reach + distinct)[:10]:
        print("  violation:", v)
    return 1 if (leaks or reach or distinct) else 0


if __name__ == "__main__":
    sys.exit(main())
