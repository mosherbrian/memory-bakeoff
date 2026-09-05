"""`spec-grounded-assertion-provenance-v1`: make every test name its requirement.

Gen60 measured the unchanged generator on a corpus that could finally score it.
It caught every wrong implementation it was allowed to judge, and it also
rejected known-correct code in four of eight tasks. The detection half is good;
the false-alarm half is what makes it unusable unattended.

The hypothesis here is that the false alarms come from tests the model invented
rather than derived - a requirement it supposed rather than read. So this is the
smallest generator-side change that could plausibly reduce them: each test must
quote the sentence of the visible instruction it claims to test, and any test
whose quote is not actually in that instruction is dropped before the bank runs.

Nothing else moves. Same pinned model, sampling, repetitions, corpus, task order
and screen as Gen60. No critic, no second model, no human selection - the
exclusion rule is mechanical and is frozen here, before any Gen61 output exists.

The rule deliberately cannot consult the hidden verifier or the named
requirements in the truth package. It compares the model's quote against
`spec.txt`, which the generator was already shown. Grounding is checked against
what the generator could see, never against the answer.
"""
from __future__ import annotations

import ast
import hashlib
import re
from typing import Any

CONTRACT_VERSION = "spec-grounded-assertion-provenance-v1"
MARKER = "REQUIREMENT:"
MINIMUM_QUOTE_WORDS = 4

GENERATOR_PROMPT = """You are writing additional tests for a Python project.

You are given the task instruction that a developer received, and the project as
it looked before any work was done. You will NOT see their solution.

Your job: write extra pytest tests that would FAIL if the developer implemented
the instruction incorrectly or incompletely, and PASS if they implemented every
part of it correctly.

Rules you must follow exactly:
- Output ONE python code block and nothing else.
- Write only tests. Do not modify or re-implement the project's source.
- Do not rewrite the project's existing tests; add new ones.
- Import the project's modules the same way the existing tests do.
- Cover EVERY requirement stated in the instruction, including any constraint
  that the existing tests do not appear to check.
- Prefer several small, specific assertions over one broad one.
- EVERY test function must start with a DOCSTRING - a triple-quoted string, as
  the first statement inside the function - whose first line is
  `REQUIREMENT: <text>`, where <text> is copied WORD FOR WORD from the task
  instruction above: the exact sentence or clause that test checks. Copy it
  verbatim; do not paraphrase, summarise or invent it. Exactly like this:

      def test_something():
          \"\"\"REQUIREMENT: <the sentence, copied from the instruction>\"\"\"
          assert ...

  The REQUIREMENT line must be INSIDE the triple quotes. A bare line of text in
  the function body is a syntax error and the whole answer will be discarded.
- If you cannot point to wording in the instruction that demands a behaviour,
  do not write a test for it.

The task instruction the developer received:
---
{prompt}
---

The project as shipped, before any work:
{tree}
"""


def normalise(text: str) -> str:
    """Compare on words alone, so quoting is not defeated by wrapping or case."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def cited_requirement(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    doc = ast.get_docstring(node)
    if not doc:
        return None
    first = doc.strip().splitlines()[0].strip()
    if not first.upper().startswith(MARKER):
        return None
    return first[len(MARKER):].strip()


def is_grounded(quote: str | None, spec: str) -> bool:
    """A citation is defensible when its words really are in the instruction.

    Short quotes are refused: three common words appear in almost any prose and
    would let an invented requirement pass by accident.
    """
    if not quote:
        return False
    words = normalise(quote)
    if len(words.split()) < MINIMUM_QUOTE_WORDS:
        return False
    return words in normalise(spec)


def ground_bank(code: str, spec: str) -> dict[str, Any]:
    """Drop every test that does not cite wording from the visible instruction.

    Whole functions go, not individual asserts: a test is the unit pytest
    reports, so an ungrounded assertion cannot be removed without removing the
    test that carries it. Module-level imports and helpers are kept, because a
    surviving test may need them.
    """
    tree = ast.parse(code)
    kept, dropped = [], []

    def sift(body: list[ast.stmt]) -> list[ast.stmt]:
        out = []
        for node in body:
            if isinstance(node, ast.ClassDef):
                node.body = sift(node.body) or [ast.Pass()]
                out.append(node)
                continue
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name.startswith("test_")):
                quote = cited_requirement(node)
                if is_grounded(quote, spec):
                    kept.append({"test": node.name, "quote": quote})
                    out.append(node)
                else:
                    dropped.append({"test": node.name, "quote": quote,
                                    "reason": "no citation" if not quote
                                    else "citation not found in the instruction"})
                continue
            out.append(node)
        return out

    tree.body = sift(tree.body)
    grounded = ast.unparse(tree)
    return {"code": grounded, "kept": kept, "dropped": dropped,
            "kept_count": len(kept), "dropped_count": len(dropped),
            "sha256": hashlib.sha256(grounded.encode()).hexdigest()}


def contract() -> dict[str, Any]:
    body = {
        "contract_version": CONTRACT_VERSION,
        "question": "does forcing each generated test to quote the requirement it "
                    "tests reduce the rate at which banks reject correct code?",
        "single_change_from_gen58_gen60": "the generator prompt requires a verbatim "
                                          "REQUIREMENT citation per test, and a "
                                          "mechanical filter removes tests whose "
                                          "citation is not in the visible instruction",
        "unchanged": ["pinned model", "sampling", "repetitions per task",
                      "evidence-generation-gen59-v1 corpus", "frozen task order",
                      "gen60-generated-evidence-screen-v1 at b694f7b8",
                      "bank assembly by concatenation, no semantic filtering"],
        "no_critic": "no second model, no critic pass, no cross-model check",
        "grounding_source": "spec.txt only - the text the generator was already shown; "
                            "the hidden verifier and the named requirements in the "
                            "truth package are never consulted",
        "exclusion_unit": "the whole test function, because that is what pytest reports",
        "minimum_quote_words": MINIMUM_QUOTE_WORDS,
        "comparison_rule": "case-folded, punctuation-stripped, whitespace-collapsed "
                           "substring of the instruction",
        "primary_false_alarm_metric": "UNSAFE_AS_GATE rate; Gen60 baseline 4 of 8",
        "specificity_note": "retained for continuity but non-discriminating - it is "
                            "measured after the validity gate has already removed "
                            "every bank that rejects a correct tree",
        "detection_is_not_diagnosis": "a flag records that the bank failed on a wrong "
                                      "tree, not that it failed for the requirement "
                                      "that tree breaks",
        "frozen_before_exposure": True,
        "attempt": 2,
        "attempt_1_superseded": "the formatting instruction was ambiguous and the "
                                "model wrote the citation as a bare statement, which "
                                "is a syntax error; 8 of 24 outputs died in the "
                                "sanitizer. Discarded before any bank was run against "
                                "any candidate, so no outcome informed the repair. "
                                "The grounding rule is unchanged; only the formatting "
                                "instruction and its worked example differ.",
    }
    body["contract_sha256"] = hashlib.sha256(
        repr(sorted(body.items())).encode()).hexdigest()
    return body
