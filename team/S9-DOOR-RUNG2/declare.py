#!/usr/bin/env python3
"""S10-1 rung-2 declaration writer (kiln-flash, 2026-09-18).

Freezes the rung-1 items (byte for byte, verified against the rung-1 pin),
generates the query-adjacent pressure load (ten families per item, seeded,
evidence-free by construction and asserted), writes pressure_chunks.jsonl
then declaration.json exactly ONCE, BEFORE any run exists. Re-running after
the run would break every row's hash binding and the gate would say so.

Rung 1's diagnosis was narrow: its ten chunk families shared no vocabulary
with any query, so no tool chunk ever reached a top-k. Rung 2's load keeps
rung 1's scale (>= 20,000 bytes/item) and shape (10 tool-output records,
~2 KB each, ingested after the base records) and changes the one declared
thing: every chunk now shares its item's query vocabulary, so the load has
to be weighed by top-k selection. Answer material is excluded by design:
the one port, pool, path, approver and limit that any item's evidence names
appear nowhere in the load, and the evidence-freeness assertion is
recomputed here per chunk before anything is written.
"""
import hashlib
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = HERE.parent
S8 = TEAM / "S8-DOOR"
FAMILIES_PER_ITEM = 10
CHUNK_MIN_CHARS = 2050            # per chunk; 10 chunks >= the declared load
RUNG1_DECLARED_LOAD = 20000

# the rung-2 gate's stopword set, copied so the adjacency pre-assertion here
# is the same mechanical rule the gate recomputes later
STOP = {"what", "which", "when", "where", "does", "that", "this", "with",
        "from", "have", "will", "should", "would", "there", "their", "about"}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def words(text: str) -> set:
    return set(re.findall(r"[a-z0-9][a-z0-9-]{3,}", text.lower())) - STOP


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rng_for(item_id: str, family: int) -> random.Random:
    seed = int(sha_bytes(f"door-rung2|{item_id}|{family}".encode())[:16], 16)
    return random.Random(seed)


def fill(lines: list) -> str:
    """rung 1's padding rule: repeat lines verbatim to the 2,050-char floor."""
    body = list(lines)
    i = 0
    while sum(len(x) + 1 for x in body) < CHUNK_MIN_CHARS:
        body.append(lines[i % len(lines)])
        i += 1
    return "\n".join(body)


def _ip(r) -> str:
    return "10.%d.%d.%d" % (r.randint(0, 9), r.randint(0, 40), r.randint(1, 250))


def _user(r) -> str:
    return r.choice(["amara", "viktor", "josie", "ren", "talia", "marcus"])


# ---- sel-001: what port does the staging service listen on for tenant 100?
# vocabulary: staging, service, port, listen, tenant. Ports 9443/9444/9445/
# 7443/8480, tenants t-2xx. No "8443", no "tenant 100".

def _s1_f0(r):  # staging service inventory
    return ['{"inventory": "staging fleet", "date": "2026-09-18", "entries": ['] + [
        ' {"tenant": "t-%d", "service": "staging-%s", "listen": "0.0.0.0:%d", "state": "%s"}' % (
            r.randint(200, 260), r.choice(["api", "web", "worker", "sync", "relay"]),
            r.choice([9443, 9444, 9445, 7443, 8480]), r.choice(["ok", "ok", "draining"]))
        for _ in range(r.randint(6, 9))] + [']}', '{"inventory": "end"}']


def _s1_f1(r):  # port allocation ledger
    return ["# staging port allocation ledger, rack c%d" % r.randint(1, 4)] + [
        "tenant t-%d  staging %-8s listen :%d  allocated 2026-08-%02d by %s" % (
            r.randint(200, 260), r.choice(["api", "web", "worker", "sync"]),
            r.choice([9443, 9444, 9445, 7443, 8480]), r.randint(1, 28), _user(r))
        for _ in range(8)]


def _s1_f2(r):  # staging service config dump
    return ["# /etc/staging/service.conf (validated 2026-09-17)"] + [
        "%s = %s" % (k, v) for k, v in [
            ("staging_service.listen", "0.0.0.0:%d" % r.choice([9443, 9444])),
            ("staging_service.port", str(r.choice([9443, 9444, 7443]))),
            ("staging_service.tenant_scope", "t-%d" % r.randint(200, 260)),
            ("staging_service.max_conn", str(r.choice([64, 128, 256]))),
            ("staging_service.tls", "on"),
            ("staging_service.upstream_timeout_s", str(r.choice([5, 10, 30]))),
            ("staging_service.log_level", r.choice(["info", "warn"])),
            ("staging_service.drain_grace_s", str(r.choice([10, 30, 60]))),
        ]]


def _s1_f3(r):  # listening-socket audit
    return ["# ss -ltnp audit, staging segment, host stg-node-%02d" % r.randint(1, 9)] + [
        "LISTEN 0.%d 0.0.0.0:%d  users:((\"staging-%s\",pid=%d,fd=%d)) tenant t-%d" % (
            r.randint(0, 9), r.choice([9443, 9444, 9445, 7443, 8480]),
            r.choice(["api", "web", "worker", "sync"]), r.randint(400, 4000),
            r.randint(3, 40), r.randint(200, 260))
        for _ in range(8)]


def _s1_f4(r):  # port-scan log, staging subnet
    return ["# nmap staging subnet 10.%d.0.0/16, scan id SC%d" % (r.randint(0, 9), r.randint(100, 999))] + [
        "host stg-web-%02d (%s)  port %d/tcp open  service staging-%s" % (
            r.randint(1, 20), _ip(r), r.choice([9443, 9444, 9445, 7443, 8480]),
            r.choice(["api", "web", "sync"]))
        for _ in range(8)] + ["# scan complete: 0 filtered, %d open" % r.randint(20, 40)]


def _s1_f5(r):  # nginx upstream blocks
    return ["# /etc/nginx/conf.d/staging-upstreams.conf"] + [
        "upstream staging_%s_t%d { least_conn; server %s:%d max_fails=3; }  # tenant t-%d" % (
            svc, r.randint(200, 260), _ip(r), r.choice([9443, 9444, 9445]),
            r.randint(200, 260))
        for svc in ["api", "web", "worker", "sync", "relay", "api", "web"]]


def _s1_f6(r):  # kubernetes Service manifests
    out = []
    for _ in range(6):
        out += ["---", "kind: Service", "metadata:",
                "  name: staging-%s" % r.choice(["api", "web", "worker", "sync"]),
                "  labels: {tenant: t-%d, lane: staging}" % r.randint(200, 260),
                "spec:",
                "  ports: [{name: listen, port: %d, targetPort: %d, protocol: TCP}]" % (
                    r.choice([9443, 9444, 9445]), r.randint(8000, 9000))]
    return out


def _s1_f7(r):  # listener re-point tickets
    return ["# change tickets, staging listener maintenance"] + [
        "CHG-%d [approved] re-point tenant t-%d staging-%s listener :%d -> :%d, window 02:00, owner %s" % (
            r.randint(3000, 3999), r.randint(200, 260),
            r.choice(["api", "web", "sync"]), r.choice([9443, 9444, 9445]),
            r.choice([9443, 9444, 9445]), _user(r))
        for _ in range(8)]


def _s1_f8(r):  # port-check probes
    return ["# probe output: staging service port checks, interval 30s"] + [
        "probe staging-port-check target stg-%02d.internal:%d state %s rtt=%dms tenant t-%d" % (
            r.randint(1, 12), r.choice([9443, 9444, 9445, 7443, 8480]),
            r.choice(["up", "up", "up", "degraded"]), r.randint(1, 90),
            r.randint(200, 260))
        for _ in range(10)]


def _s1_f9(r):  # firewall rules
    return ["# pf ruleset excerpt, staging segment"] + [
        "pass in inet proto tcp from 10.%d.0.0/16 to %s port %d label \"tenant-t%d-staging-%s\" keep state" % (
            r.randint(0, 9), _ip(r), r.choice([9443, 9444, 9445, 7443, 8480]),
            r.randint(200, 260), r.choice(["api", "web", "sync"]))
        for _ in range(10)]


# ---- sel-002: which runner pool is approved for the deploy pipeline?
# vocabulary: runner, pool, approved, deploy, pipeline. Pools a/c/d/e only.
# No "runners-pool-b", no "self-hosted".

POOLS = ["runners-pool-a", "runners-pool-c", "runners-pool-d", "runners-pool-e"]


def _s2_f0(r):  # runner inventory
    return ["# runner inventory, %d registered" % (4 * r.randint(3, 6))] + [
        "runner-r%02d os=%s pool=%s status=%s labels: deploy,pipeline" % (
            n, r.choice(["fedora-43", "debian-13", "ubuntu-24.04"]),
            r.choice(POOLS), r.choice(["idle", "idle", "busy"]))
        for n in range(1, 15)]


def _s2_f1(r):  # pipeline yaml
    out = ["# .ci/deploy-pipeline.yaml (branch main)"]
    for _ in range(4):
        out += ["pipeline:", "  stage_%d_deploy:" % r.randint(1, 4),
                "    runs-on: %s" % r.choice(POOLS),
                "    steps: [build, sign, deploy, verify]",
                "    approved_by: %s" % _user(r)]
    return out


def _s2_f2(r):  # approval log
    return ["# deployment approvals, week %d" % r.randint(34, 38)] + [
        "APPR-%d deploy pipeline #8%d approved for pool %s by %s at 0%d:%02d" % (
            r.randint(500, 999), r.randint(10, 99), r.choice(POOLS), _user(r),
            r.randint(0, 9), r.randint(10, 59))
        for _ in range(8)]


def _s2_f3(r):  # dispatch log
    return ["# pipeline dispatcher, queue depth %d" % r.randint(0, 5)] + [
        "0%d:%02d:%02d pipeline #8%d dispatched to pool %s (runner-r%02d), job deploy, wait %ds" % (
            r.randint(0, 9), r.randint(10, 59), r.randint(10, 59),
            r.randint(10, 99), r.choice(POOLS), r.randint(1, 15), r.randint(1, 30))
        for _ in range(10)]


def _s2_f4(r):  # pool capacity
    return ["# runner pool capacity, sampled 5 min"] + [
        "%s busy %d/%d queue depth %d last deploy %d min ago" % (
            p, r.randint(0, 6), r.randint(6, 10), r.randint(0, 4), r.randint(1, 90))
        for p in POOLS for _ in range(2)]


def _s2_f5(r):  # policy dump
    return ["# deployment policy, effective 2026-09-01",
            "approved_pools:",
            "  - " + "\n  - ".join(POOLS),
            "approval: {deploy: required, pipeline_cancel: optional}",
            "note: pipelines outside approved_pools are refused by the gate"]


def _s2_f6(r):  # heartbeats
    return ["# runner heartbeats"] + [
        "runner-r%02d pool=%s alive ts=2026-09-18T0%d:%02d jobs_done=%d" % (
            r.randint(1, 15), r.choice(POOLS), r.randint(0, 9),
            r.randint(10, 59), r.randint(10, 400))
        for _ in range(12)]


def _s2_f7(r):  # pool-move tickets
    return ["# tickets: pipeline pool moves"] + [
        "OPS-%d [planned] move the %s deploy pipeline from %s to %s; approver %s" % (
            r.randint(4100, 4999), r.choice(["mobile", "web", "batch", "docs"]),
            r.choice(POOLS), r.choice(POOLS), _user(r))
        for _ in range(8)]


def _s2_f8(r):  # approval audit
    return ["# audit: who approved pipeline runs, last 30d"] + [
        "pipeline #8%d approved by %s scope deploy/%s pool %s verdict ok" % (
            r.randint(10, 99), _user(r), r.choice(["staging", "canary", "prod"]),
            r.choice(POOLS))
        for _ in range(8)]


def _s2_f9(r):  # executor log
    return ["# executor trace, deploy pipeline"] + [
        "runner-r%02d (%s) picked up pipeline #8%d stage %s elapsed %ds exit 0" % (
            r.randint(1, 15), r.choice(POOLS), r.randint(10, 99),
            r.choice(["build", "sign", "deploy", "verify"]), r.randint(5, 600))
        for _ in range(10)]


# ---- sel-003: where do staging artifact files end up after a build?
# vocabulary: staging, artifact, files, after, build. Stores qa/dev/archive.
# No "/srv/artifacts/staging".

STORES = ["/srv/artifacts/qa", "/srv/artifacts/dev", "/srv/artifacts/archive"]


def _s3_f0(r):  # store listing
    return ["# ls -la the staging artifact store %s (snapshot)" % r.choice(STORES)] + [
        "drwxr-xr-x ci ci 4096 Sep %02d 0%d:%02d build-9%d/  (%d files)" % (
            r.randint(1, 17), r.randint(0, 9), r.randint(10, 59), r.randint(0, 9),
            r.randint(5, 40))
        for _ in range(8)]


def _s3_f1(r):  # prune cron log
    return ["# cron artifact-prune, nightly"] + [
        "0%d:10 pruned %d artifact files older than 7 days from %s after the nightly build" % (
            r.randint(0, 9), r.randint(80, 400), r.choice(STORES))
        for _ in range(6)]


def _s3_f2(r):  # publish log
    return ["# CI publish step"] + [
        "build #9%d published %d artifact files (%d MB) to %s after tests passed" % (
            r.randint(10, 99), r.randint(6, 30), r.randint(20, 200),
            r.choice(STORES))
        for _ in range(8)]


def _s3_f3(r):  # retention config
    return ["# /etc/artifact-retention.conf (reloaded after each build)"] + [
        "%s = %s" % (k, v) for k, v in [
            ("artifact_root", "/srv/artifacts"),
            ("stores", "qa, dev, archive"),
            ("retention_days", str(r.choice([7, 14]))),
            ("prune_after_build", "yes"),
            ("max_store_gb", str(r.choice([400, 500, 600]))),
            ("compress_after_days", str(r.choice([2, 3]))),
        ]]


def _s3_f4(r):  # sync log
    return ["# artifact sync to the archive store"] + [
        "rsync %s -> /srv/artifacts/archive: %d files, %d MB, %ds, ok" % (
            r.choice(STORES[:2]), r.randint(10, 60), r.randint(50, 500),
            r.randint(10, 300))
        for _ in range(6)]


def _s3_f5(r):  # disk usage
    return ["# du -sh, artifact stores"] + [
        "%s\t%dG" % (s, r.randint(80, 500)) for s in STORES] + [
        "# growth after build #9%d: +%d MB" % (r.randint(10, 99), r.randint(20, 300))]


def _s3_f6(r):  # publish-step yaml
    out = ["# .ci/publish.yaml"]
    for _ in range(3):
        out += ["publish:", "  artifact_files:", "    paths: [dist/*.tar, dist/*.sha256]",
                "    destination: %s/$BUILD_ID/" % r.choice(STORES),
                "    expire_after: {days: %d, purge: after_next_build}" % r.choice([7, 14])]
    return out


def _s3_f7(r):  # checksum manifest
    import string
    return ["# sha256 manifest, build-9%d artifact files" % r.randint(10, 99)] + [
        "%s  %s/build-9%d/artifact-%02d.tar" % (
            "".join(r.choice(string.hexdigits.lower()[:16]) for _ in range(64)),
            r.choice(STORES), r.randint(10, 99), n)
        for n in range(1, 9)]


def _s3_f8(r):  # prune tickets
    return ["# tickets: artifact store housekeeping"] + [
        "OPS-%d [open] %s near quota; raise prune cadence to after every build" % (
            r.randint(4100, 4999), r.choice(STORES))
        for _ in range(6)]


def _s3_f9(r):  # download audit
    return ["# artifact download audit, 24h"] + [
        "ci-bot fetched %s/build-9%d/artifact-%02d.tar %d min after the build finished" % (
            r.choice(STORES), r.randint(10, 99), r.randint(1, 30), r.randint(1, 90))
        for _ in range(8)]


# ---- sel-004: who signs off the queue worker rollout?
# vocabulary: signs, queue, worker, rollout. Approvers amara/viktor/josie/ren.
# No "Priya".

def _s4_f0(r):  # approval matrix
    return ["# rollout approval matrix, ops handbooks"] + [
        "%s rollout: approver of record %s; deputy %s" % (
            comp, _user(r), _user(r))
        for comp in ["queue worker", "edge gateway", "cache tier", "metrics stack",
                     "log shipper", "queue router"]] + [
        "# matrix reviewed 2026-09-1%d" % r.randint(0, 7)]


def _s4_f1(r):  # queue snapshots
    return ["# queue worker snapshots, ops fleet"] + [
        "queue build-jobs depth=%d oldest=%ds workers=%d busy=%d" % (
            r.randint(0, 40), r.randint(5, 900), r.randint(4, 16), r.randint(0, 12))
        for _ in range(8)] + [
        "queue mail-jobs depth=%d oldest=%ds workers=%d busy=%d" % (
            r.randint(0, 20), r.randint(5, 300), r.randint(2, 8), r.randint(0, 6))]


def _s4_f2(r):  # rollout waves
    return ["# worker rollout schedule, v2.%d" % r.randint(4, 7)] + [
        "wave %d: hosts queue-0%d..queue-0%d, window 02:0%d, signoff recorded by %s" % (
            n, n, n + 1, r.randint(0, 9), _user(r))
        for n in range(1, 6)]


def _s4_f3(r):  # worker heartbeats
    return ["# queue worker heartbeats"] + [
        "worker queue-w-%d alive ts=2026-09-18T0%d:%02d lag=%.1fs jobs=%d" % (
            r.randint(1, 9), r.randint(0, 9), r.randint(10, 59),
            r.uniform(0.1, 2.0), r.randint(50, 900))
        for _ in range(10)]


def _s4_f4(r):  # rollout tickets
    return ["# tickets: queue worker rollout v2.%d" % r.randint(4, 7)] + [
        "OPS-%d [in-review] wave %d rollout of the queue worker; approver %s signs after the canary reads clean" % (
            r.randint(4100, 4999), r.randint(2, 5), _user(r))
        for _ in range(6)]


def _s4_f5(r):  # worker config
    return ["# /etc/queue/worker.conf"] + [
        "%s = %s" % (k, v) for k, v in [
            ("worker_concurrency", str(r.choice([8, 16, 32]))),
            ("queue_prefetch", str(r.choice([2, 4, 8]))),
            ("rollout_wave_size", str(r.choice([1, 2]))),
            ("ack_timeout_s", str(r.choice([30, 60]))),
            ("drain_grace_s", str(r.choice([60, 120]))),
            ("heartbeat_interval_s", str(r.choice([10, 15]))),
        ]]


def _s4_f6(r):  # signoff audit
    return ["# signoff audit trail, releases"] + [
        "signoff line appended by %s for rollout REL-%d (queue worker v2.%d, wave %d)" % (
            _user(r), r.randint(200, 299), r.randint(2, 6), r.randint(1, 5))
        for _ in range(8)]


def _s4_f7(r):  # deploy-gate yaml
    return ["# deploy-gate.yaml", "gate: rollout",
            "required_approvers:",
            "  - " + "\n  - ".join(r.sample(["amara", "viktor", "josie", "ren"], 2)),
            "checks: [canary_clean, queue_lag_nominal, worker_drain_ok]",
            "policy: a rollout without the signoff entry does not ship"]


def _s4_f8(r):  # status page
    return ["# ops status page, queue section"] + [
        "queue %s: workers %d/%d up, consumer lag %d ms, oldest job %ds" % (
            name, r.randint(6, 8), 8, r.randint(1, 200), r.randint(1, 400))
        for name in ["build-jobs", "mail-jobs", "ingest-jobs"]] + [
        "# last worker rollout: wave %d at 02:%02d, no rollbacks" % (r.randint(2, 5), r.randint(10, 59))]


def _s4_f9(r):  # rollout checklist
    return ["# queue worker rollout checklist, v2.%d" % r.randint(4, 7),
            "- [x] canary wave drained clean",
            "- [x] queue lag nominal through the window",
            "- [ ] wave %d signoff - approver: %s" % (r.randint(3, 5), _user(r)),
            "- [ ] final wave rollout after the signoff entry lands",
            "- notes: drain_grace raised to %ds for the rollout" % r.choice([60, 120])]


# ---- sel-005: what is the maximum request body size the public API accepts?
# vocabulary: maximum, request, body, size, public, accepts. Limits 2m/4m,
# edge/preview gateways. No "1 MiB", no "rejects request bodies over".

def _s5_f0(r):  # gateway config
    return ["# /etc/gateway/edge.conf (reloaded 2026-09-1%d)" % r.randint(0, 7)] + [
        "%s %s" % (k, v) for k, v in [
            ("client_max_body_size", r.choice(["2m", "4m"])),
            ("keepalive_requests", str(r.choice([100, 1000]))),
            ("proxy_read_timeout", "%ds" % r.choice([30, 60])),
            ("large_client_header_buffers", "4 16k"),
            ("request_size_telemetry", "on"),
        ]]


def _s5_f1(r):  # access log with 413s
    return ["# edge gateway access log, public vhosts, request body size in kb"] + [
        '10.%d.%d.%d - - [18/Sep/2026:0%d:%02d:%02d +0000] "POST %s HTTP/1.1" %s %d' % (
            r.randint(0, 9), r.randint(0, 40), r.randint(1, 250), r.randint(0, 9),
            r.randint(10, 59), r.randint(10, 59),
            r.choice(["/api/v2/ingest", "/upload", "/api/v2/reports"]),
            r.choice(["200 812", "201 94", "413 212", "413 212", "200 1503"]),
            r.randint(1, 9))
        for _ in range(12)]


def _s5_f2(r):  # endpoint limit table
    return ["# request size limits by endpoint, edge vs internal"] + [
        "%-22s edge maximum %s  internal maximum %s" % (
            ep, r.choice(["2m", "2m", "1.5m"]), r.choice(["4m", "8m"]))
        for ep in ["/api/v2/ingest", "/api/v2/reports", "/upload", "/avatar",
                   "/api/v2/health", "/export"]] + [
        "# the public door is the edge column; internal doors sit behind the mesh"]


def _s5_f3(r):  # changelog
    return ["# gateway changelog"] + [
        "2026-09-%02d  raised the maximum accepted body on the preview gateway from 1m to 2m" % r.randint(1, 14),
        "2026-09-%02d  edge gateway: maximum upload size tuned for the mobile pool" % r.randint(1, 14),
        "2026-09-%02d  request body telemetry switched on for public endpoints" % r.randint(1, 14),
        "2026-09-%02d  413 pages now name the endpoint limit that refused the request" % r.randint(1, 14)]


def _s5_f4(r):  # config dump
    return ["# gateway -s dump"] + [
        "%s = %s" % (k, v) for k, v in [
            ("max_body_size", str(r.choice([2097152, 4194304]))),
            ("max_header_size", "16384"),
            ("body_buffer", "16k"),
            ("public_listeners", "0.0.0.0:443,0.0.0.0:8080"),
            ("request_timeout_s", str(r.choice([30, 60]))),
            ("accept_encoding", "gzip, br"),
        ]]


def _s5_f5(r):  # size telemetry
    return ["# request body size, public endpoints, 24h"] + [
        "%-20s p50 %dk p90 %dk p99 %.1fm maximum seen %.1fm refused_over_limit %d" % (
            ep, r.randint(2, 40), r.randint(80, 900), r.uniform(0.3, 1.4),
            r.uniform(1.5, 2.4), r.randint(0, 60))
        for ep in ["/api/v2/ingest", "/upload", "/api/v2/reports"]]


def _s5_f6(r):  # upload tickets
    return ["# tickets: body size limits"] + [
        "OPS-%d [triage] %s uploads hit the edge body cap; raise the maximum for the %s pool" % (
            r.randint(4100, 4999), r.choice(["mobile", "partner", "batch"]),
            r.choice(["mobile", "partner", "batch"]))
        for _ in range(6)]


def _s5_f7(r):  # WAF rules
    return ["# waf rules, public door"] + [
        "deny phase:request_body if body_size > %s label \"oversized-body\"" % r.choice(["4m", "8m"]),
        "allow phase:request if path_beg /api/v2/health",
        "log oversize refusals to the size-telemetry sink",
        "note: the edge maximum is the one the client sees; waf sits behind it",
    ]


def _s5_f8(r):  # api doc snippet
    return ["# public api reference, generated 2026-09-1%d" % r.randint(0, 7),
            "## payload limits",
            "maximum request body: 2 mib at the edge gateway (public door);",
            "larger bodies are refused there with 413 and an X-Body-Limit header;",
            "the internal mesh accepts up to %d mib between services;" % r.choice([4, 8]),
            "clients chunking uploads should target <= 1.5 mib per request"]


def _s5_f9(r):  # load test log
    return ["# load test, public ingest door"] + [
        "sample %02d: request body %.1fm %s at the edge (%d ms)" % (
            n, r.uniform(0.2, 2.4),
            r.choice(["accepted", "accepted", "refused over the maximum"]),
            r.randint(20, 400))
        for n in range(1, 11)]


FAMILIES = {
    "sel-001": [_s1_f0, _s1_f1, _s1_f2, _s1_f3, _s1_f4,
                _s1_f5, _s1_f6, _s1_f7, _s1_f8, _s1_f9],
    "sel-002": [_s2_f0, _s2_f1, _s2_f2, _s2_f3, _s2_f4,
                _s2_f5, _s2_f6, _s2_f7, _s2_f8, _s2_f9],
    "sel-003": [_s3_f0, _s3_f1, _s3_f2, _s3_f3, _s3_f4,
                _s3_f5, _s3_f6, _s3_f7, _s3_f8, _s3_f9],
    "sel-004": [_s4_f0, _s4_f1, _s4_f2, _s4_f3, _s4_f4,
                _s4_f5, _s4_f6, _s4_f7, _s4_f8, _s4_f9],
    "sel-005": [_s5_f0, _s5_f1, _s5_f2, _s5_f3, _s5_f4,
                _s5_f5, _s5_f6, _s5_f7, _s5_f8, _s5_f9],
}


def main() -> int:
    for name in ("items.jsonl", "pressure_chunks.jsonl", "declaration.json"):
        if (HERE / name).exists():
            print(f"declare.py: {name} already on disk; not rewriting")
            return 1

    r1_decl = json.loads((S8 / "declaration.json").read_text(encoding="utf-8"))

    # items: rung 1's bytes, verified against rung 1's pin. Nothing is
    # written until every assertion below has passed.
    items_bytes = (S8 / "items.jsonl").read_bytes()
    items_sha = sha_bytes(items_bytes)
    if items_sha != r1_decl["items_sha256"]:
        print("declare.py: rung-1 items.jsonl does not match the rung-1 pin")
        return 1
    items = [json.loads(l) for l in items_bytes.decode().splitlines() if l.strip()]

    # the load: ten query-adjacent families per item, seeded and deterministic
    all_evidence = [norm(h) for i in items for h in i["helpful_evidence"] if h.strip()]
    chunk_lines, totals = [], {}
    for item in items:
        iid, qwords = item["item_id"], words(item["query"])
        chunks = [fill(FAMILIES[iid][f](rng_for(iid, f)))
                  for f in range(FAMILIES_PER_ITEM)]
        far = [n for n, c in enumerate(chunks)
               if len(qwords & words(c)) < min(2, len(qwords))]
        if far:
            print(f"declare.py: ABORT chunks {far} for {iid} share fewer than "
                  f"two query words; adjacency is the point of rung 2")
            return 1
        leaky = [n for n, c in enumerate(chunks)
                 if any(h in norm(c) for h in all_evidence)]
        if leaky:
            print(f"declare.py: ABORT chunks {leaky} for {iid} contain helpful "
                  f"evidence; the load must compete, not help")
            return 1
        totals[iid] = sum(len(c.encode("utf-8")) for c in chunks)
        if totals[iid] < RUNG1_DECLARED_LOAD:
            print(f"declare.py: ABORT load for {iid} is {totals[iid]} bytes, "
                  f"below rung 1's declared {RUNG1_DECLARED_LOAD}")
            return 1
        chunk_lines.append({"item_id": iid, "chunks": chunks})

    (HERE / "items.jsonl").write_bytes(items_bytes)
    chunks_path = HERE / "pressure_chunks.jsonl"
    chunks_path.write_text(
        "".join(json.dumps(c) + "\n" for c in chunk_lines), encoding="utf-8")
    chunks_sha = sha_bytes(chunks_path.read_bytes())

    declared_load = min(totals.values())   # the guaranteed per-item floor
    declaration = {
        "declared_at": datetime.now(timezone.utc).isoformat(),
        "budget_chars": r1_decl["budget_chars"],
        "scoring": r1_decl["scoring"],
        "pressure": {"tool_output_bytes": declared_load,
                     "chunks_sha256": chunks_sha},
        "items_sha256": items_sha,
        "adapters": r1_decl["adapters"],
    }
    (HERE / "declaration.json").write_text(
        json.dumps(declaration, indent=1) + "\n", encoding="utf-8")

    print(f"items frozen: {len(items)} (rung-1 bytes, sha {items_sha[:12]}...)")
    print(f"load frozen: {len(chunk_lines) * FAMILIES_PER_ITEM} query-adjacent "
          f"chunks, sha {chunks_sha[:12]}...")
    for line in chunk_lines:
        print(f"  {line['item_id']}: "
              f"{sum(len(c.encode('utf-8')) for c in line['chunks'])} bytes injected")
    print(f"declared at {declaration['declared_at']}, budget "
          f"{declaration['budget_chars']} chars, load floor {declared_load} "
          f"bytes/item (rung 1 declared {RUNG1_DECLARED_LOAD}); nothing has run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
