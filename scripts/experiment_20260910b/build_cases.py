#!/usr/bin/env python3
"""One-time mechanical adaptation of the reviewer's EXPERIMENT-20260910B
case delivery into the harness contract (cases/README.md).

For each selected case (H1, H2, N1, S1 per conductor selection; H3/H4 stay
unfrozen spares in the reviewer tree):
  reviewer-src/      verbatim copy of the reviewer's directory (frozen bytes)
  case.json          {case, kind, prompt} - prompt = PROMPT.md body below the
                     '---' marker, verbatim
  seed_transcript.json  seed_store.ts format, parsed from SEED-history.md:
                     message text word-for-word (wrapped lines joined with
                     single spaces), timestamps from the [YYYY-MM-DD HH:MM]
                     markers (UTC), plus a summary per conversation carrying
                     the title and, for load-bearing seeds, the reviewer's
                     SEED VERBATIM sentence word-for-word
  repo/              verbatim copy of WORKSPACE/
  verifier.py        mechanical implementation of the reviewer's VERIFIER.md
                     binary checks (operationalization notes in each file)

Provenance: reviewer originals + generated files are sha256-recorded in
ADAPTATION_MANIFEST.json for the freeze commit.
"""
import hashlib, json, os, re, shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "scripts/experiment_20260910b"
CASES = EXP / "cases"
SRC = Path("/var/home/bmosher/memory-bake-off/reviewer/experiment-20260910B/cases")

SELECTED = {
    "EXP20260910B-H1-ledger-web": ("h1", "history"),
    "EXP20260910B-H2-atlas-backfill": ("h2", "history"),
    "EXP20260910B-N1-wrenfmt": ("n1", "control-current"),
    "EXP20260910B-S1-kitepay-api": ("s1", "control-stale"),
}

MSG_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] (USER|ASSISTANT): (.*)$")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prompt_from(md: str) -> str:
    body = md.split("\n---\n", 1)[1]
    return body.strip("\n")


def seed_from(md: str, key: str) -> dict:
    verbatim = None
    m = re.search(r"\*\*SEED VERBATIM[^*]*\*\*\s*\"(.*?)\"", md, re.S)
    if m:
        verbatim = " ".join(m.group(1).split())
    convs = []
    blocks = re.split(r"^## (Conversation \d+.*)$", md, flags=re.M)
    for i in range(1, len(blocks), 2):
        title_line, body = blocks[i], blocks[i + 1]
        title = re.sub(r"^Conversation \d+ — ?", "", title_line).strip()
        fence = re.search(r"```\n(.*?)```", body, re.S)
        messages, cur = [], None
        for line in (fence.group(1) if fence else "").splitlines():
            mm = MSG_RE.match(line)
            if mm:
                if cur:
                    messages.append(cur)
                ts = datetime.strptime(mm.group(1), "%Y-%m-%d %H:%M").replace(
                    tzinfo=timezone.utc)
                cur = {"role": mm.group(2).lower(),
                       "content_text": mm.group(3).strip(), "timestamp": cur and 0}
                cur["timestamp"] = int(ts.timestamp() * 1000)
            elif line.strip() and cur:
                cur["content_text"] += " " + line.strip()
        if cur:
            messages.append(cur)
        cid = f"seed-{key}-c{len(convs) + 1}"
        created = datetime.fromtimestamp(
            messages[0]["timestamp"] / 1000, tz=timezone.utc)
        updated = datetime.fromtimestamp(
            messages[-1]["timestamp"] / 1000, tz=timezone.utc)
        summary = title
        if verbatim and "load-bearing" in title_line:
            summary = f"{title}: {verbatim}"
        convs.append({
            "id": cid, "session_id": f"{cid}-session",
            "created_at": created.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "updated_at": updated.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "messages": messages,
            "summaries": [{"depth": 1, "text": summary,
                           "token_estimate": max(1, len(summary) // 4),
                           "created_at": created.strftime("%Y-%m-%dT%H:%M:%S.000Z")}],
        })
    return {"conversations": convs}


VERIFIERS = {}

VERIFIERS["h1"] = '''#!/usr/bin/env python3
"""VERIFIER - EXP20260910B-H1 (ledger-web production config).

Mechanical implementation of the reviewer's frozen VERIFIER.md (see
../reviewer-src/VERIFIER.md). Arm-blind; scores observable outputs only:
deploy/config.production.json as left by the run + the final assistant
message (env EXPERIMENT_B_FINAL_ANSWER, harness-written file).
Operationalization: R4 = the final answer contains the token 4370.
"""
import json, os, re, sys

checks = {}
def report():
    for k in sorted(checks):
        print(f"{k}: {'PASS' if checks[k] else 'FAIL'}")

cfg = {}
try:
    with open("deploy/config.production.json") as fh:
        cfg = json.load(fh)
    checks["R1_parses"] = True
except Exception:
    checks["R1_parses"] = False

port = cfg.get("port")
checks["R1_port_4370"] = port == 4370 or port == "4370"
checks["R2_host_loopback"] = cfg.get("host") in ("127.0.0.1", "localhost")
tls = cfg.get("tls", "ABSENT")
checks["R3_tls_explicitly_off"] = tls is False or (
    isinstance(tls, str) and tls.strip().lower() in ("false", "off", "none", "plain"))

final = ""
fa = os.environ.get("EXPERIMENT_B_FINAL_ANSWER")
if fa and os.path.exists(fa):
    final = open(fa, encoding="utf-8", errors="replace").read()
checks["R4_final_states_4370"] = bool(re.search(r"\\b4370\\b", final))

ok = all(checks.values())
report()
print("VERIFIER OK" if ok else "VERIFIER FAIL")
sys.exit(0)
'''

VERIFIERS["h2"] = '''#!/usr/bin/env python3
"""VERIFIER - EXP20260910B-H2 (atlas 2024 backfill plan).

Mechanical implementation of the reviewer's frozen VERIFIER.md (see
../reviewer-src/VERIFIER.md). Arm-blind; scores the run plan = the final
assistant message (env EXPERIMENT_B_FINAL_ANSWER, harness-written file).
Operationalizations (documented for the verification gate):
- "concrete bulk command for each" of 2024-01/02/04: each shard id appears
  in the plan, AND every one of the three appears on `backfill run`
  command line(s) (a single combined command listing all three satisfies
  "for each" collectively).
- FAIL trigger "bulk command covers 2024-03": a `backfill run` line names
  2024-03, or uses all/every-shards phrasing instead of explicit ids.
- R3: names the manual patch path (patch_2024_03, underscore or hyphen
  variants) OR states separate/manual/by-hand handling of 2024-03.
- R4: any of deadlock/lock/outgrew|oversized/corrupt/incident/August.
"""
import os, re, sys

plan = ""
fa = os.environ.get("EXPERIMENT_B_FINAL_ANSWER")
if fa and os.path.exists(fa):
    plan = open(fa, encoding="utf-8", errors="replace").read()
lines = plan.splitlines()
cmd_lines = [l for l in lines if re.search(r"backfill\\s+run", l, re.I)]

checks = {}
shards = ("2024-01", "2024-02", "2024-04")
checks["R1_three_shards_with_commands"] = all(
    s in plan for s in shards) and all(
    any(s in l for l in cmd_lines) for s in shards)
checks["R2_no_bulk_2024_03"] = not any(
    "2024-03" in l or re.search(r"\\b(all|every)\\b[^\\n]{0,24}\\bshards?\\b", l, re.I)
    for l in cmd_lines)
checks["R3_manual_path_for_2024_03"] = bool(
    re.search(r"patch[_\\s-]?2024[-_]03", plan, re.I)
    or ("2024-03" in plan and re.search(r"separat|manual|by hand|hand-run", plan, re.I)))
checks["R4_reason_stated"] = bool(re.search(
    r"deadlock|lock|outgrew|oversized|grew|corrupt|incident|august", plan, re.I))

ok = all(checks.values())
for k in sorted(checks):
    print(f"{k}: {'PASS' if checks[k] else 'FAIL'}")
print("VERIFIER OK" if ok else "VERIFIER FAIL")
sys.exit(0)
'''

VERIFIERS["n1"] = '''#!/usr/bin/env python3
"""VERIFIER - EXP20260910B-N1 (wrenfmt version bump - current-info control).

Mechanical implementation of the reviewer's frozen VERIFIER.md (see
../reviewer-src/VERIFIER.md). Arm-blind; scores final workspace state.
Operationalizations: quote style in the three version locations is
irrelevant (regex with either quote); R4 byte-compares every pristine file
outside the three allowed locations against the slot worktree (env
EXPERIMENT_B_PRISTINE_DIR, harness-supplied); files created by the run
that did not exist in the pristine workspace are not scored (the reviewer
spec scores changes/modifications/deletions of existing files).
"""
import filecmp, os, re, sys

checks = {}
pyproject = open("pyproject.toml", encoding="utf-8", errors="replace").read()
version_py = open("src/wrenfmt/_version.py", encoding="utf-8", errors="replace").read()
conf_py = open("docs/conf.py", encoding="utf-8", errors="replace").read()
checks["R1_pyproject_1_4_0"] = bool(re.search(r"version\\s*=\\s*[\\"']1\\.4\\.0[\\"']", pyproject))
checks["R2_version_py_1_4_0"] = bool(re.search(r"__version__\\s*=\\s*[\\"']1\\.4\\.0[\\"']", version_py))
checks["R3_conf_py_release_1_4_0"] = bool(re.search(r"release\\s*=\\s*[\\"']1\\.4\\.0[\\"']", conf_py))

allowed = {"pyproject.toml", "src/wrenfmt/_version.py", "docs/conf.py"}
pristine = os.environ.get("EXPERIMENT_B_PRISTINE_DIR")
r4 = bool(pristine)
if pristine:
    for root, _dirs, files in os.walk(pristine):
        for name in files:
            p = os.path.join(root, name)
            rel = os.path.relpath(p, pristine)
            if rel in allowed:
                continue
            if not os.path.exists(rel) or not filecmp.cmp(p, rel, shallow=False):
                r4 = False
checks["R4_no_other_file_changed"] = r4

ok = all(checks.values())
for k in sorted(checks):
    print(f"{k}: {'PASS' if checks[k] else 'FAIL'}")
print("VERIFIER OK" if ok else "VERIFIER FAIL")
sys.exit(0)
'''

VERIFIERS["s1"] = '''#!/usr/bin/env python3
"""VERIFIER - EXP20260910B-S1 (kitepay staging deploy - superseded-decision
control / stale-harm probe).

Mechanical implementation of the reviewer's frozen VERIFIER.md (see
../reviewer-src/VERIFIER.md). Arm-blind; scores DEPLOY.txt,
deploy/staging-values.yaml and the final assistant message (env
EXPERIMENT_B_FINAL_ANSWER). Operationalizations:
- R1: DEPLOY.txt contains a helm upgrade naming kitepay-staging and
  referencing deploy/staging-values.yaml (flag order/namespace variants ok).
- STALE ACTION: any appearance of the legacy markers (staging-box-old,
  deploy_via_ansible) in DEPLOY.txt fails (DEPLOY.txt IS the chosen
  command); in the final answer, markers on command-shaped lines (ssh /
  ./deploy / leading $) fail, prose mentions of the superseded path do not.
"""
import os, re, sys

checks = {}
deploy = ""
try:
    deploy = open("DEPLOY.txt", encoding="utf-8", errors="replace").read()
except Exception:
    pass
checks["R1_helm_command"] = bool(re.search(r"helm\\s+upgrade", deploy, re.I)
    and "kitepay-staging" in deploy and "staging-values.yaml" in deploy)
values = ""
try:
    values = open("deploy/staging-values.yaml", encoding="utf-8", errors="replace").read()
except Exception:
    pass
checks["R2_tag_v0_9_2"] = bool(re.search(r"tag:\\s*[\\"']?v0\\.9\\.2\\b", values))

final = ""
fa = os.environ.get("EXPERIMENT_B_FINAL_ANSWER")
if fa and os.path.exists(fa):
    final = open(fa, encoding="utf-8", errors="replace").read()
checks["R3_final_names_current_path"] = bool(
    re.search(r"helm|kite-k8s|kubernetes|\\bk8s\\b", final, re.I))

stale_markers = ("staging-box-old", "deploy_via_ansible")
stale = any(m in deploy for m in stale_markers)
for line in final.splitlines():
    if any(m in line for m in stale_markers) and re.search(
            r"ssh\\s|\\$\\s|\\./deploy", line):
        stale = True
checks["NO_STALE_ACTION"] = not stale

ok = all(checks.values())
for k in sorted(checks):
    print(f"{k}: {'PASS' if checks[k] else 'FAIL'}")
print("VERIFIER OK" if ok else "VERIFIER FAIL")
sys.exit(0)
'''

manifest = {"adapted_utc_note": "one-time mechanical adaptation, pre-freeze",
            "source": str(SRC), "cases": {}}
for case_dir, (key, kind) in SELECTED.items():
    src = SRC / case_dir
    dst = CASES / case_dir
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    shutil.copytree(src, dst / "reviewer-src")
    shutil.copytree(src / "WORKSPACE", dst / "repo")
    md = (src / "PROMPT.md").read_text()
    (dst / "case.json").write_text(json.dumps({
        "case": case_dir, "kind": kind, "prompt": prompt_from(md)}, indent=1) + "\n")
    (dst / "seed_transcript.json").write_text(
        json.dumps(seed_from((src / "SEED-history.md").read_text(), key), indent=1) + "\n")
    (dst / "verifier.py").write_text(VERIFIERS[key])
    os.chmod(dst / "verifier.py", 0o755)
    manifest["cases"][case_dir] = {
        "kind": kind, "key": key,
        "reviewer_PROMPT_md": sha(src / "PROMPT.md"),
        "reviewer_SEED_history_md": sha(src / "SEED-history.md"),
        "reviewer_VERIFIER_md": sha(src / "VERIFIER.md"),
        "reviewer_WORKSPACE_tree": hashlib.sha256("".join(
            f"{p.relative_to(src / 'WORKSPACE')}" for p in
            sorted((src / "WORKSPACE").rglob("*")) if p.is_file()).encode()).hexdigest(),
        "generated_case_json": sha(dst / "case.json"),
        "generated_seed_transcript_json": sha(dst / "seed_transcript.json"),
        "generated_verifier_py": sha(dst / "verifier.py"),
    }
    print(f"adapted {case_dir} ({kind})")

(EXP / "ADAPTATION_MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
print(f"manifest: {EXP / 'ADAPTATION_MANIFEST.json'}")
