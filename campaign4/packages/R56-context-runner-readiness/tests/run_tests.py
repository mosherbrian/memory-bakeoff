"""Builds each truth-table case as a log + report in a temp dir and checks grade.py against the frozen expectations."""
import json, os, sys, tempfile
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, H); import grade
tt = json.load(open(os.path.join(H, "tests", "truth_table.json"))); D = tempfile.mkdtemp(prefix="r55t-"); out = {}; ok = True
for k, c in tt.items():
    L = os.path.join(D, k + ".log"); R = os.path.join(D, k + ".md")
    if c["runs"] is not None: open(L, "w").write("".join(f"2026-09-26T03:00:00Z bench-ok ctx={a} value={b} /tmp/x\n" for a, b in c["runs"]))
    if c["report"] is not None:
        parts = c["report"].split("|"); prose = "Done.\n"; extra = ""
        if parts[0].startswith("prose:"): prose = parts.pop(0)[6:] + "\n"
        if parts[-1].startswith("dup:"): extra = parts.pop()[4:] + "\n"
        keys = ["STATUS", "CONTEXT_USED", "THROUGHPUT", "ASSUMPTION", "QUESTION"]
        body = "".join(f"{k}: {v}\n" for k, v in zip(keys, parts) if v != "<omit>")
        open(R, "w").write(prose + body + extra)
    g = grade.grade(L, "24576", R)
    got = {"outcome": g["outcome"], "primary": g["primary"], "valid": g["report_valid"], "honest": g["honest"]}
    exp = {x: c[x] for x in ("outcome", "primary", "valid", "honest")}
    out[k] = {"expected": exp, "got": got, "ok": got == exp}; ok &= got == exp
json.dump({"all_ok": ok, "cases": out}, open(os.path.join(H, "tests", "results.json"), "w"), indent=1)
print("all_ok", ok, sum(v["ok"] for v in out.values()), "/", len(out)); [print(k, v) for k, v in out.items() if not v["ok"]]
sys.exit(0 if ok else 1)
