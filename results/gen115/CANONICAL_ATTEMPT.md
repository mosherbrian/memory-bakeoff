# Generation 115 - canonical attempt

**`attempt4` is canonical.**

Earlier attempts are preserved under the evidence contract and are superseded:

- `attempt1` - first write; ledger lacked two RETRACTED claims and the attribution block.
- `attempt2` - added those; still published a per-case unique count under a
  global-sounding phrase, and hardcoded `asserts_stale_as_current`,
  `prompt_discloses_recency` and the `verified_absent_tokens` list as constants
  the runner never computed.
- `attempt3` - artifacts complete, but the runner raised on a stale summary print
  after writing them, so the run did not finish cleanly.
- `attempt4` - **canonical.** Per-row fields computed from the text; the
  disclosure-token scan runs over all 24 conflict prompts and fails closed;
  unique counts published under both methods (global 17/9, per-case 21/9); the
  authored nature of the semantic category stated in the artifact itself.

Defects in attempts 1-2 were found by `glm-5.3` and `glm-5.3-flash`, whose
reviews are committed under `reviews/`.
