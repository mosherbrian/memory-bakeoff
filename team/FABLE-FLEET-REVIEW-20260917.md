**Review of the autonomous research fleet, 2026-09-17**

I checked the files on disk, and items marked [verified] come from that. I did not run the poller suite or any agent. I am the same model as the author of the brief and as plumb-fable, so expect shared blind spots.

## 1. Top three weaknesses

**A. A green gate counts as done, but the gates check that receipts exist, not that they are true.** All items here are [verified].
- All three S6 gates passed by 08:40, and the poller logged S6-1 and S6-2 "done on EVIDENCE". No corvid verdict exists for either.
- kiln wrote `S6-CORRECTION/review.json` itself. It names Astra as reviewer, but Astra reviewed the predecessor document, not this one. The gate accepts it.
- `publication.json` gives the artifact's own directory as the destination. No stranger can read it there. `memory-bake-off` has no `.git` of its own. It sits inside the home-directory repo, which has one commit ("init", April) and no remote.
- In S6-2, the manifest's `declared_at` is 93 ms before the `results.jsonl` mtime, and one script wrote both. The "declared before run" check cannot fail.
- No code compares gate and artifact mtimes. `rowcheck`, `gate-batch` and the poller have no such comparison; it exists only as prose in the row for corvid. All files are 644 under one uid, so kiln can edit a failing gate.
- **Failure:** a second S4-12, this time with a stronger-looking certificate. It has already happened once, today.
- **Cheapest fix:**
  - Run `git init` in `team/`.
  - Commit each gate when `gate-batch` drains.
  - Commit the design, manifest and corpus before each run.
  - Make gates check commit order and file hash instead of clocks.
  - Make sprint close require `SCVER == SCDONE`; the poller already computes both.

**B. The 2026-09-20 cutover has no spend instrument.**
- From that date, spend is the binding limit. `fleet-quota` has no counter for Go seats, and `fleet-discipline` reports hit rate, not dollars.
- Three changes land on one Sunday: a new provider, concurrency unlocked, and R&D interleaving that grows the prefix.
- Muse cache decays from one minute. A two-minute local test run gives roughly a 60% hit on the next call. So "a working worker keeps its own cache warm" is false on Muse.
- My arithmetic from your numbers: at a 38:1 price ratio, going from 96.7% to 85.2% hit is about 2.9x the cost for the same tokens. This is an estimate.
- **Trigger:** the first full build day on Muse.
- **Fix:**
  - Sum per-message `cost` from `opencode.db` in `fleet-discipline`, and add a daily dollar stop.
  - Put kiln on deepseek-v4.1-flash, which holds 100% out to 25 minutes. `acp-go-deepseek` exists. The brief never says why Muse was chosen.

**C. `QUEUE.md` is the database, the lock, the policy document and the decision log in one file.** [verified]
- It is 172 KB, about 43k fresh tokens each time a seat reads it.
- At least four separate parsers read it: the poller (four parsers inside it), `rowcheck`, `gate-batch` and `fleet-discipline`. Today's `isrow()` guard is not in `fleet-discipline.rows()`, so the table bug is still live there.
- **Trigger:** 09-20. The Z.ai slot serialises writers today; after that, three seats edit the file at once. I expect lost claims, but I have not proven it.
- **Fix:**
  - Keep rows only in `QUEUE.md` and move the prose out.
  - Use one parser, imported everywhere.
  - Add a `claim` command wrapped in `flock`.

## 2. Rules that nothing enforces, and checks that cannot fail

- The mtime rule, the 93 ms pre-registration, the author-written review and the self-destination publication: all covered in 1A.
- **Claimable depth >= 1:**
  - It is sampled once a day at 17:25, and invented rows satisfy it.
  - It is fleet-wide, but every D-row is kiln-only, so corvid's depth is 0 by design.
  - Its own output contradicts itself: "claimable 3 ... 4 of them standing debt". [verified]
- **Page counter:** it counts only lines with `: OK`. A broken pager therefore reads as calm. [verified]
- **Cache alarm:** it fired SLIPPING today on 3 Muse calls (65.6%). There is no minimum call count. [verified]
- **Re-measurement rule, map placement and "never edit config.json":** these are prose only. The "advances neither" exit always passes.
- **Pages:** the instrument read 17 in the last 24 h at 08:51, against a threshold of 6. Your own test says the fixes failed if it still reads 18. That reading falls due at 17:25 today, because the 24 h window still overlaps yesterday.
- **One rule is real:** the two-batch cap is enforced in code.

## 3. Budget model

**Claims that are not evidence as stated:**
- "$0.40/day busy 24-7" was never run for 24 hours; the window is 10 hours. GLM is free, so this is a list-price model, not a bill.
- "The constraint was never spend" cannot be falsified as stated.
- The "150-160 s cliff" is a Muse number. Your own document corrected it the same day. It is still in the `gate-batch` docstring and the alarm text, and it is applied to an Anthropic seat, where this harness reports a 1-hour TTL.

**The conclusion does not follow from the numbers.** $5.47 over 288 polls is about $0.02 per cold call. Stopped costs $0 and busy costs $0.40. So the rule should be "stop a seat when it has nothing to do", not "supply work".

**What the model does not count:**
- The Claude session that builds the fleet, which is the largest spender.
- Astra calls, which any seat can make with no cap. [verified]
- Board reads.
- Brian's hours.
- Rework: S4-12 cost two sprints.

## 4. Staffing

- **The shape is wrong.** There is one builder and four overseers, plus three council seats and Astra. Sprint 6 was 40 minutes of kiln work.
- **Same-model review:** kiln and corvid run the same model. Your own evidence says the cross-model reader caught what the same-model pair missed. Give corvid a different model from kiln; deepseek also suits its gappy traffic.
- **Delete `anvil-oai`.** The `astra` command line tool reaches the same model, and a started seat is only a risk of accidental dispatch.
- **Conductor:** a local 27B model writes the document Brian decides from. Generate the demo from `rowcheck` plus the dispatch ledger, and let cairn add only a plain-language gloss.
- **Missing role 1:** an owner for infra changes. The driving Claude session is the sixth seat, not on the roster, and it tests its own work. Its apostrophe bug went into the live poller today.
- **Missing role 2:** a publication owner with a real external destination.

## 5. Sprint process

- The work took 40 minutes. The ceremony is a demo, three retros, an Astra review, a three-seat council, an Astra decision and Brian's review.
- It stalls at Brian's review every sprint. Nothing says who decides when he is silent.
- "Plan when the last row is claimed" gave about 8 minutes of lead time today, because one seat holds WIP of 1.
- **Fix:**
  - Size a sprint to one kiln-day.
  - Run the ceremony once, at 17:00.
  - If Brian is silent, the fleet stays stopped.
  - Run the retro weekly.

## 6. Delete

- `anvil-oai`.
- The keep-warm proxy and its five design documents. Treat it as dead until the dollar instrument shows a need.
- The debt buffer as a cost device. Keep it as a backlog only.
- R&D done to keep the cache warm. Replace it with a daily one-shot card run on a stopped seat.
- `fleet-ratio`, which is blind to two-thirds of the fleet. Replace it with rows closed on evidence.
- The council contributors. The first run changed no goal. Keep Astra plus the brief.
- The mirror copy of the poller.
- The 13 `.bak-*` files. Use git instead.

## Ranked by failures prevented per cost

1. Make sprint close require the verifier count to equal the done count (one condition).
2. `git init` in `team/`, with commit-order gates.
3. A dollar-per-day figure with a hard stop, and a minimum call count on the cache alarm.
4. deepseek for kiln, and a different model for corvid.
5. Per-seat stop-when-empty.
6. Rows-only `QUEUE.md`, one parser and a `flock` claim.
7. The deletions above.

**What I would not do:**
- Build the proxy.
- Build request-level gating.
- Move the queue to a real database.
- Add seats.
- Lower the 85% floor to stop the alarm.

Each of these adds mechanism to a fleet whose real failure today was certification, not cost.
