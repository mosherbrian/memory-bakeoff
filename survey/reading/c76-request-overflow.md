# Reading note c76 — provider request-overflow: does the API reject, truncate, or configure?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 76.**
Skeleton first; **requirement 2 component hunt**: one current primary Anthropic Messages API
documentation path on input/context-window overflow. Does the server **reject** an oversized
request, **silently truncate**, or expose **configurable** behavior? Separate input-too-long
rejection from output `max_tokens` stopping, model/window limits, and optional compaction. Exact
boundary: the **received request** — not evidence about what a host discarded *before* sending.
Is a fail-on-overflow provider boundary a legitimate narrow requirement-2 **yes**, and what is
still absent from Brian's index path? Pin source/model/option; no API call; if docs don't
establish it, preserve unknown and stop. One queue.

*(facts + rating appended below)*

## The pinned primary (platform.claude.com, read 26 Sep 2026)

**Input overflow is a hard rejection.** Context-windows doc, verbatim: *"If the input alone
already exceeds the model's context window, the API returns a **400 invalid_request_error
('prompt is too long') on every model.**"* Plus a second, distinct boundary: **413
request_too_large** for byte-size limits — on the direct API, Cloudflare rejects **before the
request reaches API servers** (errors doc). So: two server-side refusal modes, both errors, no
silent input truncation documented.

**What must not be conflated with it:**
- **Output-side stop**: on Claude 4.5+, input+`max_tokens` over window is **accepted**; generation
  stops at the window with `stop_reason: "model_context_window_exceeded"` (beta header on earlier
  models). That is a generation stop, not input rejection.
- **One documented silent-adaptation exception, input-side**: oversized **images** default to
  `"downsize"` — scaled **without telling you**; `"error"` is opt-in. So "never silently
  modified" is true for text, **not** for images.
- **Optional compaction** is a separate feature; nothing here makes overflow behavior
  configurable for text.

## The exact boundary

The guarantee attaches to the **received request** (or Cloudflare-received bytes). It says
**nothing about what the host discarded before sending** — which is Brian's failure shape: an
index truncated **client-side** produces a *successful* call with missing memory, never a 400.
The provider boundary can only refuse what arrives whole.

## Requirement 2 rating

**Narrow yes — legitimate**: as a *provider-side fail-on-overflow contract for text input*, this
is a real, documented, non-configurable-toward-silence boundary (400/413), the shape requirement
2 asks for: structural limit, no actor diligence required, observable failure.

**Still absent from Brian's index path:** (1) anything bounding **pre-send** host assembly — the
truncation happens upstream of the guarantee; (2) a **delivery-level** check that intended items
were in the request (the API validates size, not membership); (3) the image downsize exception
kept visible if images enter memory payloads. A matrix cell: *provider request-overflow refusal:
yes (text, received-request scope); host pre-send assembly bound: no; content-membership
assurance: no.*

**Confidence: high on the quoted rejection and the 4.5+ stop-reason split (verbatim doc), high on
the image-downsize exception (verbatim), high that this is not evidence about client-side
truncation (boundary of the guarantee is explicit).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c75.md.