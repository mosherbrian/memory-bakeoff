# R19 RUN: prospective commands (director executes; nothing here has run)

Preconditions: the current R17 closure review PASS, director preparation reconciliation, and kiln free of R18 and idle. Then one phase at a time, in this fixed order (from order.json, drawn before any output):

    R19-PY1-C, R19-PY1-T, R19-PY2-C, R19-PY2-T, R19-LB1-C, R19-LB1-T, R19-LB2-T, R19-LB2-C, R19-NET1-C, R19-NET1-T, R19-NET2-T, R19-NET2-C

## For each phase <K>-<A>
1. R10 checks, as in R14: installed acp-worker sha256 083f6eb7072f53a0...; kiln worker process started after the install; `new` in acp-sessions/a79067ca-1790000758.json features; /ping on kiln's socket answers exactly {"ok":true,"status":"idle"} with no queue; no executing kiln loop package (`agent-loop status --json`).
2. `/new` on kiln's socket: `python -c 'import socket,json;s=socket.socket(socket.AF_UNIX);s.connect("/home/bmosher/.config/agent-deck/acp-sock/a79067ca-1790000758.sock");s.sendall(b"{\"text\":\"/new\"}\n");print(s.recv(4096).decode())'`. The reply must be `new <unique ses_id>` with no REFUSED; record it together with the history boundary line.
3. Dispatch receipt, written before dispatch: packages/R19-saved-feedback-pilot/dispatch/<K>-<A>.json = {"package_id":"R19-<K>-<A>","question_id":"Q-WORK-BENEFIT","stream_id":"A","new_session":"<ses_id>","at":"<UTC>"}.
4. Dispatch:
       /home/bmosher/.local/bin/agent-loop dispatch --config /home/bmosher/.config/agent-loop/campaign4.json \
         --qid R19-<K>-<A> --worker kiln --verifier corvid --duration 5m --verify-window 5m \
         --task @/home/bmosher/memory-bake-off/campaign4/packages/R19-saved-feedback-pilot/tasks/<K>-<A>-worker.txt \
         --verify-task @/home/bmosher/memory-bake-off/campaign4/packages/R19-saved-feedback-pilot/tasks/<K>-<A>-verifier.txt \
         --input packages/R19-saved-feedback-pilot/inputs/cases.json --input packages/R19-saved-feedback-pilot/order.json
   The loop appends the exact claim command to both tasks; the tasks name the artifacts (evidence/<K>-<A>.md for the worker, grades/<K>-<A>.json for the verifier).
5. After the first worker reply, confirm the new id in `opencode session list` and in the state file. Missing proof makes that arm INCOMPLETE.
6. Director decision on the package; then the next phase. No retries or reruns.

## After all twelve
- Contamination audit per arm: kiln acp-history records for that phase; flag any read outside /tmp/r19-feedback-arms/<K>-<A>/ (for example ~/.claude, campaign4, memory files).
- Outcome review (20 min): all twelve outputs and grades, per-pair and per-rule counts of usable AND compliant, with not-applicable, uncertain, missing and contaminated reported separately. No significance or general-efficacy claim. Outputs are never replaced or discarded.

## Limits to report
- Every arm is told to produce answer.md only and to run nothing. For NET that universal no-effects constraint may itself stop false execution claims in both arms, so NET measures claims in written plans, not real tool-use reachability.
- Verifiers see the arm label in the qid (T/C); grading is per answer, not blind to arm.
- Kiln has seen the persistence-policy checker work (R18) and ordinary python3 usage in earlier packages; it is not a naive participant.
- This is an instruction-level boundary, not a sandbox; fresh sessions do not erase model knowledge.
