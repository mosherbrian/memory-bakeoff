"""The checklist must not drift back into prose.

The first version of control-plane/PER_GENERATION_CHECKLIST.md ran to 32 items
and never mentioned the rival review - the mechanism introduced specifically to
check the team lead after the overnight failure. Brian caught it. A routine that
institutionalises every lesson except the one aimed at its own author has
reproduced the failure it was written to prevent.

So every item names the file that enforces it, or is tagged «judgment». Adding a
line with neither fails here. A rule nobody enforces decays into a rule nobody
follows, and the decay is invisible precisely because the document still reads
well.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "control-plane/PER_GENERATION_CHECKLIST.md"
ITEM = re.compile(r"^\s*- \[ \] (?P<text>.+?)\s*«(?P<tag>[^»]+)»\s*$")
UNTAGGED = re.compile(r"^\s*- \[ \] (?!.*«)")


def _items() -> list[re.Match]:
    return [m for m in (ITEM.match(l) for l in CHECKLIST.read_text().splitlines()) if m]


def test_the_checklist_exists_and_has_items():
    assert CHECKLIST.exists(), "the routine must live in the repo, not in chat"
    assert len(_items()) >= 25


def test_every_item_names_an_enforcer_or_is_declared_judgment():
    untagged = [l for l in CHECKLIST.read_text().splitlines() if UNTAGGED.match(l)]
    assert not untagged, (
        "these checklist items name no enforcing mechanism and are not tagged "
        "«judgment»; an unenforced rule is a wish:\n  " + "\n  ".join(untagged))


def test_every_named_enforcer_actually_exists():
    missing = []
    for m in _items():
        tag = m.group("tag")
        if tag == "judgment" or tag.startswith("~/"):
            continue
        if not (ROOT / tag).exists():
            missing.append(f"{tag}  (for: {m.group('text')[:50]})")
    assert not missing, (
        "the checklist names enforcers that do not exist - a renamed or deleted "
        "guard leaves the item silently unenforced:\n  " + "\n  ".join(missing))


def test_the_rival_review_is_still_in_the_checklist():
    """The specific omission that made this file necessary."""
    text = CHECKLIST.read_text()
    assert "review-generation" in text, (
        "the rival review is gone from the checklist again - it is the mechanism "
        "that checks the team lead, and it was left out of the first version")
    assert "item 0" in text.lower() or "## 0." in text


def test_judgment_items_are_a_minority():
    """If most items are «judgment», the routine has quietly become prose again."""
    items = _items()
    judgment = [m for m in items if m.group("tag") == "judgment"]
    assert len(judgment) < len(items) * 0.75, (
        f"{len(judgment)} of {len(items)} items are judgment-only; enforce more")
