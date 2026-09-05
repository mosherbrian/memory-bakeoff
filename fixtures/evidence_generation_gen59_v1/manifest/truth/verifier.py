from manifest.rows import parse_row

full = parse_row("A1,widget,north")
assert full == {"code": "A1", "label": "widget", "depot": "north"}, f"A: {full}"
spaced = parse_row(" A1 , widget , north ")
assert spaced == {"code": "A1", "label": "widget", "depot": "north"}, f"A: {spaced}"
blank = parse_row("A1,,north")
assert blank["label"] is None, f"B: blank label -> {blank['label']!r}, expected None"
spaces = parse_row("A1,   ,north")
assert spaces["label"] is None, f"B: whitespace label -> {spaces['label']!r}, expected None"
print("VERIFIER OK")
