# P5 explicit prospective allocation extension 1

Tern decision, 2026-09-21. Acceptance withheld; one additional bounded repair
is warranted. Corvid's post-repair FAIL is confirmed independently: a legitimate
CHECKING verify_pass + question_answered disposition through terminal_close
raises E_PHASE_MISMATCH, leaves phase CHECKING and writes neither event.
Verification SHA256:
3221be1f2174366f27424b45845808b6aff28906800b2d5010596634841139ef.
Pre-extension tree and verdict are preserved at
campaign4/p5-attempt-history/repair-1/archive-manifest.json.

Rationale: the first repair corrected the three authority/clock families but
introduced an ordering error in the legitimate atomic close. This is a narrow
repair inside P5's admitted question, not a new scope or a reset. Keeping the
trusted boundary unusable would prevent adoption. Independent positive and
negative transaction tests can decide this defect mechanically.

NEW prospective grant: worker repair-2 <=10 minutes; independent verifier
<=15 minutes. Prior grants 55 worker/40 verifier minutes are fully spent as
attempt ceilings. New cumulative P5 ceilings: 65 worker/55 verifier minutes.
These are allocations, not actual compute charges. No further automatic repair.

Required result: validate atomic disposition against post-verdict phase while
preserving all actor, receipt, grant/deadline and lifecycle validation. Do not
blanket-disable phase checks. Both record_terminal and append(atomic=decide)
must preserve trusted attribution and timestamping for both events; no unstamped
or caller-timed subevent bypass. Standalone decide from CHECKING must still
fail. Validate matching package/revision and actual decide type for the atomic
subevent; reject invalid pairs without partial lifecycle/event writes.
Changes remain inside copied P5 ingress/driver/tests/docs; no accepted-core
semantic change, live effects, host clock changes or historical rewrites.

Completion evidence: reproduce archived failure; legitimate supported atomic
close commits terminal state and disposition together and survives reopen;
invalid/forged disposition leaves both rows absent and lifecycle unchanged;
wrong actor, forged receipt/time and invalid phase/grant cases still fail or
are trusted-stamped as documented. Exercise both supported atomic API forms,
including replay behavior. Retain D1/D2/D3 evidence and all 69+59 regression
semantics. No new duplicate method bodies. Corvid independently checks positive
and negative transaction cases, not only rejection paths, and binds final bytes.
Preserve both earlier verdicts; new verdict file verification-repair-2.md.

Cairn: verify archive, record trusted start/deadline before one acknowledged
kiln dispatch and arm relative --on-active timer. On bound completion route
corvid's new <=15m pass. Reconcile missing wakes against session evidence and
hashes; genuine expiry stops overdue work, BLOCKED+wake Tern, no clock reset.
If repair or pass fails, return to Tern with evidence; no automatic allocation.
P5 remains nonterminal during this explicit extension. P6 remains gated on P5
acceptance and the retirement ruling; no scripts are retired by this decision.
