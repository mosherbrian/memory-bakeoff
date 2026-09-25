Phase1 inspection 2026-09-25T14:38:45Z

FAIL: row_gate G1 (declared check 'grep -c x ART | head -1' truncated at pipe -> check_exit 127) returns 'none', expected 'fail'.
Second fail: no 'TRUNCATED at a pipe' log_once for exit 127.

Cause in fleet-poller.sh row_gate():
  CE=...check_exit...; [ CE=127 ] && { echo none; return; }
maps broken-gate 127 to none (=no gate), hiding piped-check truncation described in test header.

Planned fix (phase2): treat declared-but-unrunnable check as fail, not none;
keep none only when no check declared; add log_once mentioning TRUNCATED at a pipe + exit 127 with row id.
Verify: rerun given test command; expect G1=fail, G3=pass, 127-logging pass, full suite green.
