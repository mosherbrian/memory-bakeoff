#!/usr/bin/env python3
"""Gen35 preflight: prove the retirement flag is the only thing that changes.

Unrelated synthetic domain only, run on the patched build in both arms plus the
unpatched pinned build as the upstream reference. Every check is fail-closed: a
check that cannot be evaluated raises rather than returning a plausible value.
"""
from __future__ import annotations

import argparse, importlib.util, json, os, sys, tempfile, time
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
loader = SourceFileLoader("g13", str(ROOT / "scripts/run_agentmemory_gen13.py"))
spec = importlib.util.spec_from_loader("g13", loader)
g13 = importlib.util.module_from_spec(spec)
loader.exec_module(g13)

PATCHED = ROOT / "external/agentmemory-gen35"
UPSTREAM = ROOT / "external/agentmemory"
FLAG = "AGENTMEMORY_EXPERIMENT_DISABLE_AUTO_SUPERSESSION"
PROJECT = "gen35-preflight"

# Unrelated synthetic domain, no fixture vocabulary. The first pair straddles
# the >0.7 lexical threshold (two-character difference); the second pair does not.
ABOVE = [
    ("S001", "Greenhouse bench alpha humidity target measured 55 percent."),
    ("S002", "Greenhouse bench alpha humidity target measured 62 percent."),
]
BELOW = [
    ("S003", "The orchard irrigation controller runs a dawn cycle on weekdays."),
    ("S004", "Seedling trays use a coarse perlite blend for drainage."),
]


def rows_of(base: str, agent: str) -> list[dict]:
    payload = g13.isolated_rows(base, agent)
    rows = payload.get("results") or payload.get("memories")
    if rows is None:
        raise SystemExit(f"memory listing returned no rows key: {sorted(payload)}")
    return [{"id": m.get("id"), "sourceObservationIds": m.get("sourceObservationIds"),
             "isLatest": m.get("isLatest"), "version": m.get("version"),
             "parentId": m.get("parentId"), "supersedes": m.get("supersedes"),
             "content": (m.get("content") or "")[:70]} for m in rows]


def arm(tree: Path, label: str, writes: list[tuple[str, str]], instance: int, disable: bool,
        query: str) -> dict:
    state = Path(tempfile.mkdtemp(prefix=f"agentmemory-gen35-pf-{label}-", dir="/private/tmp"))
    agent = f"memory-bakeoff-gen35-preflight-{label}"
    if disable:
        os.environ[FLAG] = "1"
    else:
        os.environ.pop(FLAG, None)
    launcher = None
    try:
        base, startup, launcher = g13.start_service(tree, state, instance, agent)
        for record_id, content in writes:
            g13.request_json(base, "/agentmemory/remember", body={
                "agentId": agent, "project": PROJECT, "content": content,
                "sourceObservationIds": [record_id]})
            time.sleep(0.1)
        rows = rows_of(base, agent)
        search = g13.request_json(base, "/agentmemory/smart-search", body={
            "agentId": agent, "project": PROJECT, "query": query, "limit": 5})
        hits = [{"rank": n, "sourceObservationIds": h.get("sourceObservationIds"),
                 "score": h.get("score"), "content": (h.get("content") or "")[:60]}
                for n, h in enumerate(search.get("results") or [], start=1)]
    finally:
        if launcher is not None:
            g13.stop_service(tree, state, instance, agent, launcher)
        os.environ.pop(FLAG, None)
    return {"label": label, "tree": str(tree), "flag_disable": disable, "agent_id": agent,
            "state_dir": str(state), "rows": rows, "retired": [r for r in rows if r["isLatest"] is False],
            "search": hits}


def shape(rows: list[dict]) -> list[dict]:
    """Semantic shape only: native ids and timings are allowed to differ."""
    out = []
    for r in sorted(rows, key=lambda r: (r["sourceObservationIds"] or [""])[0]):
        out.append({"source": (r["sourceObservationIds"] or [None])[0], "isLatest": r["isLatest"],
                    "version": r["version"], "has_parent": bool(r["parentId"]),
                    "supersedes_count": len(r["supersedes"] or []), "content": r["content"]})
    return out


def ranking(hits: list[dict]) -> list[str | None]:
    return [(h["sourceObservationIds"] or [None])[0] for h in hits]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/agentmemory_gen35_preflight.json"))
    args = ap.parse_args()
    if not PATCHED.exists():
        raise SystemExit(f"patched tree missing: {PATCHED}")

    q_above = "bench alpha humidity target"
    q_below = "irrigation controller dawn cycle"
    findings = {
        "above_on": arm(PATCHED, "above-on", ABOVE, 41, False, q_above),
        "above_off": arm(PATCHED, "above-off", ABOVE, 42, True, q_above),
        "above_upstream": arm(UPSTREAM, "above-upstream", ABOVE, 43, False, q_above),
        "below_on": arm(PATCHED, "below-on", BELOW, 44, False, q_below),
        "below_off": arm(PATCHED, "below-off", BELOW, 45, True, q_below),
    }

    checks: dict[str, bool] = {}
    a_on, a_off, a_up = findings["above_on"], findings["above_off"], findings["above_upstream"]
    b_on, b_off = findings["below_on"], findings["below_off"]

    checks["above_on_retires_exactly_one"] = len(a_on["retired"]) == 1 and len(a_on["rows"]) == 2
    checks["above_off_retires_nothing"] = len(a_off["retired"]) == 0 and len(a_off["rows"]) == 2
    checks["above_off_has_no_supersession_state"] = all(
        not r["parentId"] and not (r["supersedes"] or []) and (r["version"] in (1, None))
        for r in a_off["rows"])
    checks["above_on_matches_unpatched_upstream"] = shape(a_on["rows"]) == shape(a_up["rows"])
    checks["below_on_retains_both"] = len(b_on["rows"]) == 2 and not b_on["retired"]
    checks["below_off_retains_both"] = len(b_off["rows"]) == 2 and not b_off["retired"]
    checks["below_arms_identical_shape"] = shape(b_on["rows"]) == shape(b_off["rows"])
    checks["below_arms_identical_ranking"] = ranking(b_on["search"]) == ranking(b_off["search"])
    checks["below_arms_identical_scores"] = (
        [h["score"] for h in b_on["search"]] == [h["score"] for h in b_off["search"]])
    checks["off_arm_indexes_new_memory"] = len(b_off["search"]) > 0 and len(a_off["search"]) > 0
    env = g13.service_env("preflight")
    checks["no_llm_credentials"] = all(env.get(k) == "" for k in
        ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"))
    checks["local_embeddings_only"] = env.get("EMBEDDING_PROVIDER") == "local"

    findings["checks"] = checks
    findings["passed"] = all(checks.values())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(findings, indent=2, sort_keys=True) + "\n")
    for name, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"wrote {out}")
    if not findings["passed"]:
        raise SystemExit("gen35 preflight failed; no scored run may proceed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
