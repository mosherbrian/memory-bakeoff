# Muse ideation batch 4 — blind spots in a static evidence-integrity guard set

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Authorization:** fleet-poller R&D pulse 2026-09-13 (standing Muse cadence,
`team/RD-THREADS.md` Corvid thread; original approval Brian via GiLMore
2026-09-12, `PROTOCOL.md`). Public methodology only; no project-specific detail
on the wire.
**Cost:** one batched call, meter read `$3.1851` → `$3.1967` = **~$0.012**
(under the ≤$1 per-task cap). No block signals. Latency 60.5 s, 3,613 chars.
**Receipts:** `implementer/repo-glm-dsh3/scripts/experiment_20260912_muse_ideation/receipts/batch4-*`
(summary sha `b5a922f4…`, stream sha `f8e93193…`); prompt `PROMPT4.txt`
(sha `27eaa46a…`, recorded before sending).

**Plain English (for Brian):** I asked Muse where a set of static evidence
checkers is likely blind. It named five classes. Four are worth a bounded
check; one does not apply because this corpus has no include/transclusion
mechanism. The two cheapest and most concrete now have **live instances in
today's own record**: a checker that prints FAIL but exits 0 (Alice's S6
finding) and the same policy file disagreeing across repository copies (today's
AGENTS.md/`KNOWN_FAILURES.json` drift).

## Prompt (verbatim, preregistered)

> A research team runs a small set of static checkers over a Markdown evidence
> repository: they resolve links, compare stated numbers against committed
> result files, verify that cited runs are not invalidated, check canonical
> record identifiers, and pin a suite baseline recorded in a policy document.
> Name five OTHER static-checkable evidence-integrity failure classes that such
> a guard set is likely blind to. Deliberately include (a) at least one class
> where a checker computes the right answer but signals it only in prose or a
> zero exit code, so a machine gate reads a bad state as clean; (b) at least one
> class where the same policy or index file exists in several repository copies
> that drift apart; (c) candidates that need a maintained index to exist before
> the check is possible. For each, give the minimal check, a one-line self-test
> that would reject a synthetic bad input, and why a naive implementation would
> pass that bad input.

## Muse output and dispositions

| # | Muse item | Verdict | Reason / next step |
|---|---|---|---|
| 4.1 | **[E] Verdict-signalling failure** — checker computes FAIL but reports it only in prose / exit 0; gate asserts exit code *and* a machine-readable verdict | **ACCEPT** | Already demonstrated live: Alice's S6 boundary finding (`ALICE-S6-GUARD-SECONDCHECK.md`, 07:50) — INCONCLUSIVE was stdout-only, rc 0, so a count/rc gate read an unavailable scan as clean. New guard class: a **process-level positive control** — run each checker against a synthetic bad root and assert the CLI returns nonzero *and* a structured verdict. Our own self-tests assert detection logic but always return 0, so they do not cover the exit contract. Cheapest next build. |
| 4.2 | **[E] Duplicated-canonical drift** — the same policy/index file in several checkouts disagrees | **ACCEPT (narrowed)** | Live instance is today's drift: canonical `AGENTS.md` vs its own `KNOWN_FAILURES.json`, plus the two forks (my `CORVID-AGENTS-BASELINE-DRIFT.md`). `team_sync.py`/`MIRRORS.txt` already one-way-mirrors `team/`, so the gap is **repo-level** policy files, which have no declared canonical copy. Needs a canonical-path declaration before a check can exist; otherwise a naive equality test false-positives on legitimate forks. |
| 4.3 | **[H] Orphan evidence** — committed result files that no Markdown cites, hiding contradicting runs | **ACCEPT (proposed)** | Genuinely inverts the existing checkers (citations→files) to files→citations. Real risk given the "do not overwrite completed result directories" rule and the volume of probe runs. Needs a grace window / intentional-uncited allowlist or it drowns in probe dirs. Medium value; build after 4.1. |
| 4.4 | **[E] Transitive-include invalidation escape** — an invalidated run cited only through an include the checker never expands | **REJECT** | Out of scope: this corpus has no `!include`/transclusion syntax and does not symlink evidence dirs, so there is nothing to expand. Revisit only if an include mechanism is ever added. |
| 4.5 | **[H] Selective-metric omission** — every cited number matches, but a failing metric in the same file is simply never cited | **ACCEPT (proposed)** | Directly serves the AGENTS rule "always report exact returned context size and harmful/prohibited presence; do not rely on prohibited fraction alone." Needs a per-result-type expected-schema index (required keys, e.g. `hit` + `prohibited@k` + `n`) so the checker can demand each material key be cited or explicitly waived. High portfolio value; index-dependent. |

**Tally:** 4 ACCEPT · 1 REJECT.

## What I take from it

- **Chase first: 4.1 (exit/verdict contract).** It is the smallest guard and it
  already has a live motivating receipt; it retrofits a positive control to the
  nine checkers I own rather than adding a tenth static scan.
- **4.2 is real but policy-blocked:** the drift is proven (canonical AGENTS.md),
  yet a check needs an explicit "this copy is canonical" declaration for repo
  policy files, the way `team/MIRRORS.txt` declares it for `team/`.
- **4.3 and 4.5 need an index first:** orphan detection needs a citation-side
  inventory; selective-metric detection needs a per-result-type schema. Both
  are worth building only once the index exists — the same gate Muse 3.2/3.4
  hit.
- **4.4 rejected on corpus grounds**, not on importance.
- Muse remains divergence, not truth: each ACCEPT becomes a proposed check and
  becomes a finding only after it rejects a real bad input through its own
  self-test.

— **Corvid** (`worker-glm-dsh3`). Four of five suggestions are new classes; the
first one already has a live receipt from this morning.

## Follow-up (same day): 4.1 built

`4.1` is no longer a proposal. `repo-glm-dsh3/scripts/check_checker_exit_contracts.py`
(sha `9d6d27fe…`, `--self-test` PASS) runs each of the nine sibling guards' real
CLI twice — minimal clean root must exit 0, minimal dirty root must exit 1 — and
its own self-test proves it catches a checker that prints `FAIL` but exits 0.
Result: **9/9 exit contracts hold**. Added as the tenth guard in
`team/CORVID-RD-CHECKER-SUITE.md`. The other three ACCEPTs remain proposals.

## Follow-up (same day): 4.1 hardened — crash is not a detection

Alice's second-seat power check (`team/ALICE-EXITCONTRACT-METAGUARD-CHECK.md`,
sha `18eba0db…`) found that the dirty control asserted only rc == 1, so a guard
that **throws** on the dirty root passed as a detection — and that 4.1's own
"nonzero **and a structured verdict**" was only half built. Fixed in place:
sha `9d6d27fe…` → **`fa579cc7…`**. `evaluate()` now requires, on dirty, rc == 1
**and** no Python traceback **and** a match of that guard's declared finding
marker; on clean, rc == 0 and no traceback. `--self-test` now covers four
synthetic contract classes (correct, prose-only/exit-0, crashy, finding-less
exit-1), and the real set still reads **9/9 hold**. Detail:
`team/CORVID-EXITCONTRACT-CRASH-FIX.md`. 4.1's stated scope is now fully
instantiated.

