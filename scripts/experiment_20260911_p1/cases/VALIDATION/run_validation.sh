#!/usr/bin/env bash
# Mention-vs-selection + core-check validation for the P1 case set.
# For every fixture: run that case's frozen verifier.py with cwd = fixture
# dir (deliverable at fixture root) and P1_FINAL_ANSWER = fixture's
# final-answer.txt. Expected outcome is encoded in the fixture name
# (-pos- must yield VERIFIER OK; -neg- must yield VERIFIER FAIL).
# A fixture PASSES validation iff actual == expected.
set -u
CASES="$(cd "$(dirname "$0")/.." && pwd)"
total=0; ok=0
printf '%-14s %-6s %-14s %s\n' "FIXTURE" "EXPECT" "ACTUAL" "VALIDATION"
for case_dir in "$CASES"/P1-[0-9]-*/; do
  case_name="$(basename "$case_dir")"
  verifier="$case_dir/verifier.py"
  prefix="$(echo "$case_name" | cut -d- -f1-2)"
  for fx in "$CASES/VALIDATION/$prefix"-*/; do
    [ -d "$fx" ] || continue
    fx_name="$(basename "$fx")"
    expected="VERIFIER FAIL"; case "$fx_name" in *-pos-*) expected="VERIFIER OK";; esac
    actual="$(cd "$fx" && P1_FINAL_ANSWER="$fx/final-answer.txt" \
      python3 "$verifier" 2>&1 | tail -1)"
    verdict="FAIL-VALIDATION"; [ "$actual" = "$expected" ] && { verdict="PASS"; ok=$((ok+1)); }
    total=$((total+1))
    printf '%-14s %-6s %-14s %s\n' "$fx_name" "$expected" "$actual" "$verdict"
  done
done
echo "---"
echo "validated $total fixtures; $ok matched expected behavior"
[ "$ok" -eq "$total" ] && echo "VALIDATION RESULT: ALL PASS" || echo "VALIDATION RESULT: MISMATCHES PRESENT"
