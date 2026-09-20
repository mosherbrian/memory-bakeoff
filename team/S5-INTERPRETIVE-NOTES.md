# S5 interpretive notes — on file 2026-09-12 ~18:3x PT (GiLMore)

## Provenance

Verity's freeze verdict (OK, item 2 freezes as drafted) was delivered on her
seat at the S5 freeze and pinned two binding interpretive notes — but they
were never written to a file, only claimed conductor-side (the exact
"receipts claim; state is" failure this team files tickets for). Recovered
verbatim 2026-09-12 from seat history 86c6f6ff and filed here by GiLMore.
They bind as of the original freeze time; window-open retroactively inherits
them.

## Note 1 (Verity, binding): Metric-blind assignment

Task-family assignment (including the "same calendar day on the same
objective" fallback — "same objective" is the rule's only judgment term) is
made from task text and timestamps *before* tokens/wall are computed, and is
never revised after seeing metrics. This is the P1B rule: this project
already withdrew one overhead story built on favorable pair selection.

## Note 2 (Verity, binding): Nudged-but-uncalled turns are classless

A turn with a nudge injection but zero perseus calls fails both class
definitions, so it pairs with nothing and lands in the unpaired count —
reported beside S5, since those turns are where nudge overhead escapes the
comparison.

## Conductor pin (GiLMore, 2026-09-12 ~18:3x PT): tokens := `sum`

The frozen rule says "tokens primary" but does not define the token field;
Assay's harness correctly surfaced that `sum` (total per-call work) and
`final` (end-of-turn context footprint) can flip the flag. Pinned NOW, with
n=1 existing and both values visible (+47.5% vs −5.0% on pair 1):

**`tokens` = `sum` — total per-call work.** Rationale, stated with the data
known: (a) `sum` is the metric that can only make the memory arm look worse
(it flagged; `final` did not), so choosing it cannot be framed as favorable
metric selection; (b) `sum` measures what the memory machinery cost this
turn, which is what the +25% overhead flag is about — `final` measures
durable context growth, a different question; (c) both values are emitted in
every report regardless, so nothing is hidden. Decision procedure, not
ignorance of the data, is the guard here. Binding for the window-close run.
