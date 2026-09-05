from manifest.rows import parse_row


def test_whitespace_stripped_from_code():
    assert parse_row(" A1 ,widget,north")["code"] == "A1"


def test_whitespace_stripped_from_label():
    assert parse_row("A1, widget ,north")["label"] == "widget"


def test_whitespace_stripped_from_depot():
    assert parse_row("A1,widget, north ")["depot"] == "north"


def test_blank_code_becomes_none():
    assert parse_row(",widget,north")["code"] is None


def test_blank_label_becomes_none():
    assert parse_row("A1,,north")["label"] is None


def test_blank_depot_becomes_none():
    assert parse_row("A1,widget,")["depot"] is None


def test_whitespace_only_code_becomes_none():
    assert parse_row(" ,widget,north")["code"] is None


def test_whitespace_only_label_becomes_none():
    assert parse_row("A1, ,north")["label"] is None


def test_whitespace_only_depot_becomes_none():
    assert parse_row("A1,widget, ")["depot"] is None


def test_all_blank_fields_become_none():
    result = parse_row(", , ")
    assert result["code"] is None
    assert result["label"] is None
    assert result["depot"] is None


def test_keys_order_is_code_label_depot():
    result = parse_row("A1,widget,north")
    keys = list(result.keys())
    assert keys == ["code", "label", "depot"]


def test_empty_label_distinguishable_from_none():
    # A field that is blank (empty or whitespace) must be None
    # This tests that we don't return "" for a missing/blank field
    result = parse_row("A1,,north")
    assert result["label"] is None
    assert result["label"] != ""


def test_whitespace_label_distinguishable_from_none():
    result = parse_row("A1, ,north")
    assert result["label"] is None
    assert result["label"] != ""


def test_single_field_line():
    result = parse_row("A1")
    assert result["code"] == "A1"
    assert result["label"] is None
    assert result["depot"] is None


def test_two_field_line():
    result = parse_row("A1,widget")
    assert result["code"] == "A1"
    assert result["label"] == "widget"
    assert result["depot"] is None


def test_extra_fields_ignored():
    result = parse_row("A1,widget,north,extra")
    assert result["code"] == "A1"
    assert result["label"] == "widget"
    assert result["depot"] == "north"


def test_no_extra_keys_in_result():
    result = parse_row("A1,widget,north")
    assert set(result.keys()) == {"code", "label", "depot"}
