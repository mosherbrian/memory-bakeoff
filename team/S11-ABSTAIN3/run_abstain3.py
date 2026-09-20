#!/usr/bin/env python3
"""S12-2 runner: BM25 abstention under the declared corpus-coverage rule.

S7-1 declare-then-run: the preregistered declaration.json (sha
06317c6fe3ec0df92bae953677ee56ba35556656ef5aba54c65b82b4d3b41b80) is read
from disk and every result row binds its bytes. The runner reads both case
sets only after the declare event, computes each row and report counter from
its own implementation of the gate's documented formulas (idf =
log(1 + (N - df + .5)/(df + .5)), all query tokens including repetitions,
document-ID tie breaking, no result when all scores are zero; coverage =
fraction of distinct content tokens with df >= min_document_frequency;
abstain exactly when coverage < threshold), writes results.jsonl and
report.json (both sets separately, whole grid, no selected threshold), then
records the run and finish events. $0, local, no LLM, no score import.
"""
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVENTS = HERE / "events.jsonl"
TOKEN = re.compile(r"[a-z0-9]+")
SETS = ("declaration", "holdout")
METRICS = (
    "irrelevant_total", "irrelevant_baseline_retrieved", "irrelevant_rejected",
    "useful_total", "baseline_useful_retrieved", "useful_retrieved",
    "useful_lost",
)


def tokens(text):
    return TOKEN.findall(text.lower())


def bm25_top1(case, retrieval):
    docs = [(d["id"], Counter(tokens(d["text"]))) for d in case["documents"]]
    lengths = [sum(c.values()) for _, c in docs]
    average = sum(lengths) / len(docs)
    if average == 0:
        return None
    df = Counter()
    for _, c in docs:
        df.update(c.keys())
    query = tokens(case["query"])
    k1, b = retrieval["k1"], retrieval["b"]
    best = None
    for (doc_id, counts), length in zip(docs, lengths):
        score = 0.0
        for term in query:
            freq = counts.get(term, 0)
            if not freq:
                continue
            idf = math.log(1 + (len(docs) - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * freq * (k1 + 1) / (
                freq + k1 * (1 - b + b * length / average))
        if best is None or (-score, doc_id) < (-best[0], best[1]):
            best = (score, doc_id)
    return best[1] if best is not None and best[0] > 0 else None


def coverage(case, rule):
    query = tokens(case["query"])
    content = sorted(set(query) - set(rule["content_stopwords"]))
    corpus = [set(tokens(d["text"])) for d in case["documents"]]
    frequencies = {t: sum(t in doc for doc in corpus) for t in content}
    supported = sum(
        1 for t in content if frequencies[t] >= rule["min_document_frequency"])
    fraction = supported / len(content) if content else 0.0
    return query, content, frequencies, fraction


def replay(case, declaration, threshold):
    query, content, frequencies, fraction = coverage(case, declaration["rule"])
    abstain = fraction < threshold
    baseline = bm25_top1(case, declaration["retrieval"])
    return {
        "query_tokens": query,
        "content_tokens": content,
        "document_frequencies": frequencies,
        "support_fraction": fraction,
        "baseline_top1": baseline,
        "decision": "abstain" if abstain else "retrieve",
        "returned_top1": None if abstain else baseline,
    }


def measurements(cases, declaration, threshold):
    out = {name: 0 for name in METRICS}
    for case in cases:
        row = replay(case, declaration, threshold)
        baseline, returned = row["baseline_top1"], row["returned_top1"]
        if case["relevant_ids"]:
            out["useful_total"] += 1
            before = baseline in case["relevant_ids"]
            after = returned in case["relevant_ids"]
            out["baseline_useful_retrieved"] += int(before)
            out["useful_retrieved"] += int(after)
            out["useful_lost"] += int(before and not after)
        else:
            out["irrelevant_total"] += 1
            out["irrelevant_baseline_retrieved"] += int(baseline is not None)
            out["irrelevant_rejected"] += int(row["decision"] == "abstain")
    return out


def now():
    return datetime.now(timezone.utc).isoformat()


def last_at():
    lines = (EVENTS).read_text().splitlines()
    return json.loads(lines[-1])["at"] if lines else None


def append(event):
    t = now()
    prev = last_at()
    while prev is not None and t <= prev:
        t = now()
    merged = {"at": t, **event}
    with EVENTS.open("a") as fh:
        fh.write(json.dumps(merged, sort_keys=True) + "\n")
    print("event:", merged["event"], merged["at"])


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def main():
    declaration_bytes = (HERE / "declaration.json").read_bytes()
    declaration = json.loads(declaration_bytes)
    declaration_sha = sha_bytes(declaration_bytes)

    cases = {}
    for name in SETS:
        data = (HERE / declaration["artifacts"][name + "_cases"]["path"]).read_bytes()
        append({"event": "read", "actor": "runner", "artifact": name + "_cases",
                "sha256": sha_bytes(data)})
        assert sha_bytes(data) == declaration["artifacts"][name + "_cases"]["sha256"]
        cases[name] = json.loads(data)["cases"]

    rows = []
    report = {"sets": {}}
    for name in SETS:
        report["sets"][name] = {"grid": []}
        for threshold in declaration["thresholds"]:
            report["sets"][name]["grid"].append({
                "threshold": threshold,
                **measurements(cases[name], declaration, threshold),
            })
        for case in cases[name]:
            for threshold in declaration["thresholds"]:
                rows.append({
                    "set": name,
                    "case_id": case["id"],
                    "threshold": threshold,
                    "declaration_sha256": declaration_sha,
                    "cases_sha256": declaration["artifacts"][name + "_cases"]["sha256"],
                    **replay(case, declaration, threshold),
                })
    results_bytes = b"".join(
        (json.dumps(r, sort_keys=True, allow_nan=False) + "\n").encode()
        for r in rows)
    report_bytes = (json.dumps(report, sort_keys=True, indent=2,
                               allow_nan=False) + "\n").encode()
    (HERE / "results.jsonl").write_bytes(results_bytes)
    (HERE / "report.json").write_bytes(report_bytes)

    append({"event": "run", "sha256": declaration_sha})
    append({"event": "finish",
            "results_sha256": sha_bytes(results_bytes),
            "report_sha256": sha_bytes(report_bytes)})
    print("rows:", len(rows))


if __name__ == "__main__":
    main()
