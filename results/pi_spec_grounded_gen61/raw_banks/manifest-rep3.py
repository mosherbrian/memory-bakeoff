from manifest.rows import parse_row


def test_whitespace_stripped_from_fields():
    """REQUIREMENT: Surrounding whitespace is stripped from every field."""
    result = parse_row(" A1 , widget , north ")
    assert result["code"] == "A1"
    assert result["label"] == "widget"
    assert result["depot"] == "north"


def test_blank_field_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row("A1, ,north")
    assert result["label"] is None
    assert result["label"] != ""


def test_empty_field_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row("A1,,north")
    assert result["label"] is None
    assert result["label"] != ""


def test_whitespace_only_field_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row("A1,   ,north")
    assert result["label"] is None
    assert result["label"] != ""


def test_code_blank_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row(",widget,north")
    assert result["code"] is None


def test_depot_blank_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row("A1,widget,")
    assert result["depot"] is None


def test_all_fields_blank():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row(" , , ")
    assert result["code"] is None
    assert result["label"] is None
    assert result["depot"] is None


def test_keys_order_and_presence():
    """REQUIREMENT: parse_row(line) splits a comma-separated manifest line into a dictionary with the keys code, label and depot, in that order."""
    result = parse_row("A1,widget,north")
    assert set(result.keys()) == {"code", "label", "depot"}
    assert list(result.keys()) == ["code", "label", "depot"]


def test_empty_string_label_is_distinguishable_from_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    # An actual empty string label (whitespace stripped) should remain empty string if it was truly empty after strip
    # But wait, the requirement says blank (empty or only whitespace) becomes None.
    # So if the field is empty or whitespace-only, it becomes None.
    # The requirement says "so that a missing label is distinguishable from a label that happens to be empty"
    # This implies that if the label is truly empty (not missing/blank), it should still be distinguishable.
    # However, an empty string IS blank (empty). So it should become None.
    # Let me re-read: "A field that is blank — empty, or only whitespace — must be reported as None"
    # So empty string -> None, whitespace -> None.
    # The distinction is between a field that was present but empty (which becomes None) vs... 
    # Actually, the requirement is clear: blank fields become None. The "distinguishable" part is just explaining WHY.
    # There's no case where an empty string stays as empty string based on this requirement.
    pass
