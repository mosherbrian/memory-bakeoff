# P5-r2 — unambiguous atomic ingress authority

DRAFT. Tern author/director; corvid independent admission and verifier; kiln
worker; cairn controller/duty. Implementation, same cumulative P5 question.
No live integration. Separate admission and explicit conditional release below.

## Evidence and task

P5 exhausted 65 worker/55 verifier minutes of attempt ceilings, with initial
PASS withheld on actor/deadline/epoch defects, repair-1 FAIL on terminal ordering,
repair-2 PASS withheld on atomic ambiguity. History remains spent and pinned.
A call supplying BOTH atomic.hold and atomic.decide makes ingress validate hold
then return, while Store.append prioritizes decide. The candidate committed
COMPLETE plus a forged kiln/director decision dated 2099 with no trusted receipt.
This is a real breach of the boundary P5 was building, not new live scope.

Implement one unambiguous validation/stamping path for each atomic operation.
Reject mixed or unsupported atomic forms before any lifecycle/event mutation.
Every accepted subevent must receive trusted attribution/time and the same
identity/type/phase checks regardless of API spelling. Do not remove valid
atomic close or hold to make negative tests pass. No blanket bypass or catch-all
success. Legacy internal store APIs and test fakes are not public ingress.

## Pinned inputs

- Parent campaign4/packages/P5-clock-ingress at 88f2c18b68c1f71ace8911cec7b74a3df752d2e4, including
  director-final-manifest.json and three verdicts; copy into this directory,
  never edit originals. Rejected baseline ingress SHA256
  371b189d16596fe736869e39cdb3a3b3424fd06529428fce8ad1febfc8f1e549.
- Parent package.md at ec3325463eff8677fab733d2413fd7bc8266fbe8,
  director-repair-decision.md at a339939 and allocation-extension-1.md at92299f8.
- campaign4/CLOCK-AUTHORITY-DECISION-20260921.md at650830c and
  campaign4/CONTROLLER-DEPLOYMENT-20260921.md atf858729.
- Accepted core P3-r3 atd27d5be7b4086556260974bca9aef2ec6f8b1db8;
  frozen P2 boundary spec at5bfbb071e6efdb6f15de1c582295363a94cd08c7.
- director-mixed-atomic-probe.py in this package, independent observed evidence.
Cairn resolves abbreviated commits in receipt; no moving HEAD input.

## Completion check

1. Reproduce the mixed hold+decide forged-authority commit on pinned parent;
   candidate rejects it deterministically before either event is persisted.
   Cover key ordering, unknown keys, non-dict/malformed atomic values, missing
   trusted actor and forged receipt/time. Use explicit schema/allowed variants.
2. Both record_terminal and append(atomic=decide) accept genuine verdict plus
   disposition together; both rows trusted-stamped, correct qid/revision/type,
   legitimate post-verdict terminal phase, replay behavior documented, reopen
   preserves history. Invalid subevent/type/identity/actor/disposition produces
   no partial event rows or lifecycle changes, also after reopening.
3. Genuine bounded atomic hold works with authorized deadline and owned decision
   task. Reject unauthorized hold deadlines and mixed forms. Preserve D1/D2/D3
   actor, all action-deadline/phase grants, epoch/restart/clock checks; no direct
   test-only store helper exposed through supported production entrypoints.
4. Retain 77 local and59 core regression semantics and no-duplicate dispatch,
   REST/INVALID/ACTION_DUE semantics. Tests assert legitimate success as well as
   rejection. No duplicated methods, stdlib only, no live effects. Document
   fake.py as internal test-only; it is not an alternate accepted write API.
5. Corvid independently reproduces parent failure and mutates both atomic API
   forms, including combinations not supplied to worker. Check persisted rows,
   attribution/receipt, rollback and reopen, not only returned errors. Bind
   full per-file hashes and report any accepted-core semantic change before it.

## Outputs and permissions

Only this directory src/, tests/, fixtures/, README.md, interface.md,
implementation-report.md; disposable /tmp stores. Copy P5 baseline; amendments
limited to atomic ingress validation/stamping and tests/docs, with copied driver
adaptation if required. No live state, timers, seat actions, model calls, host
clock changes, research, old-source edits, migration or script retirement.

## Allocation and dispatch

New worker initial<=20m, sole eligible repair<=10m. Independent verifier<=15m
per pass, including postrepair. New grant30 worker/30 verifier minutes;
cumulative P5 ceilings95 worker/85 verifier minutes. Previous65/55 spent,
never reset or transferred; actual runtime and provider charges distinct.
Admission corvid<=10m plus one<=5m confirmation if Tern corrects contract.

Tern conditionally authorizes cairn to execute ONLY after corvid ACCEPTED on
unchanged pinned contract, director admission record and pinned parent EXHAUSTED
disposition exist. No overlap. Start/deadline from host tools before wake;
relative --on-active one-shot timer, compact<=200char control events. Preserve
initial bytes before any repair; bind completion before verifier dispatch.
On missing wake reconcile session evidence and hashes; real expiry stops work,
BLOCKED+wake Tern. Controller recovery<=5m inside current grant, no extension.
No second automatic repair. Terminal boundary returns to Tern to accept and
open P6 if warranted, or record the next bounded disposition. P6 retirement
ruling remains in force; no live script retires from this package.
