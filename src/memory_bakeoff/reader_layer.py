"""`reader-layer-gen85-v1`: one reader, bolted onto frozen evidence from every engine.

Gen83 and Gen84 attributed the two universal zeros in Gen68's table, and both
came back the same way: the capability the case was named for was never
exercised. `recommended_procedure` asked which of two attempts to adopt and
graded the retrieved set; `negative_unknown` asked whether a system would decline
and graded top-k. Neither question reaches a retriever.

This module adds the missing layer and nothing else.

**One architectural component changes.** The engines are not re-run. Their
already-committed retrieval outputs for `LQ10` and `LQ16` are replayed into a
single pinned reader, identical for all four. Any difference in the result is
therefore the evidence each engine returned, not a different reader.

**What the reader is allowed to see.** The query, and the public
`canonical_observation_id` and `assertion` of exactly the records that engine
returned, in the order it returned them. Nothing else. Not the truth key, the
transition, the lineage, `procedure_outcome`, `historical_only`, the expected or
prohibited ids, the scorer's state, or which engine produced the evidence.
`assert_reader_input_clean` fails closed on all of it, and the assertion text is
the same text that was written to the engines in the first place.

**Why citation, not prose.** The reader is asked to end on a `CITE:` line naming
record ids or `NONE`. Ids are public — they were published to every engine — so
citing them leaks nothing, and it makes grading exact rather than a second model
judging a first. A reader that cites is a filter over retrieval, and its output
drops straight into the frozen scorer.

**This is a different system configuration, not a correction.** A retrieval-only
result stays `NOT_DEMONSTRABLE`. Nothing here revises what any engine scored.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence

READER_VERSION = "reader-layer-gen85-v2"
CONFIGURATION = "retrieval_plus_reader"
RETRIEVAL_ONLY = "retrieval_only"

# Frozen before any model call.
MODEL = "qwen3.6-35b-vulkan-nothink"
ENDPOINT_PATH = "/v1/chat/completions"
TEMPERATURE = 0.0
TOP_P = 1.0
MAX_TOKENS = 512
REPETITIONS = 3

UNPARSED = "UNPARSED_NO_CITE_LINE"
REFUSAL_TOKEN = "NONE"
# v2: match CITE anywhere, not only at line start. Attempt 1 anchored it to the
# start of a line and mis-scored replies that put it inline after the prose; see
# results/reader_layer_gen85/superseded_attempt_1/README.md.
CITE_PATTERN = re.compile(r"CITE:\s*(.+?)\s*$", re.MULTILINE)
ID_PATTERN = re.compile(r"\bL\d{3}\b")

SYSTEM_PROMPT = (
    "You answer questions using only the numbered records provided. "
    "You never use outside knowledge and you never invent records. "
    "If the records do not answer the question, you say so."
)

USER_TEMPLATE = """Question: {query}

Records:
{records}

Answer the question in one or two sentences using only the records above.
If no record answers the question, say that it is unknown.

Then, on the final line and nothing after it, write CITE: followed by the ids of
the records your answer rests on, separated by spaces. If no record answers the
question, write CITE: NONE."""

# Anything from the truth model that must never reach the prompt.
FORBIDDEN_IN_PROMPT = (
    "truth_key", "transition", "corrects_id", "supersedes_id", "retracts_id",
    "invalidates_id", "historical_only", "procedure_outcome", "expected_ids",
    "prohibited_ids", "rationale", "target_kind", "failure_class",
)


def render_records(records: Sequence[tuple[str, str]]) -> str:
    return "\n".join(f"{index}. [{id}] {text}"
                     for index, (id, text) in enumerate(records, start=1))


def build_prompt(query: str, records: Sequence[tuple[str, str]]) -> dict[str, str]:
    return {
        "system": SYSTEM_PROMPT,
        "user": USER_TEMPLATE.format(query=query, records=render_records(records)),
    }


def assert_reader_input_clean(prompt: Mapping[str, str], *, engine: str) -> None:
    """Fail closed if the prompt carries truth, scorer state or engine identity."""
    blob = (prompt["system"] + "\n" + prompt["user"]).lower()
    leaked = sorted({term for term in FORBIDDEN_IN_PROMPT if term in blob})
    if engine.lower() in blob:
        leaked.append(f"engine_identity:{engine}")
    if leaked:
        raise ValueError(f"reader prompt leaks {sorted(set(leaked))}")


def parse_answer(text: str) -> dict[str, Any]:
    """Deterministic parse. No model judges another model's output.

    A missing or unparsable CITE line is `UNPARSED` — recorded as its own state
    rather than silently folded into a refusal, since 'the reader declined' and
    'the reader did not follow the format' are different results.
    """
    matches = CITE_PATTERN.findall(text)
    if not matches:
        return {"cited_ids": (), "refused": None, "parsed": False,
                "raw_cite": None}
    final = matches[-1].strip()
    if final.upper().startswith(REFUSAL_TOKEN):
        return {"cited_ids": (), "refused": True, "parsed": True, "raw_cite": final}
    ids = tuple(dict.fromkeys(ID_PATTERN.findall(final)))
    return {"cited_ids": ids, "refused": not ids, "parsed": True, "raw_cite": final}


def contract() -> dict[str, Any]:
    return {
        "reader_version": READER_VERSION,
        "configuration": CONFIGURATION,
        "model": MODEL,
        "sampling": {"temperature": TEMPERATURE, "top_p": TOP_P,
                     "max_tokens": MAX_TOKENS},
        "repetitions": REPETITIONS,
        "system_prompt": SYSTEM_PROMPT,
        "user_template": USER_TEMPLATE,
        "reader_sees": ["the query",
                        "the public canonical id and assertion of each record the "
                        "engine returned, in the engine's own order"],
        "reader_never_sees": list(FORBIDDEN_IN_PROMPT) + ["engine identity",
                                                          "scorer state",
                                                          "records the engine did not return"],
        "parse_rule": "the LAST CITE: occurrence anywhere in the reply; an absent CITE is UNPARSED and excluded from both verdicts, never scored as a failure",
        "grading": "the CITE line is parsed deterministically and fed to the frozen "
                   "scorer; no model grades another model",
        "engines_rerun": False,
        "status_of_retrieval_only_results": "NOT_DEMONSTRABLE, unchanged",
        "this_is": "a different system configuration, not a correction to any engine",
    }


def contract_sha256() -> str:
    return hashlib.sha256(
        json.dumps(contract(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# --- controls, run before any model call ----------------------------------
CANNED = {
    "cites_the_successful_attempt": "Use warmup and a fixed batch.\nCITE: L008",
    "cites_the_failed_attempt": "Run it without warmup.\nCITE: L007",
    "cites_both": "Two attempts are recorded.\nCITE: L008 L007",
    "declines": "The records do not say who is on call.\nCITE: NONE",
    "asserts_without_support": "Nimbus is on call this week.\nCITE: L001",
    "ignores_the_format": "I think it is the second one.",
}


def controls(score_case, score_claim, fixture, procedure_case, unknown_case) -> dict[str, Any]:
    """Prove both graders behave, with fixed strings and no model in the loop."""
    def grade_procedure(name):
        parsed = parse_answer(CANNED[name])
        return {"cited": parsed["cited_ids"], "parsed": parsed["parsed"],
                "classes": tuple(score_case(fixture, procedure_case,
                                            parsed["cited_ids"]).failure_classes)}

    def grade_unknown(name):
        return grade_abstention(score_claim, score_case, fixture, unknown_case,
                                parse_answer(CANNED[name]))
    return {
        "procedure_adoption": {name: grade_procedure(name) for name in
                               ("cites_the_successful_attempt", "cites_the_failed_attempt",
                                "cites_both", "ignores_the_format")},
        "unknown_abstention": {name: grade_unknown(name) for name in
                               ("declines", "asserts_without_support", "ignores_the_format")},
    }


def grade_abstention(score_claim, score_case, fixture, case,
                     parsed: Mapping[str, Any]) -> dict[str, Any]:
    """Grade one abstention answer, keeping UNPARSED out of both verdicts.

    A reply that never produced a CITE line is not a refusal and not an
    assertion. Charging it `unknown_hallucination` would be the same mistake this
    whole line of work exists to catch: a verdict a check cannot avoid reaching.
    """
    if not parsed["parsed"]:
        return {"cited": (), "refused": None, "parsed": False, "status": UNPARSED,
                "claim_classes": (), "retrieval_classes": (),
                "excluded_from_scoring": True}
    supported = bool(parsed["refused"])
    return {
        "cited": parsed["cited_ids"], "refused": parsed["refused"], "parsed": True,
        "status": "abstained" if supported else "asserted",
        "claim_classes": tuple(score_claim(case, assertion_supported=supported)),
        "retrieval_classes": tuple(score_case(fixture, case,
                                              parsed["cited_ids"]).failure_classes),
        "excluded_from_scoring": False,
    }
