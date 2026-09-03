#!/usr/bin/env python3
"""Gen36: freeze what MemConflict means before any product is adapted to it.

Computes dataset statistics from the pinned bytes, publishes the public/scorer-only
field registry, records the audited upstream scoring behaviour, freezes a label-blind
calibration subset, and emits a deterministic content digest. Runs no product and no LLM.
"""
from __future__ import annotations

import argparse, collections, hashlib, json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.round2_reporting import ReportingError, Status

# Audited by reading Evaluation/eval_scoring.py at the pinned commit. Line numbers are
# from that file; every claim here is a statement about upstream source, not about us.
SCORING_AUDIT = {
    "audited_files": ["Evaluation/eval_scoring.py", "Evaluation/eval_memzero.py"],
    "primary_top_k": M.UPSTREAM_PRIMARY_TOP_K,
    "top_k_variants": list(M.UPSTREAM_TOP_K_VALUES),
    "metrics_by_conflict_type": {
        "dynamic_conflict": {
            "black_box": ["dynamic_answer_accuracy", "update_awareness_and_order_consistency_score"],
            "white_box": ["updated_evidence_hit_at_3", "updated_evidence_log_rank_score_at_3"],
        },
        "static_conflict": {
            "black_box": ["static_answer_accuracy", "conflict_recognition_score"],
            "white_box": ["truth_evidence_hit_at_3", "truth_evidence_log_rank_score_at_3"],
        },
        "conditional_conflict": {
            "black_box": ["conditional_answer_accuracy"],
            "white_box": ["correct_condition_evidence_hit_at_3",
                          "correct_condition_evidence_log_rank_score_at_3"],
        },
    },
    "white_box_is_llm_judged": True,
    "white_box_support_decision": (
        "the judge is shown the top-K retrieved memory strings with their created_at values and "
        "returns a support rank; there is no released identifier in that decision, so upstream "
        "white-box scoring is semantic, not exact (eval_scoring.py build_llm_judge_prompt, "
        "parse_llm_metric_result, derive_white_box_metrics_from_rank)"
    ),
    "log_rank_formula": "1/log2(rank+1) for 1<=rank<=K, else 0.0",
    "retrieved_memory_timestamps_affect_scoring": True,
    "chronology": (
        "eval_memzero.py Generate_Single_Persona_Evaluation iterates the session chain in order, "
        "adds session i's dialogue, then answers session i's questions; the allowed history for a "
        "question is sessions 0..i inclusive"
    ),
    "failure_semantics": {
        "missing_model_answer": {
            "upstream_behaviour": "build_missing_answer_result returns every metric as 0.0 with "
                                  "Error_Tags=['missing_model_answer']",
            "is_measured_zero": False,
            "our_treatment": "UNMEASURED",
        },
        "llm_judge_unavailable_or_raising": {
            "upstream_behaviour": "evaluate_question_with_llm catches every exception and returns None; "
                                  "Evaluate_Single_Question then falls back to build_rule_based_result, "
                                  "which leaves all white-box metrics at 0.0 although nothing was measured",
            "is_measured_zero": False,
            "our_treatment": "UNMEASURED, and the lane is named upstream_rule_fallback, never merged "
                             "with upstream_llm_judge",
        },
        "judge_omits_a_metric_key": {
            "upstream_behaviour": "parse_llm_metric_result reads parsed_result.get(metric_key, 0), so a "
                                  "missing key scores zero",
            "is_measured_zero": False,
            "our_treatment": "UNMEASURED",
        },
        "unparsable_support_rank": {
            "upstream_behaviour": "parse_support_rank returns 0 on any parse failure, which reads as a miss",
            "is_measured_zero": False,
            "our_treatment": "UNMEASURED",
        },
    },
    "official_result_requires_llm_judge": True,
    "reader_status_in_gen36": "requires_reader_authorization: no LLM, no external API, no GPU was used",
}


def dataset_statistics(personas: list[dict]) -> dict:
    sessions_by_type = collections.Counter()
    questions_by_type = collections.Counter()
    session_counts, question_counts, message_counts = [], [], []
    dialogue_characters = 0
    total_messages = 0
    total_turns = 0
    persona_ids = []
    anomalies: list[dict] = []
    duplicate_question_keys = []
    seen_keys = set()

    for persona in personas:
        persona_ids.append(persona["ID"])
        chain = persona["Full_Session_Chain"]
        session_counts.append(len(chain))
        units, persona_anomalies = M.parse_dialogue(persona)
        anomalies.extend(persona_anomalies)
        total_messages += len(units)
        total_turns += len({(u.session_id, u.turn_index) for u in units})
        dialogue_characters += sum(len(u.text) for u in units)
        message_counts.append(len(units))
        persona_questions = 0
        for session in chain:
            sessions_by_type[session["Session_Type"]] += 1
            for item in session.get("Session_Questions") or []:
                questions_by_type[item["conflict_type"]] += 1
                persona_questions += 1
                key = (persona["ID"], session["Session_ID"], item["question_id"])
                if key in seen_keys:
                    duplicate_question_keys.append(key)
                seen_keys.add(key)
        question_counts.append(persona_questions)

    if duplicate_question_keys:
        raise ReportingError(f"duplicate question keys: {duplicate_question_keys[:5]}")

    return {
        "personas": len(personas),
        "persona_ids_unique": len(set(persona_ids)) == len(persona_ids),
        "questions_total": sum(questions_by_type.values()),
        "questions_by_conflict_type": dict(sorted(questions_by_type.items())),
        "sessions_total": sum(sessions_by_type.values()),
        "sessions_by_type": dict(sorted(sessions_by_type.items())),
        "sessions_per_persona": {"min": min(session_counts), "max": max(session_counts),
                                 "mean": round(statistics.mean(session_counts), 3),
                                 "median": statistics.median(session_counts)},
        "questions_per_persona": {"min": min(question_counts), "max": max(question_counts),
                                  "mean": round(statistics.mean(question_counts), 3),
                                  "median": statistics.median(question_counts)},
        "dialogue_messages_total": total_messages,
        "dialogue_turns_total": total_turns,
        "dialogue_characters_total": dialogue_characters,
        "dialogue_messages_per_persona": {"min": min(message_counts), "max": max(message_counts),
                                          "mean": round(statistics.mean(message_counts), 3)},
        "malformed_messages_excluded": len(anomalies),
        "malformed_messages_by_anomaly": dict(sorted(collections.Counter(
            a["anomaly"] for a in anomalies).items())),
        "malformed_message_ids": [f"{a['persona_id']}|S{a['session_id']}|T{a['turn']}|M{a['message']}"
                                  for a in anomalies],
        "question_id_unique_within_session": True,
        "question_id_unique_within_persona": all(
            len({q.question_id for q in M.questions(p)}) == len(M.questions(p)) for p in personas),
        "note": "token counts are omitted: they are tokenizer-specific and upstream's are not reproducible here",
    }


def support_coverage(personas: list[dict]) -> dict:
    coverage = collections.Counter()
    reasons = collections.Counter()
    for persona in personas:
        for question in M.questions(persona):
            gold = M.gold_for(persona, question)
            coverage[(gold.conflict_type, gold.support_status)] += 1
            if gold.support_status == str(Status.UNMEASURED):
                reasons[gold.support_reason] += 1
    by_type: dict[str, dict[str, int]] = {}
    for (conflict_type, status), count in coverage.items():
        by_type.setdefault(conflict_type, {})[status] = count
    total = sum(coverage.values())
    exact = sum(c for (_, status), c in coverage.items() if status == str(Status.PRESENT))
    return {
        "by_conflict_type": {k: dict(sorted(v.items())) for k, v in sorted(by_type.items())},
        "exact_mappable": exact,
        "unmeasurable": total - exact,
        "total": total,
        "unmeasurable_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/memconflict_gen36_contract"))
    args = ap.parse_args()

    observed = M.dataset_sha256()
    if observed != M.DATASET_SHA256:
        raise ReportingError(f"pinned dataset hash drift: expected {M.DATASET_SHA256}, found {observed}")

    personas = M.load_personas()
    stats = dataset_statistics(personas)
    coverage = support_coverage(personas)
    persona_ids = [p["ID"] for p in personas]
    calibration = M.calibration_personas(persona_ids)

    registry = {
        "public_input_fields": M.PUBLIC_INPUT_FIELDS,
        "scorer_only_fields": M.SCORER_ONLY_FIELDS,
        "public_question_fields": sorted(M.PUBLIC_QUESTION_FIELDS),
        "rule": "no scorer-only field may enter product writes, query text, metadata, ranking or filters",
    }
    manifest = {
        "selection": "personas whose SHA-256 hex digest is divisible by 5, chosen without reading any label",
        "fraction": 5,
        "calibration_persona_ids": calibration,
        "calibration_persona_count": len(calibration),
        "held_out_persona_count": len(persona_ids) - len(calibration),
        "status": "permanently development-exposed; never reported as blind evaluation",
    }

    content = {
        "contract_version": M.CONTRACT_VERSION,
        "contract_sha256": M.contract_sha256(),
        "upstream": {"repo": M.UPSTREAM_REPO, "commit": M.UPSTREAM_COMMIT,
                     "dataset_path": M.DATASET_RELATIVE_PATH, "dataset_blob": M.DATASET_BLOB,
                     "dataset_sha256": observed},
        "dataset_statistics": stats,
        "exact_support_coverage": coverage,
        "field_registry": registry,
        "calibration_manifest": manifest,
        "scoring_audit": SCORING_AUDIT,
    }
    digest = hashlib.sha256(canonical_json(content).encode()).hexdigest()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "dataset-stats.json").write_text(json.dumps(
        {"dataset_statistics": stats, "exact_support_coverage": coverage}, indent=2, sort_keys=True) + "\n")
    (out / "field-registry.json").write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")
    (out / "scoring-audit.json").write_text(json.dumps(SCORING_AUDIT, indent=2, sort_keys=True) + "\n")
    (out / "calibration-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (out / "contract.json").write_text(json.dumps(content, indent=2, sort_keys=True) + "\n")
    (out / "content-digest.txt").write_text(digest + "\n")

    print(f"malformed messages excluded {stats['malformed_messages_excluded']} "
          f"{stats['malformed_messages_by_anomaly']}")
    print(f"personas {stats['personas']}, questions {stats['questions_total']} "
          f"{stats['questions_by_conflict_type']}")
    print(f"sessions {stats['sessions_total']} {stats['sessions_by_type']}")
    print(f"exact support: {coverage['exact_mappable']}/{coverage['total']} mappable, "
          f"{coverage['unmeasurable']} unmeasurable")
    for conflict_type, statuses in coverage["by_conflict_type"].items():
        print(f"  {conflict_type}: {statuses}")
    print(f"calibration personas {len(calibration)}/{len(persona_ids)}")
    print(f"contract {M.contract_sha256()}")
    print(f"content digest {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
