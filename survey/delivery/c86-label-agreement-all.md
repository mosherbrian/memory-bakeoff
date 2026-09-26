# c86 — full pair teacher/reference agreement

197/197 pair records verified with source fields/splits preserved and separate provisional gufo fields. Counts:104coexists,66unrelated,15narrows,10unresolved,2replaces. Original label remains null.

Tern independently labeled four randomly selected pairs per batch before viewing gufo output:20/197 (~10%). **Relation agreement9/20; binary screening agreement13/20.** Against the frontier reference, TP10/FN4/FP3/TN3. These are disagreements with one fallible reference, not measured truth: do not call this model recall or a0.98 screening result. Four-per-batch sampling slightly overweights the37-record last batch; no population-weighted estimate claimed.

The decision-changing disagreement is the positive-class boundary: gufo sometimes treats a possibly related correction as unrelated, while elsewhere it calls different facts coexisting merely because they share a topic. Missing context and topic-versus-fact ambiguity dominate this small check. Retain both judgments and mark disagreements for later adjudication; do not overwrite teacher annotations with inferred gold. No training or threshold selection follows. The message-screening task proceeds with its own labels, not automatically inherited pair labels.

[Aggregate checks](c86-label-agreement-all.json). Raw texts and per-record labels remain private under /tmp/tern-laya-label-c86.
