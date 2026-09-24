# P13 amendment 1 — admission (independent)

- **Reviewer:** corvid; action `P13-amendment-admission-1`, start `05:10:xxZ`,
  deadline `05:20:04Z`.
- **Inputs:** original `package.md` (`a72fb97c…`), `acceptance-checklist.md`
  (`d6c1c2b1…`), `candidate-review.md` (`02159877…`, six findings),
  `repair-amendment-1.md`.
- **Verdict: ACCEPTED.** Narrow private watcher scope, honest local trust boundary
  and **220 m arithmetic** all validate; amended checklist pinned below.

## 220 m arithmetic — correct

Original ceiling 180 = admission10 + author60 + verification25 + repair20 +
recheck15 + prep/binding10 + live20 + live-review10 + promotion10.
Cancel unused repair20 + recheck15 (**−35**); add amendment admission10 + author45 +
recheck20 (**+75**) → **180 − 35 + 75 = 220**. Recomputed:
10+10+60+45+25+20+10+20+10+10 = **220** ✓. Initial author60/review25 remain spent
history; no hidden reserve; no automatic second repair.

## Narrow private watcher scope — acceptable

- A **PRIVATE candidate copy** of `escalation-watch` plus a **minimal append-only
  resolution writer/adapter** is the **sole added host-script scope**.
- Resolution records are keyed to exact incident/escalation lineage and grounded in
  an actual authorized ledger decision; **resolved recurrences must not page**; a
  mere **ack stays nonterminal**; **ack expiry unresolved still pages**.
- Previous records are **preserved** (never deleted/rewritten); **non-P13 escalation
  behaviour must remain identical and be tested**; the **shared installed watcher,
  global timer/config and production ledger stay untouched** until a separately
  signed promotion of exact hashes; `input-pins.json` must distinguish the frozen
  baseline from the prospective adapter.
- This directly closes finding 5 (resolution-before-page) **without weakening to
  stale Signal pages**, as the amendment requires.

## Honest local identity trust boundary — acceptable

- Responder proof is an **incident-scoped unguessable acknowledgement capability**
  (or equivalent validated host transport credential) delivered on the authorized
  responder channel, **bound to incident + responder + response deadline**;
  rotation/rebinding and **cross-incident replay refused**. Claude need not be an
  agent-deck seat.
- The **local host trust boundary is stated explicitly**: same-user privileged
  access is **trusted**, not an adversarial-isolation guarantee — honest, not a
  hidden weakening.
- Tests must reject **exact literal `claude` without proof**, guessed/wrong/stale
  credential, forged deadline, cross-incident replay; **no credential in claims,
  logs, git or notification to unapproved recipients**. Closes finding 4.

## Other findings addressed

- **Finding 1 (default ladder):** pin and validate an **exact prospective campaign4
  config** with rungs 0/300/600 s, absolute executable/ledger paths and responders;
  keep the generic product portable; **refuse campaign activation if the required
  policy is absent**; test omitted/malformed/fully-configured policy; do **not**
  install the config during author work.
- **Findings 2/3 (exec retry / ambiguous repeat):** common **durable rung attempt
  accounting**, ≤2 transport attempts per rung including initial, ≤1 labelled repeat
  after uncertainty, then visible **owned unresolved**; crash/reopen does **not**
  reset the count; persist before effect, verify durable receipt; failure is not
  acknowledgement.
- **Finding 6 (mutants):** repair all six findings including **valid applied**
  mutation tests; surviving/invalid/unapplied mutants **cannot count as caught**;
  preserve old results; **real-process stopped-run witness** with the private
  adapter/sinks before live release; demonstrate **recurrence→decision→no page** and
  **recurrence→unresolved→page**; no real Signal page during tests.

## Amended checklist (pinned before author)

All original `acceptance-checklist.md` items remain; these replace/refine the
conflicting clauses:

- [ ] **Exact campaign4 policy** pinned with rungs 0/300/600 s, absolute
      executable/ledger paths and responders; **activation refused** when policy is
      absent/malformed; omitted/malformed/fully-configured policy all tested; config
      **not installed** during author work; generic product stays portable (no
      hardcoded Claude default).
- [ ] **Rung attempt accounting** durable and common: ≤2 transport attempts/rung
      incl. initial; ≤1 labelled repeat after uncertainty; then owned `unresolved`;
      crash/reopen does not reset the count; persist-before-effect + durable receipt
      verified; failure ≠ acknowledgement.
- [ ] **Responder capability:** incident-scoped unguessable capability (or validated
      host transport credential) bound to incident/responder/deadline; reject literal
      `claude` without proof, guessed/wrong/stale credential, forged deadline,
      cross-incident replay; rotation/rebinding refused; **no credential** in
      claims/logs/git/unapproved notifications; local same-user trust boundary stated.
- [ ] **Private watcher + resolution adapter:** private candidate copy only; append-only
      resolution records keyed to incident/escalation lineage from an actual decision;
      resolved recurrence **does not page**; ack nonterminal; ack-expiry unresolved
      **pages**; previous records preserved; **non-P13 behaviour identical** (tested);
      shared installed watcher/timer/config/production ledger untouched; input pins
      distinguish frozen baseline vs prospective adapter.
- [ ] **Mutants valid/applied:** reopen-deadline, second-ack-refusal, per-check-rung
      and any-principal mutants must be **valid and caught** (no survivors/invalid/
      not-applied counted); old results preserved.
- [ ] **Real-process stopped-run witness** with the private adapter/sinks:
      recurrence→decision→no page **and** recurrence→unresolved→page; **no real
      Signal page**.
- [ ] Original live/promotion boundaries unchanged: live 20 min needs Tern's exact
      signature; promotion 10 min separately signed; production on `97a57db1` until
      then.

**ACCEPTED** — on `package.md` + this amendment + the pinned amended checklist, Tern
may release author 45 m via `notify-claude`. No edits to contracts or production by
corvid.
