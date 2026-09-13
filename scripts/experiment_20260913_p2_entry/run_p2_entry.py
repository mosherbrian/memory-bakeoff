#!/usr/bin/env python3
"""P2 ENTRY run: the charter's locked baseline arms on the MemConflict benchmark.

Protocol (frozen contract, src/memory_bakeoff/memconflict.py):
- heldout 27 personas (frozen list from results/memconflict_gen38_full_release/
  heldout-27-derived.json — never re-derived);
- chronology rule: ingest session i, then ask session i's questions
  (allowed prefix 0..i inclusive); sessions append — the store GROWS;
- query contract: released question text only; gold (scorer-only) is used
  AFTER retrieval, for scoring only, never shown to any arm;
- provenance: returned items are credited by session identity via released
  identifiers (canonical provenance_id), never by text similarity;
- scoring: first_support_rank + hit_at_k (k = 2/3/5, primary 3) from the
  contract module; measured vs unmeasured vs measured-zero kept separate.

Arms (charter Patch 3 locked baselines; no LLM, all local, $0):
- pi_lcm_store_reader   (provider interface, controlled core)
- pi_lcm_history_null   (provider interface, raw-history null)
- longcontext_null      (engine seam, the row-4 instrument)

Records mapping (identical to tests/test_portfolio_realdata_smoke.py):
provenance_id -> canonical id; unit.date -> UTC timestamp with a
per-date running ordinal (released chronology preserved, no invented dates);
persona|S<zero-padded session> -> conversation.
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from memory_bakeoff import memconflict as M  # noqa: E402
from memory_bakeoff.longcontext_null import ARM_VERSION, LongContextNull  # noqa: E402
from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.portfolio import assert_run_pins  # noqa: E402
from memory_bakeoff.providers.pi_lcm_store_reader import (  # noqa: E402
    PiLcmHistoryNullProvider,
    PiLcmStoreReaderProvider,
)

HERE = Path(__file__).resolve().parent
OUT = REPO / "results" / "p2_entry_20260913"
HELDOUT_JSON = REPO / "results" / "memconflict_gen38_full_release" / "heldout-27-derived.json"
TOP_K = 5
PRIMARY_K = 3
MAX_RELAXATION_ATTEMPTS = 6  # verbatim from extensions/pi-project-recall


def relaxed_variants(query: str) -> list[str]:
    """Verbatim port of the extension's relaxedVariants: progressive
    trailing-term drop (keep >= 2 terms), then single tokens, last first."""
    tokens = [t for t in query.split() if t]
    variants: list[str] = []
    for keep in range(len(tokens) - 1, 1, -1):
        if len(variants) >= MAX_RELAXATION_ATTEMPTS:
            break
        variants.append(" ".join(tokens[:keep]))
    for i in range(len(tokens) - 1, -1, -1):
        if len(variants) >= MAX_RELAXATION_ATTEMPTS:
            break
        variants.append(tokens[i])
    return variants


def tool_level_retrieve(reader, q, session_units_by_index, top_k):
    """The pi-project-recall tool's query behavior ported to the benchmark:
    exact AND query first; if it returns nothing or only hits from the
    question's OWN session (the recorded live-prompt-echo failure mode),
    try relaxed variants and take the first whose hits reach prior sessions.
    Returns (items, relaxed_with)."""
    case = QueryCase(id=q.key, category="real", query=q.text, relevant_ids=())
    result = reader.retrieve(case, top_k=top_k)
    unit_session = session_units_by_index

    def reaches_prior(items):
        prior = [i for i in items if i.record_id in unit_session and
                 unit_session[i.record_id].session_index < q.session_index]
        return len(prior) > 0

    multi_session = len(session_units_by_index) > 1
    if not multi_session or (result.items and reaches_prior(result.items)):
        return result, None
    if not result.items or not reaches_prior(result.items):
        reason = "matched only the current session" if result.items else "returned nothing"
        for variant in relaxed_variants(q.text):
            vcase = QueryCase(id=q.key, category="real", query=variant, relevant_ids=())
            vresult = reader.retrieve(vcase, top_k=top_k)
            if reaches_prior(vresult.items):
                return vresult, variant
        return result, None
    return result, None


def unit_records(units) -> list[MemoryRecord]:
    """Units -> MemoryRecords. Timestamp = released date at UTC midnight plus
    a running per-date ordinal in seconds (preserves released chronology)."""
    from datetime import timedelta

    ordered = sorted(units, key=lambda u: (u.session_index, u.turn_index, u.message_index))
    per_date: dict[str, int] = {}
    records = []
    for u in ordered:
        ordinal = per_date.get(u.date, 0)
        per_date[u.date] = ordinal + 1
        stamp = datetime.fromisoformat(u.date).replace(tzinfo=timezone.utc) + timedelta(seconds=ordinal)
        records.append(MemoryRecord(
            id=u.provenance_id,
            text=u.text,
            timestamp=stamp,
            session_id=f"{u.persona_id}|S{u.session_index:04d}",
            scope=u.persona_id,
            metadata={"role": u.role},
        ))
    return records


def run_arm_on_persona(arm: str, persona: dict):
    units = M.ingestion_units(persona)
    unit_by_id = {u.provenance_id: u for u in units}
    by_session = defaultdict(list)
    for u in units:
        by_session[u.session_index].append(u)
    qs_by_session = defaultdict(list)
    for q in M.questions(persona):
        qs_by_session[q.session_index].append(q)

    reader = (PiLcmStoreReaderProvider()
              if arm in ("pi_lcm_store_reader", "pi_lcm_store_reader_toollevel") else None)
    history_null = PiLcmHistoryNullProvider() if arm == "pi_lcm_history_null" else None
    cumulative: list = []
    prov_session: dict[str, int] = {}
    lcn: LongContextNull | None = None
    if arm == "longcontext_null":
        lcn = LongContextNull([])

    rows = []
    for session_index in sorted(set(by_session) | set(qs_by_session)):
        session_records = unit_records(by_session.get(session_index, []))
        if session_records:
            if arm in ("pi_lcm_store_reader", "pi_lcm_store_reader_toollevel"):
                reader.append(session_records)
            if arm == "pi_lcm_history_null":
                history_null.append(session_records)
            cumulative.extend(by_session.get(session_index, []))
            for u in by_session.get(session_index, []):
                prov_session[u.provenance_id] = u
            if arm == "longcontext_null":
                lcn = LongContextNull(
                    [{"id": u.provenance_id, "text": u.text} for u in cumulative])

        for q in qs_by_session.get(session_index, []):
            started = time.perf_counter()
            relaxed_with = None
            if arm == "pi_lcm_store_reader_toollevel":
                result, relaxed_with = tool_level_retrieve(reader, q, prov_session, TOP_K)
                returned_ids = [i.record_id for i in result.items]
                offered = len(result.items)
            elif arm == "pi_lcm_store_reader":
                result = reader.retrieve(QueryCase(id=q.key, category="real", query=q.text, relevant_ids=()), top_k=TOP_K)
                returned_ids = [i.record_id for i in result.items]
                offered = len(result.items)
            elif arm == "pi_lcm_history_null":
                result = history_null.retrieve(QueryCase(id=q.key, category="real", query=q.text, relevant_ids=()), top_k=TOP_K)
                returned_ids = [i.record_id for i in result.items][:TOP_K]
                offered = len(result.items)
            else:
                items, _lat = lcn.search(q.text)
                returned_ids = [i["native_id"] for i in items[:TOP_K]]
                offered = len(items)
            wall_ms = (time.perf_counter() - started) * 1000.0
            returned_units = [unit_by_id[rid] for rid in returned_ids if rid in unit_by_id]
            gold = M.gold_for(persona, q)
            rank = M.first_support_rank(returned_units, gold)
            rows.append({
                "persona": q.key.split("|")[0],
                "question_key": q.key,
                "session_index": q.session_index,
                "conflict_type": gold.conflict_type,
                "rank_status": rank.status.value if hasattr(rank.status, "value") else str(rank.status),
                "rank": rank.count,
                "offered": offered,
                "relaxed_with": relaxed_with,
                "wall_ms": round(wall_ms, 3),
            })
    for provider in (reader, history_null):
        if provider is not None:
            provider.close()
    return rows


def aggregate(rows: list[dict]) -> dict:
    dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "no_hit": 0}
    measured = unmeasured = 0
    hits = {2: 0, 3: 0, 5: 0}
    measured_total = 0
    for r in rows:
        if r["rank_status"] == "unmeasured":
            unmeasured += 1
            continue
        measured += 1
        measured_total += 1
        rank = r["rank"] or 0
        if 1 <= rank <= 5:
            dist[str(rank)] += 1
        else:
            dist["no_hit"] += 1
        for k in hits:
            if 1 <= rank <= k:
                hits[k] += 1
    out = {
        "questions_executed": len(rows),
        "measured": measured,
        "unmeasured": unmeasured,
        "first_support_rank_distribution": dist,
    }
    for k, count in hits.items():
        out[f"hit@{k}"] = round(count / measured_total, 4) if measured_total else None
        out[f"hits@{k}"] = count
    return out


def main() -> int:
    pins = assert_run_pins()
    derived = json.loads(HELDOUT_JSON.read_text())
    heldout_ids = sorted(next(iter(derived.values()))["per_persona"].keys())
    personas = {p["ID"]: p for p in M.load_personas()}
    missing = [pid for pid in heldout_ids if pid not in personas]
    if missing:
        raise SystemExit(f"heldout personas missing from dataset: {missing[:3]}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pins.json").write_text(json.dumps(pins, indent=2, sort_keys=True, default=str), encoding="utf-8")

    arms = ["pi_lcm_store_reader_toollevel", "pi_lcm_store_reader",
            "pi_lcm_history_null", "longcontext_null"]
    summary = {}
    with (OUT / "per_question.jsonl").open("w", encoding="utf-8") as per_q:
        for arm in arms:
            all_rows: list[dict] = []
            for pid in heldout_ids:
                rows = run_arm_on_persona(arm, personas[pid])
                for r in rows:
                    r["arm"] = arm
                all_rows.extend(rows)
                print(f"  {arm}: {pid[:8]}… {len(rows)} questions", flush=True)
            for r in all_rows:
                per_q.write(json.dumps(r, sort_keys=True) + "\n")
            by_type = defaultdict(list)
            for r in all_rows:
                by_type[r.get("conflict_type", "unknown")].append(r)
            summary[arm] = {
                "overall": aggregate(all_rows),
                "by_conflict_type": {t: aggregate(rs) for t, rs in sorted(by_type.items())},
            }
            print(f"{arm}: {summary[arm]['overall']}", flush=True)

    (OUT / "summary.json").write_text(json.dumps(
        {"pins": pins, "protocol": {"top_k": TOP_K, "primary_k": PRIMARY_K,
                                    "heldout": len(heldout_ids),
                                    "chronology": "ingest session i, then ask session i's questions",
                                    "scoring": "first_support_rank by session identity (contract module)"},
         "arms": summary}, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print("wrote", OUT / "summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
