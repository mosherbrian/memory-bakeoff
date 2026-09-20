#!/usr/bin/env python3
"""Guard: invocation-corpus topic moments must be reachable under the BINDING trigger.

F1 (S09) class: a manifest `topic_reachable: true` moment whose prompt shares no
binding `tokensOf` token with the scenario's record summaries is structurally
unfireable — a guaranteed FBMR miss. This re-derives each label from the real
trigger source (stopwords + token regex parsed out of the extension), not a
naive tokenizer, so a corpus selftest using weaker rules cannot pass it.

Usage:
  check_invocation_corpus_reachability.py [--corpus DIR] [--extension FILE]
Exit 1 = at least one label/reachability mismatch (a finding); 0 = consistent.
Known limitation: reads only `record.summary` (the trigger's topic surface);
record `content` is deliberately excluded because `topicsFromNotifyFile` never
reads it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEF_CORPUS = os.path.join(ROOT, "team", "invocation-corpus-v1")
DEF_EXT = os.path.join(ROOT, "implementer", "repo", "extensions",
                       "pi-change-trigger", "index.ts")

STOPWORDS_RE = re.compile(r"const STOPWORDS = new Set\(\[(.*?)\]\)", re.S)
TOKENS_RE = re.compile(r"match\((/[^/]+/g)\)")
TOKEN_LITERAL = r"[a-z0-9][a-z0-9-]{3,}"


def parse_trigger(path):
    """Return (stopwords, token_pattern). Fail closed on source-shape drift."""
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as exc:
        raise SystemExit(f"missing prerequisite: cannot read trigger source {path}: {exc}")
    m = STOPWORDS_RE.search(src)
    if not m:
        raise SystemExit(f"trigger source shape changed: STOPWORDS block not found in {path}")
    stop = set(re.findall(r'"([^"]+)"', m.group(1)))
    if not stop:
        raise SystemExit(f"trigger source shape changed: STOPWORDS block empty in {path}")
    tm = TOKENS_RE.search(src)
    if not tm or tm.group(1) != f"/{TOKEN_LITERAL}/g":
        raise SystemExit(
            "trigger source shape changed: tokensOf regex is not "
            f"/{TOKEN_LITERAL}/g in {path}")
    return stop, TOKEN_LITERAL


def tokens_of(text, stop):
    toks = re.findall(TOKEN_LITERAL, text.lower())
    return [t for t in toks if t not in stop]


def load_corpus(corpus_dir):
    cpath = os.path.join(corpus_dir, "corpus.jsonl")
    mpath = os.path.join(corpus_dir, "manifest.json")
    if not os.path.isfile(cpath):
        raise SystemExit(f"missing prerequisite: {cpath}")
    if not os.path.isfile(mpath):
        raise SystemExit(f"missing prerequisite: {mpath}")
    scenarios = {}
    for line in open(cpath, encoding="utf-8"):
        line = line.strip()
        if line:
            rec = json.loads(line)
            scenarios[rec["scenario_id"]] = rec
    manifest = json.load(open(mpath, encoding="utf-8"))
    labels = {s["scenario_id"]: bool(s.get("topic_reachable"))
              for s in manifest.get("scenarios", [])}
    return scenarios, labels


def check(scenarios, labels, stop):
    findings, matrix = [], []
    for sid, rec in sorted(scenarios.items()):
        topics = set()
        for r in rec.get("records", []):
            topics.update(tokens_of(r.get("summary", ""), stop))
        moment = next((t for t in rec.get("turns", [])
                       if str(t.get("type", "")).startswith("moment_")), None)
        if moment is None:
            findings.append(f"{sid}: no moment_* turn")
            continue
        matched = sorted(set(tokens_of(moment.get("text", ""), stop)) & topics)
        reachable = bool(matched)
        label = labels.get(sid)
        if label is None:
            findings.append(f"{sid}: no manifest topic_reachable label")
        elif label != reachable:
            findings.append(
                f"{sid}: manifest topic_reachable={label} but binding trigger "
                f"reachable={reachable} (matched={matched or '[]'})")
        for t in rec.get("turns", []):
            m = sorted(set(tokens_of(t.get("text", ""), stop)) & topics)
            matrix.append((sid, t.get("turn"), t.get("type"), bool(m), m))
    return findings, _check_fillers(matrix)


def _check_fillers(matrix):
    """F2 design call: off-topic moments must not fire; near-miss fires are the
    NearMissFire positive control and must not be vacuous at smoke scale."""
    findings = []
    for sid, turn, typ, fired, m in matrix:
        if typ == "moment_offtopic" and fired:
            findings.append(
                f"{sid} t{turn}: moment_offtopic fires on topic (matched={m}) — "
                "AvoidRate material is contaminated")
    near = [r for r in matrix if r[2] == "filler_near_miss"]
    if near and not any(r[3] for r in near):
        findings.append(
            "no filler_near_miss fires: NearMissFire's expected positive is "
            "vacuous at smoke scale (F2 positive control missing)")
    return findings


def self_test():
    stop = {"the", "this", "with"}
    good = {"scenario_id": "T1", "records": [{"summary": "service port"}],
            "turns": [{"type": "moment_topic", "text": "write the service config"}]}
    bad = {"scenario_id": "T2", "records": [{"summary": "signoff required"}],
           "turns": [{"type": "moment_topic", "text": "ship the queue worker rollout"}]}
    f, _ = check({"T1": good, "T2": bad}, {"T1": True, "T2": True}, stop)
    assert any(x.startswith("T2:") for x in f), f
    assert not any(x.startswith("T1:") for x in f), f
    assert check({"T1": good}, {"T1": True}, stop)[0] == []
    off = {"scenario_id": "T3", "records": [{"summary": "service port"}],
           "turns": [{"type": "moment_offtopic", "text": "write the service config"}]}
    a2, b2 = check({"T3": off}, {"T3": True}, stop)
    assert any("moment_offtopic fires" in x for x in a2 + b2), (a2, b2)
    vac = {"scenario_id": "T4", "records": [{"summary": "signoff required"}],
           "turns": [{"type": "filler_near_miss", "text": "check the database port"},
                     {"type": "moment_topic", "text": "ship the queue rollout"}]}
    a3, b3 = check({"T4": vac}, {"T4": False}, stop)
    assert any("vacuous" in x for x in a3 + b3), (a3, b3)
    s, rx = parse_trigger(DEF_EXT)
    assert "this" in s and rx == TOKEN_LITERAL, (len(s), rx)
    print("self-test: PASS")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", default=DEF_CORPUS)
    p.add_argument("--extension", default=DEF_EXT)
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args(argv)
    if a.self_test:
        return self_test()
    stop, _ = parse_trigger(a.extension)
    scenarios, labels = load_corpus(a.corpus)
    label_findings, filler_findings = check(scenarios, labels, stop)
    findings = label_findings + filler_findings
    print(f"=== {a.corpus}")
    print(f"    scenarios={len(scenarios)} findings={len(findings)}")
    for x in label_findings:
        print(f"    unreachable-topic: {x}")
    for x in filler_findings:
        print(f"    filler-fire: {x}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
