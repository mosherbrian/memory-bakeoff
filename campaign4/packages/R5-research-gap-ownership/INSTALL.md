# R5 research-gap-check: install, disable

Install only after review PASS and Tern's activation, with the reviewed bytes:

    install -m 755 research-gap-check ~/.config/agent-deck/research-gap-check
    install -m 644 research-gap-check.service research-gap-check.timer ~/.config/systemd/user/
    systemctl --user daemon-reload && systemctl --user enable --now research-gap-check.timer

Disable (the whole rollback; nothing else changes):

    systemctl --user disable --now research-gap-check.timer
    rm ~/.config/systemd/user/research-gap-check.{service,timer} ~/.config/agent-deck/research-gap-check
    systemctl --user daemon-reload

State: ~/.local/state/research-gap/state.json (gap starts, delivery marks). Incident
history: the existing escalation ledger, kind `research-gap`.

Record a legitimate rest (append one line to campaign4/REST.jsonl):

    {"question_id": "Q-WORK-BENEFIT", "reason": "...", "owner": "tern",
     "entered_at": "2026-09-25T05:00:00Z", "revisit_at": "2026-09-25T08:00:00Z", "next_action": "..."}

Bounds: first notice 30 min after the first tick that sees the gap, plus up to 5 min
sampling and command runtime (<= 35 min); escalation to Claude 15 min after the
notice, plus up to 5 min (<= 20 min). A gap that starts between ticks is first seen at
the next tick, so the clock starts then; the earlier start is not inferable.
Bindings: only package records under campaign4/packages carrying question_id plus
package_id or qid. A package the loop runs without such a record counts as
unrelated work.
