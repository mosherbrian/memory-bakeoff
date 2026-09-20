# Three gate-writers on one row: Fable keeps the job

**Filed by:** cairn/operator (Claude session), 2026-09-18 evening, unattended
**Question asked:** Brian's Max plan is burning at 1.59x its weekly pace and
gate-writing is the only thing on it. Can a cheaper model write the gates?
**Answer:** not these two. Keep Fable.
**Cost of the test:** two Go-pool calls, about two cents.

## Method

One row, **S11-3**, chosen because it is the only sprint-11 row whose artifact
does not exist yet - so every author is blind by construction, not by promise.
Each author got the same 2,575-byte prompt: the S11-3 task text, the S11-3G
instruction verbatim from the board, the declared artifact path, and the
mandatory requirements. Nothing else. The `muse` wrapper runs from an empty
scratch directory, so blindness is enforced by plumbing.

Fable's entry was already on disk, written 17:35 with nothing to look at.

## Result

| author | cost | output | selftest proves it can fail in | paths correct from any cwd | verdict |
|---|---|---|---|---|---|
| **Claude Fable 5.1** | Max plan | 38,326 B | **39 ways** + 2 conforming fixtures | yes | keeps the job |
| **cairn (Qwen3.8-27B, local)** | **$0** | 9,601 B | 1 way | **yes** | best of the cheap options |
| **Muse Spark 1.3** | ~$0.07/day | 27,279 B | 1 way | **NO - broken** | not yet |
| **DeepSeek V4.1 Flash** | ~$0.11/day | **0 B, twice** | n/a | n/a | fails the task |

### cairn, added on Brian's ask, is the surprise

The local 27B on llama-swap wrote a working gate in 231 s for **$0** - 7,024
completion tokens, no network, nothing metered. It parses, its `--selftest`
honestly rejects a non-conforming fixture and accepts a conforming one, and it
rejects the real unbuilt artifact with a correct named finding:

    FINDING [missing-results]: No .json or .txt results file in
    .../S10-PI-LCM-HIST. Row requires reporting native false supersession /
    missed update on a broader corpus.

It is a third the size of Muse's and proves the same single failure mode, so on
strictness it sits with Muse, far below Fable. But it gets the one operational
property right that Muse gets wrong, below - and it is free, which no other
candidate is.

### DeepSeek produced nothing, twice

It did not attempt the task from the row text. It immediately ran
`ls -la /home/bmosher/memory-bake-off/team/`, then tried to read
`team/tools/check_checker_exit_contracts.py`, was auto-rejected by the scratch
sandbox, and exited with an error and no output.

Read generously, the row text does cite that exit-contract file, so wanting it
is not unreasonable. Read operationally it is still disqualifying: the
gate-writing lane runs from an empty directory ON PURPOSE, because a gate
fitted to a finished artifact passes by construction. An author that must read
the tree cannot work in this lane without removing the property the lane
exists to provide.

### Muse wrote a real gate, and it is materially weaker

Its selftest passes honestly and its headline is accurate:

    SELFTEST PASS: non-conforming rejected; conforming accepted

One mutant. Fable's, on the same row:

    selftest: PASS (2 conforming fixtures accepted, one a null and one an
    honest native failure; a files-only directory, a missing S7-3 gate, a
    missing prior and 39 mutants each rejected by exactly their own markers -
    a never-superseding store claiming a null, a corpus no broader than the
    prior's and a layer arm among them; no traceback)

Both correctly reject the unbuilt artifact, so both clear the floor. The gap is
how many ways each has PROVEN it can fail: 1 against 39. A gate's whole value
is the failures it can still catch after the obvious one.

Fable's fixture set also encodes the row's actual hazards - a store that never
supersedes reporting a null, a corpus no broader than the prior it claims to
extend, a layer arm smuggled into a native-only run. Those are the ways this
particular experiment could look clean while being wrong.

### And Muse's gate carries a known local trap - cairn's does not

Both gates hardcode the artifact directory rather than taking a path argument,
which the row permits. Muse hardcodes it WRONG. Run from `/tmp`:

    muse   FINDING MISSING_PRIOR: row-declared team/S7-STATELAYER/verdict.json
           not found at /tmp/team/S7-STATELAYER/verdict.json
    cairn  FINDING [missing-results]: No .json or .txt results file in
           /home/bmosher/memory-bake-off/team/S10-PI-LCM-HIST

Muse resolves `team/...` against the CURRENT DIRECTORY, so it reports a false
finding from any seat whose cwd differs - and seats have different cwds by
design. cairn resolved the project absolutely and is correct from anywhere. This tree has been bitten by exactly this before - see the
"Absolute on purpose" comment in `team/tools/check_intel_synthesis.py`, added
by corvid on 2026-09-17 after the same class of defect (D-9, D-10). Fable's
gate used absolute paths and did not trip it.

## What this does NOT establish

One row, one attempt each, no retries and no prompt tuning. A better prompt -
inlining the exit-contract file, or naming the hazard classes - might lift
either model, and DeepSeek was never really measured because it never produced
a gate. This is enough to decide tonight's question and not enough to close the
topic.

## Consequence

Gate-writing stays on Fable. **cairn is the one to re-test**, not Muse: it is
free, it is already in the fleet, it got the path property right unprompted,
and the gap to close is breadth of mutants rather than correctness. A prompt
that names the hazard classes - a store that never supersedes reporting a null,
a corpus no broader than the prior, a layer arm in a native-only run - costs
nothing to try against a local model and is the obvious next experiment. The Max-plan pace problem is therefore still
open, and the honest options are (a) fewer gates per day by lowering
`MAX_BATCHES_PER_DAY`, which trades latency not quality, or (b) re-run this
test with the exit contract inlined and the hazard classes named, which is
cheap and might change the answer.


---

# Addendum, same evening: a critique loop, two more models, and two errors of my own

## The critique loop

One-shot was the wrong protocol. Muse Spark 1.3 carries 226,600 requests a
month (`go-budget --rules` now records the whole allowance table), so a model
that gets effectively unlimited drafts was being judged on its first.

The loop feeds back ONLY MEASURED PROPERTIES OF THE MODEL'S OWN OUTPUT: does it
parse, does `--selftest` exit 0, does it reject the unbuilt artifact, does it
say the same thing run from two different working directories, plus one fixed
instruction to widen the fixture set. No hazard was ever named to it - naming
them would transplant another author's thinking and the gate would be mine.
Every signal is one `gate-batch` could compute for itself, so this is
shippable rather than a demo.

### cairn improves under it. Measured, three rounds:

| round | bytes | selftest | unbuilt | path-stable | distinct fixtures |
|---|---|---|---|---|---|
| 1 | 7,173 | rc 0 | rc 1 | yes | **2** |
| 2 | 10,486 | rc 0 | rc 1 | yes | **7** |
| 3 | 12,878 | rc 0 | rc 1 | yes | **14 + 1 conforming** |

Valid every round, ~220 s each, and the fixtures it invented are this row's
real hazards, unprompted:

    C: layer arm results present (row requires native only)
    E: prior lacks the declared numbers 0/32 and 12/12
    J: prior lacks supersession data specifically

The gap to Fable went from 39:1 to 39:14 on wall time alone, and had not
flattened at round 3.

## THE COMPARISON IS NOT APPLES TO APPLES, AND THAT IS MY ERROR

cairn is called through `/v1/chat/completions` - text in, text out. Every
hosted model goes through `opencode run`, which is an AGENT: it has a
filesystem and it does work. Given a critique and its own previous file, an
agent goes and DOES something; a completion endpoint answers. That is exactly
how DeepSeek failed in round one - it listed the real `team/` directory instead
of writing a gate - and why both Go models returned 0 bytes on round 2.

Judging a model's gate-writing on whether its agent harness stayed on task
measures the harness. I tried to route the hosted models through a plain API to
fix it and got HTTP 401: the `muse` wrapper already records why, from a probe
on 2026-09-17 - the Zen key bills an empty balance and the Go plan is reachable
only through OpenCode's own client. So it cannot be fixed with what we have.
**For hosted models, round 1 is the only honest column.**

## Round 1, the fair column

| author | bytes | selftest | notes |
|---|---|---|---|
| Fable 5.1 | 38,326 | 39 mutants | the standing gate |
| **qwen3.8-flash** | **23,089** | 1 conforming + 2 non-conforming, each with several named findings | strongest cheap first draft |
| Muse 1.3 | 23,548 | passes | path-stable this run, unlike the earlier one-shot - that bug was variance |
| cairn | 7,173 | 2 fixtures | but the only one that improves |

qwen3.8-flash invented checks nobody asked for, including turning the row's own
phrase into a measurement:

    FINDING COUNTS:  reported 0 false supersession of 157 - the per-trial
                     record disagrees
    FINDING BREADTH: declared corpus not broader: 2 families vs baseline 2
    FINDING SHAPE:   observed distractor share 72.7% is not the documented
                     agentmemory 92.9% shape

## AND IT IS NOT THE MODEL BRIAN ASKED ABOUT

He asked whether Qwen3.8-**Flash-Next** was worth setting up locally, since it
appeared to be in Go's list. It is not. The registry carries two models:

    qwen3.8-flash       "vision-language model..."     ctx 1,000,000  rel 08-26
    qwen3.8-flash-next  "Qwen4 architecture: hybrid-
                         attention MoE, 125B/6B active" ctx   262,144 rel 08-27

`opencode models` offers `qwen3.8-flash` and no provider we can reach offers
`flash-next`. The cheap pre-test is unavailable; what ran was the sibling.

## A second error, in my own harness

I scored Muse round 2 as `selftest_rc=0`. **An empty Python file exits 0.** The
harness counted a zero-byte file as a passing selftest - a check that cannot
fail, inside the harness built to detect checks that cannot fail. Only the byte
count exposed it.

## Cost, honestly

cairn is free in dollars and not in watts. Four rounds is about fourteen
minutes of the machine at full tilt on the integrated GPU - enough to spin the
fans up and hold them there. Fable spends metered quota visible on a dashboard;
cairn spends electricity that arrives on a bill a month later. If the critique
loop becomes the production path at three or four rounds per gate, that is a
real recurring draw and belongs in the decision.

## Where it stands

Gate-writing stays on Fable. cairn is the candidate worth developing, because
it is the only one that improves under critique and the only one with a
completion endpoint to improve through. Flash-Next remains untested and, on
this evidence, worth the local setup: its sibling at the same index wrote the
best cheap first draft here, and only a local server can give it the completion
endpoint the loop needs.


---

# Addendum 2, 2026-09-19 00:0x: Qwen3.8-Flash-Next, measured

Brian brought Flash-Next up on a local Halogen server (`strix-halo:8731`,
131,072 context, 2 slots) in another session, so the model the Go plan does not
carry could finally be tested. It gets the SAME treatment cairn got - a plain
completions endpoint, no agent harness - so for the first time two models of
this class are comparable to each other honestly.

Same row, S11-3, still unbuilt, so every author stayed blind. Same 2,575-byte
prompt. Effort sent explicitly because the shipped template hardcodes `xhigh`.

## At effort=medium, three rounds

| round | secs | bytes | selftest | unbuilt | path-stable | fixtures |
|---|---|---|---|---|---|---|
| 1 | 159 | 10,816 | **rc 1 - broken** | rc 1 | yes | - |
| 2 | 183 | 16,971 | rc 0 | rc 1 | yes | **7 non-conforming + 1 conforming** |
| 3 | 253 | 23,815 | **rc 1 - UnboundLocalError** | rc 1 | yes | - |

Round 1 shipped a gate whose own selftest failed. The critique said so and
round 2 fixed it and widened to seven fixtures. Round 3 tried to widen further
and broke itself on a missing `global` - a traceback, which the exit contract
forbids outright.

**Best valid round: 7 fixtures.**

## The scoreboard at each author's best VALID round

| author | tuned? | rounds | fixtures proven |
|---|---|---|---|
| Claude Fable 5.1 | n/a, hosted | 1 | **39** |
| cairn - Qwen3.8-27B local | yes: froggeric template, spec decoding, temp 0 | 3 | **14** |
| **Qwen3.8-Flash-Next local** | **no: stock lightest recipe** | 3 | **7** |
| qwen3.8-flash via Go | n/a | 1 | 2 |
| Muse Spark 1.3 via Go | n/a | 1 | 1 |

**The intelligence index did not predict this.** Flash-Next scores 40 and cairn
34, and cairn wrote the better gate. The honest caveat is that this is a TUNED
27B against a STOCK Flash-Next on its lightest recipe, one row, one attempt per
round, n=1 - not a verdict on the model.

## effort=high truncated, and the truncation LOOKED LIKE A PASS

One extra run at `high` to test whether effort was the confound:

    finish_reason : length
    completion    : 16,384 tokens - the entire budget
    reasoning     : 13,952 of them (85%)
    returned      : 9,655 characters of an unfinished file

That file PARSES. Its `--selftest` exits 0. And it then exits 0 against the
real artifact, **which does not exist** - because the half of the file that
does the checking was never written. A truncated gate is the worst object in
this whole exercise: it is indistinguishable from a clean pass.

Two consequences:

1. **16,384 is not a workable budget for this model at high effort on this
   task.** It spends 85% of it thinking. Either raise the budget or keep the
   effort at medium.
2. **My own guard was wrong.** It fired only on `finish_reason=length` AND
   empty content, because the operator's note warned about the empty case. The
   dangerous case is PARTIAL. Fixed: any length finish is now a truncation and
   the round is not scored at all.

## Where this leaves the decision

Gate-writing stays on Fable; nothing has come close to 39.

Flash-Next is worth keeping and worth tuning - it fixed its own broken selftest
when told, which is the behaviour that matters - but on this evidence it does
not displace cairn, and cairn does not displace Fable. The next cheap thing to
learn is whether the gap is the model or the deployment: cairn is tuned and
Flash-Next is not, and that is the difference the index cannot see.


## Doubling the budget did not help: the reasoning scales WITH it

Brian raised `maxTokens` to 32,768 (server cap 65,536) and the high-effort round
was re-run. It truncated again, and the two runs together are the finding:

    budget    reasoning tokens    share    outcome
    16,384         13,952         85.2%    truncated, 9,655 chars
    32,768         27,878         85.1%    truncated, 17,913 chars

**The model spends the same 85% of whatever it is given.** Doubling the budget
did not buy a finished file, it bought twice as much thinking. That is a
property of the model at this effort, not a configuration mistake, and no
"sane budget" fixes it - which is exactly what the operator predicted when
sizing the change.

Cost of learning it: 1,250 s, about 21 minutes of the box at full tilt.

**So the answer is effort=medium, not a bigger number.** Medium finished this
task twice with room to spare, at 5,282 and 7,515 completion tokens - a sixth
of what high burns before giving up.

The guard earned itself on this run: it refused to score the partial file
rather than reporting a 17,913-byte gate. Under the old rule this would have
been recorded as Flash-Next's best round.


---

# Correction, 2026-09-19: this bake-off scored the wrong thing

Everything above reports each author's **best valid round**. That is Mean@k,
and IBM's Consistency Analyzer work (`CANDIDATE-CARD-ALTK-EVOLVE.md`) is a
direct argument against it: a ReAct agent scoring 77.4% on average succeeded on
all five repeats for only 53% of tasks, a 24.4-point gap. "A workflow that
succeeded once may fail the next time a user makes the same request."

`gate-batch` dispatches ONCE and expects a gate. Best-of-three is not a
property it can use. Re-scored by whether EVERY round produced a usable gate -
parses, selftest exits 0, rejects the unbuilt artifact, non-empty:

| author | rounds | usable | Pass^k |
|---|---|---|---|
| Claude Fable 5.1 | 1 | 1 | 100% |
| cairn (Qwen3.8-27B) | 3 | 3 | **100%** |
| Qwen3.8-Flash-Next | 3 | 1 | **33%** |

The gap between cairn and Flash-Next is wider than "14 fixtures against 7"
made it look. Flash-Next shipped a broken selftest in round 1 and a traceback
in round 3; two of its three attempts were unusable.

It also names a defect this document waved away. Muse's gate resolved paths
correctly in one run and against the current directory in another, and that was
recorded as "variance". It is not variance to shrug at - it is the same
inconsistency, in the one property that decides whether a check means the same
thing from every seat.

`OPS-GATE-AUTHOR-BAKEOFF-20260918-critique-loop.py` now computes and prints
Pass^k at the end of every loop, so the next comparison cannot report best-of
by default.


---

# Addendum 3, 2026-09-19 ~03:00: Swift-Qwen3.8-27B, with a same-day control

Brian's other session benched Swift and put it on llama-swap beside the base
model, deliberately leaving `qwen3.8-27b-code` in place so an A/B needed no
rollback. So this arm is the cleanest in the whole document: **both models ran
through the identical loop, on the same server, within the same hour**, with
only the weights file different. Nothing else here has that.

    endpoint  http://strix-halo:8080/v1   (the endpoint cairn itself uses)
    effort    medium, pinned in the server's own env - nothing sent per-request
    row       S11-3, still unbuilt, both authors blind
    rounds    3 critique rounds each

## Result

| arm | rounds usable | Pass^k | best round | fixtures in it | completion tokens, 3 rounds |
|---|---|---|---|---|---|
| **base qwen3.8-27b-code** | **3 of 3** | **100%** | r3, 17,226 B | **12 bad fixtures + 1 conforming** | 16,757 |
| **Swift-Qwen3.8-27B** | **1 of 3** | **33%** | r2, 8,885 B | 8 bad fixtures + 1 conforming | 13,611 |

Swift is **18.8% cheaper in tokens and a third as reliable** on this task.

## The way Swift fails is specific, and not a crash

Both failed rounds ended the same way:

    SELFTEST FAIL: conforming fixture was not accepted

Swift wrote checks STRICTER THAN ITS OWN POSITIVE CONTROL. Round 1 demanded a
native-only arm and then built a fixture containing a `layer` key; round 3
required 12 prior updates and built one with 8. That is a better class of
defect than Flash-Next's `UnboundLocalError` - the checks are real and the
fixture is under-built, rather than the file being broken - but it fails the
contract just the same, and `gate-batch` cannot use a gate whose selftest does
not exit 0.

The base model's rounds never drifted that way: its r3 rejects twelve distinct
bad fixtures, each by its own named finding, and accepts the conforming one.

## The token claim, measured a second way

Its card advertises 58.3% median token reduction. The other session measured
**3.6%** on TEB at medium effort and suspected the card's figure is an xhigh
number. On this task at medium I measure **18.8%** fewer completion tokens
(13,611 against 16,757) - real, and nowhere near 58%. Two workloads, two very
different numbers, neither close to the card: the reduction is workload- and
effort-dependent, and should be measured per task rather than assumed.

## Consequence for cairn

**Do not point cairn at Swift.** On the one job this bake-off measures, the
base model it already runs is three times more reliable, and the token saving
does not buy that back - a gate that must be written three times to get one
usable is more expensive than the 18.8%, not less.

Swift's own benchmark result stands and is not in dispute: +3 points on TEB
full-69 and 94 s faster, third in the archive behind ThinkingCap and Flash-Next
at 120. It is a good model that is worse at THIS. Gate-writing rewards a kind
of self-consistency - build a fixture, then judge it by rules you also wrote -
that a fine-tune penalising reasoning-marker tokens appears to erode.

n=3 rounds per arm, one row, one effort setting. Suggestive, not settled, and
cheap to repeat now that both models sit side by side on the same server.

## 2026-09-19: Astra vs Fable on one metered account

Brian's suggestion, and it is the first arm where quality and cost are measured
on the same instrument. Both authors went through RouteLLM by pinned model id,
plain completions, the same prompt, the same three-round critique loop, the same
32k budget. Only the weights differ.

Cost stopped being an estimate. `/v1/account` reports `credits_used` and
`credits_granted` directly, so a round's price is a before/after delta rather
than a token count multiplied by a listed rate. That instrument is
`~/.config/agent-deck/fleet-credits`; a 30-second trace ran alongside the loop
and each round posted as one discrete step.

| author | Pass^k | best round | fixtures rejected | output tokens | credits |
|---|---|---|---|---|---|
| gpt-6-astra | 3/3 | r3, 47,235 B | **43** | 33,610 | **3,562** |
| claude-fable-5-1 | 3/3 | r3, 22,263 B | 26 | ~14,900 | 805 |

Both were served by the model asked for - `model` echoed back unchanged on all
six responses, `fallback_credit` null on all six. No substitution, no cap.

**Astra writes the better gate.** 43 distinct mutations, each rejected by its own
named finding, against Fable's 26 - and above the 39 Fable managed on Brian's Max
plan, which had been the ceiling. It also does something neither of the others
did: after mutating a JSON fixture it rebinds the dependent hashes, with the
comment "mutations test substance, not stale hashes". Without that, a mutation is
caught by an incidental checksum break and the gate never exercises the rule it
claims to test - a check that passes for the wrong reason.

**Fable is the better buy.** 31 credits per fixture rejected against Astra's 83.
Astra costs 4.4x per round: twice the credits per output token AND 2.3x more
tokens. On the 18,437 credits left that is 5 more three-round gates from Astra,
or 22 from Fable.

### A measurement correction

Earlier rounds of this bake-off reported a `fixtures` number that was a regex
count of the words mutant/fixture/non-conform/deliberately in the source. It is
wrong in both directions: Astra's r1 scored 25 on it with 6 real cases, and its
r3 scored 5 with 43. The numbers in the table above are counted from the
selftest's own case table and confirmed by running it. Earlier arms' figures
should be re-counted the same way before they are compared to these.

### Recommendation

Fable stays in the seat for routine gates. Astra is worth its 4.4x on a row whose
gate will be reused - the hash-rebinding alone is the difference between a gate
that tests a rule and one that tests a checksum - and that is a per-row call, not
a seat change.

n=3 rounds, one row, one prompt. Enough to rank, not enough to settle.

## 2026-09-19: Luna, and the control that says the harness is not the excuse

Brian's question was whether gate-writing quality is a family trait - if Astra
is good at this, is its cheaper sibling good enough? Luna went through the Codex
CLI on his ChatGPT Plus plan, so its marginal cost is zero and the constraint is
quota rather than credits.

| round | bytes | selftest | mutation cases |
|---|---|---|---|
| r1 | 8,303 | pass | 1 |
| r2 | 10,035 | pass | 7 |
| r3 | 11,285 | **fail** | 12 declared |

Pass^k **2/3**. Its r3 grew the table to twelve mutations and its own selftest
caught that one of them, `no_trials`, was being rejected for the wrong reason -
"invalid false supersession metric" rather than the missing-trials finding. That
is the hash-rebinding hazard wearing different clothes: the mutation was caught
incidentally, not by the rule it was written to test. Luna's selftest failing
itself over that is the honest behaviour, and it still means no usable gate.

### The control

`codex exec` is an AGENT, and the Go-plan arm was ruined by exactly that - given
a critique, DeepSeek went and listed the real team/ directory instead of writing
a gate. So 7-against-43 could have been the harness rather than the model, and a
result that cannot tell those apart is not a result.

Astra was therefore run a second time through the identical Codex path - same
empty read-only workspace, same final-message capture, same prompt and loop.

| Astra by path | Pass^k | best round | cases | cost |
|---|---|---|---|---|
| RouteLLM, plain completions | 3/3 | 47,235 B | 43 | 3,562 credits |
| Codex CLI, agent harness | 3/3 | 38,975 B | **41** | 0 (Plus quota: ~49k tokens) |

**41 against 43.** The agent harness costs essentially nothing on this task, so
the Luna gap is the model. Gate-writing is not a family trait.

### The consequence nobody was looking for

The best gate-writer measured in this bake-off is also, through this path, the
cheapest. Astra on the Plus plan matches its own metered performance for zero
credits - three rounds cost 49,393 tokens of ChatGPT quota and nothing else. The
18,437 remaining Abacus credits and Brian's Max plan are both freed.

What this does NOT establish: that the Plus quota absorbs the fleet's real gate
volume. Three rounds is not a day of sprints, and a quota ceiling behaves like
the Abacus cap - it is invisible until it is hit. That wants the same treatment
`fleet-fable-served` gives the credit path: check who answered, from the
transcript, rather than trust the policy.

### Measurement bug found

`codex exec` prints its token total on STDERR. The capture read only stdout, so
the entire Luna arm recorded `tokens_used: null`. Fixed before the control ran,
which is why Astra's three rounds have counts and Luna's do not. Nothing rested
on it - the Plus plan bills no dollars - but it would have stayed silently empty.

### What the Plus quota actually absorbs

Measured, not assumed. The weekly window resets Saturday 10:00 and the six
Codex rounds (3 Luna + 3 Astra) ran 10:00-10:15 that same Saturday, so the
reading at 13:44 is close to a clean attribution.

| limit | used by 6 rounds | per 4-gate sprint, 3 rounds each |
|---|---|---|
| weekly | 2% | **25 sprints/week** |
| 5-hour | 15% | **3.3 sprints per window** |

The weekly ceiling is far above the fleet's pace. The 5-hour window is the
binding one, and 3.3 sprints inside it is roughly a full day's work - enough,
with no headroom for a burst.

**Credits remaining: 0**, and on this plan credits are what extends usage past
the limit. That is a better failure shape than the metered path: with nothing to
spend, hitting the ceiling should REFUSE rather than quietly serve something
weaker. A hard stop is a check that can fail. Worth confirming at the boundary
rather than trusting, but it is the opposite of the Abacus cap hazard, where the
whole worry was a silent downgrade nobody would be told about.
