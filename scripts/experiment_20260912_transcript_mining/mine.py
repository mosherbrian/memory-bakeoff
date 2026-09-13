#!/usr/bin/env python3
"""Transcript mining: correction events + durable facts from Claude session JSONL.

Brian directive 2026-09-12 (via GiLMore). All LOCAL: raw transcript content
and any transcript-derived text stay in the output directory (default under
~/.local/share/memory-bakeoff/), never in the repository, never sent to any
hosted model. Only aggregate statistics leave the machine (team/ findings).

PILOT scope: the memory-bake-off* project directories only.

Usage:
    mine.py --projects-dir ~/.claude/projects \
            --project-glob '-var-home-bmosher-memory-bake-off*' \
            --out ~/.local/share/memory-bakeoff/transcript-mining/pilot-<date>

Detection is deliberately deterministic (regex + repetition), no model in
the loop: this pilot measures how far pattern classes alone get.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Records that are not operator speech, whatever they contain.
NON_OPERATOR_PREFIXES = (
    "<command-name>", "<command-message>", "<local-command",
    "caveat: the messages", "<bash-input>", "<bash-stdout>", "<bash-stderr>",
    "[request interrupted", "api error",
    # auto-generated session-continuation summaries injected as user records
    "this session is being continued",
    # conductor/system event records
    "<task-notification>",
    # a frequently-reused operator MACRO (condense-for-vault): its pasted
    # payload tail fires several correction classes; scale-up precision
    # pass found it in ~20% of the sampled events (2026-09-13)
    "condense the tool payload below",
)

# Conductor seat-dispatch templates ("fsync — watch tick:", "RETRO-1 (…"):
# dispatch voice, not the operator's.
DISPATCH_RE = re.compile(
    r"^(?:fsync|ledger|corvid|alice|assay|stratum|verity|cairn|builder|kiln|"
    r"anvil-oai|giL?More|retro-\d|team-\d|probe-|mission\b|watch tick|"
    r"collection-log|row ?\d+|signal)\b\s*[—–:(]", re.I)

CORRECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("wrong", re.compile(
        r"\b(?:that'?s|that is|this is|you'?re|you are|he'?s|she'?s|it'?s) wrong\b"
        r"|\bincorrect\b|\bnot right\b|\bnope\b|\bwrong (?:approach|direction|file|path|assumption)\b", re.I)),
    ("negation", re.compile(
        r"^\s*(?:no|nope|stop|don'?t|do not|dont|never|not)\b[,!.\s]",
        re.I)),
    ("i_said", re.compile(
        r"\bi (?:already )?said\b|\bas i (?:said|mentioned|noted)\b|\blike i said\b"
        r"|\bi told you\b|\bas mentioned\b|\bper (?:my|the) (?:last|previous|earlier)\b"
        r"|\bfor the (?:last|second|third) time\b", re.I)),
    ("env_fact_correction", re.compile(
        r"\b[\w./~@:-]{1,20}\s*,\s*not\s+[\w./~@:-]{1,20}\b", re.I)),
    ("actually", re.compile(
        r"^\s*actually\b|\bactually[,]\s|\bin fact\b|\bcorrection:\s", re.I)),
]

FACT_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("convention", re.compile(
        r"\b(?:always|never)\s+\w+"
        r"|\bconvention(?:s)?\s*(?:is|are|:)\b"
        r"|\bfrom now on\b|\bgoing forward\b"
        r"|\bwe (?:decided|agreed|settled|chose)\b"
        r"|\bremember (?:that|to)\b"
        r"|\binstead of\b|\bprefer\b|\bplease\s+always\b|\bdon'?t ever\b", re.I)),
    ("env_fact", re.compile(
        r"(?<!\w)/(?:home|var|etc|opt|mnt|usr)/[\w./@:-]+"
        r"|\b[A-Z][A-Z0-9_]{2,}=\S"
        r"|\bport \d{2,5}\b"
        r"|\bhttps?://[\w.-]+"
        r"|\b(?:runs?|running) on\b"
        r"|\bv?\d+\.\d+(?:\.\d+)?\s*(?:on|server|version)"
        r"|\bpinned (?:at|to|commit)\b", re.I)),
]

REPEAT_MIN_CHARS = 25

QUOTED_SPAN = re.compile(r'"[^"]{2,}"|[“”][^“”]{2,}[“”]')


def mask_quotes(text: str) -> str:
    """Blank out quoted spans (operator quoting a model is not an operator
    correction — the pilot's main residual false-positive class)."""
    return QUOTED_SPAN.sub(" ", text)


def normalize_for_repeat(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", "", text.lower())).strip()


def operator_texts(record: dict) -> str:
    """Extract operator-authored text from a user record; '' when none.

    Tool results, command wrappers, meta records and interrupted markers are
    not operator speech.
    """
    if record.get("type") != "user" or record.get("isMeta"):
        return ""
    content = (record.get("message") or {}).get("content")
    parts: list[str] = []
    if isinstance(content, str):
        parts.append(content)
    elif isinstance(content, list):
        parts.extend(block.get("text", "") for block in content
                     if isinstance(block, dict) and block.get("type") == "text")
    text = "\n".join(p for p in parts if p).strip()
    if not text or text.lower().startswith(NON_OPERATOR_PREFIXES):
        return ""
    if DISPATCH_RE.match(text):
        return ""
    return text


def iter_records(path: Path):
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield line_no, record


def _event_id(rel: str, line_no: int, cls: str) -> str:
    """Stable id for one mined record (corpus-private, deterministic)."""
    return "tm-" + hashlib.sha256(f"{rel}:{line_no}:{cls}".encode()).hexdigest()[:16]


def scan(projects_dir: Path, project_glob: str, out_dir: Path,
         exclude_mtime_within_minutes: int = 0) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = out_dir / "correction-events.jsonl"
    facts_path = out_dir / "durable-facts.jsonl"
    repeat_index: dict[str, list[dict]] = {}
    user_turns = 0
    files_scanned = 0
    files_excluded_open = 0
    excluded_names: list[str] = []
    scan_facts: list[dict] = []
    import time as _time
    now = _time.time()
    fresh_cutoff = now - exclude_mtime_within_minutes * 60
    with events_path.open("w", encoding="utf-8") as events_fh, facts_path.open("w", encoding="utf-8") as facts_fh:
        project_dirs = sorted(projects_dir.glob(project_glob))
        for project_dir in project_dirs:
            for path in sorted(project_dir.rglob("*.jsonl")):
                # CLOSED-SESSIONS rule (Brian, scale-up 2026-09-13): skip any
                # file still being written (modified within the cutoff).
                if exclude_mtime_within_minutes and path.stat().st_mtime > fresh_cutoff:
                    files_excluded_open += 1
                    excluded_names.append(str(path.relative_to(projects_dir)))
                    continue
                files_scanned += 1
                rel = str(path.relative_to(projects_dir))
                # Subagent JSONLs' "user" records are the ORCHESTRATOR's briefs
                # (model-authored), not operator speech — excluded from voice
                # detection, still counted for corpus shape.
                is_subagent = "/subagents/" in rel
                n_user = 0
                for line_no, record in iter_records(path):
                    text = operator_texts(record)
                    if not text:
                        continue
                    n_user += 1
                    if is_subagent:
                        continue
                    user_turns += 1
                    where = {
                        "file": rel,
                        "line": line_no,
                        "timestamp": record.get("timestamp"),
                        "session": record.get("sessionId"),
                    }
                    # correction events run on quote-masked text: the
                    # operator QUOTING a model is not the operator correcting
                    masked = mask_quotes(text)
                    for cls, pattern in CORRECTION_PATTERNS:
                        if pattern.search(masked if cls != "negation" else masked[:40]):
                            events_fh.write(json.dumps(
                                {"record_id": _event_id(rel, line_no, cls),
                                 "class": cls, "excerpt": text[:400], **where},
                                sort_keys=True) + "\n")
                    # env-fact correction variant "it's X, not Y" is covered by
                    # env_fact_correction + actually; repeats handled after scan
                    norm = normalize_for_repeat(text)
                    if len(norm) >= REPEAT_MIN_CHARS:
                        # 60-char normalized prefix: groups verbatim repeats
                        # AND trailing-addition near-repeats; 25-char floor
                        # keeps templated greetings out.
                        key = norm[:60]
                        repeat_index.setdefault(key, []).append({**where, "excerpt": text[:400]})
                    # durable facts
                    seen_cls: set[str] = set()
                    for cls, pattern in FACT_PATTERNS:
                        if cls not in seen_cls and pattern.search(text):
                            seen_cls.add(cls)
                            facts_fh.write(json.dumps(
                                {"record_id": _event_id(rel, line_no, "fact-" + cls),
                                 "class": cls, "excerpt": text[:400], **where},
                                sort_keys=True) + "\n")
                scan_facts.append({"file": rel, "user_turns": n_user,
                                   "bytes": path.stat().st_size})

    # repeated instructions: normalized text seen in >=2 distinct turns
    repeats = 0
    with events_path.open("a", encoding="utf-8") as events_fh:
        for digest, spots in repeat_index.items():
            if len(spots) < 2:
                continue
            repeats += 1
            events_fh.write(json.dumps(
                {"class": "repeated_instruction", "occurrences": len(spots),
                 "excerpt": spots[0]["excerpt"],
                 "spots": [{k: v for k, v in s.items() if k != "excerpt"} for s in spots]},
                sort_keys=True) + "\n")

    stats = {
        "project_glob": project_glob,
        "files_scanned": files_scanned,
        "files_excluded_open": files_excluded_open,
        "excluded_open_names": excluded_names,
        "exclude_mtime_within_minutes": exclude_mtime_within_minutes,
        "user_text_turns": user_turns,
        "scan_by_file": scan_facts,
        "by_project": {},
        "correction_classes": Counter(
            json.loads(line)["class"] for line in events_path.read_text().splitlines()),
        "fact_classes": Counter(
            json.loads(line)["class"] for line in facts_path.read_text().splitlines()),
        "repeated_instruction_groups": repeats,
        "outputs": {"correction_events": str(events_path), "durable_facts": str(facts_path)},
    }
    # per-project breakdown (scaling upgrade 2): first path component is
    # the project dir; counts only, never content
    per_project: dict[str, dict[str, int]] = {}
    for row in scan_facts:
        project = Path(row["file"]).parts[0]
        agg = per_project.setdefault(project, {"files": 0, "user_turns": 0})
        agg["files"] += 1
        agg["user_turns"] += row["user_turns"]
    stats["by_project"] = per_project
    stats["correction_classes"] = dict(stats["correction_classes"])
    stats["fact_classes"] = dict(stats["fact_classes"])
    (out_dir / "stats.json").write_text(json.dumps(stats, indent=2, sort_keys=True), encoding="utf-8")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--projects-dir", type=Path, required=True)
    parser.add_argument("--project-glob", default="-var-home-bmosher-memory-bake-off*")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--exclude-mtime-within-minutes", type=int, default=0,
                        help="closed-sessions rule: skip files modified within the last N minutes")
    args = parser.parse_args()
    stats = scan(args.projects_dir, args.project_glob, args.out,
                 exclude_mtime_within_minutes=args.exclude_mtime_within_minutes)
    print(json.dumps({k: v for k, v in stats.items()
                      if k not in ("scan_by_file", "outputs")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
