from manifest.rows import parse_row

def test_whitespace_stripped_from_fields():
    """REQUIREMENT: Surrounding whitespace is stripped from every field."""
    result = parse_row(' A1 , widget , north ')
    assert result['code'] == 'A1'
    assert result['label'] == 'widget'
    assert result['depot'] == 'north'

def test_blank_field_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1, ,north')
    assert result['label'] is None
    assert result['label'] != ''

def test_empty_field_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,,north')
    assert result['label'] is None
    assert result['label'] != ''

def test_whitespace_only_field_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,   ,north')
    assert result['label'] is None
    assert result['label'] != ''

def test_code_blank_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row(',widget,north')
    assert result['code'] is None

def test_depot_blank_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,widget,')
    assert result['depot'] is None

def test_all_fields_blank():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row(' , , ')
    assert result['code'] is None
    assert result['label'] is None
    assert result['depot'] is None

def test_keys_order_and_presence():
    """REQUIREMENT: parse_row(line) splits a comma-separated manifest line into a dictionary with the keys code, label and depot, in that order."""
    result = parse_row('A1,widget,north')
    assert set(result.keys()) == {'code', 'label', 'depot'}
    assert list(result.keys()) == ['code', 'label', 'depot']

def test_empty_string_label_is_distinguishable_from_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    pass