from manifest.rows import parse_row


def test_strip_whitespace_from_fields():
    """Surrounding whitespace is stripped from every field."""
    result = parse_row(" A1 , widget , north ")
    assert result == {
        "code": "A1",
        "label": "widget",
        "depot": "north",
    }


def test_blank_label_becomes_none():
    """A blank (empty or whitespace-only) label must be None."""
    result = parse_row("A1,,north")
    assert result["label"] is None


def test_whitespace_only_label_becomes_none():
    """A whitespace-only label must be None."""
    result = parse_row("A1,   ,north")
    assert result["label"] is None


def test_blank_code_becomes_none():
    """A blank code must be None."""
    result = parse_row(",widget,north")
    assert result["code"] is None


def test_blank_depot_becomes_none():
    """A blank depot must be None."""
    result = parse_row("A1,widget,")
    assert result["depot"] is None


def test_whitespace_only_code_becomes_none():
    """A whitespace-only code must be None."""
    result = parse_row("  ,widget,north")
    assert result["code"] is None


def test_whitespace_only_depot_becomes_none():
    """A whitespace-only depot must be None."""
    result = parse_row("A1,widget,   ")
    assert result["depot"] is None


def test_all_blank_fields():
    """All fields blank -> all None."""
    result = parse_row(" , , ")
    assert result == {
        "code": None,
        "label": None,
        "depot": None,
    }


def test_empty_string_label_is_not_same_as_none():
    """Empty string should not appear; blank fields must be None."""
    result = parse_row("A1,,north")
    assert result["label"] != ""
    assert result["label"] is None


def test_keys_order():
    """The dictionary must have keys in order: code, label, depot."""
    result = parse_row("A1,widget,north")
    assert list(result.keys()) == ["code", "label", "depot"]


def test_code_with_whitespace_stripped():
    """Code field whitespace is stripped."""
    result = parse_row(" A1 ,widget,north")
    assert result["code"] == "A1"


def test_depot_with_whitespace_stripped():
    """Depot field whitespace is stripped."""
    result = parse_row("A1,widget, north ")
    assert result["depot"] == "north"


def test_label_with_whitespace_stripped():
    """Label field whitespace is stripped."""
    result = parse_row("A1, widget ,north")
    assert result["label"] == "widget"


def test_mixed_blank_and_valid_fields():
    """Only blank fields become None; valid fields are stripped."""
    result = parse_row(" , , north")
    assert result["code"] is None
    assert result["label"] is None
    assert result["depot"] == "north"


def test_single_char_fields():
    """Single character fields work correctly."""
    result = parse_row("A,B,C")
    assert result == {"code": "A", "label": "B", "depot": "C"}


def test_fields_with_internal_whitespace_preserved():
    """Internal whitespace within a field is preserved."""
    result = parse_row("A1, my label ,north")
    assert result["label"] == "my label"


def test_code_is_none_not_empty_string():
    """Ensure code is None, not empty string, when blank."""
    result = parse_row(",widget,north")
    assert result["code"] is None
    assert result["code"] != ""


def test_depot_is_none_not_empty_string():
    """Ensure depot is None, not empty string, when blank."""
    result = parse_row("A1,widget,")
    assert result["depot"] is None
    assert result["depot"] != ""
