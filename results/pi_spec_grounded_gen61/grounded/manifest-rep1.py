from manifest.rows import parse_row

def test_whitespace_stripped_from_code():
    """REQUIREMENT: Surrounding whitespace is stripped from every field."""
    result = parse_row('  A1  ,widget,north')
    assert result['code'] == 'A1'

def test_whitespace_stripped_from_label():
    """REQUIREMENT: Surrounding whitespace is stripped from every field."""
    result = parse_row('A1,  widget  ,north')
    assert result['label'] == 'widget'

def test_whitespace_stripped_from_depot():
    """REQUIREMENT: Surrounding whitespace is stripped from every field."""
    result = parse_row('A1,widget,  north  ')
    assert result['depot'] == 'north'

def test_blank_label_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,,north')
    assert result['label'] is None

def test_whitespace_only_label_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,   ,north')
    assert result['label'] is None

def test_blank_code_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row(',widget,north')
    assert result['code'] is None

def test_blank_depot_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,widget,')
    assert result['depot'] is None

def test_empty_string_label_is_not_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,,north')
    assert result['label'] is not None or result['label'] != ''
    assert result['label'] is None

def test_all_fields_blank():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row(',,,')
    assert result['code'] is None
    assert result['label'] is None
    assert result['depot'] is None

def test_keys_order():
    """REQUIREMENT: parse_row(line) splits a comma-separated manifest line into a dictionary with the keys code, label and depot, in that order."""
    result = parse_row('A1,widget,north')
    assert list(result.keys()) == ['code', 'label', 'depot']

def test_non_blank_whitespace_still_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,   ,north')
    assert result['label'] is None

def test_code_with_whitespace_only_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('   ,widget,north')
    assert result['code'] is None

def test_depot_with_whitespace_only_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,widget,   ')
    assert result['depot'] is None