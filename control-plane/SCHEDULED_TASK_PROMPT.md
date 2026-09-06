# The scheduled control-plane task

Paste the block below into a ChatGPT scheduled task, set to run **hourly**. Make
five of them in five chats, offset by 12 minutes, and the loop is checked every
12 minutes around the clock with no webhook, no PR title to get right, and no
dependence on the implementer remembering to escalate.

Each task is self-contained: it reads one file and decides for itself. If there
is nothing to do it stops without writing, so four of every five firings should
be silent.

---

Check whether the memory bake-off needs a control-plane instruction.

1. Read `control-plane/PENDING.json` on the `main` branch of
   `github.com/mosherbrian/memory-bakeoff`.

2. If `status` is not `awaiting`, STOP. Do nothing, write nothing, say nothing
   further. This is the expected outcome most of the time.

3. If `status` is `awaiting`, read the `CHATGPT_TO_CODEX` Google Doc. If it
   already carries an instruction whose `source_generation` and `source_commit`
   both equal the values in `PENDING.json`, then this request has already been
   answered — by you or by one of the other scheduled chats. STOP.

4. Otherwise, write the next generation's instruction to `CHATGPT_TO_CODEX`,
   replacing its contents. It MUST begin with exactly these five lines:

       generation: <requested_generation from PENDING.json>
       source_generation: <source_generation from PENDING.json>
       source_commit: <source_commit from PENDING.json>
       trigger_pr: none
       status: requested

   The `source_commit` must be copied verbatim. An instruction pinned to any
   other commit is rejected as stale by the implementer's provenance check and
   your turn is wasted.

5. Before writing, read the top entry of `handoff/CODEX_TO_CHATGPT.md` at that
   exact commit, and the artifacts it names. Work from what is in the repository
   rather than from memory of earlier turns.

6. Lead the instruction with a plain-English section. Brian follows this project
   through that section, not through the artifacts.

## Why it is shaped this way

- **`PENDING.json` is the only trigger.** A webhook that filtered PR titles
  failed silently on 2026-09-06 when a doorbell was mis-titled: the control plane
  was never called for 6h47m, and nothing checked whether the request had been
  delivered. A file that is read on a schedule cannot be mis-addressed.
- **The answer is the lock.** Nothing coordinates the five chats. Step 3 makes a
  second writer a no-op, because a request that is already answered is no longer
  awaiting.
- **The commit pin is not decoration.** The implementer verifies
  `source_generation` and `source_commit` before acting and refuses a mismatch.
  This has already caught two stale handoffs.
