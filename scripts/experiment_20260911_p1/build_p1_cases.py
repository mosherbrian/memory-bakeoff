#!/usr/bin/env python3
"""One-time adaptation of the reviewer's STUDY-20260911-P1 case delivery
into the P1 harness contract.

For each case: reviewer-src/ (verbatim, including the reviewer's validated
verifier.py), repo/ (= WORKSPACE/), case.json {case, kind, prompt from
below the '---' marker}, records.json — the Perseus vault seeding spec:
one record per seeded conversation (message text verbatim), plus (per the
reviewer's LINEAGE map) a D2 mirror record carrying the current-decision
text from the map verbatim, and for P1-3 a staging-scoped derivative of
D1 seeded in BOTH arms so record-level supersession cannot orphan staging
(single variable preserved: arms differ only by the supersede link).

Predeclared mapping decisions (documented in LINEAGE.md):
- load-bearing conversation = Conversation 1 in every case;
- links applied at seed time (Gen102 binding_on), from_key = OLD;
- D2 mirror records are seeded in BOTH B and C (identical information; the
  dispatch's no-information-confound rule).
"""
import hashlib, json, re, shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "scripts/experiment_20260911_p1"
CASES = EXP / "cases"
SRC = Path("/var/home/bmosher/memory-bake-off/reviewer/study-20260911-P1/cases")

SELECTED = {
    "P1-1-tessellate-export": ("p1", "history-needed"),
    "P1-2-quarryline-ci": ("p2", "stale-prevention"),
    "P1-3-gullwing-deploy": ("p3", "scope-preservation"),
    "P1-4-cobalt-invoice": ("p4", "current-only-noise"),
}

# D2 mirror text, VERBATIM from each case's SEED-history LINEAGE section.
D2_MIRROR = {
    "p2": {"key": "record-p2-d2-current",
           "source_doc": "MAINTENANCE.md (2026-09-10)",
           "decision": ("maintenance runs through the scheduler service as job "
                        "`maint` via `schedulerctl run maint`; D1 is decommissioned.")},
    "p3": {"key": "record-p3-d2-current",
           "source_doc": "DEPLOY.md (2026-09-05)",
           "decision": "production ships via flux-managed GitOps."},
}
# P1-3 scope derivative: D1 sentence verbatim, scoped to staging, BOTH arms.
P3_D1_SENTENCE = ("DECISION: gullwing-deploy ships every environment — staging and "
                  "production alike — with the pull-deploy process "
                  "(scripts/pull_deploy.sh).")

MSG_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] (USER|ASSISTANT): (.*)$")


def prompt_from(md: str) -> str:
    return md.split("\n---\n", 1)[1].strip("\n")


def conversations(md: str) -> list:
    convs = []
    blocks = re.split(r"^## (Conversation \d+.*)$", md, flags=re.M)
    for i in range(1, len(blocks), 2):
        title_line, body = blocks[i], blocks[i + 1]
        title = re.sub(r"^Conversation \d+ — ?", "", title_line).strip()
        date = re.search(r"- date: (\d{4}-\d{2}-\d{2})", body)
        fence = re.search(r"```\n(.*?)```", body, re.S)
        messages, cur = [], None
        for line in (fence.group(1) if fence else "").splitlines():
            mm = MSG_RE.match(line)
            if mm:
                if cur:
                    messages.append(cur)
                ts = datetime.strptime(mm.group(1), "%Y-%m-%d %H:%M").replace(
                    tzinfo=timezone.utc)
                cur = {"role": mm.group(2).lower(), "text": mm.group(3).strip(),
                       "at": mm.group(1),
                       "epoch_ms": int(ts.timestamp() * 1000)}
            elif line.strip() and cur:
                cur["text"] += " " + line.strip()
        if cur:
            messages.append(cur)
        convs.append({"title": title,
                      "date": date.group(1) if date else None,
                      "messages": messages,
                      "verbatim_sentence": _verbatim(body)})
    return convs


def _verbatim(body: str) -> str | None:
    m = re.search(r"\*\*SEED VERBATIM[^*]*\*\*\s*\"(.*?)\"", body, re.S)
    return " ".join(m.group(1).split()) if m else None


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


manifest = {"source": str(SRC), "cases": {}}
for case_dir, (key, kind) in SELECTED.items():
    src = SRC / case_dir
    dst = CASES / case_dir
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    shutil.copytree(src, dst / "reviewer-src")
    shutil.copytree(src / "WORKSPACE", dst / "repo")
    shutil.copy2(src / "verifier.py", dst / "verifier.py")

    seed_md = (src / "SEED-history.md").read_text()
    convs = conversations(seed_md)
    records, links = [], []
    for i, c in enumerate(convs, start=1):
        records.append({
            "key": f"record-{key}-c{i}", "category": "decision",
            "kind": "conversation",
            "body": {"title": c["title"], "date": c["date"],
                     "messages": [{"role": m["role"], "at": m["at"],
                                   "text": m["text"]} for m in c["messages"]],
                    "verbatim_sentence": c["verbatim_sentence"]},
        })
    if key in D2_MIRROR:
        d2 = D2_MIRROR[key]
        records.append({
            "key": d2["key"], "category": "decision", "kind": "lineage-mirror",
            "body": {"title": "current decision (mirrors workspace doc)",
                     "source_doc": d2["source_doc"], "decision": d2["decision"]},
        })
        # link: from OLD (conversation 1) to NEW (current) — from_key=OLD
        links.append({
            "from_key": f"record-{key}-c1", "to_key": d2["key"],
            "relationship": "supersedes",
            "reason": f"STUDY-P1 lineage map ({case_dir}): current replaces D1"
                      + (" scope=production-only; staging preserved by the "
                         "d1-staging derivative" if key == "p3" else
                         " scope=all environments"),
        })
    if key == "p3":
        records.append({
            "key": "record-p3-d1-staging", "category": "decision",
            "kind": "scope-derivative",
            "body": {"title": "staging deploy strategy (scope derivative of the "
                              "2026-06-12 decision)",
                     "scope": "staging", "decision": P3_D1_SENTENCE},
        })

    (dst / "case.json").write_text(json.dumps({
        "case": case_dir, "kind": kind,
        "prompt": prompt_from((src / "PROMPT.md").read_text())}, indent=1) + "\n")
    (dst / "records.json").write_text(
        json.dumps({"records": records, "links": links}, indent=1,
                   ensure_ascii=False) + "\n")
    manifest["cases"][case_dir] = {
        "kind": kind, "key": key,
        "reviewer_PROMPT_md": sha(src / "PROMPT.md"),
        "reviewer_SEED_history_md": sha(src / "SEED-history.md"),
        "reviewer_VERIFIER_md": sha(src / "VERIFIER.md"),
        "reviewer_verifier_py": sha(src / "verifier.py"),
        "generated_case_json": sha(dst / "case.json"),
        "generated_records_json": sha(dst / "records.json"),
    }
    # verbatim preservation check: every marked sentence survives in records
    blob = json.dumps(records, ensure_ascii=False)
    for c in convs:
        if c["verbatim_sentence"]:
            assert c["verbatim_sentence"] in blob, f"{case_dir}: verbatim lost"
    print(f"adapted {case_dir} ({kind}): {len(records)} records, {len(links)} links")

# validation artifacts copied verbatim once
if (CASES / "VALIDATION").exists():
    shutil.rmtree(CASES / "VALIDATION")
shutil.copytree(SRC / "VALIDATION", CASES / "VALIDATION")
print("validation artifacts copied")
(EXP / "ADAPTATION_MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
print(f"manifest: {EXP / 'ADAPTATION_MANIFEST.json'}")
