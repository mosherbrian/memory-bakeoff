"""Analyse one realprocess.sh output directory. Usage: python analyse.py OUTDIR. Prints facts only; no verdict is
assumed by the parser: each line states what was measured."""
import collections, glob, json, os, re, statistics, sys

d = sys.argv[1]
rd = lambda n: open(os.path.join(d, n)).read() if os.path.exists(os.path.join(d, n)) else ''
env = dict(kv.split('=') for kv in rd('env.txt').split() if re.match(r'^(stall_start|stall_end|stop_at)=', kv))
print('== env'); print(rd('env.txt').strip())

# 1. accepted markers: first and last time seen in the 0.5 s samples
seen, last = {}, {}
samples = []
for l in rd('samples.log').splitlines():
    t, due, pas = l.split(' ', 2)
    t = float(t); names = [n for n in due[4:].split(',') if n]
    samples.append((t, names, pas))
    for n in names:
        seen.setdefault(n, t); last[n] = t
dl = {}
for l in rd('callbacks.log').splitlines():
    q = l.split()[0]; kv = dict(x.split('=') for x in l.split()[1:]); dl[q] = kv
print('\n== backlog: %d distinct accepted due markers observed (pre-registered N=14, required >= 12)' % len(seen))
cb_rc = collections.Counter(v['rc'] for v in dl.values())
print('callbacks: %d processes, rc %s' % (len(dl), dict(cb_rc)))
for q in sorted(dl):
    out = rd('cb-%s.out' % q)
end_t = samples[-1][0] if samples else 0
order_w = sorted(seen, key=lambda n: (seen[n], n))
settled = {n: last[n] + 0.5 for n in seen if last[n] < end_t - 0.25}
order_s = sorted(settled, key=lambda n: (settled[n], n))
inv = sum(1 for i, a in enumerate(order_s) for b in order_s[i + 1:] if order_w.index(a) > order_w.index(b))
print('settled (marker gone) within the finite window: %d of %d; never settled: %s' % (len(settled), len(seen), sorted(set(seen) - set(settled))))
print('drain order: %d pairwise inversions against first-seen order (0.5 s sample resolution; ties by name)' % inv)
lat = []
for n in order_s:
    q = n.split('-')[0]; dead = float(dl.get(q, {}).get('deadline', 'nan'))
    lat.append((settled[n] - dead, settled[n] - seen[n], n))
    print('  %-12s deadline=%s marker_seen=+%.1fs settled=+%.1fs after deadline (marker age at settlement %.1fs)' % (n, int(dead), seen[n] - dead, settled[n] - dead, settled[n] - seen[n]))
if lat:
    print('MAX settlement latency after deadline: %.1fs (%s); MAX marker age: %.1fs; n=%d (empirical, this host, this workload)' % (max(lat)[0], max(lat)[2], max(x[1] for x in lat), len(lat)))
print('final due dir:', rd('due-dir-final.txt').strip().replace('\n', ' | '))

# 2. final ledger state of every backlog package
print('\n== final status (status --json after the window)')
try:
    st = json.loads(rd('status-final.json'))
    for p in st['packages']:
        if p['qid'].startswith('B'):
            t = p.get('timeout') or {}
            print('  %s step=%s cancel=%s director=%s duty=%s at=%s deferred=%s' % (p['qid'], p['step'], t.get('cancel'), t.get('director'), t.get('duty'), t.get('at'), t.get('deferred_callback')))
    print('  B timed-out: %d of %d; outbox_pending=%s' % (sum(1 for p in st['packages'] if p['qid'].startswith('B') and p['step'] == 'timed-out'), sum(1 for p in st['packages'] if p['qid'].startswith('B')), st.get('outbox_pending')))
    print('  ordinary packages registered: %d' % sum(1 for p in st['packages'] if p['qid'].startswith('O')))
except Exception as e:
    print('  status unreadable: %r %s' % (e, rd('status-final.err')[:300]))
arr = rd('arrivals.log').splitlines()
print('ordinary arrivals: %d attempted, rc %s' % (len(arr), dict(collections.Counter(l.split()[1] for l in arr))))

# 3. lock holds, hand-offs, yields
ev = [l.split() for l in rd('lock.log').splitlines()]
open_, holds = {}, []
for e in ev:
    t, pid, what, cmd = int(e[0]) / 1e9, e[1], e[2], (e[3] if len(e) > 3 else '')
    if what == 'acquire': open_[pid] = (t, cmd)
    elif pid in open_: s, c = open_.pop(pid); holds.append((s, t, pid, c))
print('\n== lock: %d completed holds; unreleased at end (a killed holder shows here): %s' % (len(holds), {p: c for p, (s, c) in open_.items()}))
wk = []
for l in rd('wake.log').splitlines():
    f = l.split(' ', 6)
    wk.append(dict(s=float(f[0]), e=None if f[1] == '-' else float(f[1]), pid=f[2], seat=f[3], kind=f[4], out=f[5], text=f[6] if len(f) > 6 else ''))
by = collections.defaultdict(list); local = collections.defaultdict(list)
for s, e, pid, c in holds:
    by[c].append(e - s)
    iv = sorted((max(w['s'], s), min(w['e'] if w['e'] else e, e)) for w in wk if w['pid'] == pid and w['s'] < e and (w['e'] or e) > s)
    io, cur = 0.0, None
    for a, b in iv:
        if cur and a <= cur[1]: cur = (cur[0], max(cur[1], b))
        else:
            if cur: io += cur[1] - cur[0]
            cur = (a, b)
    if cur: io += cur[1] - cur[0]
    if c != 'fixture': local[c].append((e - s) - io)
for c in sorted(by):
    v = by[c]; print('  hold %-15s n=%-4d max=%.2fs median=%.3fs' % (c, len(v), max(v), statistics.median(v)))
allloc = [x for v in local.values() for x in v]
print('\n== local (non-subprocess) time inside holds = hold - union of stub wake intervals of the holder')
for c in sorted(local):
    v = sorted(local[c]); print('  %-15s n=%-4d max=%.3fs p50=%.3fs p95=%.3fs' % (c, len(v), v[-1], statistics.median(v), v[int(0.95 * (len(v) - 1))]))
if allloc: print('  ALL holders n=%d MAX local=%.3fs (includes fork/exec of stubs, SQLite, file I/O, CPU; empirical, not a guarantee)' % (len(allloc), max(allloc)))
runs = sorted([h for h in holds if h[3] == 'run'], key=lambda h: h[0])
yl = [l for f in sorted(glob.glob(os.path.join(d, 'run*.out'))) for l in open(f) if 'yield' in l]
hb = [s for s in samples if '"yielded":true' in s[2]]
print('\n== yield: %d yield lines in run output; %d heartbeat samples with yielded=true' % (len(yl), len(hb)))
for l in yl[:5]: print('  ', l.strip())
if hb: print('   heartbeat sample:', hb[0][2][:200])
seq = sorted(holds, key=lambda h: h[0])
hand = collections.Counter()
for i, h in enumerate(seq[:-1]):
    if h[3] == 'run': hand['run->' + seq[i + 1][3]] += 1
gaps = [(b[0] - a[1], a[1]) for a, b in zip(runs, runs[1:])]
if gaps: g = max(gaps); print('  longest gap between run holds: %.1fs (from %.1f s after the stall start); run pass skips (E_LEDGER_BUSY): %d' % (g[0], g[1] - float(env['stall_start']), sum(open(f).read().count('pass skipped') for f in glob.glob(os.path.join(d, 'run*.out')))))
print('  hand-offs after a run hold (next holder): %s' % dict(hand))
# yields matched to their run hold: the run hold whose release precedes the yield line's print
print('  run holds >= 4s (budget spent on due work): %d; longest run hold %.2fs' % (sum(1 for h in runs if h[1] - h[0] >= 4), max((h[1] - h[0] for h in runs), default=0)))

# 4. effects vs attempts per backlog package, SATURATED, ambiguous delivery
print('\n== transport: attempts (lines) vs effects (ok|landed) vs failures')
print('  by kind/outcome: %s' % dict(collections.Counter((w['kind'], w['out']) for w in wk)))
sat = [w for w in wk if 'SATURATED' in w['text']]
print('  SATURATED notices to duty: %d attempts, outcomes %s; first: %s' % (len(sat), dict(collections.Counter(w['out'] for w in sat)), sat[0]['text'][:140] if sat else '-'))
eff = collections.Counter((w['seat'], w['text']) for w in wk if w['out'] in ('ok', 'landed') and w['kind'] == 'notice' and 'SATURATED' not in w['text'])
dups = {k: v for k, v in eff.items() if v > 1}
print('  identical notice EFFECTS delivered more than once: %d %s' % (len(dups), [(k[0], k[1][:90], v) for k, v in dups.items()]))
per = collections.defaultdict(collections.Counter)
for w in wk:
    m = re.search(r'\] (B\d\d):', w['text']) or re.search(r'deadline-expired:(B\d\d)', w['text'])
    if m and w['kind'] == 'notice': per[m.group(1)][w['seat'] + ':' + w['out']] += 1
for q in sorted(per): print('  %s notices %s' % (q, dict(per[q])))
amb = [w for w in wk if w['kind'] == 'dispatch' and w['out'] == 'landed']
rep = [w for w in wk if w['kind'] == 'dispatch' and w['out'] == 'replied']
print('  slow ordinary dispatches: %d landed (effect) / %d replied before the sender stopped waiting -> %d ambiguous deliveries (effect landed, sender saw no receipt)' % (len(amb), len(rep), len(amb) - len(rep)))

# 5. crash
if os.path.exists(os.path.join(d, 'crash-pre.txt')):
    print('\n== crash'); print(rd('crash-pre.txt').strip())
    kp = re.search(r'run_pid=(\d+)', rd('crash-pre.txt'))
    if kp:
        k = kp.group(1)
        ka = float(re.search(r'kill_at=([\d.]+)', rd('crash-pre.txt')).group(1))
        inflight = [w for w in wk if w['pid'] == k and (w['e'] is None or w['e'] > ka)]
        print('  sends by the killed run that ended after the kill (effect after the sender died): %s' % [(w['seat'], w['out'], w['text'][:80]) for w in inflight])
        pre = re.findall(r'(B\d\d-w1\.json)', rd('crash-pre.txt'))
        print('  markers present at the kill: %d %s; settled afterwards: %s' % (len(pre), pre, all(n in settled for n in pre)))
