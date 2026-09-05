"""`entailment-critic-ablation-v1`: ask whether the quote really licenses the test.

Gen61 established that provenance is not the problem. The generator quotes real
requirements - 223 citations, 223 of them genuine - and then overextends what
those requirements demand. `pathsafe` quotes "must be refused by raising
ValueError" and goes on to insist a Windows drive letter be refused; `culvert`
quotes "must keep reporting the SAME number of steps" and then asserts 80 where
the same number is 40.

That is a semantic judgement, not a lookup, so this component adds the first
second-pass model in the programme: the same pinned weights, in a separate
stateless call, asked one question per test - is what this test asserts actually
entailed by the sentence it cites? Tests judged not entailed are removed.

The critic is deliberately given very little. It sees the cited requirement and
the test source, and nothing else: no repository, no candidate implementation,
no hidden verifier, no outcome, and no other test. It cannot know whether
removing a test helps or hurts, which is what keeps its judgement independent of
the score.

The banks themselves are frozen. Gen61's generated tests are not regenerated,
rewritten or reordered; the critic may only delete.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

CONTRACT_VERSION = "entailment-critic-ablation-v1"

CRITIC_PROMPT = """You are reviewing a single automated test.

The test was written to check one requirement from a task instruction. The exact
sentence it cites is given below, followed by the test itself.

Answer one question: is everything the test asserts REQUIRED by the cited
sentence?

Answer ENTAILED if every assertion follows from the cited sentence.
Answer NOT_ENTAILED if the test asserts anything the sentence does not require -
a stricter condition, an extra case, a different value, or a behaviour the
sentence is silent about.

Judge only against the cited sentence. Do not guess what the wider project might
want, and do not reward a test for being reasonable.

Reply with exactly one word on the first line, ENTAILED or NOT_ENTAILED, then one
short line giving your reason.

Cited requirement:
---
{quote}
---

The test:
---
{test}
---
"""

VERDICTS = ("ENTAILED", "NOT_ENTAILED")


def parse_verdict(text: str) -> dict[str, Any]:
    """Frozen reader. An unreadable answer KEEPS the test.

    Defaulting to keep matters: it means the critic can only reduce the bank when
    it actually says so, and a malformed reply cannot quietly delete evidence.
    """
    head = text.strip().upper()
    # NOT_ENTAILED contains ENTAILED, so the negative must be tested first.
    match = re.search(r"\bNOT[_ ]?ENTAILED\b", head)
    if match:
        return {"verdict": "NOT_ENTAILED", "removed": True, "readable": True}
    if re.search(r"\bENTAILED\b", head):
        return {"verdict": "ENTAILED", "removed": False, "readable": True}
    return {"verdict": None, "removed": False, "readable": False,
            "reason": "no verdict word in the reply; test kept"}


def contract() -> dict[str, Any]:
    body = {
        "contract_version": CONTRACT_VERSION,
        "question": "can a second pass by the same model remove the assertions that "
                    "overextend a correctly quoted requirement, without removing the "
                    "assertions that catch wrong implementations?",
        "single_change_from_gen61": "a critic pass over the frozen Gen61 banks; the "
                                    "critic may delete a test and may do nothing else",
        "unchanged": ["the Gen61 generated banks, byte for byte",
                      "the generator prompt", "pinned model", "sampling",
                      "evidence-generation-gen59-v1 corpus", "frozen task order",
                      "gen60-generated-evidence-screen-v1 at b694f7b8"],
        "critic_is_the_same_model": "the same pinned weights as the generator, in a "
                                    "separate stateless call; this is a second pass, "
                                    "not a second opinion, and cross-model "
                                    "independence remains untested",
        "critic_inputs_permitted": ["the cited requirement sentence",
                                    "the source of the single test under review"],
        "critic_inputs_forbidden": ["the repository", "any candidate implementation",
                                    "the hidden verifier", "any outcome or score",
                                    "any other test", "the task name"],
        "unreadable_reply_keeps_the_test": "so a malformed answer cannot silently "
                                           "delete evidence",
        "deletion_only": "the critic cannot edit, reorder or add a test",
        "primary_comparison": {"gen61_unsafe_as_gate": "4 of 8",
                               "gen61_sensitivity": 1.0},
        "secondary_measurement": "of the 27 assertions known to be false, because they "
                                 "reject a trusted positive, how many does the critic "
                                 "remove; and how many assertions that reject no "
                                 "positive does it remove wrongly",
        "labels_are_evaluator_side": "known-false and valid labels come from running "
                                     "each test against the trusted positives; the "
                                     "critic never sees them",
        "frozen_before_exposure": True,
    }
    body["contract_sha256"] = hashlib.sha256(
        repr(sorted(body.items())).encode()).hexdigest()
    return body
