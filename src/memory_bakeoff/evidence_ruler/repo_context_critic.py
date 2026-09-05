"""`candidate-blind-repo-context-critic-v1`: show the checker the code, not the answer.

Gen60 to Gen65 established that a checker reading one requirement sentence and
one test cannot tell an overreaching assertion from a sound inference. Both look
the same from there: `position_mm(0) == 0` and "a Windows drive letter must be
rejected" are each a claim the sentence does not literally make.

The obvious remaining variable is context. A checker that can see what the code
actually is - that `position_mm` takes a step count, that a depot name is a
relative path - has the material to tell those apart.

The danger in giving a checker context is equally obvious, and it is why this
was held back until the text-only question was closed: a checker that reads the
implementation under test will start agreeing with it, and a test that merely
agrees with the code proves nothing. That is exactly the Gen49 failure the whole
programme exists to detect.

So the boundary here is drawn deliberately, and it is what makes this an
experiment rather than a capitulation:

**Permitted** - the reference repository as shipped, before any work, and its
visible tests. This is identical for every candidate, so nothing the critic reads
can be evidence about the particular implementation being judged.

**Forbidden** - the candidate under test, any diff, the hidden evaluator, any
outcome, and the known-wrong labels.

The critic therefore learns what the code IS, and cannot learn what the
candidate DID. It stays candidate-blind while ceasing to be code-blind.

Everything else is Gen64 unchanged: same pinned model, one stateless call per
test, deletion only, and a deletion is honoured only when a specific extra
condition is named. The reader is imported from Gen64 rather than reimplemented,
so the two runs differ in exactly one respect.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from memory_bakeoff.evidence_ruler.justified_critic import (  # noqa: F401
    MINIMUM_JUSTIFICATION_WORDS, VAGUE, parse_verdict,
)

CONTRACT_VERSION = "candidate-blind-repo-context-critic-v1"

CRITIC_PROMPT = """You are reviewing a single automated test.

The test was written to check one requirement from a task instruction. You are
given the exact sentence it cites, the project as it looked BEFORE anyone worked
on it, and the test itself.

The project code is there so you can tell what the code actually is - what a
function takes, what it returns, what its inputs mean. Use it to judge whether
the test's demands make sense for this project. It is the ORIGINAL code, not
anybody's solution, so it cannot tell you what the right answer is.

Most tests are fine. A test is only a problem if it demands something the cited
sentence does not ask for - a stricter limit, an extra case, a different value,
or a behaviour neither the sentence nor the shape of the code supports.

If the test only checks what the sentence asks for, reply exactly:
KEEP

If the test demands something extra, reply with two lines:
REMOVE
EXTRA: <the specific extra condition the test imposes that the sentence does not>

The EXTRA line must name a concrete condition you can point to in the test - the
value, case or behaviour it demands. Do not write a general complaint such as
"the sentence does not require this" or "it is too strict". If you cannot name
the specific extra condition, reply KEEP.

Checking a stated requirement with several examples is NOT an extra condition.
Neither is asserting something that follows plainly from what the code is.

Cited requirement:
---
{quote}
---

The project as shipped, before any work:
{tree}

The test:
---
{test}
---
"""


def build_prompt(quote: str, test: str, tree: str) -> str:
    return CRITIC_PROMPT.format(quote=quote, test=test, tree=tree)


def isolation_report(prompt: str, forbidden: tuple[str, ...]) -> dict[str, Any]:
    """Prove the assembled prompt carries no candidate or evaluator token."""
    found = sorted({token for token in forbidden if token.lower() in prompt.lower()})
    return {"clean": not found, "found": found,
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "prompt_bytes": len(prompt.encode())}


def contract(repo_root: Path | None = None) -> dict[str, Any]:
    body = {
        "contract_version": CONTRACT_VERSION,
        "experimental_family": "repository-informed checking; NOT a continuation of "
                               "the Gen61-64 text-only line, which is closed",
        "question": "can reference repository context let the critic separate an "
                    "overreaching assertion from a sound inference, without learning "
                    "to agree with the candidate and without hollowing the banks?",
        "single_change_from_gen64": "the critic additionally sees the reference "
                                    "repository as shipped and its visible tests",
        "candidate_blind": "the repository shown is the pre-work state, identical for "
                           "every candidate, so nothing in it is evidence about the "
                           "implementation under judgement",
        "critic_inputs_permitted": ["the cited requirement sentence",
                                    "the reference repository as shipped",
                                    "the visible tests shipped with it",
                                    "the source of the single test under review"],
        "critic_inputs_forbidden": ["the candidate under test", "any diff",
                                    "the hidden evaluator", "any outcome or score",
                                    "the known-wrong labels", "any other generated test",
                                    "the Gen62 or Gen64 verdicts"],
        "unchanged_from_gen64": ["the Gen61 generated banks, byte for byte",
                                 "pinned model", "sampling", "deletion only",
                                 "one stateless call per test",
                                 "the verdict reader, imported not reimplemented",
                                 "gen63-retention-guardrail-v1"],
        "default_is_keep": "an unreadable reply, a REMOVE with no EXTRA line, a "
                           "too-short justification or a vague restatement all KEEP",
        "baseline": {"gen64_unsafe_as_gate": "4 of 8",
                     "gen64_removal_precision": 0.267,
                     "gen64_retention": "0.821-0.964",
                     "gen61_unsafe_as_gate": "4 of 8"},
        "failure_this_must_not_produce": "a critic that keeps a test because the "
                                         "shipped code happens to behave that way; "
                                         "the shipped code is the UNFIXED state, so "
                                         "agreeing with it is not agreeing with a "
                                         "candidate",
        "frozen_before_exposure": True,
    }
    body["contract_sha256"] = hashlib.sha256(
        repr(sorted(body.items())).encode()).hexdigest()
    return body
