from valve.limits import opening_percent

assert opening_percent(150) == 100, f"A: opening_percent(150) -> {opening_percent(150)}"
assert opening_percent(40) == 40, f"A: opening_percent(40) -> {opening_percent(40)}"
assert opening_percent(-5) == 0, f"B: opening_percent(-5) -> {opening_percent(-5)}, expected 0"
assert opening_percent(-1) == 0, f"B: opening_percent(-1) -> {opening_percent(-1)}, expected 0"
print("VERIFIER OK")
