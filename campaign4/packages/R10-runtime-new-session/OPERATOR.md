# R10 /new: operator notes

**Use.** Send one line over the seat socket: `{"text": "/new"}`. The reply is one of:
- `new <id>`: switched. Model and mode were re-applied to `<id>`.
- `new <id> SWITCHED but ... REFUSED`: switched, but a model or mode pin was refused. The old context is gone. Treat this as an error.
- `new refused: ...`: the seat is busy (a turn is running, prompts are queued, or a permission is pending), another prompt or /new is being admitted, or the lane is pinned with ACP_RESUME. Nothing changed.
- `new failed: ... still on <old>`: the adapter errored, or returned no id or the same id. The old session is still in use.

It never sends a prompt. The pane accepts `/new` too.

**Three records.** The reply id is what the adapter created. acp-history gets one line: `[new session] <old> -> <new> (operator /new ...)`. `acp-sessions/<seat>.json` holds the new id only after the new session answers a prompt; until then it holds `null`, so a restart starts fresh rather than resuming an unconfirmed session (the existing proven-session rule).

**ACP_RESUME lanes** refuse /new. A resume-pinned lane asking for session/new would reopen its named conversation.

**Freshness evidence for a trial.** The reply id differs from every earlier id. The history boundary names both ids. After the first answered prompt, the state file holds the new id, and `opencode session list` shows it for opencode-engine lanes.

**Activation (after PASS, director release only).** Install the exact reviewed bytes, keeping a copy of the old file:

    cp -p ~/.config/agent-deck/acp-worker ~/.config/agent-deck/acp-worker.bak-R10
    install -m 755 <reviewed acp-worker> ~/.config/agent-deck/acp-worker

New code on disk does not change a running worker. Kiln adopts it only on its next start, which is a separately authorized stop/start of idle kiln. Other seats adopt it at their next normal restart; do not restart them for this. To check which version a seat runs, compare the file hash with the worker process's start time and install time; /new answering `new ...` rather than being sent to the model as a prompt proves the new code is live. Test that only on an idle seat.

**Rollback.** `install -m 755 ~/.config/agent-deck/acp-worker.bak-R10 ~/.config/agent-deck/acp-worker`. A worker already running the new code keeps it until its next restart. Any restart is a separate, permission-checked action.

**Mirror.** The source is conductor-chat `workers/acp-worker` on branch `r10-new-session`. Merge after acceptance.
