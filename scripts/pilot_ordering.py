#!/usr/bin/env python3
"""PILOT - NOT EVIDENCE. Does presentation order change current-state accuracy?

Substrate: LongMemEval oracle, question_type == 'knowledge-update'. Each item has
exactly two sessions: the earlier states a value, the later supersedes it, and the
gold answer is the later one. Perfect retrieval by construction.

Manipulation: the two sessions are shown STALE_FIRST (chronological, as the
dataset ships them) or CURRENT_FIRST (reversed). Nothing else differs - same
tokens, same content, same question.

Why a HALF: running these items unfrozen exposes them. Anything measured here can
only be exploratory, because the rule that judges it will have been chosen after
seeing it - that is exactly the Gen114 error. So the pilot takes a seeded random
half and the other half is HELD OUT, untouched, for a preregistered run whose
rule is fixed before anyone looks.

Scoring here is the crude one on purpose: does the gold string appear in the
answer. Good enough to see whether an effect exists; not good enough to publish.
"""
import json, random, sys, urllib.request, hashlib, datetime
from pathlib import Path

SRC = Path("/home/bmosher/.cache/huggingface/hub/datasets--xiaowu0162--longmemeval-cleaned/"
           "snapshots/98d7416c24c778c2fee6e6f3006e7a073259d48f/longmemeval_oracle.json")
ENDPOINT = "http://strix-halo.local:8080/v1/chat/completions"
READER = "qwen3.6-35b-vulkan-nothink"
SPLIT_SEED = 20260907
OUT = Path("research/pilot_ordering")


def items():
    d = json.loads(SRC.read_text())
    ku = [x for x in d if x["question_type"] == "knowledge-update"
          and not x["question_id"].endswith("_abs")]
    return [x for x in ku
            if [sum(1 for t in s if t.get("has_answer")) for s in x["haystack_sessions"]] == [1, 1]]


def split(all_items):
    ids = sorted(x["question_id"] for x in all_items)
    rng = random.Random(SPLIT_SEED)
    rng.shuffle(ids)
    half = len(ids) // 2
    return set(ids[:half]), set(ids[half:])


def render(item, order, show_dates=True):
    """order: 'stale_first' ships as-is; 'current_first' reverses the two sessions.

    show_dates=False removes the date labels. GLM 5.3 found the first pass left
    them in, so reversing the order still left the reader an explicit recency cue
    and the manipulation was 'position vs a stated date', not position alone.
    """
    pairs = list(zip(item["haystack_dates"], item["haystack_sessions"]))
    if order == "current_first":
        pairs = pairs[::-1]
    blocks = []
    for i, (date, sess) in enumerate(pairs, 1):
        turns = "\n".join(f"{t['role'].upper()}: {t['content']}" for t in sess)
        head = f"=== conversation on {date} ===" if show_dates else f"=== conversation {i} ==="
        blocks.append(f"{head}\n{turns}")
    lead = ("Below are past conversations between a user and an assistant, each with "
            "its date.\n\n" if show_dates else
            "Below are past conversations between a user and an assistant.\n\n")
    return (lead + "\n\n".join(blocks) +
            f"\n\n=== question ===\n{item['question']}\n\n"
            "Answer with the value that is true NOW, as of the most recent "
            "conversation. Reply with the value only.")


def ask(prompt):
    body = json.dumps({"model": READER,
                       "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0, "seed": 0,
                       "max_tokens": 128, "stream": False}).encode()
    req = urllib.request.Request(ENDPOINT, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        raw = r.read()
    return raw


def hit(gold, answer):
    g, a = str(gold).lower(), answer.lower()
    if g.strip(" .") in a:
        return True
    import re
    keys = re.findall(r"[\d][\d,:.]*", g)
    return bool(keys) and all(k in a for k in keys)


def main():
    show_dates = "--no-dates" not in sys.argv
    all_items = items()
    pilot_ids, heldout_ids = split(all_items)
    pilot = [x for x in all_items if x["question_id"] in pilot_ids]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = OUT / (stamp + ("" if show_dates else "-nodates"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "HELD_OUT_IDS.json").write_text(json.dumps(
        {"note": "NEVER run these in an exploratory pass; they are the preregistered set",
         "split_seed": SPLIT_SEED, "held_out": sorted(heldout_ids),
         "pilot": sorted(pilot_ids)}, indent=2))
    journal = (out / "journal.jsonl").open("a")
    rows = []
    for i, item in enumerate(pilot, 1):
        for order in ("stale_first", "current_first"):
            prompt = render(item, order, show_dates)
            raw = ask(prompt)
            journal.write(json.dumps({"question_id": item["question_id"], "order": order,
                                      "show_dates": show_dates,
                                      "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                                      "raw_b64": raw.decode("utf-8", "replace")}) + "\n")
            journal.flush()
            ans = json.loads(raw)["choices"][0]["message"]["content"].strip()
            ok = hit(item["answer"], ans)
            rows.append({"question_id": item["question_id"], "order": order,
                         "gold": item["answer"], "answer": ans, "hit": ok})
            print(f"[{i:3d}/{len(pilot)}] {item['question_id']:>12} {order:>13} "
                  f"{'HIT ' if ok else 'MISS'} gold={item['answer']!r:40.40} got={ans!r:50.50}",
                  flush=True)
    (out / "rows.json").write_text(json.dumps(rows, indent=2))
    sf = [r for r in rows if r["order"] == "stale_first"]
    cf = [r for r in rows if r["order"] == "current_first"]
    n = len(sf)
    a, b = sum(r["hit"] for r in sf), sum(r["hit"] for r in cf)
    by = {}
    for r in rows:
        by.setdefault(r["question_id"], {})[r["order"]] = r["hit"]
    flip_sf_only = sum(1 for v in by.values() if v["stale_first"] and not v["current_first"])
    flip_cf_only = sum(1 for v in by.values() if v["current_first"] and not v["stale_first"])
    summary = {"show_dates": show_dates,
               "n_items": n, "stale_first_hits": a, "current_first_hits": b,
               "discordant_stale_first_only": flip_sf_only,
               "discordant_current_first_only": flip_cf_only,
               "note": "PILOT. Exploratory. Crude string scorer. Held-out half untouched."}
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2))
    print("\n" + json.dumps(summary, indent=2))
    print("\nheld out for the preregistered run:", len(heldout_ids), "items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
