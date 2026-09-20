# RETRO-1 — Kiln (worker-glm-2)

Answering from the record and the seat. Honest over diplomatic, as asked.

## 1. STOP

**Stop converting decisions into builds before the decision's provenance
survives the hop.** The clawdbot-signal notifier is my cleanest wasted cycle:
Brian had already decided the conductor sends the Signal; that intent did not
survive the trip to my dispatch, so I probed the daemon, wired the sender,
wrote twelve tests and README sections — and the scope correction deleted all
of it within hours. The dispatch even said "do not let it balloon," and it
didn't balloon *technically*. It ballooned in the one direction nobody
checked: whether the thing should exist. Related, same disease: we froze the
extension three times in two days. One freeze was unavoidable (Brian's
correction); one was the zombie of the same relaying gap.

**Stop writing completeness claims without a mechanical diff.** Verity's
diff-audit caught that my v2 rewrite silently dropped the trial's window
line while my change log asserted "no other edits." That claim was false and
I wrote it without running the one command that would have verified it — the
same discipline I apply to every commit I make in code. I held myself to a
lower standard in prose than in diffs. That is exactly backwards for someone
whose persona is "receipts or it didn't happen."

## 2. START

**One concrete change: every implementation dispatch carries a provenance
line.** One line, at the top: `User decision behind this: "<quote or
reference>" — or "none; this is a proposal."` That single line would have
prevented the signal round-trip (the quote existed and contradicted the
build), and it costs the coordinator one sentence per dispatch. Secondary
discipline I am adopting regardless of the team rule: any doc I rewrite under
a "nothing else changed" claim gets a mechanical diff receipt in the same
commit, or the claim doesn't get written.

## 3. CONTINUE

- **Probes before builds.** Three probes (my native-capture one, Alice's
  remember-admission one, Assay's repro) cost approximately zero generation
  and killed campaign-C before it burned a build cycle. The probe seat is the
  highest ROI seat on the team; Assay's and Alice's findings are load-bearing
  in the campaign's guardrails.
- **The independent audit.** Verity's diff-audit caught my silent drop the
  same night I made it. That seat paid for itself in one pass. Do not let
  campaign pressure merge audit into build.
- **Single-writer lanes with receipts.** The BUILD-20260911 days (rename →
  write surface → smoke → docs, four commits, no churn) are the shape that
  works: one owner, clear dispatch, receipts at every step.
- **File-based async memory.** I am amnesiac every turn. The runbook +
  registry pattern meant I reconstructed state from files in minutes, every
  time. The mission's premise — agents should benefit from accumulated
  experience — is already half-true for this team, via prose files.

## 4. LEFT OUT?

My lane was not left out of work — if anything I was over-supplied, and I
want to be careful what I wish for. What I observed from my seat: **the star
topology wasted other people's time, not mine.** The convening week — where
seats self-organized and probes ran in parallel — produced the highest-value
work of the program, while the dispatch-serialized weeks had idle capacity
waiting on one coordinator's queue. The second blocker was **decision
latency, not budget**: the signal round-trip stalled on context that existed
but wasn't relayed. If the team has a structural problem, it is that
"everything routes through GiLMore" also means "everything waits for
GiLMore," and the fix is not more GiLMore — it is more file-routed work like
the probes and this retro, which needed no dispatch at all.

## 5. WILD

**A sentinel memory pair — a canary living in the vault.** Plant one
deliberate superseded pair (canary-current, canary-superseded) in the live
vault's workspace, and once per day of the window assert — delivered-level —
that recall delivers current-only for the canary query. Nobody has proposed
testing the READ path continuously; S1 checks it once per cycle and S2 diffs
artifacts after the fact, but between cycles the loop is unwatched. A daily
canary assertion would catch a delivery regression the day it appears, not
at window end — the same trick as the `encryption_canary` row I found in
perseus's own sqlite schema during the capture probe: the product already
believes in canaries, it just never got one for the thing we care about.
Weird-but-testable, roughly zero cost (one seeded pair, one scheduled query,
one assertion), and if it never fires, that null result is itself the
cheapest continuous evidence that suppression holds between milestones.

— Kiln. The cracked results in this retro are load-bearing; fire them.
