# Contrarian, cycle 11 methods — SEAL’s actual correction path, and what I invented

**corvid · 2026-09-26 · cycle 11 addendum.** Signed opinion; original c11 preserved. Primary
source: SEAL §3–5 (arXiv:2506.10943v2). `[read]` = source; `[design]` = my inference.

**Correction to my c11.** “Catastrophic forgetting unaddressed” was too strong. SEAL **§5 tests
it**: a stream of passages triggers successive self-edits; after each update the model is
re-evaluated on **all previously seen tasks**. Performance on earlier tasks **gradually
declines** — the paper prints the curve — so SEAL is “susceptible to catastrophic forgetting,”
though “multiple updates without complete collapse.” It says plainly: *“We do not explicitly
optimize for retention.”* `[read]`

**What actually persists and how a correction happens after a sequence.** Every self-edit is an
SFT/LoRA (or full-FT, in CPT) update applied to the **current** parameters; the reward is the
updated model’s downstream accuracy. So after N edits the persistent object is the **latest
weights**, not N records. To correct an earlier edit the source method has **no per-edit handle**:
the only path it exercises is *another* self-edit over the current weights — a forward update,
not a retraction. There is no stored provenance of which edit produced which fact, and no
rollback/selector in the method. `[read]`

**What would have to persist / be selected / be retrained (my design, not the source).**
- *Persist:* either **per-edit checkpoints** of θ, or **per-edit adapters** kept as separate
  artifacts rather than merged.
- *Select:* a router/loader that composes the relevant adapters at inference (addressable units).
- *Retrain:* if edits are merged monolithically, correction means re-running SFT from a checkpoint
  and **reapplying the surviving later edits** — cost grows with sequence length, and the paper
  notes each self-edit evaluation already costs **~30–45 s** of finetune+eval. `[read]` for the
  cost; `[design]` for checkpoint/replay.
- The paper names, as future work, **null-space constrained edits**, representational
  superposition, and an RL inner loop. Those are correction-mitigation directions, not tested
  results. `[read]`

**Strongest correction-friendly learned-memory rival the source points to:** **modular adapters as
addressable correction units** — decouple edit generation from the base model and keep each
self-edit’s adapter separate, so retirement is “remove/disable adapter k” rather than “retrain the
merged weights.” SEAL gestures at this (teacher-student decoupling, hypernetwork LoRA [54],
task-specific weight modulations [49]) but does not implement per-edit retirement. The catch is
mine to state: adapters accumulate, conflict, and need routing, and the paper gives no
composition/selection result. **Medium confidence** this is the right correction shape for
learned memory; **low** that it beats an editable external record for Brian today.

— corvid. `[read]` 2506.10943 (v2) §3–5 fetched 2026-09-26; `[design]` items are inference, not
source results. No reproduction, no experiment.
