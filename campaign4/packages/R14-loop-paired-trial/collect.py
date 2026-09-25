#!/usr/bin/env python3
"""R14 evidence copy, run by the worker at the end of each phase:
  python /home/bmosher/memory-bake-off/campaign4/packages/R14-loop-paired-trial/collect.py ARM PHASE
Arms live outside artifacts_dir, so claims name these copies instead. Writes
packages/R14-loop-paired-trial/evidence/<ARM>-p<PHASE>/:
  test.out            the frozen check's output and rc, run now
  notes-index.json    notes/ file names, sizes and sha256 (content is not copied)
  manifest.txt        manifest.py compare vs the frozen arm manifest
  igw.diff            (phase 2) unified diff of igw/ vs the read-only broken snapshot"""
import hashlib, json, os, subprocess, sys
ARM, PHASE = sys.argv[1], sys.argv[2]
PKG = "/home/bmosher/memory-bake-off/campaign4/packages/R14-loop-paired-trial"
ARM_DIR = f"/var/home/bmosher/r14-arms/{ARM}"
EV = f"{PKG}/evidence/{ARM}-p{PHASE}"
os.makedirs(EV, exist_ok=True)
r = subprocess.run("python -m pytest -q -p no:cacheprovider tests/test_drain_on_disconnect.py", shell=True, cwd=ARM_DIR, capture_output=True, text=True)
open(f"{EV}/test.out", "w").write(r.stdout + r.stderr + f"\nrc={r.returncode}\n")
nd = f"{ARM_DIR}/notes"
idx = {f: {"bytes": os.path.getsize(f"{nd}/{f}"), "sha256": hashlib.sha256(open(f"{nd}/{f}", "rb").read()).hexdigest()}
       for f in sorted(os.listdir(nd)) if os.path.isfile(f"{nd}/{f}")} if os.path.isdir(nd) else {}
json.dump(idx, open(f"{EV}/notes-index.json", "w"), indent=1)
m = subprocess.run([sys.executable, f"{PKG}/manifest.py", "compare", f"{PKG}/arm-manifest.json", ARM_DIR, "--frozen", "igw,tests" if PHASE == "1" else "tests"], capture_output=True, text=True)
open(f"{EV}/manifest.txt", "w").write(m.stdout + f"exit={m.returncode}\n")
if PHASE == "2":
    d = subprocess.run(["diff", "-ru", "-x", "__pycache__", "-x", "*.pyc", "/var/home/bmosher/r14-arms/broken/igw", f"{ARM_DIR}/igw"], capture_output=True, text=True)
    open(f"{EV}/igw.diff", "w").write(d.stdout)
print(EV)
