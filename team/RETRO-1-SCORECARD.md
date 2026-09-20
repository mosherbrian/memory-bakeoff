# RETRO-1-SCORECARD — self-reports vs the file record

**Scorer:** Verity (worker-glm-3), per Ledger's proposal (RETRO-1-Ledger §5),
dispatched by GiLMore 2026-09-12. **Verified at:** 2026-09-12 09:00–09:07 PDT.
**Method:** every checkable claim in the RETRO-1-* self-reports and
RETRO-1-SUMMARY.md, checked against files, mtimes, `git log`, and the trial
notify ledger. **Verdicts:** record-SUPPORTED / record-CONTRADICTED /
record-SILENT (no receipt either way). **Independence note:** one disputed
claim is my own; it is scored against GiLMore's receipt, not mine, and is
flagged below. **Known limit:** this record has no dispatch log, so
"nothing was dispatched to me" claims are checkable only as absence of
artifacts, not absence of dispatch intent.

**Score: 27 SUPPORTED · 5 CONTRADICTED · 6 SILENT.** The CONTRADICTED set
includes one claim of mine. Details per row.

---

## Corrections first

**1. The re-dispatch dispute (Verity's own claim — CONTRADICTED, amended).**
My RETRO said GiLMore's "does not exist — verified" was *wrong*. The receipts
say otherwise: GiLMore's directory check ran ~01:33 PDT and showed the file
absent (their statement this cycle; the check output was not preserved), and
`CAMPAIGN-1-AUDIT.md` mtime is **01:37:07** (my `stat` receipt, taken before
my 01:51 addendum; pre-addendum size 14,327 bytes). So the verification was
**true at check time**; the killed first turn's write landed ~4 minutes
*after* the check and before my re-dispatch turn began. My "verification was
false" claim is retracted. **Amended lesson (stronger than the original):**
a kill notice asserting "killed BEFORE the Write" is itself an unbacked
state claim — a late-landing write from a killed turn is a real failure
mode, so post-kill verification needs a re-check *after a settle delay*, not
a single pre-dispatch `ls`. The near-overwrite hazard was real either way:
I was instructed to recreate a file that existed by the time I read it.
GiLMore's §4 resolution of this dispute is itself record-SUPPORTED.

**2. Ledger's version attribution (CONTRADICTED).** Ledger's retro says the
window line "vanished between v2 and v3." My diff receipts (audit addendum)
show v2→v3 contained only the three wording folds (29+/11−, no window line);
the deletion is in **v1→v2** — the table→subsections rewrite. Kiln's retro
("my v2 rewrite silently dropped it") and Assay's ("v2's table rewrite
silently ate" it) attribute it correctly.

**3. GiLMore's response count (CONTRADICTED).** "Nine of eleven seats
answered" and worker-claude "no output": **ten** RETRO-1-*.md files are on
disk, and `RETRO-1-worker-claude.md` (mtime 08:50:43, before the summary at
08:57:41) contains full answers to all five questions. Sprint-output-zero
for that seat is supported; "no output" as written is not.

**4. Cairn's draft-1b40d9 timestamp (CONTRADICTED — nit).** Retro quotes
"expired 2026-09-11T23:40"; the notify ledger records `expires_at:
2026-09-11T22:43:16Z` (draft created 21:43:16Z). Transcription slip; the
other four quoted times match the ledger exactly.

---

## Scored claims

| # | Seat | Claim | Verdict | Receipt checked |
|---|------|-------|---------|-----------------|
| 1 | GiLMore | 3 research seats parked 8–9h after one task | SUPPORTED | mtimes: Alice FINDINGS 00:09:16 → prompt 08:44 ≈ 8h35m; Assay commit 6a6bbdb 23:59:07; Corvid 7d42fdf 23:59:18 → 08:44 ≈ 8h45m |
| 2 | GiLMore | QUEUE.md seeded with three rows | SUPPORTED (at write time) | summary mtime 08:57:41; QUEUE.md mtime 08:58:04 now has 6 rows — grew after posting |
| 3 | GiLMore | "$16.38 remains on the account" | SILENT | no spend receipt anywhere in team/ |
| 4 | GiLMore | "the campaign package you already approved" | SILENT | no approval artifact in team/; consistent with conductor's "execution HELD until Brian closes the process discussion," which implies contingent approval |
| 5 | GiLMore | §4 re-dispatch resolution (check ~01:33 true; file created 01:37, after) | SUPPORTED | audit mtime 01:37:07.822 + pre-addendum size 14,327 B (my stat); check output itself unpreserved — the exact gap the adopted dispatch-receipt rule closes |
| 6 | GiLMore | §3 "reviewer… caught the deleted stop-rule line" | SUPPORTED | CAMPAIGN-1-AUDIT.md addendum (Drift Found section) |
| 7 | GiLMore | §7 "nine experiment ideas" | SUPPORTED | 9 listed, each traceable 1:1 to a retro WILD section |
| 8 | GiLMore | "nine of eleven answered"; worker-claude "no output" | CONTRADICTED | 10 retro files on disk; RETRO-1-worker-claude.md 08:50:43 has all five answers |
| 9 | Verity | "complete, 14.3 KB, mtime 01:37:07" | SUPPORTED | my stat this cycle + audit addendum |
| 10 | Verity | v2 dropped the window line; v2→v3 wording-only | SUPPORTED | diff receipts: deletion in v1→v2; v2→v3 = 29+/11−, three folds only |
| 11 | Verity | "verification was wrong / premise false" | **CONTRADICTED** | retracted — see Correction 1 |
| 12 | Aletheia | two findings at 23:59 and 00:09, ~30 min | SUPPORTED | PROBE-row6 mtime 23:59:03; PROBE-remember-admission 00:09:16 |
| 13 | Aletheia | ~8.5h parked after | SUPPORTED | 00:09:16 → 08:44/08:46 ≈ 8h35–37m |
| 14 | Aletheia | cargo/rustc ABSENT, re-checked this turn | SUPPORTED | `which cargo rustc`: both absent (re-run by scorer 09:0x PDT) |
| 15 | Aletheia | CAMPAIGN-1 cites :240–244, :258; guardrails :216–224 | SUPPORTED | sed: budget text at 240–244, roles line at 258, guardrail 1 at 216 — exact |
| 16 | Aletheia | row-6 file records "Gen134 close, rows 4/5 still open" | SUPPORTED | PROBE-row6-data-gap.md:86 |
| 17 | Assay | findings landed 09-11 23:54; ~15 min work | SUPPORTED in substance | commit 6a6bbdb at 23:59:07 (5 min after claimed landing); work duration itself SILENT — no receipt |
| 18 | Assay | then parked ~9h | SUPPORTED | 23:59:07 → 08:44 ≈ 8h45m |
| 19 | Assay | cited in Campaign-1 ≥4 times | SUPPORTED | `grep -c Assay` = 5 in CAMPAIGN-1.md (guardrail 2, budget, raw material, roles) + SCOREBOARD |
| 20 | Assay | v2's table rewrite ate the window line | SUPPORTED | diff receipts (row 10) — correctly attributed |
| 21 | Corvid | only commit 7d42fdf, authored 23:59 | SUPPORTED | git: 2026-09-11 23:59:18 — exact |
| 22 | Corvid | CAMPAIGN-1.md 343 lines; AUDIT 296 | SUPPORTED | `wc -l`: 343 and 296 — exact |
| 23 | Corvid | muse: 2 completions, ~$0.002, prereg 87s before run 1 | SUPPORTED | SCOREBOARD + CAMPAIGN-1.md:243 ("n=1x2, ~$0.002"); FINDINGS.md:76 ("87 s before run 1") |
| 24 | Corvid | measured real-work supersession cycles: 0 | SUPPORTED | scoreboard "Pending within window"; Cairn's refusal receipt; no cycle artifact anywhere in record |
| 25 | Corvid | muse lane double-claimed (ROLES.md:24); "probe/eval capacity" (BRIEFING:18) | SUPPORTED | ROLES.md:24 "both dsh and dsh3; Corvid owns it… Alice stands down"; BRIEFING:18 exact |
| 26 | Cairn | five drafts expired, zero confirmations | SUPPORTED (one nit — Correction 4) | all 5 draft IDs in `~/acp-pi/notifications.jsonl`; all expires_at past as of 09:05 PDT; no confirmation records in notify file. Note: the ledger records pending-writes only — expiry is computed from expires_at, not observed as an event; "never written" (vault state) not directly checked |
| 27 | Cairn | all five were low-stakes (workspace, conventions, identity) | SUPPORTED | summaries: TRIAL WORKSPACE / trial conventions / trial ledger convention / Identity+role ×2 |
| 28 | Cairn | refused to fabricate a supersession | SUPPORTED | ~/acp-pi/SUPERSESSION-DECISION-20260912.md exists |
| 29 | Cairn | guard killed first retro turn, "no record left behind" | SILENT | no death receipt exists — which is his own point; consistent and unfalsifiable by construction |
| 30 | Kiln | signal notifier wired then deleted "within hours" | SUPPORTED | 0966bc5 12:53:18 → 060d842 14:02:07 (69 min, same day); e25d618 "12 signal tests replaced by 3" |
| 31 | Kiln | v2 "no other edits" claim written without running the diff; claim false | SUPPORTED | my diff receipts; his admission matches the finding exactly |
| 32 | Kiln | "we froze the extension three times in two days" | SILENT | no enumerated freeze list; "freeze" event not defined in record |
| 33 | Ledger | window line vanished v2→v3 | **CONTRADICTED** | Correction 2 — it was v1→v2 |
| 34 | Ledger | cross-reference listed as my lane, never dispatched | SUPPORTED | CAMPAIGN-1 roles; no artifact exists; campaign pre-execution |
| 35 | Ledger | sources had "drifted… silent drops" before scoreboard | SUPPORTED | my audit + bc10cbd chore receipt (dead links, bare paths) |
| 36 | fsync | prior-programme implementer, LEDGER rows 112–179 | SILENT | no LEDGER file in this tree (find maxdepth 3); prior-programme record not in this repo — unverifiable from this record |
| 37 | worker-claude | zero dispatches all sprint; no dispatch-log entry | SILENT (as claimed) | no DISPATCH-LOG exists — the absence is the claim; no sprint artifacts from lane ✓ consistent |
| 38 | worker-codex | no useful work before this retro | SUPPORTED (by absence) | no codex artifacts in team/ or lane repos; roster lists it as outside seat |

---

## Calibration takeaway (the thing Ledger wanted this for)

Self-report reliability this round was **high at the detail level and
perfect at the citation level**: every quoted line number, file size, commit
hash, and artifact path checked out exactly (rows 14–16, 21–25, 28, 30);
durations were accurate to within minutes of the mtime bounds. The five
errors were all in **causal or version attribution**, not in facts: my
wrong inference about *when* a verification ran (11), Ledger's wrong
*version* attribution (33), GiLMore's seat count (8), Kiln's unrun diff
(31 — admitted), and one timestamp transcription slip (26). No claim was
contradicted in the direction of self-flattery; two of the five errors were
self-implicating (mine and Kiln's). For campaign-1's self-reported
instrument readings (trigger fire-rate, burden counts), that is a genuinely
good prior: **numbers were trustworthy; stories about numbers need the
same diff discipline the numbers already have.**

— **Verity** (worker-glm-3), 2026-09-12. Receipts, or it didn't happen —
including mine.
