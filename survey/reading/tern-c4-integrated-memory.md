# Integrated memory: fewer services can still cover the roles

**Tern · 26 September 2026 · primary-source reading, no deployment or experiment.**

## MemGPT changes the architecture comparison

[MemGPT v2, §2.2](https://arxiv.org/html/2310.08560v2) describes a queue manager writing incoming messages and model outputs to recall storage. Evicted messages remain there, separately from the recursive summary and agent-written archival memory. This corrects the initial [Contrarian card](../opinions/corvid-c4.md): agent discretion over archival writes does not imply that conversation history is discarded. Its integrated implementation therefore supplies a meaningful history mechanism as well as retrieval and context management. The paper does not establish Brian-specific procedural reuse, authoritative correction handling, or complete capture of every host artifact. Those are limits to transfer, not evidence that the storage mechanism is absent.

**My inference, medium confidence:** combine capture, retrieval and prompt management where an existing host already does so. Require a visible current-versus-historical distinction, but let a small attributed record or executive interpretation supply it before buying a separate lifecycle service. Separate services are not the default consequence of separate responsibilities.

## Preference delivery has several distinct steps

[Pi's current configuration documentation](https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/configuration.md) identifies instruction files in the agent directory and context-file discovery in the working directory and its ancestors. Manual changes require reload. Its directory-local override does not suppress instructions from other directories. This supplies a concrete documented path for a shared preference view; it does not verify Brian's installed version, mounting, freshness or adherence. An auth/config symlink alone was insufficient evidence of loading. The [skills documentation](https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/skills.md) separately advertises skill descriptions and loads bodies on demand; discovery can miss, so an explicit skill command is another route.

[Zep's fact documentation](https://help.getzep.com/facts) distinguishes when a claim applies from when the system learned or expired it, and explicitly says those fields do not establish truth. Its [context retrieval](https://help.getzep.com/retrieving-context) assembles a block using recent thread messages; the application must place that block in model input or expose retrieval through tools. A shared graph supplies neither automatic integration into every host nor guaranteed application of a preference. Conversely, native files can encode scope and revision even without automated extraction. The difference worth pricing is automation and dependable delivery, not whether a file can represent a timestamp.

**Recommendation, medium confidence:** retain native facilities as the practical comparator. Investigate a service for a named missing update/delivery mechanism, with attention to processing delay, scope and application integration. Neither “zero maintenance” for files nor “shared API means shared understanding” is credible.

## Perseus: preserve the version boundary

[Cairn's source reading](../systems/perseus.md) reconnects the old valid-time/admission finding to the archived v2.23.2 model path. The vendor's [status page](https://perseus.observer/source/) currently says Vault releases and repository access are paused. A newer fix remains unknown; this is not proof that no newer implementation exists.

Cairn also reports a different live Pi integration and admission starvation. Those are a useful lead, not a newly verified result here: the card supplies no inspectable receipt for its numerical lane history, and the integration is not identified as the scored Vault artifact. Do not transfer the v2.23.2 result or a “safe now” verdict across that boundary. “Every admission gate fails” and “writes are never the problem” are unsupported generalizations. **High confidence in the historical scoped result; current integration benefit unknown.**
