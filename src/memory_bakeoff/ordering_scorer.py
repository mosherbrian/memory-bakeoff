"""The scorer fixed by research/pilot_ordering/PREREGISTRATION.md section 4.

Written to the specification, not tuned to any outcome. Every rule here is
traceable to a line of that document; nothing was added because it improved a
number. The pilot's crude scorer marked `4` wrong against gold `four`, a
false-negative class that hits BOTH arms and so cannot create a direction - but
it wastes items, so the specification removes it.

Deliberately NOT an LLM judge and NOT a new dependency.
"""
from __future__ import annotations

import re

# zero..twenty and the ordinals, per the specification. Not extended: a number
# outside this range in a gold value is compared as digits or not at all.
_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve "
          "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty").split()
_ORDINALS = ("zeroth first second third fourth fifth sixth seventh eighth ninth "
             "tenth eleventh twelfth thirteenth fourteenth fifteenth sixteenth "
             "seventeenth eighteenth nineteenth twentieth").split()
_WORD_TO_DIGIT = {w: str(i) for i, w in enumerate(_WORDS)}
_WORD_TO_DIGIT.update({w: str(i) for i, w in enumerate(_ORDINALS)})
_DIGIT_TO_WORD = {str(i): w for i, w in enumerate(_WORDS)}

_NUM = re.compile(r"\d[\d,]*(?:[.:]\d+)*")
_WORDCHARS = re.compile(r"[a-z0-9]+")


def normalise(text: str) -> str:
    """Casefold, drop terminal punctuation, strip currency and thousands marks."""
    t = str(text).casefold().strip()
    t = t.strip(" .!?,;:\"'")
    t = re.sub(r"[$£€]", "", t)
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)
    return re.sub(r"\s+", " ", t)


def _number_variants(t: str) -> set[str]:
    """The same string with spelled numbers as digits, and digits as words."""
    out = {t}
    toks = t.split()
    if any(w.strip(" .!?,;:") in _WORD_TO_DIGIT for w in toks):
        out.add(" ".join(_WORD_TO_DIGIT.get(w, w) for w in toks))
    if any(w in _DIGIT_TO_WORD for w in toks):
        out.add(" ".join(_DIGIT_TO_WORD.get(w, w) for w in toks))
    return out


def numeric_tokens(text: str) -> list[str]:
    """Numbers in the text, thousands separators removed, spelled numbers mapped."""
    t = normalise(text)
    nums = [n.replace(",", "") for n in _NUM.findall(t)]
    nums += [_WORD_TO_DIGIT[w] for w in t.split() if w in _WORD_TO_DIGIT]
    return nums


def _contains_at_word_boundary(haystack: str, needle: str) -> bool:
    """Containment that will not match `one` inside `money`.

    Plain substring containment scored gold `one` against the answer "I spent
    the money". This repo has shipped that bug before - a bare `sol` matched
    inside `resolver` and `solstice` in the leak gate - so the boundary is not
    an optimisation, it is the known failure mode of this exact operation.
    """
    return re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack) is not None


def hit(gold: str, answer: str) -> bool:
    """PREREGISTRATION section 4. HIT iff the normalised gold is contained in the
    normalised answer under number-form equivalence, OR every numeric token of
    the gold appears in the answer.

    Containment is deliberately one-directional: an answer that says more than
    the gold ("your best time is 25:50") is a HIT. The specification records the
    accepted consequence - an answer naming BOTH values also scores HIT.
    """
    g, a = normalise(gold), normalise(answer)
    if not g:
        return False
    gv, av = _number_variants(g), _number_variants(a)
    if any(_contains_at_word_boundary(y, x) for x in gv for y in av):
        return True
    gn = numeric_tokens(gold)
    if gn:
        an = set(numeric_tokens(answer))
        return all(n in an for n in gn)
    return False
