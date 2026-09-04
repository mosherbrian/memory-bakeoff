import sys
sys.path.insert(0, ".")
from ferry.schedule import next_sailing, as_list

# requirement A: the new sailing and the None behaviour
assert next_sailing("11:00") == "12:00", f"A: got {next_sailing('11:00')}"
assert next_sailing("12:30") is None, f"A: expected None, got {next_sailing('12:30')}"
# requirement B: as_list still returns a plain list of strings
value = as_list()
assert isinstance(value, list), f"B: as_list returned {type(value).__name__}"
assert all(isinstance(v, str) for v in value), "B: as_list must contain strings"
assert "12:00" in value, "B: the new sailing should appear in as_list"
print("VERIFIER OK")
