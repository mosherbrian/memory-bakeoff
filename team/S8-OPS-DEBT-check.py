#!/usr/bin/env python3
"""Gate for QUEUE row S8-6 (restart-actor attribution and the headline-aging
residual).

plumb-fable, row S8-6G, 2026-09-17. Written FROM ROW S8-6's TEXT ALONE, while
`team/S8-OPS-DEBT.md` did not exist. Read for this gate: the board row, the
prior it names (team/RETRO-4-SUMMARY.md, carried-forward entries) and the
journal itself for the two recorded restarts. The interface below is declared
by the gate, not fitted to a document; every finding names what it wants.

It lives at `team/S8-OPS-DEBT-check.py` and checks `team/S8-OPS-DEBT.md`, the paths
the board declares (first written under the S7- name the board carried that
afternoon; moved when the board was corrected).

This gate is an INSTRUMENT where it can be. Every journal line the artifact
quotes as evidence is looked up in the journal, in the two minutes round the
restart it is quoted for. An actor is accepted only when the evidence names it.
A file the disposition leans on must exist.

Declared interface: one markdown file with these lines
  Driver unit: <name>.service       the fleet's only driver
  Prior: ... RETRO-4-SUMMARY.md     the carried-forward entries
  Advances: neither ...             as the row says
  one block per restart, at least the two the row records (16:39:59, 16:52:31):
      Restart: YYYY-MM-DD HH:MM:SS
      Actor: human:<user> | service:<unit> | timer:<unit> | script:<path>
             | unattributed
      Evidence:
      > <journal line, verbatim>      (one or more; a stop AND a start of the
      > <journal line, verbatim>       driver among them)
      Control added: <path>           only for unattributed: an existing file
                                      that names the driver and will attribute
                                      the next restart
  Disposition (headline-aging residual): fixed - <mechanism, naming an
      existing file>   |   accepted-with-mitigation - mitigation: <...>;
      residual: <...>

What the row turns on (marker in brackets)
  (a) Journal EVIDENCE, not assertion. Each quoted line is in the journal
      within 120 s of the restart it is quoted for [EVIDENCE-NOT-IN-JOURNAL];
      the block shows both a stop and a start of the driver
      [EVIDENCE-INCOMPLETE]; both recorded restarts are covered
      [RESTART-MISSING]; the journal is reachable [JOURNAL-UNAVAILABLE].
  (b) WHO OR WHAT. The actor is one of the five kinds [ACTOR-INVALID] and the
      evidence names it [ACTOR-NOT-IN-EVIDENCE]; `unattributed` is allowed
      only with a control that closes the gap next time [CONTROL-NOT-FOUND].
  (c) ONE-LINE DISPOSITION of the residual, in the row's two words
      [DISPOSITION-MISSING] [DISPOSITION-DUPLICATED] [DISPOSITION-INVALID];
      `fixed` names an existing file, `accepted-with-mitigation` names both the
      mitigation and the residual [DISPOSITION-UNSUPPORTED].
  (d) Housekeeping: driver named [DRIVER-UNNAMED]; prior cited
      [PRIOR-NOT-CITED]; advances-neither stated [ADVANCES-UNSTATED].
  other  [MISSING-FILE] [EMPTY]

Limits, stated on purpose: the journal proves a line was logged, not that the
named actor CAUSED the stop; the gate cannot tell a good mitigation from a
weak one, or that the `fixed` mechanism fixes anything. Those stay with the
named verifier. Journal retention is finite: an export can be given with
--journal once the live journal no longer covers 2026-09-16.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S8-6 gate findings: N`, never a traceback.

Usage:
  python3 S8-OPS-DEBT-check.py [OPS-DEBT.md] [--journal FILE] [--repo DIR]
  python3 S8-OPS-DEBT-check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "S8-OPS-DEBT.md"
REPO = HERE.parent
PRIOR = "RETRO-4-SUMMARY.md"
RECORDED = ("16:39:59", "16:52:31")  # the restarts the row records
KINDS = ("human", "service", "timer", "script", "unattributed")
WINDOW = timedelta(seconds=120)
STOP = re.compile(r"\b(Stopping|Stopped|Deactivated)\b")
START = re.compile(r"\b(Starting|Started)\b")
ISO = re.compile(r"(\d{4}-\d\d-\d\d)[T ](\d\d:\d\d:\d\d)")
MONTH = re.compile(r"\b([A-Z][a-z]{2}) +(\d{1,2}) (\d\d:\d\d:\d\d)")
DISPO = re.compile(r"^\**Disposition\**[^:\n]*:\**\s*(.+?)\s*$", re.I | re.M)


def _line(text: str, key: str) -> str | None:
    m = re.search(rf"^\**{key}\**:\**\s*(.+?)\s*$", text, re.I | re.M)
    return m.group(1) if m else None


def _msg(line: str) -> str:
    """The message part of a journal line: after `unit[pid]: `, or the
    whole line when there is no such prefix; whitespace collapsed."""
    m = re.search(r"\]:\s*(.*)$", line)
    return re.sub(r"\s+", " ", (m.group(1) if m else line)).strip()


def _when(line: str, year: int) -> datetime | None:
    m = ISO.search(line)
    if m:
        return datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}")
    m = MONTH.search(line)
    if m:
        try:
            return datetime.strptime(f"{year} {m.group(1)} {m.group(2)} "
                                     f"{m.group(3)}", "%Y %b %d %H:%M:%S")
        except ValueError:
            return None
    return None


def _journal(at: datetime, export: Path | None) -> list[str] | None:
    """Journal lines within WINDOW of `at`, or None when unreachable."""
    if export is not None:
        try:
            raw = export.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
        lines = raw.splitlines()
    else:
        lines = []
        for scope in ((), ("--user",)):
            try:
                p = subprocess.run(
                    ["journalctl", *scope, "--no-pager", "-o", "short-iso",
                     "--since", (at - WINDOW).strftime("%Y-%m-%d %H:%M:%S"),
                     "--until", (at + WINDOW).strftime("%Y-%m-%d %H:%M:%S")],
                    capture_output=True, text=True, timeout=60)
            except (OSError, subprocess.SubprocessError):
                return None
            if p.returncode != 0:
                return None
            lines += p.stdout.splitlines()
    return [l for l in lines
            if (t := _when(l, at.year)) is not None and abs(t - at) <= WINDOW]


def _blocks(text: str) -> list[str]:
    parts = re.split(r"(?=^\**Restart\**:)", text, flags=re.M)
    return [p for p in parts if re.match(r"^\**Restart\**:", p)]


def _evidence(block: str) -> list[str]:
    m = re.search(r"^\**Evidence\**:\**\s*\n((?:>.*\n?)+)", block, re.I | re.M)
    return [l.lstrip("> ").rstrip() for l in m.group(1).splitlines()
            if l.strip("> ").strip()] if m else []


def _exists(ref: str, repo: Path) -> bool:
    for tok in re.findall(r"[\w./~-]+/[\w./-]+|[\w-]+\.\w+", ref):
        p = Path(tok).expanduser()
        if (p if p.is_absolute() else repo / p).is_file():
            return True
    return False


def check(path: Path, export: Path | None, repo: Path) -> tuple[list, str]:
    f: list[tuple[str, str]] = []
    if not path.is_file():
        return [("MISSING-FILE", str(path))], ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text.strip()) < 200:
        return [("EMPTY", f"{path.name} holds {len(text.strip())} characters")], ""

    # (d) housekeeping
    driver = _line(text, "Driver unit") or ""
    driver = driver.strip("`* ")
    if not re.fullmatch(r"[\w.@-]+\.service", driver):
        f.append(("DRIVER-UNNAMED", "needs `Driver unit: <name>.service`, the "
                  "fleet's only driver"))
        driver = ""
    if PRIOR not in (_line(text, "Prior") or ""):
        f.append(("PRIOR-NOT-CITED", f"needs `Prior: ...` naming {PRIOR}, whose "
                  f"carried-forward entries these are"))
    if not re.search(r"neither", _line(text, "Advances") or "", re.I):
        f.append(("ADVANCES-UNSTATED", "needs `Advances: neither a frozen goal "
                  "nor a roadmap item`, as the row says"))

    # (a) (b) restarts
    blocks = _blocks(text)
    covered = set()
    for b in blocks:
        head = _line(b, "Restart") or ""
        m = ISO.search(head)
        if not m:
            f.append(("RESTART-MISSING", f"`Restart: {head[:30]}` needs a full "
                      f"YYYY-MM-DD HH:MM:SS"))
            continue
        at = datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}")
        label = at.strftime("%H:%M:%S")
        covered.add(label)
        window = _journal(at, export)
        if window is None:
            f.append(("JOURNAL-UNAVAILABLE", f"{label}: the journal could not "
                      f"be read for {at}; pass --journal FILE with an export"))
            continue
        have = {_msg(l) for l in window}
        ev = _evidence(b)
        absent = [l for l in ev if _msg(l) not in have
                  or (t := _when(l, at.year)) is None or abs(t - at) > WINDOW]
        if not ev or absent:
            f.append(("EVIDENCE-NOT-IN-JOURNAL", f"{label}: "
                      + (f"{len(absent)} quoted line(s) not in the journal "
                         f"within {int(WINDOW.total_seconds())} s of {at}: "
                         f"{absent[0][:70]!r}" if absent else
                         "no `Evidence:` block of quoted `> ` journal lines")))
        mine = [l for l in ev if driver and driver in l]
        if not (any(STOP.search(l) for l in mine)
                and any(START.search(l) for l in mine)):
            f.append(("EVIDENCE-INCOMPLETE", f"{label}: the evidence must show "
                      f"both a stop and a start of {driver or 'the driver'}"))
        actor = (_line(b, "Actor") or "").strip("`* ")
        am = re.fullmatch(r"(\w+):\s*(\S.*)", actor)
        kind = am.group(1).lower() if am else actor.lower()
        if kind not in KINDS or (kind != "unattributed" and not am):
            f.append(("ACTOR-INVALID", f"{label}: needs `Actor: "
                      f"{' | '.join(k + ':<id>' for k in KINDS[:-1])} | "
                      f"unattributed`"))
        elif kind == "unattributed":
            ctl = _line(b, "Control added") or ""
            ok = _exists(ctl, repo)
            if ok:
                tok = next(t for t in re.findall(r"[\w./~-]+", ctl)
                           if (Path(t).expanduser() if Path(t).is_absolute()
                               else repo / t).is_file())
                p = Path(tok).expanduser()
                ok = driver in (p if p.is_absolute() else repo / p).read_text(
                    encoding="utf-8", errors="replace")
            if not ok:
                f.append(("CONTROL-NOT-FOUND", f"{label}: unattributed is "
                          f"allowed only with `Control added: <existing file "
                          f"that names {driver or 'the driver'}>`, so the next "
                          f"restart is attributable"))
        else:
            ident = Path(am.group(2).strip()).name.split(".")[0]
            if len(ident) < 3 or not any(ident in l for l in ev):
                f.append(("ACTOR-NOT-IN-EVIDENCE", f"{label}: actor {actor!r} "
                          f"is not named in any quoted evidence line"))
    missing = [t for t in RECORDED if t not in covered]
    if missing:
        f.append(("RESTART-MISSING", f"no `Restart:` block for the recorded "
                  f"restart(s) at {', '.join(missing)}"))

    # (c) the disposition
    dispos = DISPO.findall(text)
    if not dispos:
        f.append(("DISPOSITION-MISSING", "needs one line `Disposition "
                  "(headline-aging residual): fixed - ... | "
                  "accepted-with-mitigation - mitigation: ...; residual: ...`"))
    else:
        if len(dispos) > 1:
            f.append(("DISPOSITION-DUPLICATED", f"{len(dispos)} disposition "
                      f"lines; the row asks for one"))
        d = dispos[0]
        word = re.match(r"\**(fixed|accepted-with-mitigation)\b", d, re.I)
        if not word:
            f.append(("DISPOSITION-INVALID", f"disposition {d[:40]!r} must "
                      f"begin with `fixed` or `accepted-with-mitigation`"))
        elif word.group(1).lower() == "fixed":
            if not _exists(d, repo):
                f.append(("DISPOSITION-UNSUPPORTED", "`fixed` must name the "
                          "mechanism as an existing file"))
        else:
            mit = re.search(r"mitigation:\s*(.{20,}?)(;|$)", d, re.I)
            res = re.search(r"residual:\s*(.{20,})", d, re.I)
            if not (mit and res):
                f.append(("DISPOSITION-UNSUPPORTED", "`accepted-with-mitigation`"
                          " must carry `mitigation: <20+ chars>; residual: "
                          "<20+ chars>`"))
    return f, (f"{len(blocks)} restarts attributed with journal evidence; "
               f"disposition: {(dispos or ['-'])[0][:40]}")


def run(path: Path, export: Path | None, repo: Path) -> int:
    findings, summary = check(path, export, repo)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S8-6 gate findings: {len(findings)}")
        return 1
    print(f"S8-6 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_H = "strix systemd[1604]:"
_JOURNAL = f"""2026-09-16T16:39:40-07:00 strix poller-liveness[999]: STALE: last sweep 400s ago, restarting fleet-poller.service
2026-09-16T16:39:59-07:00 {_H} Stopping fleet-poller.service - Fleet poller...
2026-09-16T16:39:59-07:00 {_H} Stopped fleet-poller.service - Fleet poller.
2026-09-16T16:39:59-07:00 {_H} Started fleet-poller.service - Fleet poller.
2026-09-16T16:45:00-07:00 {_H} Started igw-poller.service - snapshot.
2026-09-16T16:52:20-07:00 strix sudo[4242]: bmosher : TTY=pts/3 ; COMMAND=/usr/bin/systemctl --user restart fleet-poller.service
2026-09-16T16:52:31-07:00 {_H} Stopping fleet-poller.service - Fleet poller...
2026-09-16T16:52:31-07:00 {_H} Stopped fleet-poller.service - Fleet poller.
2026-09-16T16:52:31-07:00 {_H} Started fleet-poller.service - Fleet poller.
"""
_J = _JOURNAL.splitlines()
_GOOD = f"""# S7 ops debt: restart-actor attribution and the headline-aging residual

Driver unit: fleet-poller.service
Prior: {PRIOR}, carried-forward entries (restart actor; headline aging)
Advances: neither a frozen goal nor a roadmap item

## Restarts

Restart: 2026-09-16 16:39:59
Actor: service:poller-liveness.service
Evidence:
> {_J[0]}
> {_J[1]}
> {_J[2]}
> {_J[3]}

Restart: 2026-09-16 16:52:31
Actor: human:bmosher
Evidence:
> {_J[5]}
> {_J[6]}
> {_J[8]}

## Headline-aging residual

Disposition (headline-aging residual): accepted-with-mitigation - mitigation: the message tells the reader to trust the row over the message; residual: a queued "row X is now done" can still age before it is read.
"""


def _swap(old: str, new: str):
    def m(t):
        assert old in t, old
        return t.replace(old, new, 1)
    return m


def _unattributed(t, control="tools/restart-attrib.sh"):
    return t.replace("Actor: human:bmosher\nEvidence:\n> " + _J[5] + "\n",
                     f"Actor: unattributed\nControl added: {control}\n"
                     f"Evidence:\n")


_FIXED = ("Disposition (headline-aging residual): fixed - the poller now "
          "re-reads the row at delivery, see tools/restart-attrib.sh")

# name -> (mutation of the good text, markers that must be EXACTLY raised)
_MUTANTS = {
    "one restart missing": (lambda t: t[:t.index("Restart: 2026-09-16 16:52")]
                            + t[t.index("## Headline"):], {"RESTART-MISSING"}),
    "restart time incomplete": (_swap("Restart: 2026-09-16 16:52:31",
                                      "Restart: around 16:52"),
                                {"RESTART-MISSING"}),
    "evidence invented": (_swap(_J[6], f"2026-09-16T16:52:31-07:00 {_H} "
                                "Stopping fleet-poller.service - by request..."),
                          {"EVIDENCE-NOT-IN-JOURNAL"}),
    "evidence from another time": (_swap(_J[1], _J[6]),
                                   {"EVIDENCE-NOT-IN-JOURNAL"}),
    "no evidence block": (_swap(f"Evidence:\n> {_J[5]}\n> {_J[6]}\n> {_J[8]}\n",
                                "Evidence: the journal shows it.\n"),
                          {"EVIDENCE-NOT-IN-JOURNAL", "EVIDENCE-INCOMPLETE",
                           "ACTOR-NOT-IN-EVIDENCE"}),
    "start without stop": (_swap(f"> {_J[1]}\n> {_J[2]}\n", ""),
                           {"EVIDENCE-INCOMPLETE"}),
    "actor kind invalid": (_swap("Actor: human:bmosher", "Actor: probably "
                                 "Brian"), {"ACTOR-INVALID"}),
    "actor not in evidence": (_swap("Actor: service:poller-liveness.service",
                                    "Actor: service:igw-watchdog.service"),
                              {"ACTOR-NOT-IN-EVIDENCE"}),
    "unattributed, no control": (lambda t: _unattributed(t).replace(
        "Control added: tools/restart-attrib.sh\n", ""), {"CONTROL-NOT-FOUND"}),
    "unattributed, control file absent": (lambda t: _unattributed(
        t, "tools/absent.sh"), {"CONTROL-NOT-FOUND"}),
    "unattributed, control names another unit": (lambda t: _unattributed(
        t, "tools/unrelated.sh"), {"CONTROL-NOT-FOUND"}),
    "disposition missing": (_swap("Disposition (headline-aging residual):",
                                  "Outcome:"), {"DISPOSITION-MISSING"}),
    "disposition duplicated": (lambda t: t + "\n" + _FIXED + "\n",
                               {"DISPOSITION-DUPLICATED"}),
    "disposition in other words": (_swap("accepted-with-mitigation - ",
                                         "mitigated - "),
                                   {"DISPOSITION-INVALID"}),
    "fixed without a mechanism file": (
        lambda t: t[:t.index("Disposition")] + _FIXED.replace(
            "tools/restart-attrib.sh", "the poller") + "\n",
        {"DISPOSITION-UNSUPPORTED"}),
    "mitigation without residual": (_swap("; residual: a queued \"row X is now "
                                          "done\" can still age before it is "
                                          "read.", "."),
                                    {"DISPOSITION-UNSUPPORTED"}),
    "driver unnamed": (_swap("Driver unit: fleet-poller.service",
                             "Driver unit: the poller"),
                       {"DRIVER-UNNAMED", "EVIDENCE-INCOMPLETE"}),
    "prior not cited": (_swap(f"Prior: {PRIOR},", "Prior: the retro,"),
                        {"PRIOR-NOT-CITED"}),
    "advances unstated": (_swap("Advances: neither a frozen goal nor a "
                                "roadmap item", "Advances: G3"),
                          {"ADVANCES-UNSTATED"}),
    "near-empty file": (lambda t: "# ops debt\n\nTBD\n", {"EMPTY"}),
}


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "journal.txt").write_text(_JOURNAL)
        (d / "tools").mkdir()
        (d / "tools" / "restart-attrib.sh").write_text(
            "#!/bin/sh\n# logs who restarts fleet-poller.service\n")
        (d / "tools" / "unrelated.sh").write_text("#!/bin/sh\necho hi\n")

        def case(name, text, want, journal="journal.txt"):
            p = d / f"{re.sub(r'[^a-z]+', '-', name)}.md"
            if text is not None:
                p.write_text(text)
            r = subprocess.run(
                [sys.executable, __file__, str(p), "--journal",
                 str(d / journal), "--repo", str(d)],
                capture_output=True, text=True, timeout=60)
            out = r.stdout + r.stderr
            got = set(marker.findall(out))
            ok = want(got) if callable(want) else got == want
            if "Traceback (most recent call last)" in out:
                bad.append(f"{name}: traceback")
            elif want is None and (r.returncode != 0 or got):
                bad.append(f"{name}: should be ACCEPTED, got exit "
                           f"{r.returncode} {sorted(got)}")
            elif want is not None and (r.returncode != 1 or not ok
                                       or "S8-6 gate findings: " not in out):
                bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                           f"{sorted(got)}")

        case("conforming", _GOOD, None)
        case("conforming, unattributed with a control", _unattributed(_GOOD),
             None)
        case("conforming, residual fixed", _GOOD[:_GOOD.index("Disposition")]
             + _FIXED + "\n", None)
        for name, (mutate, want) in _MUTANTS.items():
            case(name, mutate(_GOOD), want)
        case("file missing", None, {"MISSING-FILE"})
        case("journal unreachable", _GOOD, {"JOURNAL-UNAVAILABLE",
                                            "RESTART-MISSING"} - {"RESTART-MISSING"},
             journal="absent.txt")
        case("hostile bytes", "\x00\xff" * 200, lambda got: bool(got))

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (3 conforming files accepted; {len(_MUTANTS)} "
          f"single-defect mutants, a missing file, an unreachable journal and "
          f"hostile bytes each rejected by their own markers, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S8-6")
    ap.add_argument("path", nargs="?", default=str(DEFAULT))
    ap.add_argument("--journal", help="a journalctl -o short-iso export to "
                    "use instead of the live journal")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.path), Path(a.journal) if a.journal else None,
               Path(a.repo))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S8-6 gate findings: 1")
        raise SystemExit(1)
