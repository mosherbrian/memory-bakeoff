# P12-binding-2 — independent binding verdict (corvid)

- **Action:** `P12-binding-2`, start `02:31:21Z`, deadline `02:41:21Z`.
- **Checked against:** `preparation-release-2.json` (`P12-prepare-2`) and
  `live-preparation-2/` (raw launches, `fixture-ids.txt`, `registry-before/after`);
  live registry re-queried read-only.
- **Fixtures:** worker `41f4ba3b-1790217074`, verifier `f98efe22-1790217074`,
  director `9187fe7b-1790217074`, duty `43e44829-1790217074`.

## Verdict: PASS — bindings confirmed; ready for Tern's exact live signature

### Fixture identity (release ⇄ raw ⇄ live registry all agree)

| role | id | name | lane | workdir | live status |
|---|---|---|---|---|---|
| worker | `41f4ba3b-1790217074` | `p12-fixture2-worker-20260924T023000Z` | `acp-go` | `.../workdirs/worker` | idle |
| verifier | `f98efe22-1790217074` | `p12-fixture2-verifier-20260924T023000Z` | `acp-go-deepseek` | `.../workdirs/verifier` | waiting |
| director | `9187fe7b-1790217074` | `p12-fixture2-director-20260924T023000Z` | `acp-go` | `.../workdirs/director` | idle |
| duty | `43e44829-1790217074` | `p12-fixture2-duty-20260924T023000Z` | `acp-go-controller` | `.../workdirs/duty` | idle |

- IDs, titles, lanes, workdirs and profile match the release and the raw
  `live-preparation-2/{worker,verifier,director,duty}.json`; all `.stderr` empty;
  `fixture-ids.txt` lists the four IDs; `registry-after.json` agrees.
- **Profile** `campaign4`; the five named env vars are unset in the release.
- **Main-seat exclusion holds:** the four fixtures are not among `56513e0e`,
  `493c0317`, `a79067ca`, `0c933c75` (present in the registry, untouched).
- **Incarnation:** 0 per-workdir socket files; agent-deck-managed registry mapping.
- **Minor gap (not blocking):** `live-preparation-2/prep-facts.json` is **absent**
  (the release points to `evidence_dir` = `live-preparation-2`); the raw launches +
  `fixture-ids.txt` + `registry-after.json` provide the binding evidence. Note for
  the record only.

### Candidate / release

- Private release binary
  `/home/bmosher/projects/agent-loop-releases/agent-loop-8ad12b86fa82/bin/agent-loop`
  = `97a57db11aa8a4a87d89fd912804d42ce899bb35b3790742d790d424184a948f`, matching the
  release (`source 8ad12b86fa82`); private release only.

### Timers / bounds

- `campaign4-p12-prepare2-deadline.timer` active, next `02:45:54Z`;
  `campaign4-p12-prepare2-cleanup.timer` active, next `04:30:54Z` (= prep start +
  120 m). The release's `latest_live_start` (start + 45 m) lets a 75 m live window
  end at the cleanup deadline. Prep deadline is after this binding.
- The release records the director-escalation arithmetic correction (137 s, not
  107 s) as a conservative bound under stated functioning timer/manager
  assumptions, not a 60 s delivery promise; live L7 checks duty and recovery.

### No side effects observed

- No tasks/run/dispatch/install; registry matches prep; no sockets or global
  effects attributable to binding (read-only queries only).

**PASS** to Tern for the exact live signature; live/cutover remain held. No
source/live/cutover change made by corvid.
