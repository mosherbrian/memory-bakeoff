"""`justified-deletion-critic-v1`: name the overreach, or leave the test alone.

Gen62's critic was asked whether a test's assertions are *entailed* by the
sentence it quotes. Read strictly, almost nothing is: a sentence of prose rarely
entails a concrete assertion about a concrete value. So it answered no to 158 of
188 tests, removed all 16 that were genuinely false along with 142 that were
fine, and earned a perfect false-alarm score by destroying the evidence.

The defect was the question, not the model. "Is this required?" invites refusal.
This asks for something a careless answer cannot supply: **name the specific
extra condition the test imposes that the quoted sentence does not.** A deletion
must come with that named condition, quoted or described concretely. No name, no
deletion - the test survives.

That inverts the default. Gen62's critic could delete by saying nothing useful;
this one has to do work to delete, and doing nothing leaves the bank intact.

Everything else is Gen62's design, unchanged: the same pinned model, one
stateless call per test, seeing only the cited sentence and that test's source,
deletion only, and an unreadable reply keeps the test. Gen63's retention
guardrail is in force, so a critic that deletes indiscriminately can no longer
be scored as a success.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

CONTRACT_VERSION = "justified-deletion-critic-v1"
MINIMUM_JUSTIFICATION_WORDS = 4

CRITIC_PROMPT = """You are reviewing a single automated test.

The test was written to check one requirement from a task instruction. The exact
sentence it cites is given below, followed by the test itself.

Most tests are fine. A test is only a problem if it demands something the cited
sentence does not ask for - a stricter limit, an extra case, a different value,
or a behaviour the sentence never mentions.

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

Cited requirement:
---
{quote}
---

The test:
---
{test}
---
"""

VAGUE = (
    "the sentence does not require this", "too strict", "not required",
    "not entailed", "goes beyond the requirement", "beyond the scope",
    "not specified", "unspecified", "the sentence is silent",
)


def parse_verdict(text: str) -> dict[str, Any]:
    """Frozen reader. A deletion needs a named condition; everything else keeps.

    Three ways to keep a test, and only one way to lose it. That asymmetry is the
    experiment: Gen62 showed a critic given a cheap route to deletion will take
    it 84% of the time.
    """
    body = text.strip()
    if not re.search(r"^\s*REMOVE\b", body, re.M | re.I):
        readable = bool(re.search(r"^\s*KEEP\b", body, re.M | re.I))
        return {"verdict": "KEEP" if readable else None, "removed": False,
                "readable": readable, "justification": None,
                "reason": None if readable else "no verdict word in the reply; test kept"}

    match = re.search(r"^\s*EXTRA:\s*(.+)$", body, re.M | re.I)
    if not match:
        return {"verdict": "REMOVE", "removed": False, "readable": True,
                "justification": None,
                "reason": "removal without an EXTRA line; test kept"}

    justification = match.group(1).strip()
    if len(justification.split()) < MINIMUM_JUSTIFICATION_WORDS:
        return {"verdict": "REMOVE", "removed": False, "readable": True,
                "justification": justification,
                "reason": "justification too short to name a condition; test kept"}
    lowered = justification.lower()
    if any(phrase in lowered for phrase in VAGUE) and len(justification.split()) < 12:
        return {"verdict": "REMOVE", "removed": False, "readable": True,
                "justification": justification,
                "reason": "justification restates the complaint without naming a "
                          "condition; test kept"}
    return {"verdict": "REMOVE", "removed": True, "readable": True,
            "justification": justification, "reason": None}


def contract() -> dict[str, Any]:
    body = {
        "contract_version": CONTRACT_VERSION,
        "question": "does requiring the critic to NAME the unsupported extra condition "
                    "stop it deleting sound tests, while still removing the false ones?",
        "single_change_from_gen62": "the critic prompt and its reader; a deletion is "
                                    "only honoured when accompanied by a named "
                                    "concrete extra condition",
        "unchanged": ["the Gen61 generated banks, byte for byte",
                      "the generator prompt", "pinned model", "sampling",
                      "one stateless call per test", "deletion only",
                      "evidence-generation-gen59-v1 corpus", "frozen task order",
                      "gen60-generated-evidence-screen-v1 at b694f7b8",
                      "gen63-retention-guardrail-v1"],
        "default_is_keep": "an unreadable reply, a REMOVE with no EXTRA line, a "
                           "too-short justification, or a vague restatement all KEEP "
                           "the test; only a named condition deletes it",
        "critic_inputs_permitted": ["the cited requirement sentence",
                                    "the source of the single test under review"],
        "critic_inputs_forbidden": ["the repository", "any candidate implementation",
                                    "the hidden verifier", "any outcome or score",
                                    "any other test", "the task name",
                                    "the Gen62 verdicts"],
        "guardrail_in_force": "a bank retaining under 50% of its tests is HOLLOWED and "
                              "inadmissible, so indiscriminate deletion cannot pass",
        "comparison": {"gen61_unsafe_as_gate": "4 of 8",
                       "gen62_removals": "158 of 188, precision 0.101",
                       "gen62_corrected_verdict": "UNEVALUABLE"},
        "explicit_note": "several examples of one stated requirement are not an extra "
                         "condition; this is stated in the prompt because it is the "
                         "distinction Gen62's critic collapsed",
        "frozen_before_exposure": True,
    }
    body["contract_sha256"] = hashlib.sha256(
        repr(sorted(body.items())).encode()).hexdigest()
    return body
