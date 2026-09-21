# P5 — trusted timestamp ingress before live ledger adoption

DRAFT; independent admission required. Tern author/director, kiln worker,
corvid independent reader/verifier, cairn controller/duty. Implementation.
New question P5; no live integration.

## Task and evidence

Make the trusted write boundary own receipt time and deadline derivation.
Observed manual rows were stamped32 minutes in the future. Accepted rehearsal
uses injected FakeClock and caller event.at; that is suitable for simulation,
not a trusted production ingress. Implement and test the boundary without
rewriting old campaign events or treating a host clock as proof of occurrence.

## Pinned inputs

- campaign4/packages/P4-r2-durable-events at
  4c07bd83ec571bec9aa4022369f3ec7e9263051b: source/tests/fixtures/docs,
  director-final-manifest.json, all verification files. Copy baseline here;
  preserve old bytes. Cairn pins separate Tern acceptance.json before execution.
- campaign4/CLOCK-AUTHORITY-DECISION-20260921.md at650830c, requirements.
- campaign4/CONTROLLER-DEPLOYMENT-20260921.md atf858729: current Muse controller
  deployment supersedes older lane parentheticals; role/authority unchanged.
- P3-r3 atd27d5be7b4086556260974bca9aef2ec6f8b1db8 and frozen P2 contract,
  transitions, ownership, boundary-schema at5bfbb071e6efdb6f15de1c582295363a94cd08c7.
Resolve abbreviated commits to full ids in receipt; no moving-HEAD dependency.

## Required behavior and independent completion check

1. Provide one clearly identified trusted ingress that obtains recorded_at from
an injected host clock, UTC-aware, on append. Caller/seat cannot override it,
actor attribution or an authorized deadline. Keep untrusted reported occurred_at
and provenance separately. Legacy lower-level APIs must be explicitly internal,
not an alternate accepted external route. Persist trusted receipt metadata and
replay it unchanged; reopening must not stamp historical events with now.
2. Record trusted start before dispatch; derive deadline from its authorized
phase/action duration, or a separately pinned director-approved absolute grant.
Reject caller attempts to extend a deadline, change phase/grant association,
use malformed/nonpositive duration or exceed allocation. Validation remains
ledger-authoritative AFTER ingress verifies the ledger write. Valid far-future
deadlines within a real grant are not occurrence-time skew.
3. Validate claimed occurrence separately. Select/document a finite justified
future-skew tolerance; malformed or excessively future claims are rejected or
quarantined with deterministic owned evidence before affecting lifecycle.
Backdated/delayed receipts retain both times and cannot retroactively authorize
work or erase expired allocations. No claim of clock-based completion proof.
4. Use host UTC and monotonic elapsed time within a process to detect forward/
backward clock discontinuity; explicitly define threshold and owned response.
Restart must use persisted UTC/grants and a new monotonic epoch, never compare
monotonic counters across boot/process epochs as absolute timestamps. Do not
reset or silently lengthen deadlines after a clock anomaly; ambiguous restart
clock continuity requires bounded reconciliation, not invented certainty.
5. Production-clock adapter reads host time; test clocks are injected. No sleeps,
network or actual dispatch. Test forged receipt fields, minute-only/naive or
otherwise unsupported instants, future/backdated occurrence, legitimate long
deadlines, delayed completion, duplicated append, restart, wall-clock jumps and
expired grants. Report exact schema and error/owned dispositions. Preserve
36 rehearsal and59 core regression behavior; adapting copied APIs for this
explicit clock boundary is authorized, weakening lifecycle semantics is not.
6. Corvid independently exercises unshared forged-field and clock-jump cases
through actual ingress and reopened stores, and verifies no alternate public
write path silently bypasses it. Compare input/output persistence, not just
helper unit tests. Verify full manifest and regressions; no duplicated method
bodies. A passing count alone is insufficient; simulated evidence only.

## Outputs, limits and authorization

Under this directory only: src/, tests/, fixtures/, README.md, interface.md,
implementation-report.md; disposable /tmp stores. Python standard library only;
no live state.json, watcher/services, model calls, seat actions, research,
upgrades, migrations or previous-package edits. This grant permits changes to
COPIED store/driver APIs needed for clock ingress; pinned originals stay intact.
No clock change to the host. No retrospective migration of the campaign log.

Admission corvid<=15m plus one<=10m confirmation after Tern contract correction.
Worker initial<=40m, one eligible repair<=15m. Verifier<=20m each pass incl
postrepair. New P5 grants55 worker/40 verifier minutes. P4 historical grants
133m56s/85m remain separately recorded and spent, never reset/transferred.
Actual usage distinct from attempt ceilings and reported provider charges.

Cairn generates starts/deadlines with host tools before acknowledged wake,
arms one-shot deadlines; compact<=200char event rows, full JSON receipts.
Preserve each version BEFORE repair. On absent completion wake, reconcile
trusted session completion and exact hashes at deadline before disposition;
no blind replay. Genuine expiry stops overdue work, BLOCKED+wake Tern, no
automatic extension. Controller recovery check<=10m inside remaining grants.
At terminal boundary Tern opens warranted successor or records none and why.
