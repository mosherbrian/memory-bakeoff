# P6-r11 completion-1: freeze and independent causal verification
Tern; 2026-09-22T18:04:00.297957+00:00.
INCOMPLETE preserved at 05eba448bcec710c143fa707f328d9a5fd169d25. No acceptance or further worker grant.
Completion receipt17:52->18:22; claim17:59, report18:01. This is early return with
residuals, not proven30m exhaustion. Cancel unused worker remainder prospectively,
retire timer and ensure worker idle; retain allocated ceilings955worker/670verifier.

Release the existing unspent corvid<=30m implementation verification, ONE
P6r11-verify-1 on frozen bytes. No fresh allocation. Because known blocking defects
exist, use targeted causal review first and stop after a sufficient bounded finding;
no expensive full gate needed to rediscover a known failure. No silent scope waiver:
full retained+new gate remains REQUIRED before any later PASS.

Corvid independently reproduce FV-W on frozen candidate and compare immutable r9.
Trace action/execution/ledger phase, post-commit tamper, worker and verifier claims,
which actor's hashes are being recomputed, and exact source of E_ARTIFACT_MISMATCH.
Distinguish genuine verifier rejection from replaying worker validation after its
handoff committed. Establish whether repair is possible in authorized case_entry.py
or requires another module; identify minimal specific change, do not implement it.
Do not bless a mismatch merely because this is a failed-verification case: require
actual verifier action/evidence and accept-open, no false COMPLETE. Independently
confirm QR-W scoped improvement without promoting unrun QR-WV/expiry/full gate.

Inspect manifest31/32 including reported self-hash: identify offending path, candidate
binding versus old paths, no circular hash fix. File actual hashes as review evidence;
leave rejected manifest/claim unchanged. Check candidate-plan and missing executable
new-pass assertions against concrete-cases.md: baseline old-fail assertions must not
be passed off as unchanged new-pass tests. Retain independent expected semantics.

Write candidate-review-completion-1.md with one bounded verdict, executable reproducer,
actual results and smallest correction. No code, receipt or manifest repair by
verifier, no live effects, no retry-until-green. If time insufficient, INCOMPLETE
with exact unresolved questions, not speculative root cause.
Cairn host-read dispatch start+30m, active relative timer, bind frozen files directly
from commit (manifest known malformed), dispatch once now and return verdict Tern.
No other fixture/prep, no continuation on original worker clock. Director owns next
amendment/allocation once the causal defect is independently established.
