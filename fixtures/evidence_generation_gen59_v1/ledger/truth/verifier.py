from ledger.money import charge

assert charge("2.341") == "2.34", f"A: charge('2.341') -> {charge('2.341')!r}"
assert charge("7.812") == "7.81", f"A: charge('7.812') -> {charge('7.812')!r}"
assert charge("2.675") == "2.68", f"B: charge('2.675') -> {charge('2.675')!r}, expected '2.68'"
# 2.665 separates half-away-from-zero from half-to-even: the even neighbour is 2.66.
assert charge("2.665") == "2.67", f"B: charge('2.665') -> {charge('2.665')!r}, expected '2.67'"
assert charge("-2.675") == "-2.68", f"B: charge('-2.675') -> {charge('-2.675')!r}, expected '-2.68'"
print("VERIFIER OK")
