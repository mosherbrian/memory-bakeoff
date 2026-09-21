# P2-specify — post-repair verification

- **Verifier:** corvid (named reader; did not author these outputs)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Pass:** bounded post-repair pass (30 min; absolute deadline
  2026-09-21T16:27:00Z). Repair completed 15:57:00Z.
- **Scope:** the single v1 defect only, per the bounded instruction. The v1
  FAIL verdict is preserved at
  `campaign4/p2-attempt-history/verdicts/verification-v1-FAIL.md`
  (sha256 `3cb6847dc61fa50b47e591e5f91c16ebbc17cdbc50bb779004d8b33641f49501`).

## Verdict

**PASS.**

The single defect is repaired, the repair is bounded to exactly one line, the
three unaffected artifacts are byte-identical to v1, and the corrected value
matches the governing dispatch record. No new defect was introduced.

## Step 1 — artifact hashes (recomputed on disk)

| Artifact | sha256 (recomputed) | Expected | Result |
|---|---|---|---|
| `contract.md` | `fd573ad3d068f90afb3182fc145736c828eb34dde0798a5ebc1970076d13845e` | same | UNCHANGED |
| `transitions.md` | `77b795749631b65d7b1907bb25c65c8f03dd5faad0d43c6a355ed65f93b40252` | same | UNCHANGED |
| `ownership.md` | `c8126700897cfcb78cb25c7e481c5ecb32518858a5540e2d804874fdf84e4150` | same | UNCHANGED |
| `walkthrough.md` | `c45c72a268054d83e4878e7e542cedd3dfa00f9773d431ada4047e2bf183238e` | `c45c72a2…` | REPAIRED (v1 was `8cee5920…`) |

The three unaffected artifacts are byte-identical to the v1 copies preserved
under `campaign4/p2-attempt-history/v1/`.

## Step 2 — diff against v1

`diff campaign4/p2-attempt-history/v1/walkthrough.md
packages/P2-specify/walkthrough.md` yields exactly one changed line:

```
60c60
< 15:08:16Z, deadline 16:09:31Z); on publication cairn binds all four hashes →
---
> 15:08:16Z, deadline 16:08:16Z); on publication cairn binds all four hashes →
```

One line, one token (`16:09:31Z` → `16:08:16Z`). The surrounding text, the
ACTUAL / SIMULATED / PROJECTED labelling, and every other byte are intact. The
stored v1 walkthrough hash is `8cee592012f562a2607942bd52f42744833fd06850cbf87ca09fe71870be2d07`,
matching the v1 artifact.

## Step 3 — corrected value against the governing record

`walkthrough.md:60` now reads the P2 bound as `16:08:16Z`, which matches
`campaign4/p2-dispatch-20260921.md:10`: "Initial deadline: absolute
**2026-09-21T16:08:16Z** (start 15:08:16Z + 60m)" — the deadline that replaced
the superseded `16:09:31Z` timer ("75 seconds beyond the allocation",
`p2-dispatch-20260921.md:21-24`). The value is now internally consistent with
the example's recorded start (`start + 60m`) and with cairn's completion log
("inside the 16:08:16Z bound").

## Result

The v1 defect is cleared. The P2 outputs are verified:
`contract.md fd573ad3…`, `transitions.md 77b79574…`,
`ownership.md c8126700…`, `walkthrough.md c45c72a2…`. Freeze remains gated on
Tern's acceptance; a verification PASS is not acceptance.
