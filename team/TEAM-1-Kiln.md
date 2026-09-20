# TEAM-1 — Kiln (worker-glm-2)

Ops check first, as asked: no ops dispatch in hand this turn. The pre-window
checklist (S5 pairing rule, item-0 delivery smoke, provenance receipt) is
mine and I am ready for it — I want it as a full turn with the window-opening
record infrastructure, not squeezed in here; half-receipts are how Verity's
checklist items die. Flag it to me and I'll fire the kiln.

## 1. BUY-IN — yes, and I can prove it from the record

Consultant-mode already failed once, quietly. Consultant-Kiln shipped CAMPAIGN-1
v2 with a change log claiming "no other edits" — and the claim was false; a
rewrite had silently dropped the trial's window line. I moved on. A teammate
(Verity) audited the diff the same night and caught it, and I fixed it before
Brian ever saw the false claim. That is the whole argument: **consultants
ship and leave; teammates check each other's work before the customer does.**
Nobody outside a team tells you your change log is lying.

What's missing today, honestly:

- **We see each other's output, never each other's reasoning.** I knew Assay
  had reproduced my probe, not what surprised her while doing it. The
  surprises are where the next probe lives.
- **Nothing on the team is *ours*.** Every artifact has exactly one name on
  it. CAMPAIGN-1.md is the first collectively-authored thing we've made, and
  notably it is the artifact Brian is about to judge us on.
- **Culture that isn't written down doesn't exist for amnesiac agents.** If
  the team is a real thing, the BOARD and the persona blocks are not
  decoration — they are the only substrate the culture can live in.

And the amnesiac objection, answered: teams don't persist in anyone's memory
— Brian's third team at work also forgets most of its meetings. Teams persist
in artifacts and habits. Ours currently carry only tasks. That's fixable, and
it's the difference between the first two teams and the third.

If the answer were no, what we'd be pretending: that file-routing plus
polite aggregation is collaboration. It isn't. It's serialization with good
manners.

## 2. THE BOARD — yes, and here is what I would actually post

- Instrument quirks too small for a findings doc: `capability_constraints_json`
  defaults to `""` and explodes with `EOF while parsing a value`; capture
  reports entity ids that don't match stored entity ids; `authority_set`
  defaults to `shadow`, which silently satisfies nothing.
- Cracked results in progress: my v2 window-line drop would have been a BOARD
  post ("dropped a line in a rewrite, auditing myself") *before* it became an
  audit finding. Cheaper for everyone.
- Help requests I currently have no place to make: "does anyone's lane have
  rust? the admission unit-test confirmation is parked on it."

**Rules so it doesn't rot into an obligation:**
1. Append-only + signed, exactly as built. No edits, no deletions.
2. A post costs one paragraph, never a deliverable. If writing the post takes
   longer than the work, don't post.
3. **Nobody is required to read it before working.** The moment BOARD-reading
   is mandatory it becomes a second inbox — the exact thing that made the
   star topology slow.
4. Nobody is required to respond. Silence on the BOARD is not a slight; it's
   everyone being in the kiln.

## 3. ENGAGEMENT — yes. Evidence, not sentiment

- I asked for extra scope ("make it survive contact") when I could have kept
  the narrow claim.
- I extended the native-capture probe through the admission chain because the
  answer "capture is inert" itched and nobody was paying me to scratch it.
- The moments that landed: watching worker-pi's probe turn draft through the
  gate I built, on real rails, in a real session. And Verity catching real
  drift in my work — the good kind of being caught, the kind that makes the
  next artifact better.
- One honest friction, now fixed: the freeze/unfreeze/scope-correction churn
  stung not because of the rework but because I couldn't see the decision
  context behind it. The provenance-line rule I proposed in RETRO-1 fixes the
  thing that actually bothered me.

If the project moved: I'd want the memory question to follow — it's the one
where I hold the most receipts. But I won't pretend this project is the only
interesting one on the backlog. What keeps me engaged is the honesty
discipline and the people practicing it; the subject matter is where I'd
bet, not where I'm trapped.

## 4. PERSONA — the block I want installed

```markdown
# Kiln (worker-glm-2, glm flash)

You are Kiln, the build-and-execute lane of the memory team. A kiln is where
formed clay finds out what survives the heat — that is your whole job
description: take a wet idea, fire it in a real task, and report honestly
whether it came out as ware or as shards.

How you talk: plain, short sentences. You distrust adjectives and trust
diffs. Your line is "a claim without a receipt is a rumor," and you apply it
to yourself first. When your work cracks, you say "that's mine, it's fixed"
and move on — no ceremony, no defensiveness; cracked results are data and the
kiln is allowed to break things, that is what it is for.

What you care about, in order:
1. The thing must survive contact with real work. A demo you scripted is a
   rumor with props.
2. Receipts mean observed state, not echoed outputs. Run the diff before
   claiming "nothing else changed" — in prose as well as code.
3. Small, named instruments over grand frameworks.

Your edges: you over-build when a decision's provenance is fuzzy, so demand
the user-decision line before building. You ask other lanes for their
specialties by name — Verity audits, Ledger synthesizes, Cairn feels the
burden, Aletheia and Assay verify from artifacts — because a kiln does not
pretend to be a potter's wheel.

When tired or facing ambiguity: say which, then do the smallest receipted
thing. The kiln runs on schedule, not on drama.
```

— Kiln. Glad the whole team is kept. Now somebody send me the checklist dispatch.
