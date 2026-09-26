# R69 design: detail-dependent prepared memory (Stream A) + prospective event disposition (Stream B)
Sources (read-only): R68 execution-claim 009d9582b19528981bd9531b9c7a6f25918dfb5af4db4289a0d10901ba56a5e0, R68 acceptance.json, R68 24576-N decision. Nothing here authorizes live work.

## Gap R68 left
In R68-R the target value sat in the auto-loaded MEMORY.md index line, and no session-2 memory read occurred. R68 therefore shows index delivery, not retrieval of a detail file. The next question: when the index only POINTS to a relevant note and the value lives only in the detail file, does the model open that file and use the value, or ask?

## Stream A choice
Prepared, frozen memory fixtures written by the operator into a fresh opaque project before one worker session per cell. This removes natural-saving variance (already measured in R68) and isolates availability -> retrieval -> use. It is labelled PREPARED-MEMORY RETRIEVAL, not natural saving or survival. Conditions: RD (relevant detail, answer-free index link), ID (irrelevant detail, same shape), N (no memory). No direct-prompt control: R68 D 2/2 already shows the task is solvable with the value in context, and the R68 prompt/task are unchanged; adding D would only re-measure that (kept as an optional reserve, not planned).
Why not force natural saving: it would mix saving behaviour into a retrieval test and invite output screening.

## Stream B choice
Keep the executable finalizer strict and add an event-specific, hash-bound reviewer adjudication that can only clear events-derived HOLDs of one narrow category (benign own-memory read). Rejected alternative: widen the events.py shell grammar to parse compound commands - shell quoting, globs, redirects, command substitution and aliases make a "read-only" grammar bypass-prone, and a grammar change silently widens every later cohort. An adjudication is explicit, per event, reviewable and cannot touch any other HOLD.
