# P6-r10-live-recovery-matrix — pinned four-case acceptance checklist

Pinned by corvid-dsh at admission `P6r10-admission-1`, 2026-09-22T16:5xZ.
Brief pin: `package.md` sha256 `b6585efa82d9d921a350d44f22abf014deb20a5a3b588560413ecdee2b93923f`.
Candidate pin: `f1d7c86f0b38fb653734beb9d906dae44a10a41a`, manifest `161afac5…`,
exact CLI `case_entry.py` sha256 `9a1bb23c…`. Cases run one at a time, in order:
lost-completion, failed-verification, queued-ambiguous-restart, quiet-rest.
Each case must satisfy every item below; missing evidence is INCOMPLETE, never a
simulated PASS.

Each case's release must carry, bound to per-file hashes:
1. **Bound release** — Tern `stagec-task` signature over plan+config+binding+
   code manifest; fresh suite root/actions/executions; no old stopped sessions
   or expired signatures; `simulated=false`; no manual send or substitute
   emulator.
2. **Real identity/transport/runtime** — raw launch records → canonical
   corrected binding; live sockets/incarnations/registry/lanes checked;
   `derive-config` rc0; pre-armed exact-ID archive/cleanup verified before
   launch.
3. **Applied fault** — `faults/<case>.applied.json` with actor/control/params,
   `induced=true` for fault cases; independent source onset
   (`onset_protocol`) with finite uncertainty; `_check_causal` armed<onset<det
   (case_entry.py:845-886).
4. **Claims/artifact/verdict** — worker and verifier claims, recomputed
   artifact hashes, durable ledger/outbox, `committed_actions`/`settled_actions`
   and `timecheck`.
5. **Per-case outcome:**
   - **lost-completion** (`delay-worker-completion`): first-run owned `no-end`,
     recovered via SAME execution, `msg` +1 only, no mutated send ids, no
     extended grant; bounded owned outcome; timing accept
     (case_entry.py:1173-1211).
   - **failed-verification** (`corrupt-after-worker`): actual corruption
     independently rejected, never COMPLETE; `accept-open`; reason/disposition
     reconcile to artifact bytes (case_entry.py:614-670, :1212-1216,
     :1398-1411).
   - **queued-ambiguous-restart**: BOTH `queued` and `ambiguous` durable
     transport receipts, induced-labeled; reopen `duplicate-end-ignored`; ≤1
     delivery per intended action; ambiguity without authoritative receipt stays
     pending/BLOCKED (case_entry.py:1217-1267). **Precondition:** Tern must
     specify control/params that produce both kinds in one case.
   - **quiet-rest** (`none-declared`): post-commit quiet across a 3 s window and
     reopen, no fresh send or repeated alarm; not an active action relabeled
     (case_entry.py:1268-1295).
6. **Timing ruling** — explicit onset detect≤30 s, recover≤60 s, total≤90 s;
   suspicion 180/60/240; signed work duration separate; queued alone is not
   recovery; missing joins/unknown uncertainty = INCOMPLETE; negative controls
   and false alarms weigh equally.
7. **No duplicate effect / timers** — no duplicate after restart or backstop
   fire; host timers reconcile to ledger authority and original deadlines.
8. **Cleanup + archive** — automatic exact-ID archive/cleanup verified; only
   exact fixture IDs stopped/removed and owned units retired; actual process
   exit code archived (never reconstructed if missing).
9. **Independence + matrix** — corvid per-case verdict bound to per-file
   hashes, then a four-result matrix distinguished from the earlier positive
   witness; accepted source byte-identical, 34-test gate carried (not rerun for
   another fixture); any source drift invalidates release.

No production adoption, shadow run, script retirement, research, multi-project
refactor, session reset, shared wrapper edit, credential, main-seat stop or
implementation change. No fresh live release from admission; Tern owns each
exact signature. Unused allocations cancel at terminal disposition.
