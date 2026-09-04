from tidewatch.gauge import Gauge


def test_gauge_reads_metres():
    assert Gauge("north quay").read(250) == 2.5
