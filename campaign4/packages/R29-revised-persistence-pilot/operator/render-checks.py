"""Check six rendered texts: complete per-pair body, packet/nudge counts, C/T equality after declared substitutions."""
import json, re, sys, hashlib
D, R27 = sys.argv[1], "/var/home/bmosher/memory-bake-off/campaign4/packages/R27-revised-persistence-design"
packet = open(f"{R27}/packet.md").read().strip()
NUDGES = ["Before you end your turn", "What happens next", "If it is yours, do it now", "What might I have dropped"]
out, ok = {}, True
for pair in "ABC":
    t = {a: open(f"{D}/texts/R29-{pair}-{a}.txt").read() for a in "CT"}
    for a in "CT":
        x = t[a]
        r = {"bytes": len(x), "sha256": hashlib.sha256(x.encode()).hexdigest(),
             "packet_count": x.count(packet), "nudge_hits": [n for n in NUDGES if n in x],
             "control_note": x.count("No additional notes."),
             "body_parts": {k: v in x for k, v in {"goal": "P-INDEX-7", "failed_step": "step 2/4",
                 "allowed_command": "pindex_cli.py --action", "scope": "Scope: local files only",
                 "docs": f"--docs fixtures/docs-{pair}", "arm": f"--arm {a}", "exec": f"ex-R29-{pair}-{a}-w1"}.items()},
             "other_docs": sorted(set(re.findall(r"fixtures/docs-[A-Z]", x)) - {f"fixtures/docs-{pair}"})}
        r["ok"] = (all(r["body_parts"].values()) and not r["nudge_hits"] and not r["other_docs"]
                   and (r["packet_count"], r["control_note"]) == ((1, 0) if a == "T" else (0, 1)))
        ok &= r["ok"]; out[f"{pair}-{a}"] = r
    norm = lambda x, a: x.replace(packet, "<HEAD>").replace("No additional notes.", "<HEAD>").replace(
        f"--arm {a}", "--arm <ARM>").replace(f"ex-R29-{pair}-{a}-w1", "<EXEC>").replace(f"R29-{pair}-{a}", "<QID>").replace(f"{pair}-{a}", "<PAIR-ARM>")  # declared path substitutions
    eq = norm(t["C"], "C") == norm(t["T"], "T")
    out[f"{pair}-equal_after_substitutions"] = eq; ok &= eq
out["all_ok"] = ok
json.dump(out, open(f"{D}/checks.json", "w"), indent=1)
print("all_ok", ok); sys.exit(0 if ok else 1)
