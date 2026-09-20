# RETRO-3 — Ledger (PO seat)

1. **Close count:** S3-4 scope narrowed (no unexposed rater → disclosed seating, QUEUE); claims-expiry convention decided (24h/20min/2h, BOARD); S3-1 freeze recorded + released to build (QUEUE+BOARD); S3-8 window-report row originated; S3-9 Alice verification row originated; S3-10 PO tracking row through verification; verdicts filed (row 39 burndown PASS, BOARD); S3-1 run → Corvid verification tasked.
2. **Churn:** roughly half my turns moved queue/board state, half answered timer pings with "nothing new" — largest churn source was my own scoreboard-refresh poller trigger firing on unchanged files before Brian retired it.
3. **Event-driven grade:** B+. Gated wakes reached me well (S3-2 claim, S3-1 verdict PASS, timer trips with real content); silent when quiet after cutover. Miss: my own lane stayed on blind polling longest — the matcher/poller faults proved the old channel was load-bearing until fixed.
4. **Keep:** inactivity timers with live re-read before wake (10/20) — cheap, deterministic, caught real stalls (S3-5 stale sweep) and real staleness (rows 23/41 flags). **Kill:** per-pulse "nothing new" replies to Brian — the communication contract (translate, silence-by-default) should have applied from day one.
5. **Blind spots:** the matcher only matching numeric row IDs made all S3 rows invisible to dispatch — no gate, timer, or verifier watches the dispatcher's own parsing. Brian's outside-Claude debugging caught what the whole fleet missed.

— Ledger
