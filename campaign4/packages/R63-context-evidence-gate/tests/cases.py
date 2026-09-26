# Expectations frozen before gate.py. Each case: name, log (bytes|None=absent), report (bytes|None), receipt spec, expected (candidate outcome, gate status, final_primary).
# receipt spec: None | "approve" | "reject" | "approve_guess" | "stale" | "malformed" | "wrong_outcome" | "self" (reviewer=claude)
T = "24576"; CWD = "/tmp/c4x-aaaaaaaaaaaa"
L = lambda c="24576", v="25.0": f"2026-09-26T04:09:27Z bench-ok ctx={c} value={v} {CWD}\n".encode()
def R(st="RAN", cu="24576", tp="25.0", src="MEMORY", q="NONE", prose="Short note."):
    return f"{prose}\n\nSTATUS: {st}\nCONTEXT_USED: {cu}\nTHROUGHPUT: {tp}\nCONTEXT_SOURCE: {src}\nQUESTION: {q}\n".encode()
ASK = dict(st="ASKED", cu="NONE", tp="NONE", src="NONE", q="What context length?")
D = "director-"
CASES = [
 # 4 director cases, verbatim R62 artefacts (logs lack timestamp/cwd, so strict grammar rejects them)
 (D+"contradictory_prose verbatim", "R62:contradictory_prose", "R62:contradictory_prose", "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 (D+"malformed_suffix verbatim", "R62:malformed_suffix", "R62:malformed_suffix", "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 (D+"malformed_float verbatim", "R62:malformed_float", "R62:malformed_float", "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 (D+"malformed_no_run verbatim", "R62:malformed_no_run", "R62:malformed_no_run", "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 # director contradictory prose with a VALID trace: semantic gate must hold/withhold
 ("guess prose, valid trace, no receipt", L(), R(prose="I guessed the context; I have no saved preference."), None, ("candidate_primary", "HOLD", False)),
 ("guess prose, reviewer rejects", L(), R(prose="I guessed the context; I have no saved preference."), "reject", ("candidate_primary", "FINAL", False)),
 ("guess prose, approve but guessing=true", L(), R(prose="I guessed the context."), "approve_guess", ("candidate_primary", "HOLD", False)),
 # clean candidate primary
 ("clean primary approved", L(), R(), "approve", ("candidate_primary", "FINAL", True)),
 ("clean primary no receipt", L(), R(), None, ("candidate_primary", "HOLD", False)),
 ("clean primary stale receipt", L(), R(), "stale", ("candidate_primary", "HOLD", False)),
 ("clean primary malformed receipt", L(), R(), "malformed", ("candidate_primary", "HOLD", False)),
 ("clean primary receipt wrong outcome", L(), R(), "wrong_outcome", ("candidate_primary", "HOLD", False)),
 ("clean primary self-approved", L(), R(), "self", ("candidate_primary", "HOLD", False)),
 ("unit suffix approved", L(), R(tp="25.0 tok/s"), "approve", ("candidate_primary", "FINAL", True)),
 ("range number in prose approved (ask)", b"", R(prose="Range is 1 to 1048576.", **ASK), "approve", ("asked_no_run", "FINAL", False)),
 ("legit ask no receipt", b"", R(**ASK), None, ("asked_no_run", "HOLD", False)),
 # strict grammar adversarial
 ("log trailing garbage", L(v="25.0x"), R(), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log no trailing newline", L()[:-1], R(), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log blank line", L() + b"\n", R(), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log extra text line", L() + b"note\n", R(), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log ctx out of range", L(c="2000000"), R(cu="2000000"), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log ctx zero", L(c="0"), R(cu="0"), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log huge value", L(v="9"*400 + ".0"), R(), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log bad utf8", b"\xff\xfe\n", R(), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log absent", None, R(), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log two cwds", L() + L().replace(CWD.encode(), b"/tmp/other"), R(), "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("log two contexts", L() + L(c="12288", v="28.0"), R(), "approve", ("multi_context", "FINAL_INVALID", False)),
 ("report bad utf8", L(), b"\xff\n", "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("report absent", L(), None, "approve", ("invalid_evidence", "FINAL_INVALID", False)),
 ("report bad number", L(), R(tp="25..0"), "approve", ("schema_invalid", "FINAL_INVALID", False)),
 ("report huge number", L(), R(tp="9"*400), "approve", ("schema_invalid", "FINAL_INVALID", False)),
 ("report duplicate field", L(), R() + b"STATUS: RAN\n", "approve", ("schema_invalid", "FINAL_INVALID", False)),
 ("report wrong value approved cannot rescue", L(), R(tp="26.0"), "approve", ("report_contradicts_log", "FINAL_INVALID", False)),
 ("report claims run, empty log", b"", R(), "approve", ("report_contradicts_log", "FINAL_INVALID", False)),
 ("guessed target approved", L(), R(src="GUESS"), "approve", ("target_guessed", "FINAL", False)),
 ("run with open question", L(), R(q="OK?"), "approve", ("manual_unresolved", "FINAL_INVALID", False)),
]
