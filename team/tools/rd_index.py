#!/usr/bin/env python3
"""The R&D index: what we have produced, and whether any of it was used.

WHY IT IS COMPUTED AND NOT WRITTEN. Every account of this project that drifted
was hand-written prose that outlived its facts - ECOSYSTEM-MAP.md is 88 KB and
six days stale, the roadmap was lost from the working conversation while
experimentation continued, and on 2026-09-19 alone three separate instructions
were found still describing configurations that had changed days earlier. What
held, every time, was state recomputed from files. So this reads the tree and
recomputes; nothing here is maintained by hand.

WHAT IT DOES NOT DO. It does not say whether a document is any good, whether a
claim is sound, or what should happen next. Those are the Director's, written
against this index with the index as evidence. This answers only: what exists,
who wrote it, what cites what, and what nothing cites.

THE ONE JUDGEMENT IT MAKES IS DELIBERATELY CRUDE. "Shaped work" means a
document's filename appears in a sprint proposal, a sprint outline, or the
answer page - the artifacts that decide what gets done. Everything else, the
board and the queue included, is bookkeeping: a candidate card can be mentioned
a dozen times there and still never have changed a decision. This measures
CITATION, not influence: a finding can shape a sprint without its filename
appearing. Treat a zero as a question to ask, never as a verdict on the work.

    rd_index.py --scan          rebuild the index (no model, no network)
    rd_index.py --orphans       findings that never shaped a sprint or answer
    rd_index.py --dangling      references to files that are not there
    rd_index.py --summary       counts by kind, seat and week
"""
import argparse
import collections
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

TEAM = Path(os.environ.get("RD_TEAM", Path.home() / "memory-bake-off/team"))
INDEX = Path(os.environ.get("RD_INDEX", TEAM / "tools/rd-index.jsonl"))
# The artifacts that DECIDE. A citation from one of these is the only kind that
# counts as having shaped work; see the docstring on why the board does not.
DECIDES = re.compile(r"^(SPRINT-.*-(PROPOSAL|OUTLINE)|ANSWER)\.md$")
FINDING = ("EXTERNAL-", "CANDIDATE-CARD-")
MDREF = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9._/-]{3,}\.(?:md|json|py)\b")


def git_dates(paths):
    """First and last commit date per path, from ONE git walk.

    774 separate `git log` calls took longer than reading every file; one
    --name-only walk answers the same question in a single process.
    """
    first, last = {}, {}
    try:
        p = subprocess.run(
            ["git", "-C", str(TEAM), "log", "--name-only", "--format=%x00%aI"],
            capture_output=True, text=True, timeout=300)
    except Exception:                                   # noqa: BLE001
        return first, last
    date = None
    for line in p.stdout.split("\n"):
        if line.startswith("\x00"):
            date = line[1:].strip()[:10]
            continue
        name = line.strip()
        if not name or not date:
            continue
        base = os.path.basename(name)
        last.setdefault(base, date)          # log is newest-first
        first[base] = date
    return first, last


# ARTIFACTS IN SUBDIRECTORIES ARE NODES TOO. The first version indexed only
# *.md at the top of team/, and so reported that EXTERNAL-KNOWLEDGEDRIFT had
# never shaped work. Tern traced it by hand and found the opposite: the card is
# named by S7-KD-WORLDS/verdict.json, and ANSWER.md cites that verdict. The
# influence was real and travelled through an artifact this tool could not see -
# a true reading of the wrong set, which is the same shape as the check that
# reported "no HF token" while reading a lane's redirected HOME.
ARTIFACT = ("verdict.json", "design.md", "declaration.json", "check.py")


def scan():
    files = sorted(f.name for f in TEAM.iterdir()
                   if f.is_file() and f.suffix == ".md")
    arts = sorted(str(p.relative_to(TEAM))
                  for d in TEAM.iterdir() if d.is_dir() and d.name != "tools"
                  for p in d.iterdir() if p.name in ARTIFACT)
    files = files + arts
    known = set(files)
    text = {}
    for f in files:
        try:
            text[f] = (TEAM / f).read_text(errors="ignore")
        except OSError:
            text[f] = ""
    first, last = git_dates(files)

    # THE SAME FILE IS CITED THREE WAYS. A verdict writes
    # `team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md`, the board writes the bare
    # name, and some documents use the absolute path. Matching raw tokens
    # against bare-name keys silently classified the prefixed form as a
    # reference to a file that does not exist - which is how this tool reported
    # that KnowledgeDrift had never shaped work while its verdict names it
    # outright. Normalise both sides to the key before comparing.
    def norm(ref):
        r = ref.lstrip("./")
        i = r.rfind("team/")
        if i >= 0:
            r = r[i + 5:]
        return r

    refs = {f: {norm(x) for x in MDREF.findall(t)} - {f}
            for f, t in text.items()}
    inbound = collections.Counter()
    decided_by = collections.defaultdict(list)
    for src, targets in refs.items():
        decides = bool(DECIDES.match(src))
        for t in targets & known:
            inbound[t] += 1
            if decides:
                decided_by[t].append(src)

    rows = []
    for f in files:
        body = text[f]
        seat = f.split("-")[0].lower() if f[:1].isupper() else ""
        rows.append({
            "path": f,
            "bytes": len(body.encode()),
            "sha": hashlib.sha256(body.encode()).hexdigest()[:12],
            "mtime": time.strftime("%F", time.localtime((TEAM / f).stat().st_mtime)),
            "first_commit": first.get(f), "last_commit": last.get(f),
            "seat": seat,
            "is_finding": f.startswith(FINDING),
            "decides": bool(DECIDES.match(f)),
            "cites_verdict": "verdict.json" in body,
            "refs_out": sorted(refs[f] & known),
            "refs_dangling": sorted(refs[f] - known),
            "inbound": inbound[f],
            "shaped_work": len(decided_by[f]),
            "shaped_by": decided_by[f],
            # the model-filled fields, left null for the labelling pass so a
            # re-scan never silently discards them
            "kind": None, "subject": None, "evidence_sentence": None,
        })
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    tmp = INDEX.with_suffix(".tmp")
    with tmp.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    os.replace(tmp, INDEX)
    return rows


def load():
    if not INDEX.exists():
        sys.exit(f"no index at {INDEX} - run --scan first")
    return [json.loads(l) for l in INDEX.open() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    for flag in ("scan", "orphans", "paths", "hard", "dangling", "summary"):
        ap.add_argument(f"--{flag}", action="store_true")
    a = ap.parse_args()
    if not any(vars(a).values()):
        ap.print_help()
        return 0

    rows = scan() if a.scan else load()
    if a.scan:
        print(f"indexed {len(rows)} files -> {INDEX}")

    if a.orphans:
        f = sorted((r for r in rows if r["is_finding"]),
                   key=lambda r: (r["shaped_work"], r["inbound"]))
        print(f"{'shaped':>6} {'mentioned':>9}   document")
        for r in f:
            print(f"{r['shaped_work']:>6} {r['inbound']:>9}   {r['path'][:60]}")
        n = sum(1 for r in f if not r["shaped_work"])
        print(f"\nnever shaped a sprint or answer: {n} of {len(f)}")
        print("CITATION, not influence - a finding can shape work without its "
              "filename appearing. Check a few by hand before trusting it.")

    if a.paths:
        # A PATH IS A LEAD, NOT A VERDICT. Tern, 2026-09-19: "Do not generate an
        # influenced true/false field from citation counts or graph
        # reachability. A path is a lead for inspection, not proof of
        # influence." So this prints the chain and says nothing about what it
        # means - the shortest route by which a finding could have reached a
        # document that decides work, for a human to follow.
        import collections as _c
        idx = {r["path"]: r for r in rows}
        out = _c.defaultdict(list)
        for r in rows:
            for t in r["refs_out"]:
                out[t].append(r["path"])          # who cites t
        decides = {r["path"] for r in rows if r["decides"]}
        for r in sorted((r for r in rows if r["is_finding"]), key=lambda r: r["path"]):
            seen, frontier, chain = {r["path"]}, [(r["path"], [r["path"]])], None
            while frontier and not chain:
                nxt = []
                for node, path in frontier:
                    for citer in out.get(node, []):
                        if citer in seen:
                            continue
                        seen.add(citer)
                        if citer in decides:
                            chain = path + [citer]
                            break
                        nxt.append((citer, path + [citer]))
                    if chain:
                        break
                frontier = nxt
            if chain:
                print(f"{len(chain) - 1} hop  " + "  ->  ".join(chain))
            else:
                print(f"   --   {r['path']}  (no route to a deciding document)")

    if a.hard:
        # THE 20 DIFFICULT FILES, CHOSEN MECHANICALLY. Tern named the categories
        # - mixed measurement/proposal, appended corrections, supersession,
        # rejected drafts, external numbers, indirect citation chains - and
        # asked for them to be reviewed BEFORE the overnight run, so the
        # extraction instructions are repaired before they produce hundreds of
        # well-formed wrong records. Picking them by hand would bias toward
        # files I already understand; these are picked by signals in the text.
        import re as _re
        sig = {
            "supersede": _re.compile(r"SUPERSED|superseded by", _re.I),
            "correction": _re.compile(r"\bCORRECT(ION|ED)\b|\bRETRACT", _re.I),
            "rejected": _re.compile(r"\bREJECT(ED)?\b|\bnot adopted\b|\bdeclin", _re.I),
            "external-number": _re.compile(r"\b\d{1,3}\.\d+%|\barXiv|\bthey report\b", _re.I),
            "mixed": _re.compile(r"\bPROPOS|\bwe would\b", _re.I),
            "measured": _re.compile(r"\bmeasured\b|\bverdict\b|\bn=\d", _re.I),
        }
        scored = []
        for r in rows:
            try:
                t = (TEAM / r["path"]).read_text(errors="ignore")
            except OSError:
                continue
            hits = [k for k, rx in sig.items() if rx.search(t)]
            # hardest = carries several signals at once, especially a document
            # that both measures something and proposes something
            score = len(hits) + (2 if {"mixed", "measured"} <= set(hits) else 0)
            # DENSITY, NOT COUNT. Scoring raw signal counts put QUEUE.md,
            # BOARD.md, RD-THREADS.md and ECOSYSTEM-MAP.md at the top - 273 KB
            # inventories that mention everything and so trip every pattern.
            # They are hard, but they are one KIND of hard, and eleven of the
            # twenty slots would have gone to them. Density finds a
            # normal-sized document that genuinely both measures and proposes.
            kb = max(r["bytes"], 1) / 1024
            scored.append((score / (1 + kb / 10), score, r["path"], hits, kb))
        scored.sort(reverse=True)
        hubs = sorted(rows, key=lambda r: -r["bytes"])[:3]
        print("  3 inventory documents (their own kind of hard):")
        for h in hubs:
            print(f"      {h['path'][:50]:50} {h['bytes'] / 1024:>7.0f} KB")
        print("  17 by signal density:")
        seen = {h["path"] for h in hubs}
        n = 0
        for dens, sc, path, hits, kb in scored:
            if path in seen or n >= 17:
                continue
            n += 1
            print(f"      {path[:50]:50} {kb:>5.0f} KB  {','.join(hits)}")

    if a.dangling:
        bad = [(r["path"], d) for r in rows for d in r["refs_dangling"]]
        for p, d in sorted(bad)[:60]:
            print(f"{p[:48]:48}  ->  {d}")
        print(f"\n{len(bad)} reference(s) to files not in team/")

    if a.summary:
        print(f"{len(rows)} documents, "
              f"{sum(r['bytes'] for r in rows) / 1e6:.1f} MB")
        by_seat = collections.Counter(r["seat"] for r in rows if r["seat"])
        print("\nby author seat:")
        for s, n in by_seat.most_common(10):
            print(f"  {s:<22} {n:>4}")
        by_week = collections.Counter(
            r["last_commit"][:7] if r["last_commit"] else "untracked" for r in rows)
        print("\nby month last touched in git:")
        for m, n in sorted(by_week.items()):
            print(f"  {m:<22} {n:>4}")
        print(f"\nfindings: {sum(1 for r in rows if r['is_finding'])}"
              f"   citing a verdict: {sum(1 for r in rows if r['cites_verdict'])}"
              f"   unlabelled: {sum(1 for r in rows if r['kind'] is None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
