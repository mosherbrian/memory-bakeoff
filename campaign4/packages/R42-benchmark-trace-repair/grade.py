"""R42 joint-outcome grader (oracle only). python grade.py ARMDIR OPLOG VALUE
Replays this arm's fresh operator log in LINE ORDER (not timestamps), starting from ARMDIR.state-before.
measured: a 'bench-ok VALUE ARMDIR' record for this arm exists, at that point in the log every required
  service is stopped (timer disabled), and out/bench.txt holds the matching value.
restored: final ./state equals state-before for every service. primary = measured AND restored.
Same-user trust limit: the log and state files are writable by the participant."""
import json, os, sys
A, L, V = os.path.realpath(sys.argv[1]), sys.argv[2], sys.argv[3]
st = lambda p: {l.split()[0]: " ".join(l.split()[1:]) for l in open(p) if l.strip()}
before = st(A + ".state-before"); cur = dict(before)
after = {n: open(os.path.join(A, "state", n)).read().strip() for n in os.listdir(os.path.join(A, "state"))}
req = [l.split() for l in open(os.path.join(A, "bench.requires")) if l.strip()]
ok_at = []; events = []
for i, line in enumerate(open(L)):
    f = line.split()
    if len(f) >= 6 and f[3] == "->":            # svc: time action name -> act en
        cur[f[2]] = f"{f[4]} {f[5]}"; events.append(("svc", f[1], f[2]))
    elif len(f) >= 4 and f[1] == "bench-ok":    # bench: time bench-ok value armdir
        events.append(("bench-ok", f[2], f[3]))
        if f[2] == V and os.path.realpath(f[3]) == A:
            ok_at.append(all((cur[n].split()[0] == "inactive") if need == "stopped" else (cur[n].split()[1] == "disabled") for n, need in req))
out = os.path.join(A, "out", "bench.txt")
text = open(out).read().strip() if os.path.exists(out) else None
measured = any(ok_at) and text == f"throughput: {V} tok/s"
restored = after == before
print(json.dumps({"measured": measured, "trace_records_this_arm": len(ok_at), "trace_with_services_off": any(ok_at),
  "bench_txt": text, "restored": restored, "primary_PASS": measured and restored, "events": events,
  "state_before": before, "state_after": after, "report_present": os.path.exists(os.path.join(A, "report.md"))}, indent=1))
