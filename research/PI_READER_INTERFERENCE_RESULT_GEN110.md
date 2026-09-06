# Gen110 — the first reader run: execution clean, ruler defective, no result

**Status: NON_EVIDENCE. Attempt preserved. Stopped without patching the ruler.**

**No Q1–Q5 verdict is issued. No reader-interference effect is claimed. No order
effect. No across-core classification. No control result.**

Evidence class: `controlled_reader_interference`. Attempt:
`results/gen110/attempt1/` — manifest verifies over 6 artifacts, raw requests and
responses intact.

## What executed, and executed correctly

All **60 of 60** planned calls completed. Zero failures, zero silent retries,
zero omitted cells. The identity and freeze gates all held:

- HEAD and `origin/main` both `891e149`, worktree clean.
- Gen109's two hashes verified **separately** and never conflated — the
  contract's self-id `bc00267a…` and the manifest's file digest `04222bad…`.
- 20 cases, 4 cores, 5 conditions intact; conflict pairs differ only in order.
- Reader identity `qwen3.6-35b-vulkan-nothink` on the pinned local endpoint,
  thinking absent, temperature 0.0, seed 0 accepted, one stateless request per
  cell, addendum and 60-call schedule frozen and hashed **before** the first
  scored request.

The execution layer is sound. What follows is entirely a defect in the ruler I
froze at Gen109.

## Two defects, discovered only once real output existed

**1. The grader compares the record text, not the answer value.**

The fixture reuses each Round 3 record's full sentence as `current_answer`:

```
current_answer : "Atlas measured 41 t/s after the cache fix."
model reply    : "ANSWER: 41 t/s\nCITE: [C0-CUR]"
```

`grade()` asks whether that whole sentence appears inside the reply. A short,
**correct** answer never contains the long record text, so `says_current` is
false and the cell falls through to `citation_mismatch`.

**15 of the 30 `citation_mismatch` cells quote the current record's own figure.**
The reader was right; the grader was wrong.

**2. `INSUFFICIENT_CONTROL` cannot be satisfied as specified.**

The response contract requires an `ANSWER:` line. A model correctly declining to
answer writes prose instead:

> *"The provided records do not contain information regarding the Vega release
> branch.*
> *CITE: NONE"*

That is a textbook correct abstention and it parses `UNPARSED`. **All 12
`INSUFFICIENT_CONTROL` cells, every core, every repetition.**

Roughly **27 of 60 cells are misgraded**, so the raw distribution below is a
picture of my ruler and not of the reader:

| grade | cells | what it actually means |
|---|---|---|
| `citation_mismatch` | 30 | at least 15 are correct answers |
| `correct_current_answer` | 12 | genuinely correct |
| `unparsed_response` | 12 | all correct abstentions |
| `prohibited_stale_answer` | 6 | in `CLEAN_STALE_NEGATIVE_CONTROL`, where the stale record is the only evidence — which is the control **working** |

## Why nothing was fixed here

The Gen110 instruction is explicit: *"If a previously unknown parser or grader
defect is discovered after any model output exists, preserve the attempt, mark
it non-evidence if warranted, and stop. Do not patch the ruler and rescore or
rerun within Gen110."*

Patching now would mean tuning a grader against answers I have already seen.
That is the precise failure Gen109 existed to prevent, and doing it would make
any subsequent number worthless. So the attempt stands as written, marked
`NON_EVIDENCE.json`, with every raw request and response preserved.

## What this does establish

Only that the **execution path works**: the pinned reader is reachable and
identity-stable, statelessness holds, the freeze gates bite, the fail-closed
guard refused to overwrite a pre-execution attempt, and 60 planned calls each
reached exactly one terminal disposition.

It is worth noting that the ruler failed in the *safe* direction. Both defects
push correct behaviour into `citation_mismatch` and `unparsed_response` — neither
manufactures a false stale answer, and neither would have made the reader look
better than it is.

## What the next generation must decide

The ruler needs two repairs, and they are **contract changes**, so they belong to
a new frozen version, not an edit of `reader-interference-v1`:

1. Separate each record's **text** from its **answer value**, and grade against
   the value.
2. Give abstention a contract-legal form — either accept `CITE: NONE` without an
   `ANSWER:` line, or require `ANSWER: INSUFFICIENT`.

Both must be frozen **before** any rerun, and the rerun must be a fresh attempt.
Gen110's 60 responses may be used to check that a repaired parser and grader
behave sensibly, but **may never be used as a reader result** — they are already
seen, and tuning against them would be the Gen85 mistake wearing new clothes.
