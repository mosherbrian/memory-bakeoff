from pathsafe.paths import resolve

assert resolve("parts.csv") == "depot/parts.csv", f"A: {resolve('parts.csv')}"

for bad in ("/etc/passwd", "../secrets", "a/../../b"):
    try:
        result = resolve(bad)
    except ValueError:
        continue
    raise AssertionError(f"B: resolve({bad!r}) -> {result!r}, expected ValueError")
print("VERIFIER OK")
