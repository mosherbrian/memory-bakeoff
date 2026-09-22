# Delayed receipt, lifecycle identity and the external shadow

Tern; 2026-09-22T21:56:45.282090+00:00.
Input SHADOW-FINDINGS-20260922.md @1eff0d7. Brian independently authorized the
observe-only Go replay in ~/projects/agent-loop. It is allowed to continue; earlier
holds on this campaign's proposed shadow do not veto Brian's separate authorization.
Its translation/disagreements are diagnostic leads, not accepted campaign shadow
validation. No authority to mutate this campaign follows from a replay result.

## Completion time versus recording time

Decision: timely work may be recognized after delayed notification IF trustworthy
pre-deadline evidence binds the EXACT artifact/claim bytes, attempt/action/execution,
authorized actor and original grant. Do not require notification delivery itself to
meet the work deadline unless the contract explicitly made delivery the product.
Never use model-authored claim time alone as proof. Mutable mtimes, free-text ledger
notes and unsigned occurred_at alone are insufficient to backdate acceptance.
A trusted host receipt produced at completion, with output hashes and provenance,
is the intended instrument. Check trusted clock/epoch/uncertainty and version match;
uncertainty straddling deadline gives INCOMPLETE, not a guessed timely result.

Keep recorded_at = actual append time; store proven occurred_at and evidence ref
separately. Evaluate execution/work budget on proven completion time; notification
and recovery delay stay measured independently. Do not erase delayed receipt or
count human discovery as autonomous recovery. Existing CLOCK-AUTHORITY prohibition
on arbitrary occurred_at retro-authorization remains: this is a narrowly specified
proof-based reconciliation, not granting more work time or trusting caller clocks.

This is a prospective design amendment, NOT an implemented public ingress bypass.
Until a separately admitted implementation exists, no manual timestamp substitution
into existing APIs, no changed history. If original lifecycle action is still open,
record explicit authenticated reconciliation. If already terminal, preserve terminal
disposition and review evidence via a separately authorized successor/revision; never
silently reopen or overwrite it. No work after the original bound is authorized.
Historical P6r5 claim03:15/deadline03:23/row03:24 therefore remains UNRESOLVED TIMELINESS
unless qualifying source evidence binds those bytes. It is not automatically late
work, nor automatically timely just because a claim says so.

A verdict completed in-bound but published late follows the same proof rule. Actual
review elapsed beyond allocation remains a deviation/new prospective allocation;
minute-rounded rows do not settle second-level bounds. No retroactive extension.

## Identity and transition rulings

Verification is an independently allocated action on a pinned artifact revision,
not simply another verdict on whatever question happens to precede its row. Explicit
new verification allocation/re-dispatch must declare original package+attempt+artifact,
new verification action/execution and grant, plus whether it resumes unfinished
verification or supersedes a completed review. Same delivery replay dedupes; a new
review cannot erase an earlier verdict. An audit of cancelled work is historical
evidence, not execution resurrected or package accepted. Distinguish action terminal
from package terminal before calling this a missing lifecycle path. If truly missing,
a separate admitted successor must model it; don't overload current one-verdict API.

RUNNING cancellation: interrupt/quiesce the actual execution and record that result
before terminal cancellation, using existing BLOCKED path. A future atomic helper
may expose cancel as one user operation only if stop/ack and durable transitions
remain truthful and bounded. Historical direct CANCELLED rows lacking stop evidence
are unresolved, not invented interrupt events in the shadow translation.

Director decisions in files must be linked by explicit receipt/event reference and
full pin/hash into the future authoritative ledger. Missing link is a publication
integration defect, not proof no decision occurred. Shadow may resolve exact pinned
files, never infer acceptance from message order. Duplicate dispatch IDs need raw
execution/ack/grant evidence to distinguish duplicated observation from actual double
send; missing deadline makes record incomplete, not unlimited authorization.

The shadow's21 order-linked verifications cannot establish authoritative lifecycle
violations until joins are backed by explicit IDs/versioned receipts. Its38 non-worker
jobs require their declared action types; don't force them into worker question states.
Maintain a translation-uncertainty column and original source refs. No instruction
to rewrite or change the external shadow is issued here; its owner can apply these
semantics, and disagreements continue to be findings rather than scorekeeping.

## Confirmed lost-wake cause and current R13

Record the reported wake fix as externally applied under Brian: cross-profile search
with ambiguity refused and FAILED logging (agent-deck732d48b, conductor-chat6382cf4).
Do not claim Tern independently tested it. Campaign commands continue to explicitly
set AGENTDECK_PROFILE=campaign4; cross-profile fallback is not project authorization
and does not permit sending to another project's same-named seat. Future signed live
host inventory must rehash the changed wake executable and retain its semantics.
Existing historical inventory/pins remain evidence, not altered in place.

R13-initial-1 initial grant ended21:33; delayed controller wake21:53 is a confirmed
notification incident, not automatic proof of late work. Claim has caller timestamp
21:05; ledger says timely, but neither alone certifies exact completed bytes. Preserve
actual raw source timing, failed wake and archive hashes before self-verifier amendment.
Initial claim names full host gate unrun and manifest changes.md mismatch: classify
initial output INCOMPLETE against its contract, not acceptance-ready. Do not turn a
120s probe limit into the known~14m gate's execution budget or waive full integration.
Original bytes/claim remain unchanged. Capture late/mismatched doc versions separately.

Cairn now completes the already-authorized serial amendment7962eb0: pin initial attempt
with limits, retire old timer, corvid admission/concrete ingress cases10m, then one
new worker30m and verifier30m only after admission and pins. Full original R13 gate
plus finding11 remains required; no new grant here. If verification already active,
let it finish first as that amendment directs; never overlap or re-dispatch blindly.
No need to wait for Brian or a new director permission once its conditions hold.

Next repair order remains core integrity+independence, then host timing/recovery.
The delayed-completion proof and explicit verification-action semantics belong in
that upcoming host/recovery contract, not silently in R13 or a backfilled TSV row.
No current live release/adoption/retirement; external observe-only shadow unaffected.
