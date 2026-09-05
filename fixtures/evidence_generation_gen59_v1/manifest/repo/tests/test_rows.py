from manifest.rows import parse_row


def test_full_row():
    assert parse_row("A1,widget,north") == {
        "code": "A1", "label": "widget", "depot": "north"}
