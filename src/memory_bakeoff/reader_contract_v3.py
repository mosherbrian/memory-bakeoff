"""`reader-contract-gen86-v3`: the decision, separated from the evidence for it.

Gen85 asked the reader to cite the records its answer rested on, and scored the
citation. On perseus's evidence the reader answered correctly — *use warmup and a
fixed batch, because that attempt succeeded while the other failed* — and was
charged `failed_procedure_adoption` for citing the failed attempt. Citing the
record you contrast against is not adopting it, and a citation channel cannot
tell those apart.

So the contract now carries **two separate things**:

- **the decision** — `ADOPT: <id|NONE>` for the procedure case,
  `ANSWER: UNKNOWN|ASSERTED` for the unknown case. This is what is scored.
- **the evidence for it** — `SUPPORT:` and `CONTRAST:` lines, recorded and never
  scored. A record named under `CONTRAST` is explicitly the thing the reader
  argued *against*, and it can never make the decision fail.

Scoring is mechanical: the adopted id, and nothing else, is handed to the frozen
scorer. No model grades another model, and no citation can be mistaken for a
choice.

**Order stability is now a first-class measurement, not a footnote.** Gen85's
abstention split turned out to be the order of identical evidence — 10 refusals
and 14 assertions across the 24 arrangements of one four-record set. This
generation therefore runs **every feasible permutation of every distinct evidence
set**, and reports semantic correctness apart from order stability. An engine
comparison is reported only where the result survives ordering.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

CONTRACT_VERSION = "reader-contract-gen86-v3"
SUPERSEDES = "reader-layer-gen85-v2"

MODEL = "qwen3.6-35b-vulkan-nothink"
TEMPERATURE = 0.0
TOP_P = 1.0
MAX_TOKENS = 512

NONE_TOKEN = "NONE"
UNKNOWN = "UNKNOWN"
ASSERTED = "ASSERTED"
UNPARSED = "UNPARSED_NO_DECISION_LINE"

ADOPT_PATTERN = re.compile(r"ADOPT:\s*(.+?)\s*$", re.MULTILINE)
ANSWER_PATTERN = re.compile(r"ANSWER:\s*(.+?)\s*$", re.MULTILINE)
SUPPORT_PATTERN = re.compile(r"SUPPORT:\s*(.+?)\s*$", re.MULTILINE)
CONTRAST_PATTERN = re.compile(r"CONTRAST:\s*(.+?)\s*$", re.MULTILINE)
ID_PATTERN = re.compile(r"\bL\d{3}\b")

SYSTEM_PROMPT = (
    "You answer questions using only the numbered records provided. "
    "You never use outside knowledge and you never invent records. "
    "If the records do not answer the question, you say so."
)

PROCEDURE_TEMPLATE = """Question: {query}

Records:
{records}

Say in one or two sentences which procedure is recommended, using only the
records above. Then write exactly these three lines and nothing after them:

ADOPT: the id of the single record whose procedure you recommend, or NONE
SUPPORT: ids of records that support your recommendation, or NONE
CONTRAST: ids of records you are recommending AGAINST, or NONE"""

UNKNOWN_TEMPLATE = """Question: {query}

Records:
{records}

Answer the question in one or two sentences using only the records above, or say
that the records do not answer it. Then write exactly these two lines and nothing
after them:

ANSWER: UNKNOWN if the records do not answer the question, otherwise ASSERTED
SUPPORT: ids of records your answer rests on, or NONE"""

FORBIDDEN_IN_PROMPT = (
    "truth_key", "transition", "corrects_id", "supersedes_id", "retracts_id",
    "invalidates_id", "historical_only", "procedure_outcome", "expected_ids",
    "prohibited_ids", "rationale", "target_kind", "failure_class",
)


def render_records(records: Sequence[tuple[str, str]]) -> str:
    return "\n".join(f"{n}. [{i}] {t}" for n, (i, t) in enumerate(records, start=1))


def build_prompt(kind: str, query: str,
                 records: Sequence[tuple[str, str]]) -> dict[str, str]:
    template = PROCEDURE_TEMPLATE if kind == "procedure" else UNKNOWN_TEMPLATE
    return {"system": SYSTEM_PROMPT,
            "user": template.format(query=query, records=render_records(records))}


def assert_reader_input_clean(prompt: Mapping[str, str], *, engine: str) -> None:
    blob = (prompt["system"] + "\n" + prompt["user"]).lower()
    leaked = sorted({t for t in FORBIDDEN_IN_PROMPT if t in blob})
    if engine.lower() in blob:
        leaked.append(f"engine_identity:{engine}")
    if leaked:
        raise ValueError(f"reader prompt leaks {sorted(set(leaked))}")


def _ids(pattern: re.Pattern[str], text: str) -> tuple[str, ...]:
    found = pattern.findall(text)
    return tuple(dict.fromkeys(ID_PATTERN.findall(found[-1]))) if found else ()


def parse_procedure(text: str) -> dict[str, Any]:
    """The adopted id is the decision. SUPPORT and CONTRAST are recorded only."""
    matches = ADOPT_PATTERN.findall(text)
    if not matches:
        return {"decision": None, "adopted": None, "support": (), "contrast": (),
                "status": UNPARSED, "parsed": False}
    final = matches[-1].strip()
    ids = ID_PATTERN.findall(final)
    adopted = ids[0] if ids else None
    if adopted is None and not final.upper().startswith(NONE_TOKEN):
        return {"decision": None, "adopted": None, "support": (), "contrast": (),
                "status": UNPARSED, "parsed": False}
    return {
        "decision": adopted or NONE_TOKEN,
        "adopted": adopted,
        "support": _ids(SUPPORT_PATTERN, text),
        "contrast": _ids(CONTRAST_PATTERN, text),
        "status": "adopted" if adopted else "declined",
        "parsed": True,
    }


def parse_unknown(text: str) -> dict[str, Any]:
    matches = ANSWER_PATTERN.findall(text)
    if not matches:
        return {"decision": None, "support": (), "status": UNPARSED, "parsed": False}
    final = matches[-1].strip().upper()
    if final.startswith(UNKNOWN):
        decision = UNKNOWN
    elif final.startswith(ASSERTED):
        decision = ASSERTED
    else:
        return {"decision": None, "support": (), "status": UNPARSED, "parsed": False}
    return {"decision": decision, "support": _ids(SUPPORT_PATTERN, text),
            "status": "abstained" if decision == UNKNOWN else "asserted",
            "parsed": True}


def score_procedure(score_case, fixture, case, parsed: Mapping[str, Any]) -> dict[str, Any]:
    """Only the adopted id reaches the scorer. A contrast citation cannot fail it."""
    if not parsed["parsed"]:
        return {"status": UNPARSED, "classes": (), "correct": None,
                "excluded_from_scoring": True}
    decision = (parsed["adopted"],) if parsed["adopted"] else ()
    classes = tuple(score_case(fixture, case, decision).failure_classes)
    return {"status": parsed["status"], "adopted": parsed["adopted"],
            "support": parsed["support"], "contrast": parsed["contrast"],
            "classes": classes, "correct": classes == (),
            "excluded_from_scoring": False}


def score_unknown(score_claim, case, parsed: Mapping[str, Any]) -> dict[str, Any]:
    if not parsed["parsed"]:
        return {"status": UNPARSED, "claim_classes": (), "correct": None,
                "excluded_from_scoring": True}
    supported = parsed["decision"] == UNKNOWN
    classes = tuple(score_claim(case, assertion_supported=supported))
    return {"status": parsed["status"], "decision": parsed["decision"],
            "support": parsed["support"], "claim_classes": classes,
            "correct": classes == (), "excluded_from_scoring": False}


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "supersedes": SUPERSEDES,
        "single_change": "the decision is stated on its own line and scored alone; "
                         "SUPPORT and CONTRAST are recorded and never scored",
        "model": MODEL,
        "sampling": {"temperature": TEMPERATURE, "top_p": TOP_P, "max_tokens": MAX_TOKENS},
        "procedure_decision": "ADOPT: <id|NONE>",
        "unknown_decision": "ANSWER: UNKNOWN|ASSERTED",
        "why": "Gen85 charged a correct recommendation for citing the counterexample "
               "it argued against; a citation channel cannot separate a choice from "
               "its evidence, and this contract does",
        "order_policy": "every feasible permutation of every distinct evidence set; "
                        "semantic correctness reported apart from order stability, and "
                        "an engine comparison only where the result survives ordering",
        "engines_rerun": False,
        "unparsed_policy": "recorded and excluded from both verdicts, never scored as "
                           "a failure",
    }


def contract_sha256() -> str:
    return hashlib.sha256(
        json.dumps(contract(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# --- fixed-string controls, run before any model call ---------------------
CANNED_PROCEDURE = {
    "adopts_the_successful_attempt":
        "Use warmup and a fixed batch.\nADOPT: L008\nSUPPORT: L008\nCONTRAST: L007",
    "adopts_it_while_contrasting_the_failure":
        "Warmup succeeded where its absence failed.\nADOPT: L008\nSUPPORT: L008 L007\n"
        "CONTRAST: L007",
    "adopts_the_failed_attempt":
        "Run without warmup.\nADOPT: L007\nSUPPORT: L007\nCONTRAST: L008",
    "declines":
        "No procedure is recommended here.\nADOPT: NONE\nSUPPORT: NONE\nCONTRAST: NONE",
    "ignores_the_format": "I think it is the second one.",
}
CANNED_UNKNOWN = {
    "abstains": "The records do not say.\nANSWER: UNKNOWN\nSUPPORT: NONE",
    "asserts": "Forge C2 is active.\nANSWER: ASSERTED\nSUPPORT: L003 L004",
    "ignores_the_format": "Probably C2.",
}


def controls(score_case, score_claim, fixture, procedure_case, unknown_case) -> dict[str, Any]:
    return {
        "procedure": {name: score_procedure(score_case, fixture, procedure_case,
                                            parse_procedure(text))
                      for name, text in CANNED_PROCEDURE.items()},
        "unknown": {name: score_unknown(score_claim, unknown_case, parse_unknown(text))
                    for name, text in CANNED_UNKNOWN.items()},
    }
