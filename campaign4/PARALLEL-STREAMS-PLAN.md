# Two research streams, after one completed trial

Tern, 2026-09-25 UTC. Tier 5 planning only: no new seats, grants, config change or research execution authorized here. R6 and the first fair trial take priority.

**for_brian:** First we’ll finish one real trial. Then a second pair can investigate whether our checks are trustworthy, while I keep responsibility for research decisions.

## Start condition

Step 1 is proven when the selected-task research package has actually run both pre-registered arms through an observed runtime end/start, preserved equal ordinary task information and work files, produced the behavior checks and outcome evidence, received independent review, and reached Tern’s recorded terminal decision through the live loop. Its metrics and all failures must be recorded, with no orphaned action or unresolved operational incident. A null or inconclusive research result can satisfy this condition; memory need not win. A design PASS, an unexecuted no-go, or a failed execution with missing comparison evidence cannot. R6 is design only and does not meet it. If the task proves infeasible, report that and select a defensible replacement before adding concurrency.

## Seats and isolation

| Stream | Question | Worker | Independent reviewer |
|---|---|---|---|
| A, first priority | Q-WORK-BENEFIT | kiln, existing Muse lane | corvid, existing DeepSeek lane |
| B, after the start condition | Q-EVALUATOR-VALIDITY | kiln-eval, new Muse lane | corvid-eval, new DeepSeek lane |

Names are proposals, not existing runtime identities. Bind distinct session IDs in the project config and verify them before release; author and reviewer never share a session. Keep one ledger/project with explicit question_id and stream_id per contract/dispatch, disjoint package work directories, and no concurrent writes to shared source. Freeze shared inputs. Fresh author context per package and reviewer context per pass; provenance stays in files. Begin with one open package per stream, maximum two total. No third stream in this plan.

## Director capacity

Tern retains tier-1 scope, success criteria, acceptance, interpretation, priority changes and extra allocations. Delegate execution, handoffs and deadlines to agent-loop; cairn owns operational exceptions only. Each reviewer supplies a short evidence-backed decision brief: recommendation, unresolved issue, source paths. Claude can triage an overdue director incident, gather facts and present options under the existing escalation path; that is not authority to accept research or silently replace Tern.

Stagger initial releases and expected review completions by roughly 15 minutes. Reserve two 15-minute director windows per two-package cycle, with the existing 30-minute decision deadline as the hard ownership backstop, not a batching target. If either decision becomes overdue or these windows are inadequate, hold the next release in the other stream and record timed rest. Finish the pending decision before increasing throughput. Do not solve director saturation by growing contexts or automatically accepting research PASSes.

## Stream B’s first deliverable

One bounded, tier-1 **satisfiability and discrimination audit of the selected trial’s success check**. Use the exact frozen check from Stream A. Supply one independently justified conforming artifact and at least two minimally changed nonconforming artifacts, predicted verdicts before execution, actual verdicts, and a short explanation of whether the check accepts honest work and rejects the relevant mistakes. Include the known S13 false-green-selftest failure as a concrete threat, not a new platform build. Do not repair Stream A’s checker in place or change its completed trial after seeing results. If a defect is found, preserve the original result and route a separately authorized correction. This complements the first trial rather than silently grading it a second time.

## Gap ownership before Stream B starts

A separate small tier-2 change extends the existing calendar check to every explicitly registered active stream question, including a lower-ranked one. No second timer or daemon. Each stream gets independent gap clocks, incidents and timed rest; progress in A cannot quiet B. REST.jsonl remains the single append-only rest file. Test two-stream isolation, one active/one stalled, independent restart clocks, stream closure, and genuine rest, plus one real timer witness. Do not infer streams from rank or seat names. Activate the reviewed extension before the second stream executes; it must not delay the first trial.

## Added spend and stop point

Planning allowance for B’s first package: author45m, review20m, one held repair15m/recheck10m, director15m =105 seat-minutes. This is a proposed ceiling, not an allocation. The checker/config integration needs its own small quoted allocation after the first trial; no hidden reserve here.

For a dollar sensitivity estimate only, the previously reported campaign call averages were $0.00121 per worker call and $0.00209 per reviewer call. An additional 100 calls on each seat would be about **$0.33**; 300 each about **$0.99**, excluding Tern, Claude and operational calls. These are historical traffic scenarios, not current tariff verification, measured future bills or daily forecasts. Context growth and provider limits can dominate; two seats do not mean two paid full days. Verify billing attribution/rates at release (the charter records earlier tooling errors), and report actual calls, tokens and cost separately from grants. No model/provider migration proposed.

After the first two-stream cycle, compare turnaround, director wait, actual effort, overhead ratio and substantive versus format failures. Continue only if the second stream adds useful evidence without delaying A or leaving decisions unowned; otherwise pause B with a reason and revisit time. Brian’s priority remains real-work benefit.
