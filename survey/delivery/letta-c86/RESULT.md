# Letta fleet trial — inconclusive within the resource budget

Tern ·26September2026. **Keep the incumbent. This run supplies no later-use comparison and does not establish that Letta memory is better or worse.** The approved single experiment ran on isolated local Letta and native Pi seats, then stopped during intervening work before sessions5–7. No rerun is starting. [Machine-readable result, versions and hashes](result.json).

| Observation | Letta local | Native Pi |
|---|---:|---:|
| Successful model requests, including setup |24|20|
| Input tokens, including cached input |478,447|32,424|
| Output tokens |3,668|1,956|
| Later-use applications / repeat reminders |Not reached|Not reached|
| Wrong-learning controls |Not reached|Not reached|
| Additional purchases/API spend |$0|$0|

Both used existing ChatGPT OAuth, `gpt-5.6-sol`, low reasoning. Subscription quota was consumed; it is not free compute. Go was excluded because the read-only local calculator exposed usage rates, not a verified remaining balance. No Go debit, local-GPU inference, Letta Cloud backend or real-project edits. Copied trial credentials were removed afterward; original credentials were untouched.

**Actual stop:** combined input reached510,871 against a500,000 allowance; output5,624. The final in-flight response caused a10,871-token overshoot, and the next request was rejected. The controller checked completed-response usage before subsequent calls; it did not reserve input tokens before sending. This limitation is recorded, not described as a perfect hard token cap. Per-arm request ceilings were30; neither was exhausted.

**Driver mistake, owned:** the initial controller wrongly subdivided the shared token allowance into250,000 per arm. It stopped after acquisition session2. Tern corrected shared accounting and continued the same agent histories at session3, with no task replay or memory repair. That unplanned controller intervention is retained in [its receipt](accounting-correction.json), along with original and corrected scripts. It is not hidden as a clean uninterrupted run.

**What did work:** the sandboxed install and headless routes worked; both completed the first three teaching sessions. Separate homes/projects prevented access to the other arm and held-out scoring files. The same synthetic prompts, deterministic score predicates and pass/fail thresholds were frozen before task execution. Letta stored a synthetic-fleet memory file and its memory repository had3 commits; this is storage evidence, not evidence of later appropriate use. Setup finished inside the30-minute allowance. Native build scripts initially failed for missing `make`; the headless paths worked with installation scripts disabled. The global Pi launcher was broken, so the comparator used its pinned isolated install.

**Important runtime qualification:** Letta's step-count reflection was configured at5 with automatic merge, but all counted requests came from the foreground process; no separate reflection request was observed. Its local headless results reported step_count0 despite successful model responses. This leaves the intended automatic-upkeep path unproven in this run; it is not evidence that reflection generally fails. Enabling a different trigger or runtime would require a separately authorized follow-up, not a silent substitution.

Versions: Letta Code0.33.2, official ACP adapter0.1.11 installed but headless fallback used, native Pi0.87.1, Node22.22.2. Exact npm integrity values, lockfile/source/driver hashes and request totals are in the result manifest. The trial consumed44 successful model requests including4 successful setup requests. Early connection failures showed zero response tokens and are retained in private setup logs.

**Decision:** no demonstrated reason to switch runtimes. The delivery finding is the substantial context/request overhead of this particular local Letta configuration under the approved cap, plus an unverified step-trigger path. Neither warrants a claim about memory quality. Continue the shipped reflector corrections and provisional label checks on current hosts. Confidence high in the recorded stop/usage, low in any extrapolation to Letta's long-run benefit.
