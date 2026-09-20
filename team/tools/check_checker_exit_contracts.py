#!/usr/bin/env python3
"""Process-level exit-contract controls for the evidence-integrity guard set.

Corvid, R&D pulse 2026-09-13 (instantiates Muse batch 4 ACCEPT 4.1; motivated by
Alice's S6 finding: a checker that reports a bad state only in prose, with a zero
exit code, reads as clean to a machine gate).

Each guard's own `--self-test` asserts its detection *logic* but returns 0 for
both clean and dirty inputs, so it never exercises the CLI exit contract. This
driver runs each guard's REAL command line twice:
  - on a minimal CLEAN root  -> must exit 0 and must NOT print the finding marker;
  - on a minimal DIRTY root  -> must exit 1, must NOT be a Python traceback, and
    must print the guard's own finding marker.
If a dirty input ever exits 0, the guard is blind at the gate; if it crashes or
exits 1 without naming a finding, a machine gate still cannot tell detection from
breakage. Fixtures are drawn from each guard's own self-test recipe; the three
artifact-anchored guards reuse their own `_fixture`. The per-guard finding marker
is part of the contract on purpose: changing a guard's summary wording without
updating it here is a contract change, not a silent no-op.

Coverage (2026-09-13): all 16 sibling evidence-integrity guards, including the
six newer ones added after the first driver (`check_ledger_counts`,
`check_orphan_evidence`, `check_rd_thread_labels`, `check_required_metrics`,
`check_map_hashes`, `check_cross_copy_drift`); each gets a real clean/dirty CLI
pair, so a blind guard cannot pass merely by having no control at all. The
covered set is **declared** (`_COVERED_NAMES`) and `main` refuses to report a
clean sweep when a live `check_*.py` is not in it, so a new or renamed guard
cannot silently lose its control while the summary still reads "all hold"
(Alice second-seat, 2026-09-13).

Usage:
  python3 check_checker_exit_contracts.py            # run all controls
  python3 check_checker_exit_contracts.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"_guard_{name}", SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _w(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


# ---- inline fixtures (mirrors each guard's self-test recipe) ----

def _inv_good(root):
    (root / "results" / "ok_run").mkdir(parents=True)
    _w(root, "INDEX.md", "| a | [ok](results/ok_run) |\n")


def _inv_bad(root):
    _inv_good(root)
    _w(root, "results/bad_run/INVALIDATED.md", "x\n")
    _w(root, "INDEX.md", "| a | [bad](results/bad_run) | [ok](results/ok_run) |\n")


def _val_good(root):
    _w(root, "results/good_run/summary.csv",
       "provider,mode,hit@5,all_relevant@5\nengine,raw,0.5,0.4\n")
    _w(root, "RESULTS.md",
       "| Syst | Class | Hit/all-relevant 0.500/0.400 | caveat | research | [good](results/good_run) |\n")


def _val_bad(root):
    _w(root, "results/bad_run/summary.csv",
       "provider,mode,hit@5,all_relevant@5\nengine,raw,0.1,0.1\n")
    _w(root, "RESULTS.md",
       "| Syst | Class | Hit/all-relevant 0.900/0.900 | caveat | research | [bad](results/bad_run) |\n")


def _froz_good(root):
    _w(root, "results/run_a/detail.csv", "provider,retrieved_ids\ne,\"['M001', 'M002']\"\n")


def _froz_bad(root):
    _w(root, "results/run_b/detail.csv", "provider,retrieved_ids\ne,\"['M003', 'X9']\"\n")


def _fork_good(root):
    _w(root, "results/run_a/detail.csv", "query_id,category,relevant_ids,prohibited_ids\nQ001,exact,\"['M001']\",\"[]\"\n")
    _w(root, "results/run_c/detail.csv", "query_id,category,relevant_ids,prohibited_ids\nQ002,exact,\"['M003']\",\"[]\"\n")


def _fork_bad(root):
    _w(root, "results/run_a/detail.csv", "query_id,category,relevant_ids,prohibited_ids\nQ001,exact,\"['M001']\",\"[]\"\n")
    _w(root, "results/run_b/detail.csv", "query_id,category,relevant_ids,prohibited_ids\nQ001,exact,\"['M002']\",\"[]\"\n")


def _qual_good(root): _w(root, "GOOD.md", "agentmemory LongMemEval-S R@5 95.2%.\n")
def _qual_bad(root): _w(root, "BAD.md", "MemOS achieves LongMemEval 89.20 overall.\n")


_AG = ("(measured 2026-09-07, Gen125: 10 passed, 1 failed, 0 skipped, 0 errors)\n"
       "# Pinned by tests/pin.py against\n# tests/KNOWN_FAILURES.json\n")


def _agents_base(root):
    _w(root, "tests/KNOWN_FAILURES.json", json.dumps(
        {"_recorded": "2026-09-07, Gen125 (measured, not typed)",
         "_totals": {"passed": 10, "failed": 1, "skipped": 0, "errors": 0}}))
    _w(root, "tests/pin.py", "# reads KNOWN_FAILURES.json\n")


def _agents_good(root): _agents_base(root); _w(root, "AGENTS.md", _AG)
def _agents_bad(root):
    _agents_base(root)
    _w(root, "AGENTS.md", _AG.replace("10 passed, 1 failed, 0 skipped, 0 errors",
                                      "99 passed, 26 failed, 3 skipped, 5 errors"))


# ---- newer guards: ledger counts / required metrics / RD labels / map hashes /
#      cross-copy drift / orphan evidence. Each gets an explicit clean + dirty
#      real-CLI pair, so the exit-contract driver covers the whole sibling set.

_LEDGER_GOOD = (
    "## CLASSIFICATION — synthetic\n\n### Summary\n\n"
    "| Row | Slot | Claim | Class | Receipt |\n|---|---|---|---|---|\n"
    "| L-S01 | a | c | `vendor-only` | r |\n"
    "| L-S02 | a | c | `vendor-only (narrowed)` | r |\n"
    "| L-S03 | a | c | `third-party-measured` | r |\n"
    "| L-S04 | a | c | `unsourced` | r |\n\n"
    "**Counts:** 2 `vendor-only` · 0 `verified-by-us` ·\n"
    "1 `third-party` · 0 `contradicted` · 1 `unsourced` · 0 `no-claim`.\n"
    "**Located and byte-checked:** 3 of 4 rows.\n\n"
    "### What would move each row\n\n| Row | Action |\n|---|---|\n| L-S04 | trace it |\n"
    "## PROVENANCE — synthetic\n\n"
    "### Origin table (earliest located appearance)\n\n"
    "| Row | Claim | First appeared | Origin artifact | Chain |\n|---|---|---|---|---|\n"
    "| L-S01 | c | 2024-01-01 | art-A | — |\n"
    "| L-S02 | c | 2024-01-02 | art-B | — |\n\n"
    "**Two distinct origin artifacts for two rows:** art-A; art-B.\n\n"
    "The two claims come from two origin artifacts.\n\n"
    "- No benchmark was run; this is provenance, not verification. All two rows\n"
    "  remain `vendor-only`.\n")


def _ledger_good(root): _w(root, "L.md", _LEDGER_GOOD)


def _ledger_bad(root):
    _w(root, "L.md", _LEDGER_GOOD.replace(
        "| L-S03 | a | c | `third-party-measured` | r |",
        "| L-S03 | a | c | `vendor-only` | r |"))


def _ledger_argv(root): return [str(root / "L.md")]


def _req_good(root):
    _w(root, "good/summary.csv",
       "provider,hit@5,prohibited@5,mean_context_chars\nengine,0.5,0.1,100\n")


def _req_bad(root):
    _w(root, "bad/summary.csv", "provider,hit@5,prohibited@5\nengine,0.5,0.1\n")


def _req_argv(root): return [str(root)]


def _label_good(root):
    _w(root, "RD-THREADS.md", "**2000-01-01 — past date-only policy label.**\n")


def _label_bad(root):
    _w(root, "RD-THREADS.md", "**2099-01-01 — future date-only label.**\n")


def _label_argv(root): return [str(root / "RD-THREADS.md")]


def _map_good(root):
    (root / "scripts").mkdir()
    data = b"aaa"
    (root / "scripts" / "check_a.py").write_bytes(data)
    _w(root, "MAP.md",
       "| # | class | guard | sha |\n|---|---|---|---|\n"
       f"| 1 | x | `check_a.py` | `{hashlib.sha256(data).hexdigest()[:8]}…` |\n")


def _map_bad(root):
    _map_good(root)
    p = root / "MAP.md"
    p.write_text(p.read_text().replace(hashlib.sha256(b"aaa").hexdigest()[:8],
                                       "00000000"))


def _map_argv(root):
    return ["--map", str(root / "MAP.md"), "--scripts", str(root / "scripts")]


def _xcopy_good(root):
    (root / "a").mkdir()
    (root / "b").mkdir()
    _w(root, "a/X.md", "same\n")
    _w(root, "b/X.md", "same\n")


def _xcopy_bad(root):
    _xcopy_good(root)
    _w(root, "b/X.md", "different\n")


def _xcopy_argv(root):
    return ["--trees", str(root / "a"), str(root / "b"),
            "--files", "X.md", "--fail"]


def _orph_good(root):
    (root / "results" / "cited").mkdir(parents=True)
    _w(root, "results/cited/summary.csv", "provider,hit@5\nengine,0.5\n")
    _w(root, "INDEX.md", "see results/cited for the number\n")


def _orph_bad(root):
    _orph_good(root)
    (root / "results" / "orphaned").mkdir(parents=True)
    _w(root, "results/orphaned/summary.csv", "provider,hit@5\nengine,0.4\n")


def _orph_argv(root):
    return [str(root), "--cite", str(root), "--fail"]


_LIFE_INDEX = "superseded: L-HS-02 -> L-HS-02a, L-HS-02b\n"


def _life_good(root):
    _w(root, "LIFE.txt", _LIFE_INDEX)
    _w(root, "DOC.md", "L-HS-02a and L-HS-02b are current.\n")


def _life_bad(root):
    _life_good(root)
    _w(root, "DOC.md", "The class for L-HS-02 is contradicted.\n")


def _life_argv(root):
    return [str(root), "--index", str(root / "LIFE.txt")]


def _rt_good(root):
    _w(root, "corpus.py", 'R("M005", "The staging Redis database number is 6.", x)\n')
    _w(root, "DOC.json", '{"ctx": "- [M005] The staging Redis database number is 6."}')


def _rt_bad(root):
    _rt_good(root)
    _w(root, "DOC.json", '{"ctx": "- [M005] The staging Redis database number is 7."}')


def _rt_argv(root):
    return [str(root), "--canonical", str(root / "corpus.py")]


# invocation-corpus binding-reachability guard (adopted from the probe; the
# trigger source is synthetic so the control is hermetic).
_REACH_TS = (
    'const STOPWORDS = new Set(["this", "that", "with"]);\n'
    'export function tokensOf(text) {\n'
    '  return (text.toLowerCase().match(/[a-z0-9][a-z0-9-]{3,}/g) ?? [])\n'
    '    .filter((t) => !STOPWORDS.has(t));\n'
    '}\n')
_REACH_MAN = '{"scenarios":[{"scenario_id":"S1","topic_reachable":true}]}\n'
_REACH_GOOD = (
    '{"scenario_id": "S1", "family": "f", "split": "open", '
    '"records": [{"id": "R1", "summary": "service port"}], '
    '"turns": [{"turn": 1, "type": "filler_plain", "text": "List tickets."}, '
    '{"turn": 2, "type": "moment_topic", "text": "Write the service config."}, '
    '{"turn": 3, "type": "filler_plain", "text": "Show status."}]}\n')
_REACH_BAD = _REACH_GOOD.replace("Write the service config.",
                                 "Check the database health.")


def _reach_good(root):
    _w(root, "trigger.ts", _REACH_TS)
    _w(root, "corpus.jsonl", _REACH_GOOD)
    _w(root, "manifest.json", _REACH_MAN)


def _reach_bad(root):
    _reach_good(root)
    _w(root, "corpus.jsonl", _REACH_BAD)


def _reach_argv(root):
    return ["--corpus", str(root), "--extension", str(root / "trigger.ts")]


# experiment-class schema guard: a record's class must be in the four-value
# vocabulary; missing classes are advisory only.
_EC_GOOD = '[{"provider": "bm25", "experiment_class": "baseline"}]\n'
_EC_BAD = '[{"provider": "x", "experiment_class": "production"}]\n'


def _ec_good(root):
    _w(root, "x/run.json", _EC_GOOD)


def _ec_bad(root):
    _w(root, "x/run.json", _EC_BAD)


def _ec_argv(root):
    return ["--results", str(root)]


# candidate-card vs register consistency guard: cards need a verifier line and a
# register row, and register-table ids need a card.
_CARDREG_CARD = "Title *Good* id arXiv:2601.00001\n\nVerifier: Alice.\n"
_CARDREG_REG = "| 1 | GOOD | t | 2601.00001 | x | Alice |\n"


def _cardreg_good(root):
    _w(root, "CANDIDATE-CARD-GOOD.md", _CARDREG_CARD)
    _w(root, "SPARK-CARD-REGISTER-x.md", _CARDREG_REG)


def _cardreg_bad(root):
    _cardreg_good(root)
    _w(root, "CANDIDATE-CARD-BAD.md", "Title *Bad* id arXiv:2602.00002\n")
    _w(root, "SPARK-CARD-REGISTER-x.md",
       _CARDREG_REG + "| 2 | BAD | t | 2602.00002 | x | Alice |\n")


def _cardreg_argv(root):
    return ["--team", str(root)]


_EXT_TEAM = "team"          # the guard takes the dir holding EXTERNAL-*.md


def _ext_argv(root):
    return [str(Path(root) / _EXT_TEAM)]


def _ext_good(root):
    import pathlib
    ec = _load("check_external_cards")
    (pathlib.Path(root) / _EXT_TEAM).mkdir()
    ec._fixture(pathlib.Path(root) / _EXT_TEAM)


def _ext_bad(root):
    import pathlib
    ec = _load("check_external_cards")
    d = pathlib.Path(root) / _EXT_TEAM
    d.mkdir()
    ec._fixture(d, break_trust=True)


# name -> (clean builder, dirty builder, dirty finding marker regex)
def _build_checks() -> dict:
    g38 = _load("check_gen38_anchor")
    mb = _load("check_membukkit_parity")
    pf = _load("check_protected_findings")

    def g38_good(root): g38._fixture(root)
    def g38_bad(root): g38._fixture(root, perseus_rate=0.4000)
    def mb_good(root): mb._fixture(root)
    def mb_bad(root): mb._fixture(root, mb_hit=0.4)
    def pf_good(root): pf._fixture(root)
    def pf_bad(root): pf._fixture(root); _w(root, pf.HAB_STRESS,
                                           "provider,hit@5,prohibited@5\nhabitus,0.100,0.025\n")

    return {
        "check_invalidated_pointers": (_inv_good, _inv_bad,
                                       r"\[(?:UNCUED|DANGLING)\]"),
        "check_results_value_pointers": (_val_good, _val_bad,
                                         r"RESULTS\.md pointer findings: [1-9]"),
        "check_frozen_id_provenance": (_froz_good, _froz_bad,
                                       r"non-canonical=[1-9]"),
        "check_query_fork": (_fork_good, _fork_bad, r"FORK "),
        "check_gen38_anchor": (g38_good, g38_bad, r"anchor findings: [1-9]"),
        "check_membukkit_parity": (mb_good, mb_bad, r"parity findings: [1-9]"),
        "check_protected_findings": (pf_good, pf_bad,
                                     r"protected-finding drift: [1-9]"),
        "check_longmemeval_qualifiers": (_qual_good, _qual_bad,
                                         r"unqualified LongMemEval score lines: [1-9]"),
        "check_agents_known_failures_consistency": (_agents_good, _agents_bad,
                                                    r"\[DRIFT\]"),
        "check_identifier_lifecycle": (_life_good, _life_bad, r"uncued=[1-9]",
                                       _life_argv),
        "check_ledger_counts": (_ledger_good, _ledger_bad,
                                r"ledger count findings: [1-9]", _ledger_argv),
        "check_required_metrics": (_req_good, _req_bad,
                                   r"required-metric findings: [1-9]", _req_argv),
        "check_rd_thread_labels": (_label_good, _label_bad,
                                   r"\[AFTER-MTIME\]", _label_argv),
        "check_map_hashes": (_map_good, _map_bad,
                             r"coverage-map hash findings: [1-9]", _map_argv),
        "check_cross_copy_drift": (_xcopy_good, _xcopy_bad,
                                   r"cross-copy drift: X\.md", _xcopy_argv),
        "check_orphan_evidence": (_orph_good, _orph_bad,
                                  r"\[ORPHAN", _orph_argv),
        "check_record_text_identity": (_rt_good, _rt_bad,
                                       r"forks/drifts: [1-9]", _rt_argv),
        "check_invocation_corpus_reachability": (_reach_good, _reach_bad,
                                                 r"unreachable-topic", _reach_argv),
        "check_experiment_class_schema": (_ec_good, _ec_bad,
                                          r"out-of-vocabulary", _ec_argv),
        "check_card_register_consistency": (_cardreg_good, _cardreg_bad,
                                            r"no in-file verifier line", _cardreg_argv),
        "check_external_cards": (_ext_good, _ext_bad,
                                 r"\[NO-(?:GOAL-MAPPING|DO-NOT-TRUST)\]",
                                 _ext_argv),
    }


# The declared covered set; `_build_checks` must agree with it and `main` must
# find no live guard outside it. The driver itself is not one of the guards.
_COVERED_NAMES = frozenset({
    "check_invalidated_pointers",
    "check_results_value_pointers",
    "check_frozen_id_provenance",
    "check_query_fork",
    "check_gen38_anchor",
    "check_membukkit_parity",
    "check_protected_findings",
    "check_longmemeval_qualifiers",
    "check_agents_known_failures_consistency",
    "check_identifier_lifecycle",
    "check_ledger_counts",
    "check_required_metrics",
    "check_rd_thread_labels",
    "check_map_hashes",
    "check_cross_copy_drift",
    "check_orphan_evidence",
    "check_record_text_identity",
    "check_invocation_corpus_reachability",
    "check_experiment_class_schema",
    "check_card_register_consistency",
    "check_external_cards",
})
_DRIVER_STEM = "check_checker_exit_contracts"


def uncovered(scripts_dir: Path, covered=_COVERED_NAMES) -> list[str]:
    """Live `check_*.py` stems (minus this driver) absent from the covered set."""
    live = {p.stem for p in scripts_dir.glob("check_*.py")}
    return sorted(live - set(covered) - {_DRIVER_STEM})


def orphan_controls(scripts_dir: Path, covered=_COVERED_NAMES) -> list[str]:
    """Declared controls whose live `check_*.py` file has gone missing."""
    live = {p.stem for p in scripts_dir.glob("check_*.py")}
    return sorted(set(covered) - live)


def _run(script: Path, argv: list[str]) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(script), *argv],
                       capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stdout + p.stderr)


_TRACEBACK = "Traceback (most recent call last)"


def evaluate(script: Path, build_good, build_bad,
             dirty_marker: str | None = None,
             argv_good=None, argv_bad=None) -> list[str]:
    argv_good = argv_good or (lambda root: [str(root)])
    argv_bad = argv_bad or argv_good
    out: list[str] = []
    for label, builder, want, argv in (("clean", build_good, 0, argv_good),
                                       ("dirty", build_bad, 1, argv_bad)):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            builder(root)
            rc, text = _run(script, argv(root))
            last = (text.strip().splitlines() or [""])[-1]
            if rc != want:
                out.append(f"{script.name} [{label} control]: exit {rc}, expected "
                           f"{want} :: {last[:100]}")
                continue
            if _TRACEBACK in text:
                out.append(f"{script.name} [{label} control]: exit {want} but output "
                           f"is a crash traceback, not a verdict :: {last[:100]}")
                continue
            if label == "dirty" and dirty_marker is not None \
                    and re.search(dirty_marker, text) is None:
                out.append(f"{script.name} [dirty control]: exit 1 without the "
                           f"finding marker /{dirty_marker}/ :: {last[:100]}")
            if label == "clean" and dirty_marker is not None \
                    and re.search(dirty_marker, text) is not None:
                out.append(f"{script.name} [clean control]: exit 0 but printed the "
                           f"finding marker /{dirty_marker}/ :: {last[:100]}")
    return out


def _self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        good = root / "good.py"
        good.write_text("import sys\nfrom pathlib import Path\n"
                        "p = Path(sys.argv[1])\n"
                        "if not (p/'GOOD').exists():\n"
                        "    print('FINDING: no GOOD marker'); raise SystemExit(1)\n"
                        "raise SystemExit(0)\n")
        prose = root / "prose.py"
        prose.write_text("print('FAIL: found something')\nraise SystemExit(0)\n")
        crashy = root / "crashy.py"
        crashy.write_text("import sys\nfrom pathlib import Path\n"
                          "if not (Path(sys.argv[1])/'GOOD').exists():\n"
                          "    raise RuntimeError('boom')\n"
                          "raise SystemExit(0)\n")
        silent = root / "silent.py"
        silent.write_text("import sys\nfrom pathlib import Path\n"
                          "raise SystemExit(0 if (Path(sys.argv[1])/'GOOD').exists() else 1)\n")
        wolfer = root / "wolfer.py"
        wolfer.write_text("import sys\nfrom pathlib import Path\n"
                          "print('FINDING: cries wolf on every run')\n"
                          "raise SystemExit(0 if (Path(sys.argv[1])/'GOOD').exists() else 1)\n")

        def b_good(d): (d / "GOOD").write_text("x")
        def b_bad(d): (d / "OTHER").write_text("x")

        assert evaluate(good, b_good, b_bad, r"FINDING:") == [], \
            "correct contract false-alarmed"
        prose_v = evaluate(prose, b_good, b_bad, r"FINDING:")
        assert any("dirty control" in v and "exit 0" in v for v in prose_v), prose_v
        crash_v = evaluate(crashy, b_good, b_bad, r"FINDING:")
        assert any("crash traceback" in v for v in crash_v), crash_v
        silent_v = evaluate(silent, b_good, b_bad, r"FINDING:")
        assert any("without the finding marker" in v for v in silent_v), silent_v
        wolf_v = evaluate(wolfer, b_good, b_bad, r"FINDING:")
        assert any("clean control" in v and "printed the" in v for v in wolf_v), wolf_v

        # Covered-set completeness: a live guard outside the declared set is
        # named, and the real CLI rejects the same input before building fixtures.
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "check_a.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
            (d / "check_new.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
            assert uncovered(d, {"check_a"}) == ["check_new"], uncovered(d, {"check_a"})
            assert uncovered(d, {"check_a", "check_new"}) == [], \
                "declared covered set falsely flagged"
            assert orphan_controls(d, {"check_a", "check_gone"}) == ["check_gone"], \
                "declared control with no live file not flagged"
            (d / "check_checker_exit_contracts.py").write_text(
                Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(d / "check_checker_exit_contracts.py")],
                capture_output=True, text=True, timeout=120)
            assert r.returncode == 1 and "NO CONTROL" in r.stdout, \
                (r.returncode, r.stdout[-200:])
    print("self-test: PASS (correct contract clean; prose-only/exit-0 checker, "
          "dirty-root crash, finding-less exit-1 checker, clean-root "
          "marker-crier, and covered-set gaps in both directions "
          "all caught)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return _self_test()

    # The declared set must match the filesystem in both directions (Alice
    # second-seat + Assay's validated reverse check): a live guard outside it is
    # never run, and a declared control whose file is gone would crash the load.
    # Checked before fixture construction so a stray/missing guard fails loud
    # even in a staging copy.
    missing = uncovered(SCRIPTS)
    gone = orphan_controls(SCRIPTS)
    if missing or gone:
        for name in missing:
            print(f"  {name}: NO CONTROL (live guard not in the covered set)")
        for name in gone:
            print(f"  {name}: CONTROL WITHOUT A LIVE GUARD")
        print(f"=== checker exit contracts: INCOMPLETE -- "
              f"{len(missing)} live guard(s) uncovered, {len(gone)} control(s) "
              f"without a live guard ({len(_COVERED_NAMES)} declared covered)")
        return 1
    checks = _build_checks()
    drift = sorted(set(checks) ^ set(_COVERED_NAMES))
    if drift:
        print(f"=== checker exit contracts: INTERNAL ERROR -- _build_checks keys "
              f"!= declared covered set: {drift}")
        return 1
    total, failed = 0, 0
    for name, entry in checks.items():
        build_good, build_bad, marker = entry[:3]
        argv_good = entry[3] if len(entry) > 3 else None
        argv_bad = entry[4] if len(entry) > 4 else None
        total += 1
        violations = evaluate(SCRIPTS / f"{name}.py", build_good, build_bad, marker,
                              argv_good=argv_good, argv_bad=argv_bad)
        status = "OK" if not violations else "BROKEN"
        print(f"  {name}: {status}")
        for v in violations:
            print(f"      {v}")
        failed += bool(violations)
    print(f"=== checker exit contracts: {total - failed}/{total} hold")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
