import json

import pytest

from memory_bakeoff.om_context_production import ANCHORS, CASES, assert_lexical_isolation, fixture_sha256, folded_entries, grade_reader, parse_reader_response, projection_support, public_turns, reader_prompt, rendered_context


def test_frozen_fixture_shape_and_isolation():
    assert len(ANCHORS) == 16
    assert len(CASES) == 12
    assert len(public_turns()) == 40
    assert len({anchor for _, anchor in public_turns() if anchor}) == 16
    assert fixture_sha256() == fixture_sha256()
    assert_lexical_isolation()


def test_product_turns_cannot_contain_reader_truth():
    exposed = "\n".join(text for text, _ in public_turns()).lower()
    assert all(case.question.lower() not in exposed for case in CASES)
    assert "canonical_observation_id" not in exposed


def test_fold_projection_maps_native_entries_and_uses_rendered_summary_only():
    entry = {"type": "compaction", "summary": "[obs-1] retained note", "details": {"type": "om.folded", "observations": [{"id": "obs-1", "sourceEntryIds": ["native-a"]}], "reflections": [{"id": "ref-1", "supportingObservationIds": ["obs-1"]}]}}
    assert folded_entries([{}, entry]) == [entry]
    assert rendered_context(entry) == "[obs-1] retained note"
    assert projection_support(entry, {"native-a": "A01"}) == {"obs-1": {"A01"}, "ref-1": {"A01"}}


def test_reader_is_fail_closed_and_requires_supported_citation():
    case = CASES[0]
    support = {"obs-8": {"A08"}}
    good = parse_reader_response(json.dumps({"answer": "quartz", "citations": ["obs-8"]}))
    assert grade_reader(case, good, support)["pass"]
    bad = parse_reader_response(json.dumps({"answer": "quartz", "citations": []}))
    assert not grade_reader(case, bad, support)["pass"]
    with pytest.raises(ValueError):
        parse_reader_response("quartz")


def test_reader_prompt_accepts_only_rendered_context():
    prompt = reader_prompt("[obs-1] retained", "Which profile?")
    assert "RENDERED_MEMORY" in prompt
    assert "Which profile?" in prompt
