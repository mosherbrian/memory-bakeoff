# P8 final — NOT READY for unattended use

Tern, 2026-09-23. The single permitted repair is spent. Corvid's initial bounded
repair PASS (49102b8ae8f9) was amended in the same review after intake steering;
the complete preserved review now hashes d0c077ee755514130c805e713dcd933a7a93881658ebef52c91dfed58acd6f84.
Its live-future heartbeat reproducer returns REST/alarm=false. The observer also
ignores process incarnation, so a prior run's pass can certify a replacement.
These are actual safety gaps in the required supervisor liveness check. No second
repair is authorized and no P8-r2 opens. This does not claim the entire four-hour
ceiling was used: the one-repair boundary is spent, while unused grants are closed.

Candidate 71318c4e7a0ed142acd61d4553f31e5bad0fb474, binary
3a84efb36e1f79ffc1a03bcc4924b26cd060e52ae2d597a2f4000012f176b8e0,
remains a reviewed implementation with known defects, NOT an accepted unattended
release. Installed/main 4a00d67/8cc149bf remain unchanged. The 191-file manifest is
exact; core/host/py unchanged. Independent go vet/test and125/125 conformance pass.
71/71 mutations and detailed316/321+5 parity were author reports; the reviewer did
not independently rerun the mutation sweep. Do not collapse these evidence types.

| Before-unattended check | Evidence | Final scope |
|---|---|---|
| Restart does not duplicate | qualification-completion-review.md controlled uncertain-delivery; repair tests retain outbox | Controlled proof, actual supervised-service restart not witnessed |
| Hung attempt has owned enforcement | Stage B short timer callback with stubs; repair supervision tests | Real stop/watchdog/escalation witness still open; heartbeat defect blocks readiness |
| Author cannot self-verify | Core125 cases and Stage B same-principal checks; repaired bound runtime principals | Proven within trusted-host CLI boundary, not multiuser authentication |
| Changed inputs invalidate dispatch | Stage B missing/changed declared-input CLI cases | Proven for registered inputs; no implicit input adoption |
| Exhaustion prevents automatic attempts | Core and loop regressions; one-repair policy | Proven within declared allocation boundary |
| Pending judgments block dependents | Stage B unresolved/allowed/disallowed dependency CLI; decision visible | Enforcement proven; richer Go Expose follows in P9 |
| Interrupted evidence recovers or blocks | Stage B truncated claim/ledger reopen; atomic-close corrections and tests | Controlled proof; no broad filesystem corruption guarantee |
| Routine handoff needs no Brian | live-1 actual worker then verifier; decide failed E_UNTRUSTED_ACTOR. Repaired exact regression passes offline | Current repaired positive close not live-witnessed; historical Python/P6 is not transferred |

Sources are this package's qualification-review.md, qualification-completion-review.md,
live-1/ (preserved actual failure), live-director-findings-1.json, repair-1-claim.json,
repair-1-review.md and repair-1-intake.json. No live2 preparation was dispatched:
review hash changed before any preparation record/write/release. All three live1
fixtures were already stopped/removed and its scoped timers cleaned up.

Remaining limitations also include real restart/watchdog/start-limit/exit64 and
outside-timer observations; unmeasured long-Tick watchdog interaction; the wake
transport as notification root; external systemd as checker supervision root;
trusted-host caller authority; the callback authority-check/open window;
no migration of old packages lacking bound principals; deadlines remaining active
while run is stopped (requires a live observation). A malformed incident file
returns nonzero, but that alone is not proof anybody is notified: the check unit
has no independent OnFailure delivery. Keep this explicit, not an owned-recovery
claim. No new repair is authorized by naming these limits.

Unused P8 live/preparation/review grants and remaining reserve are cancelled,
not transferred or silently spent. Existing Cairn/coax ownership continues. No
adoption, cutover, script retirement or replacement of installed binary. The next
warranted step is the already planned P9 supervised preview: useful Go Expose and
navigable packaging with these limits visible, no concealed safety fixes.
