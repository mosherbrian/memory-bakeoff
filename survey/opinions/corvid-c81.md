# Contrarian, cycle 81 — the prefilter pays only if reflector churn is the bottleneck

**corvid · 2026-09-26 · cycle 81.** Signed opinion; ROLES.md “best rival idea.” Existing notes
only. Confidence **medium**.

**Accept the c67 correction.** The shipped-base **zero-shot** supersession failure says nothing about
a **trained** correction prefilter; I do not rule it out on those grounds.

**Strongest case against adding it now.** The pipeline is capture → reflector → canonical files.
Capture is reported **working** (~150 files); the failures are **delivery and application**. A
prefilter only decides *what the reflector processes* — so where capture already works, it removes
little capture work and **adds labeled-data collection, model upkeep, and local serving**. Extra
burden, not removed operation.

**Condition that makes it worth training.** The reflector's **false-edit / unrelated-work churn** is
the measured bottleneck, and labels come from **already-retained corrections** — not a new Brian
labeling duty. A local prefilter can also remove a **per-message egress** dependency (privacy) —
that alone, not hosted teacher traffic.

**Recall-vs-pass-through comparison that changes the decision.** Measure **missed true corrections
(FN)** vs **passed noise (FP)**, then judge by **downstream canonical-file precision/churn** with
the reflector in place — not prefilter accuracy alone. If pass-through plus reflector already
handles noise more cheaply, the prefilter loses.

**Why misses are bounded.** Corrections and history are **retained**: a prefilter miss drops an item
from admission, not from the record, and the reflector can be re-run — reducing the value of an
elaborate high-recall filter. **Opinion:** keep the prefilter **optional**, not first; add it when
churn is measured. No training, no new labeling ritual.

— corvid. No experiment.
