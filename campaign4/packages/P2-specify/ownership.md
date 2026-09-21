# Ownership map (frozen)

**Freezes:** `ACCEPTED-ARCHITECTURE.md` §2 as applied by `CHARTER.md`
(seats, lanes, profile) and closed by `director-decisions.md` (the two open
questions: overseer recovery budget, supervisor-liveness owner). Kiln does
not redesign; this map incorporates Tern's decisions.

## Who holds each role

| Role | Seat / holder | May | May not |
|---|---|---|---|
| Director (Tern) | tern (`acp-oai-worker`, gpt-6-astra via Codex) | Choose questions, propose packages, interpret findings, decide amendments, own supervisor liveness + silence backstop + unresolved supervisor-recovery decision, accept frozen outputs | Substitute another model on Codex exhaustion (stop, wait for Brian); decide what she judges she cannot reasonably decide (pause path instead) |
| Contract reader | corvid (`acp-go-deepseek`) | One-pass admission check (contract measures the question); bounded rejection; repair-confirmation of a corrected contract | Author contracts; certify a repair it materially made; renegotiate without bound |
| Worker | kiln (`acp-go`, Muse Spark 1.3) | Execute within the accepted contract; publish artifacts + raw evidence; report compactness failure as a finding | Redesign the architecture; verify own artifacts; upgrade/migrate/recreate seats; start another package on finishing |
| Independent verifier | corvid (same seat, different role) | Reproduce/assess blind-first (freeze own result before reading the verdict), compare claims, write verification receipt + discrepancies | Be the worker on the same package; rest verdict on worker self-report |
| Duty owner / overseer | cairn (`acp-pi-worker`, local Qwen; controller until software is dogfoodable) | Stop overdue work, reconcile processes, resume eligible work **within existing authorization**; own per-attempt one-shot deadlines; per-incident recovery ≤15 min + recovery-repair ≤15 min inside the package's remaining allocations | Change the research question; increase budgets; authorize another package; create work; poll (wake-driven only); certify its own repairs; raise a limit; authorize source changes |
| Controller (software, future) | to be built | Enforce authorized transitions, limits, handoffs; generate IDs/timestamps/hashes; bind attempt identity at dispatch | Make model calls in the transition core; consume anything but recorded agent/human dispositions |
| Sponsor | Brian | Scope/budget/permission decisions; intercede on Tern Codex exhaustion | Be the default operational fallback; invisible scheduler/discrepancy-resolver/liveness-monitor |

## The two closed questions

1. **Overseer recovery budget:** per incident, one ≤15-min recovery + one
   ≤15-min repair of that recovery; corvid ≤10-min verification passes where
   relied-on artifacts/conditions changed. Ceilings, not grants; first-expiring
   limit governs; history and incident identity preserved across restarts,
   renames, amendments; failed recovery stays BLOCKED → Tern; no ladder.
2. **Supervisor liveness:** Tern owns it and the host-side backstop; cairn
   owns per-attempt deadlines and reconciliation. Interim `campaign4-watch`
   timer ≠ specified enforcement (see `transitions.md`).

## Independence rules (binding)

- Worker and verifier must differ.
- Contract author and contract-validity reviewer must differ.
- The contract reader may subsequently verify execution.
- Someone who materially repairs a contract cannot independently certify that
  repair.
- Substantive disputes receive one bounded independent disposition, not
  unlimited review rounds.
- Assignments and permissions must be explicitly accepted before unattended
  operation. These were accepted in `CHARTER.md` (Brian, 2026-09-21).

## Standing constraints carried into every package

- Finishing a package never authorizes starting another. Research waits for
  plumbing unless Tern authorizes low-cost capture. Campaign-3 loop components
  stay off. No autonomous work-creation scheduler: the overseer cannot start a
  row; its own repair budget (above) is what stops the recursion.
- Spend: kiln/corvid cheap, no ceiling; Tern/Codex as needed, exhaustion =
  stop. Machinery runs today until Brian stops it.
