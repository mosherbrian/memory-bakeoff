from manifest.rows import parse_row

def test_depot_with_whitespace_only_becomes_none():
    """REQUIREMENT: A field that is blank — empty, or only whitespace — must be reported as None, not as an empty string, so that a missing label is distinguishable from a label that happens to be empty."""
    result = parse_row('A1,widget,   ')
    assert result['depot'] is None
from manifest.rows import parse_row
from manifest.rows import parse_row