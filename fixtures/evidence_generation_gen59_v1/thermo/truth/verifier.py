from thermo.convert import to_fahrenheit

assert to_fahrenheit(100, places=2) == 212.0, f"A: {to_fahrenheit(100, places=2)}"
assert to_fahrenheit(36.6, places=2) == 97.88, f"A: {to_fahrenheit(36.6, places=2)}"
assert to_fahrenheit(36.6) == 97.9, f"B: default places -> {to_fahrenheit(36.6)}, expected 97.9"
assert to_fahrenheit(0) == 32.0, f"B: default places -> {to_fahrenheit(0)}, expected 32.0"
print("VERIFIER OK")
