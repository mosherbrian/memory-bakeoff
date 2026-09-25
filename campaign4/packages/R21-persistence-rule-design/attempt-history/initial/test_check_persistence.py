import json, os, tempfile
from check_persistence import check

def test_cases():
    cases = json.load(open("cases.json"))["cases"]
    with tempfile.TemporaryDirectory() as d:
        for c in cases:
            r = c.get("receipt")
            if r and not r.get("forged"):
                with open(os.path.join(d, c["id"] + ".json"), "w") as f:
                    json.dump({k: v for k, v in r.items() if k != "forged"}, f)
        for c in cases:
            ok, _ = check(c, d)
            want = c["expect"] == "pass"
            assert ok == want, (c["id"], ok, want)
