from manifest.rows import parse_row


def test_trailing_whitespace_stripped():
    """Whitespace around fields should be stripped."""
    result = parse_row(" A1 , widget , north ")
    assert result["code"] == "A1"
    assert result["label"] == "widget"
    assert result["depot"] == "north"


def test_blank_label_becomes_none():
    """A blank (empty) label field must be reported as None."""
    result = parse_row("A1,,north")
    assert result["label"] is None
    assert result["label"] != ""


def test_whitespace_only_label_becomes_none():
    """A label field containing only whitespace must be reported as None."""
    result = parse_row("A1,   ,north")
    assert result["label"] is None
    assert result["label"] != ""


def test_blank_code_becomes_none():
    """A blank code field must be reported as None."""
    result = parse_row(",widget,north")
    assert result["code"] is None
    assert result["code"] != ""


def test_blank_depot_becomes_none():
    """A blank depot field must be reported as None."""
    result = parse_row("A1,widget,")
    assert result["depot"] is None
    assert result["depot"] != ""


def test_whitespace_only_code_becomes_none():
    """A code field containing only whitespace must be reported as None."""
    result = parse_row("   ,widget,north")
    assert result["code"] is None


def test_whitespace_only_depot_becomes_none():
    """A depot field containing only whitespace must be reported as None."""
    result = parse_row("A1,widget,   ")
    assert result["depot"] is None


def test_all_fields_blank():
    """All blank fields should all be None."""
    result = parse_row(",,")
    assert result["code"] is None
    assert result["label"] is None
    assert result["depot"] is None


def test_keys_order():
    """The returned dictionary must have keys in the order: code, label, depot."""
    result = parse_row("A1,widget,north")
    assert list(result.keys()) == ["code", "label", "depot"]


def test_distinct_none_vs_empty_string():
    """None must be distinguishable from empty string."""
    result_blank = parse_row("A1,,north")
    result_empty_label = parse_row("A1,,north")  # same as blank
    
    # Verify that blank label is None, not empty string
    assert result_blank["label"] is None
    assert result_blank["label"] != ""
    
    # Verify that a non-blank label is not None
    result_with_label = parse_row("A1,widget,north")
    assert result_with_label["label"] == "widget"
    assert result_with_label["label"] is not None
