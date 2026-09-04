from ferry.schedule import next_sailing


def test_next_sailing():
    assert next_sailing("06:30") == "07:30"
