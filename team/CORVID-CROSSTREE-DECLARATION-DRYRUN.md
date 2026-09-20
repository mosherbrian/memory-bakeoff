# Declaration-extension dry run — what `REPO-CANONICAL.txt` would surface

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, read-only (temp declaration; real file untouched)
**Purpose:** item 2 of `CORVID-EVIDENCE-INTEGRITY-DECISIONS.md` — the live
`check_cross_copy_drift` advisory reads "2 known drifts", which understates the
fork delta (`CORVID-CROSSTREE-FILE-CENSUS.md`). Dry-ran the fix to size the
signal before asking GiLMore to adopt it.

## Dry run

Appended six `shared:` lines to a **copy** of `team/REPO-CANONICAL.txt`
(`--declaration /tmp/…`) — the two missing P2 modules and the four files the
census found diverging — and ran the guard unchanged:

```
cross-copy drift over 3 trees, 12 files — findings: 8
  tests/KNOWN_FAILURES.json (known-drift)   repo=1164fbc8 dsh2=7da171eb dsh3=7da171eb
  RESULTS.md (known-drift)                  repo=abe0832f dsh2=ec3452cd dsh3=abe0832f
  missing in a tree: src/memory_bakeoff/portfolio.py :: ['repo-glm-dsh3','repo-glm-dsh2']
  missing in a tree: src/memory_bakeoff/providers/pi_lcm_store_reader.py :: ['repo-glm-dsh3','repo-glm-dsh2']
  src/memory_bakeoff/longcontext_null.py (NEW)            repo=cf59db82 dsh2=cf59db82 dsh3=31ae0f16
  src/memory_bakeoff/stale_use_penalty.py (NEW)           repo=a1576482 dsh2=a1576482 dsh3=4eddf84a
  src/memory_bakeoff/providers/__init__.py (NEW)          repo=95a69953 dsh2=c890121f dsh3=c890121f
  tests/test_known_failures_baseline.py (NEW)             repo=7b601ae6 dsh2=faf933a2 dsh3=faf933a2
```

So the guard already handles files **absent from a tree** (`missing in a tree:`);
the extension needs no code change, only the declaration edit.

## Reading

- The instrument fixes (`longcontext_null.py`, `stale_use_penalty.py`) are the
  **dsh3 src sync** now validated and handed off — they clear the moment it lands.
- `providers/__init__.py` and `test_known_failures_baseline.py` differ **because**
  the forks lack the P2 module and Kiln's loud-failure guard respectively; they
  clear with the same P2/safety syncs, not independent fixes.
- The two `missing in a tree:` entries are the P2 chain — canonical-only by
  construction, so they will never clear unless the forks take the P2 files or the
  declaration records them as canonical-only.

## Recommendation (GiLMore)

1. **Preferred short term:** add one paragraph to `AGENTS.md`/tree README stating
   the forks lag canonical on the P2 chain and instrument fixes, so "ran across
   three trees" is not over-read — zero new guard noise.
2. **Preferred durable:** declare the P2 modules and safety files, and accept the
   8-finding advisory as the honest standing fork-delta (it shrinks as syncs
   land). To avoid permanent `missing in a tree:` noise for canonical-only files,
   add a `canonical-only:` declaration category (small guard change) rather than
   `shared:`.
3. Either way, the current "2 known drifts" should not be read as the whole fork
   delta.

## Rev 2 (2026-09-14) — with guard 15's new `canonical-only:` category

The guard now supports expected-absence (map rev 22). Re-ran the dry run with the
P2 chain as `canonical-only:` and the four instrument/safety files as `shared:`:

```
canonical-only: src/memory_bakeoff/portfolio.py
canonical-only: src/memory_bakeoff/providers/pi_lcm_store_reader.py
shared: src/memory_bakeoff/longcontext_null.py
shared: src/memory_bakeoff/stale_use_penalty.py
shared: src/memory_bakeoff/providers/__init__.py
shared: tests/test_known_failures_baseline.py
```

```
cross-copy drift over 3 trees, 10 files — findings: 6
  tests/KNOWN_FAILURES.json (known-drift)   repo=1164fbc8 dsh2=7da171eb dsh3=7da171eb
  RESULTS.md (known-drift)                  repo=abe0832f dsh2=ec3452cd dsh3=abe0832f
  src/.../longcontext_null.py (NEW)         repo=cf59db82 dsh2=cf59db82 dsh3=31ae0f16
  src/.../stale_use_penalty.py (NEW)        repo=a1576482 dsh2=a1576482 dsh3=4eddf84a
  src/.../providers/__init__.py (NEW)       repo=95a69953 dsh2=c890121f dsh3=c890121f
  tests/test_known_failures_baseline.py (NEW) repo=7b601ae6 dsh2=faf933a2 dsh3=faf933a2
```

**6 findings, zero `missing in a tree:` noise** (the shared-only Rev-1 form gave
8, two of them the P2 absences). The four `(NEW)` clear as the src/P2 syncs land;
the two `known-drift` are already owned. This is the paste-ready proposal for
`REPO-CANONICAL.txt`; applying only the `canonical-only:` pair (no `shared:`
additions) changes nothing today (the files were not declared before) and just
makes the P2 chain's expected absence explicit.

## Rev 3 (2026-09-14) — full proposal including `extensions/`

Adds the extension gap (`CORVID-EXTENSIONS-CROSSTREE-CENSUS.md`): the four
`pi-change-trigger/` files as `canonical-only:` and the two `pi-perseus-recall/`
files as `shared:`.

```
cross-copy drift over 3 trees, 12 files — findings: 8
  tests/KNOWN_FAILURES.json (known-drift) · RESULTS.md (known-drift)
  src/.../longcontext_null.py (NEW)            repo=cf59db82 dsh2=cf59db82 dsh3=31ae0f16
  src/.../stale_use_penalty.py (NEW)           repo=a1576482 dsh2=a1576482 dsh3=4eddf84a
  src/.../providers/__init__.py (NEW)          repo=95a69953 dsh2=c890121f dsh3=c890121f
  tests/test_known_failures_baseline.py (NEW)  repo=7b601ae6 dsh2=faf933a2 dsh3=faf933a2
  extensions/pi-perseus-recall/index.ts (NEW)  repo=24296ad6 dsh2=1fd3a16a dsh3=1fd3a16a
  extensions/pi-perseus-recall/vault.ts (NEW)  repo=50aefb3f dsh2=97deaffa dsh3=97deaffa
```

**8 findings, zero `missing in a tree:` noise.** The 6 `(NEW)` clear as the
src/P2/extension syncs land; the 2 `known-drift` are owned. This is the complete
paste-ready proposal for `REPO-CANONICAL.txt` — it makes the whole fork delta
(the P2 chain, instrument fixes, and extension A2/trigger gap) a standing, owned
advisory instead of "2 known drifts".

## Applied (2026-09-15)

Both parts are now in `team/REPO-CANONICAL.txt`: the P2 pair as
`canonical-only:` and the four instrument/safety files as `shared:` (rev 23), and
the `extensions/` block (this Rev 3) — `pi-change-trigger` + the perseus watchdog
test as `canonical-only:`, `pi-perseus-recall/index.ts`/`vault.ts` as `shared:`.
Live guard: **6 findings, zero `missing in a tree:` noise** — 2 known + 2
fork-only P2-chain + 2 extension A2. The src-sync `(NEW)` pair cleared when the
landing-steward sweep applied it.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
