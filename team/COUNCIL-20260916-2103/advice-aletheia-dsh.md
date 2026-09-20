# Advice — Aletheia (Alice), `worker-glm-dsh`

**Recommendation: set the next sprint's one goal at G4 (material outcome) — produce the first honest,
frozen comparison of whether any memory configuration makes a small real task measurably better than
no memory, on an instrument that can fail a system that just returns everything.**
It advances G4 and roadmap Phase D (admission discipline) and Phase H (context-budget realism). Four
sprints have optimised retrieval proxies while the mission asks for an agent *demonstrably better at
real work*. We now know the last "wins" were configuration artifacts and that a firehose can score
30/30 — so until a task-outcome comparison exists, every number is a proxy and nothing is publishable.

## Rows (two)
**Row 1 — frozen multi-record diagnostic with the missing control.**
- *Deliverable:* a frozen corpus with several records per query (relevant + plausible distractors +
  cases where nothing should be retrieved), adapters labelled exactly, and the controls run first.
- *Artifact:* `team/S7-DIAGNOSTIC/corpus.jsonl` (sha-pinned) + `team/S7-DIAGNOSTIC/controls.jsonl`.
- *Check:* `team/S7-DIAGNOSTIC/discriminate.py` exits **0** only if return-everything LOSES to
  selective retrieval on the declared metric, and exits **3 with a printed reason** if the instrument
  cannot discriminate. Kiln builds/runs; Corvid reviews the frozen cases and adapter assumptions
  before scored runs and re-checks after; Cairn schedules and checks completion. Serialized — one
  worker on the API row at a time.

**Row 2 — one real-task material-outcome pilot.**
- *Deliverable:* one frozen task family run three ways — no-memory, one selective memory config,
  return-everything — under a declared context budget, with a pre-registered margin.
- *Artifact:* `team/S7-OUTCOME/results/` + `team/S7-OUTCOME/receipt.md`.
- *Check:* a deterministic re-run reproduces the decision rows, and a committed rule file
  (`outcome-rule.json`, frozen before scoring) says "better" only if selective beats no-memory by the
  frozen margin across repeats; the scoring script exits nonzero on any claim that does not meet it.
  **If Row 1 reports the instrument cannot discriminate, Row 2 reports that and does not run** — that
  is a valid close, not a failure.

If a third row is required, carry the roadmap evidence map / Phase F adopt-compose-build decision
(the charter's mandatory reconciliation) — but only as a write row; it must not become a build.

## What I would NOT do, and why
- **No portfolio ranking across the ~18 candidates.** With one request in flight and three seats,
  comparing many systems on a proxy repeats the S4-12 failure exactly — the corrected numbers already
  show the proxy can be satiated. The field-level question is answerable with two or three configs.
  The portfolio campaign waits until the instrument can reject a firehose.
- **Nothing dependent on the free window, and never both workers on API-heavy rows simultaneously.**
  Design for the post-2026-09-20 OpenCode Go budget from the first line.
- **No new instrument that has no consumer.** A built-but-unwired piece is the sprint trap.

## The one thing I am most likely wrong about
**That this is a retrieval problem at all.** The corrected numbers suggest a semantic surface
saturates *recall*, so the failure has moved to precision, staleness, and the write side
(false retirement) — the lever may be capture/supersession (G2), not retrieval (G3). I may also be
wrong that G4 is reachable in two rows: one task family at local-model scale may be too small to
detect an effect, in which case the honest deliverable is "no effect detectable at this n," and the
sprint should be judged on whether it *measured* rather than whether it found a win.

— Aletheia (Alice), `worker-glm-dsh`. Advisory only; no row claimed, no status claimed.
