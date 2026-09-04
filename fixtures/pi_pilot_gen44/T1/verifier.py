import sys
sys.path.insert(0, ".")
from tidewatch.gauge import Gauge
from tidewatch.units import cm_to_m, m_to_cm
from tidewatch.report import inches_to_feet

assert cm_to_m(250) == 2.5, "cm_to_m is wrong"
assert m_to_cm(2.5) == 250, "m_to_cm is wrong"
assert Gauge("north quay").read(250) == 2.5, "gauge reading is wrong"
assert inches_to_feet(24) == 2, "report scaling must not be changed"
print("VERIFIER OK")
