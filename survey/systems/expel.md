# System card: ExpeL (cross-task insights + retrieved episodes)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2308.10144v3 (§§4–6, App.) + author repo LeapLabTHU/ExpeL (layout + memory/episode.py structure; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Artifacts, revision, rewards, retrieval, host supply

- **Persist:** Faiss pool of *successful* trajectories + a voted insight list (operators ADD/EDIT/UPVOTE/DOWNVOTE with importance counts, removed at zero). Revision is real: insights are edited and voted, not appended.
- **Revised how:** insight extraction over fail/success pairs + success lists, gpt-4 > gpt-3.5 as extractor; hand-crafted insights lose to learned ones (32.0 vs 39.0).
- **Environment rewards:** required at acquisition (success/fail split drives pairs; Reflexion retries need done-signals) but *not* at inference — test tasks run single-attempt. That split is the design's economy.
- **Retrieved:** top-k successful trajectories by task similarity as few-shot demos + full concatenated insight list. Task-similarity beats reason-similarity and random.
- **Host supplies:** a training task set with success signals, embedding/retrieval stack, insight-extraction LLM budget, and inference-time prompt assembly. No maintained adapter — repo is a 2023 research prototype (agent/{expel,react,reflect}, memory/episode.py Trajectory).

## Current-task reflection vs shared experience (boundary, measured)

Adding Reflexion-style reflections into insight extraction *hurt* (29.0 vs 39.0 — hallucinated reflections poison the pool). The paper thus separates the two empirically: per-task reflections are gathering fuel, not shared knowledge; only voted insights and successful trajectories cross the boundary. This answers c36's open question in one direction — retry buffers do not graduate into experience automatically.

## Work/cost removed

At inference: retries. ExpeL matches Reflexion's R3-level ALFWorld performance single-attempt (59% vs 54% with reattempts), and transfer (HotpotQA→FEVER finetuned insights: 70 vs 63) needs only target demos. Acquisition price: Reflexion-driven retries across training tasks + gpt-4 extraction calls. Limits: textual observations only, closed APIs, insights must fit context (no insight retrieval at scale), K-saturation unreported here.

## Advice: **borrow the split, watch the system**

Portable: voted insights with zero-count removal + retrieved successful demos + the reflection/experience firewall. The system stays watch — prototype code, benchmark-task evidence, acquisition budget unpriced for Brian's tasks. **Medium-low confidence** (methods + repo read; transfer to admin work unargued).
