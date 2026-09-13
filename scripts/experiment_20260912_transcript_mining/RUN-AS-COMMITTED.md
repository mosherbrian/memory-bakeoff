# RUN-AS-COMMITTED

- Self-test (synthetic fixtures only, no real transcript content):
  `PYTHONPATH=/home/bmosher/.local/lib/python3.14/site-packages pytest
  tests/test_transcript_mining.py -q` → 7 passed.
- Pilot (all-local outputs; transcript-derived files NEVER enter the repo):
  `python3 scripts/experiment_20260912_transcript_mining/mine.py
  --projects-dir /home/bmosher/.claude/projects
  --project-glob='-var-home-bmosher-memory-bake-off*'
  --out /home/bmosher/.local/share/memory-bakeoff/transcript-mining/pilot-20260913`
  (note the `=` form — the glob starts with a dash).
- State coupling: **READS PRIVATE DATA** (`~/.claude/projects/`); writes
  only to the `--out` directory. Outputs are operator-private: aggregate
  stats may be quoted in team/ findings, excerpts may not.
- Detector evolution during the pilot (each step receipt-driven, see
  team/TRANSCRIPT-MINING-PILOT.md): subagent brief files excluded from
  voice detection; session-continuation summaries, `<task-notification>`
  records and conductor seat-dispatch templates excluded as non-operator;
  env-fact-correction pattern tightened (bounded token spans);
  repeat key = normalized 60-char prefix (catches trailing additions).
- Scaling (NOT yet run): same command with `--project-glob '*'` after
  Brian approves the pilot stats. Expect ~10× the pilot volume.
