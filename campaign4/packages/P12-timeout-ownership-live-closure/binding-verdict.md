# P12-binding-1 — independent binding verdict (corvid)

- **Action:** `P12-binding-1`, start `00:15:15Z`, deadline `00:25:15Z`.
- **Checked against:** `preparation-release-1.json` (`5dd7e011`) and
  `live-preparation-1/prep-facts.json`; live registry re-queried read-only.
- **Fixtures:** worker `f26eb77b-1790208904`, verifier `084c0658-1790208905`,
  director `ad541ba6-1790208905`, duty `0e586486-1790208905`.

## Verdict: PASS — bindings confirmed; ready for Tern's exact live signature

### Fixture identity (release ⇄ prep-facts ⇄ live registry all agree)

| role | id | name | lane | workdir | live status |
|---|---|---|---|---|---|
| worker | `f26eb77b-1790208904` | `p12-fixture-worker-20260924T001400Z` | `acp-go` | `.../workdirs/worker` | idle |
| verifier | `084c0658-1790208905` | `p12-fixture-verifier-20260924T001400Z` | `acp-go-deepseek` | `.../workdirs/verifier` | waiting |
| director | `ad541ba6-1790208905` | `p12-fixture-director-20260924T001400Z` | `acp-go` | `.../workdirs/director` | idle |
| duty | `0e586486-1790208905` | `p12-fixture-duty-20260924T001400Z` | `acp-go-controller` | `.../workdirs/duty` | idle |

- IDs, titles, lanes, workdirs and profile match the release and prep-facts
  exactly; raw launches `live-preparation-1/{worker,verifier,director,duty}.json`
  agree; all `.stderr` empty; `fixture-ids.txt` lists the four IDs.
- **Profile** `campaign4` on every fixture and the launch env.
- **Main-seat exclusion holds:** the four fixtures are not among `56513e0e`,
  `493c0317`, `a79067ca`, `0c933c75`; the main seats remain in the registry.
- **Incarnation:** no per-workdir socket files (0); the runtime mapping is
  agent-deck-managed via the registry (id/profile/command/path/status), as
  prep-facts states; distinct id+command+path per role.

### Candidate / release

- Private release binary
  `/home/bmosher/projects/agent-loop-releases/agent-loop-8ad12b86fa82/bin/agent-loop`
  = `97a57db11aa8a4a87d89fd912804d42ce899bb35b3790742d790d424184a948f`, matching
  the claim; **private release only** (main/installed preview untouched).

### Timers / bounds

- `campaign4-p12-prepare1-deadline.timer` active, next `00:29:00Z`;
  `campaign4-p12-prepare1-cleanup.timer` active, next `02:14:00Z`.
- `latest_live_start` `00:59:00Z`; a 75 m live window ending at the cleanup
  deadline (`02:14:00Z`) fits exactly. Prep deadline (`00:29:00Z`) is after this
  binding.

### No side effects observed

- No tasks/run/dispatch/claims/faults/install; registry matches prep; no sockets or
  global effects attributable to binding (read-only queries only).

**PASS** to Tern for the exact live signature; live/cutover remain held. No
source/live/cutover change made by corvid.
