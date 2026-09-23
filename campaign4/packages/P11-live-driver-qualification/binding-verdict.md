# P11-binding-1 — independent binding verdict (corvid)

- **Action:** `P11-binding-1`, start `15:50:30Z`, deadline `16:00:30Z`.
- **Checked against:** `preparation-release-1.json` and
  `live-preparation-1/prep-facts.json`; live registry re-queried read-only.
- **Fixtures under test:** worker `92f3baf8-1790178592`, verifier
  `83d58448-1790178593`, director `05f3f2f0-1790178593`, duty
  `bd003027-1790178593`.

## Verdict: PASS — bindings confirmed; ready for Tern's materialized live signature

### Fixture identity (release ⇄ prep-facts ⇄ live registry all agree)

| role | id | name | lane | workdir | live status |
|---|---|---|---|---|---|
| worker | `92f3baf8-1790178592` | `p11-fixture-worker-20260923T154854Z` | `acp-go` | `.../workdirs/worker` | idle |
| verifier | `83d58448-1790178593` | `p11-fixture-verifier-20260923T154854Z` | `acp-go-deepseek` | `.../workdirs/verifier` | waiting |
| director | `05f3f2f0-1790178593` | `p11-fixture-director-20260923T154854Z` | `acp-go` | `.../workdirs/director` | idle |
| duty | `bd003027-1790178593` | `p11-fixture-duty-20260923T154854Z` | `acp-go-controller` | `.../workdirs/duty` | idle |

- IDs, titles, lanes and workdirs match `preparation-release-1.json` and
  `prep-facts.json` exactly; the four IDs are distinct; each lane binary exists.
- Raw launches `live-preparation-1/{worker,verifier,director,duty}.json` show the
  same id/title/profile/path/command; all `.stderr` are empty (4× rc0).
- **Profile** `campaign4` on every fixture and on the launch environment
  (`AGENTDECK_PROFILE=campaign4`); the five named env vars were unset.
- **Main-seat exclusion holds:** the four fixtures are not among the main IDs
  (`56513e0e`, `493c0317`, `a79067ca`, `0c933c75`); the main seats remain in the
  registry, untouched.
- **Socket incarnation:** no per-workdir socket files exist; the runtime mapping is
  agent-deck-managed via the registry (id/profile/command/path/status), matching
  `prep-facts.json`. Distinct id+command+path per role = distinct incarnations.

### Candidate / source

- Candidate binary at the release path
  `/home/bmosher/projects/agent-loop-releases/agent-loop-1341f0469fba/bin/agent-loop`
  = `c1c49a293ed9434c1f6e1f539fd5d9ebf89a0fab220580cf69ddd821547afac8`, matching
  `candidate_binary_sha256`; source commit `1341f0469fba…`.
- **Not adopted:** the installed `/home/bmosher/.local/bin/agent-loop` is
  `221bb3aa…` (the pre-existing owner), i.e. the candidate is **not** installed
  during prep — consistent with `tasks_authorized:false` and no premature
  adoption. Live must install `c1c49a29…` and verify `BIN_SHA`.

### Timers / bounds

- `campaign4-p11-prep1-deadline.timer` active, next `16:04:44Z`;
  `campaign4-p11-prep1-cleanup.timer` active, next `17:39:44Z` (both verified
  active before launch, AccuracySec=1s per release).
- Constraint for live: 75 m live must end before the cleanup deadline, i.e. the
  live start/signature must be ≤ `16:24:44Z`. Tern signs after this binding
  (≤`16:00:30Z`), so the live window fits.

### No side effects observed

- No tasks sent; no Go `run`/`dispatch`; no faults; registry matches prep; no
  socket/global effects attributable to binding (read-only queries only).

**PASS** to Tern for the materialized live signature. L6 remains predeclared
NOT READY (acknowledgement/60 s component), detection to be assessed live; no
cutover. No source/live/cutover change made by corvid.
