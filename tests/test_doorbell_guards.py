"""The doorbell wakes the control plane, so every refusal is tested, not assumed.

One script rings doorbells. Each gate below exists because of a specific failure:
the recap gate (recaps lapsed for five generations), the title prefix (a
hand-typed title cost six hours), the origin/main pin and the clean-tree check
including untracked files (a drill fired a live PR), the review and ledger gates
(doorbells rang after a FIX FIRST verdict, and a finding reported three times was
never fixed), and --fire (no safe way to test an irreversible effect).

No test here passes --fire, so the suite cannot ring anything.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "doorbell"
SRC = SCRIPT.read_text()


def run(args, cwd=ROOT):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd,
                          capture_output=True, text=True,
                          env={**os.environ, "PATH": os.environ.get("PATH", "/usr/bin:/bin")})


@pytest.fixture
def recap(tmp_path):
    p = tmp_path / "recap.md"
    p.write_text("Gen116 froze a new version of the measuring stick and ran nothing "
                 "against any model. Twelve brand new subjects, sixty different "
                 "questions, and every record now carries a plain revision number so "
                 "there is an answer the reader can work out instead of guess.\n")
    return p


def test_only_one_doorbell_script_exists():
    assert SCRIPT.exists()
    assert not (ROOT / "scripts" / "ring-doorbell").exists(), \
        "two doorbell scripts means one of them is the untested one"


def test_script_parses():
    subprocess.run([sys.executable, "-c", f"import ast;ast.parse(open({str(SCRIPT)!r}).read())"],
                   check=True)


def test_no_arguments_prints_usage_and_refuses():
    r = run([])
    assert r.returncode == 2


def test_missing_recap_refuses(tmp_path, recap):
    r = run(["116", str(tmp_path / "absent.md"), str(recap)])
    assert r.returncode != 0 and "REFUSED" in r.stdout + r.stderr


def test_short_recap_refuses(tmp_path, recap):
    short = tmp_path / "short.md"
    short.write_text("Done.\n")
    r = run(["116", str(short), str(recap)])
    assert "REFUSED" in r.stdout + r.stderr and "chars" in r.stdout + r.stderr


def test_jargon_recap_refuses(tmp_path, recap):
    """A recap in contract-speak is not a recap."""
    jargon = tmp_path / "jargon.md"
    jargon.write_text(
        "The attempt1 directory verifies against the frozen contract_version and "
        "every artifact carries its sha256 in the manifest, pinned to the recorded "
        "source_commit for the run, so the whole chain reconstructs from a clean "
        "checkout without any further intervention from anybody at all today.\n")
    assert len(jargon.read_text().strip()) > 200, "must pass the length gate to test the jargon gate"
    r = run(["116", str(jargon), str(recap)])
    out = r.stdout + r.stderr
    assert "REFUSED" in out and "jargon" in out


def test_title_prefix_is_constructed_not_accepted():
    assert 'title = f"BAKEOFF_HANDOFF Gen{generation}"' in SRC
    assert 'if not title.startswith("BAKEOFF_HANDOFF")' in SRC


def test_pins_origin_main_not_head():
    assert 'git("rev-parse", "origin/main")' in SRC
    assert 'rev-parse", "HEAD"' not in SRC


def test_untracked_files_count_as_dirty():
    assert "grep -v" not in SRC
    assert 'dirt = git("status", "--porcelain")' in SRC


def test_review_verdict_and_ledger_are_gates():
    """PROCEED and CARRY ring; anything else refuses.

    This asserted the literal `verdict != "PROCEED"`, so when Gen120 changed the
    rule to honour the reviewers' own severity, a correct change broke a test that
    was pinning the old wording rather than the behaviour. Rewritten to state what
    must be true: the two accepting verdicts, the refusal for everything else, and
    the ledger conditions.
    """
    assert '"PROCEED", "CARRY"' in SRC, "both accepting verdicts must be named"
    # A blocking review must still stop the bell: FIX FIRST is not in the accept
    # set, so it falls through to the refusal.
    accept = SRC[SRC.index('if verdict not in ("PROCEED", "CARRY")'):][:400]
    assert "REFUSED" in accept

    assert "LEDGER.md" in SRC and "| OPEN |" in SRC, "open findings must block"
    # Carrying must be real, or "minor" becomes a way to drop findings silently.
    assert '"| CARRIED |" not in text' in SRC
    assert "carrying is not the same as ignoring" in SRC


def test_firing_requires_an_explicit_flag():
    assert '"--fire" in argv' in SRC
    assert "DRY RUN" in SRC


def test_dry_run_creates_nothing(recap):
    before = subprocess.run(["git", "branch", "-a"], cwd=ROOT,
                            capture_output=True, text=True).stdout
    r = run(["116", str(recap), str(recap)])
    after = subprocess.run(["git", "branch", "-a"], cwd=ROOT,
                           capture_output=True, text=True).stdout
    assert before == after, "a run without --fire must not create a branch"
    out = r.stdout + r.stderr
    assert ("REFUSED" in out) or ("DRY RUN" in out), out
