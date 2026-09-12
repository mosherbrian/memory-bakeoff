# CAMPAIGN-1 (DRAFT v1 — converged overnight 2026-09-12; DRAFTING ONLY, no execution begun)

**Status:** converged by Kiln per GiLMore's overnight directive. **Verity
audits the success criteria next; Brian holds one veto in the morning.**
Authors of record: Kiln (spine + workstream), Cairn (tiered-capture pushback,
fused as the burden arm), with raw material from Assay, Aletheia (Alice),
Corvid, Ledger. Standing limits unchanged; extension stays frozen at the
060d842 lineage for the live arm.

## One-line thesis

An agent demonstrably adapts when its world changes — on real work, with the
human paying roughly one confirmation a day and zero stale actions — by
closing the supersession loop on the live trial and making retrieval
triggering change-aware instead of human-dependent.

## Design (fused: Kiln A-spine + B-workstream + Cairn's tiered-capture)

### Spine — close the supersession loop on real work (from Kiln A + the frozen trial)

The trial's pre-registration (docs/EXPERIMENT-20260911-trial.md) already
contains the decisive test: a deliberate convention change on real work →
worker drafts a supersede → recall thereafter delivers current-only →
stale-action events = 0. The campaign runs the trial to that cycle. Memory
that adapts when circumstances change is the charter's "adapt when
circumstances change," made measurable with instruments the team already
trusts.

### Workstream — change-aware triggering (from Kiln B + the self-noticing data)

The measured weakness is not storage or suppression — it is that the agent
does not LOOK (F1 0/8 spontaneous vs F2 8/8 nudged; trial finding: self-
noticing weak). Build a change-aware trigger in the nudge layer: fire
retrieval on (new task in a known project · contradiction with a stored
decision · resumption after a gap). Mechanism-small, nudge-layer only, no
perseus changes, no extension unfreeze. Metric: unprompted relevant
retrievals x/y, from session logs.

### Burden arm — risk-tiered capture (from Cairn's pushback, fused)

Cairn's pushback accepted: **universal human-confirm is itself the burden**,
and burden is Brian's attention — the one resource the charter says not to
spend. The campaign therefore runs capture in two tiers as its measured
variable:

- **T0 (agent-confirmed, low-stakes):** conventions, notes, pointers — the
  worker self-captures via `confirmed_by: "agent"` (the 7a exception switch
  the frozen extension already has: `allowAgentConfirmed: true`,
  **config-only, no unfreeze**). Every T0 record is logged (notify file +
  session logs) and audited after the fact by Verity for proportionality;
  any T0 record is correctable by supersede, so the cost of a mistake is one
  T1 confirm, not a corrupted store.
- **T1 (human-confirmed, high-stakes):** decisions that bind future behavior
  (architecture, deployments, project conventions) — operator-confirmed as
  today, with the finding-#1 plain-language presentation format REQUIRED.

This is an in-experiment amendment to 7a's default, which is exactly what
Brian's veto covers. If he rejects tiering, the campaign still runs with
universal T1 (the burden numbers then measure the untiered baseline — also
publishable).

## Pre-registered success criteria (Verity to audit; all descriptive, small-n, no causal claims)

| # | Criterion | Instrument | Target |
|---|---|---|---|
| S1 | Supersession cycle closes on real work: ≥1 deliberate convention change → supersede drafted + confirmed → recall delivers current-only | delivered-level check (P1B instrument), never stream-level | ≥1 complete cycle |
| S2 | Stale-action events (acting on a superseded record) | trial ledger | **0**; any occurrence reported prominently as failure |
| S3 | Burden: human confirms/day vs the proposal's 1–3/day estimate, with T1 coverage at 100% | trial ledger + notify file | **≤1/day** under tiering (vs 1–3); clarity rating per prompt (finding-#1 format) |
| S4 | Self-noticing: unprompted relevant retrievals in stored-record-relevant turns | session logs | ≥3/5 relevant turns (n stated honestly) |
| S5 | Overhead: memory turn vs paired no-memory turn (wall + tokens) | pi session logs; pre-trial turns as baseline pairing | within **+25%**; beyond → flagged, not hidden |
| S6 | Capture-at-rest integrity: no record lost or demoted | status checks per write | **0 demotions**; any `active→proposed` transition = immediate stop-and-report |

Window: 10 confirmed T1 cycles OR 3 working days, whichever first; Brian
stop-anytime (kill switch `PI_PERSEUS_RECALL=0` or a word).

## Hard guardrails from the probes (non-negotiable build constraints)

1. **CLI `write` remains the only activation path.** Aletheia (reproduced x2):
   native `remember` on an active key **demotes it active→proposed** with an
   `ok:true, action:"updated"` receipt; recall then abstains. No record
   migrates to native remember. (team/PROBE-remember-admission-FINDINGS.md)
2. **The native admission chain is treated as inert** until a record is
   OBSERVED going proposed→active through public tools (never observed;
   attested-journal route unreached — HMAC canonicalization, 15 formats
   rejected; method limit stated). `maintain`/`consolidate` do not promote
   proposals (Assay). Corollary: campaign-C (upstream repair) stays gated.
3. **Everything is measured at DELIVERY level** (the P1 root cause):
   stream-level presence is necessary-but-insufficient, always.
4. **Capability vocabulary trap:** only `memory.propose` / `memory.commit` /
   `memory.read` are real nouns; `memory.write.*` silently denies while
   echoing the wrong noun back (Alice). Any authority work uses the verified
   vocabulary + explicit `capability_constraints_json` + explicit
   `mode: "enforce"`.
5. **Negative results are deliverables,** preserved verbatim with receipts.

## Budgets

- worker-pi (Cairn): local, free — the trial continues as the live arm.
- Kiln (build + execute) and Verity (audit): flash lanes, free.
- Ledger (claude): tried/failed/open cross-reference feeding the window-end
  report — claude lane.
- dsh lanes (Aletheia, Assay, Corvid): **metered with no counter → bounded
  tasks only.** No new native-pipeline spend this campaign. Open bounded
  item: the admission-path unit-test confirmation needs `cargo`/`rustc`,
  absent on this host — parked unless a lane has rust. Muse: calibrated
  (Corvid, ANSWERED/CORRECT/STABLE n=1x2, ~$0.002); no further spend.
- **Brian's attention is the real cost:** T1 confirms only (target ≤1/day),
  one veto now, stop-anytime.

## Roles

- **Cairn** — dogfooder; lives the tiers; reports burden, clarity, self-
  noticing from inside.
- **Kiln** — build + execute + survive-contact proof; change-aware trigger;
  tiering config (config-only) and its receipts.
- **Verity** — audits THESE criteria next; audits ledger-vs-claims at window
  end (T0 proportionality included).
- **Ledger** — synthesis: tried/failed/open cross-reference as the report's
  spine.
- **Aletheia, Assay, Corvid** — standing probe seats, bounded tasks only;
  their findings are this proposal's raw material and the window's audit
  baseline.

## Raw material (receipts)

- Assay: native-capture repro — non-delivery is status withholding by
  construction (NON_SERVEABLE_STATUSES); three divergences from the Kiln
  probe (id-match note, abstention reason env-dependent, admission gate
  transport-identity bound); maintain/consolidate do not promote.
  scripts/repro-20260912-assay/
- Aletheia: remember+admission probe (demotion x2; capability traps;
  attestation unreached) — team/PROBE-remember-admission-FINDINGS.md;
  row-6 data gap (answer_id never captured — "capture is the hole," fourth
  preregistration-class failure) — team/PROBE-row6-data-gap.md.
- Kiln: native capture probe (no derived lineage; proposed-state wall) —
  scripts/experiment_20260912_native_capture/FINDINGS.md, commit 84cc6b9.
- Trial pre-registration (window/metrics/roles/budget) — commit 6df91c7;
  finding #1 presentation format — commit 4fbd904; decision-memory build —
  3f9498f..e9e5621 + 060d842.
- Corvid: Muse calibration — commit 7d42fdf.

## Open items for Brian's morning veto

1. Approve T0/T1 tiering as the in-experiment amendment to 7a (agent-
   confirmed LOW-STAKES only, after-the-fact audit, correctable by
   supersede). Everything else in 7a stands.
2. Confirm the window (10 T1 cycles / 3 days) and the ≤1/day burden target.
3. (Optional, zero-cost) bless campaign-C (upstream capture repair) as the
   pre-approved campaign-2 should A/B show capture is the binding constraint.
