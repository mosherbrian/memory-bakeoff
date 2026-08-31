from __future__ import annotations

from datetime import datetime, timezone, timedelta

from memory_bakeoff.models import MemoryRecord, QueryCase

UTC = timezone.utc


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=UTC)


def build_corpus(distractors: int = 0) -> tuple[list[MemoryRecord], list[QueryCase]]:
    """Coding-flavored deterministic corpus with explicit relevance labels.

    The corpus intentionally mixes lexical identifiers, paraphrases, corrections,
    multi-hop dependencies, procedures, failures, attribution/scope, and distractors.
    """
    R = MemoryRecord
    records = [
        # Exact/lexical facts
        R("M001", "The CI signing failure E_SIG_47 is fixed by refreshing the cosign OIDC token, not by rotating repository secrets.", dt("2026-01-02T09:00:00"), "s01"),
        R("M002", "The generated API client lives at internal/gen/payments_client.go and must not be edited by hand.", dt("2026-01-02T09:05:00"), "s01"),
        R("M003", "The payment proto source is api/payments/v2/payments.proto.", dt("2026-01-02T09:06:00"), "s01"),
        R("M004", "Run 'buf generate' from the repository root to regenerate payment protobuf code.", dt("2026-01-02T09:07:00"), "s01", outcome="success"),
        R("M005", "The staging Redis database number is 6.", dt("2026-01-03T10:00:00"), "s02"),
        # Semantic/paraphrase facts
        R("M006", "The cache invalidator must release cacheMu before calling broadcastInvalidation because the callback can synchronously re-enter the cache.", dt("2026-01-05T13:00:00"), "s03"),
        R("M007", "When the indexer appears hung with low CPU, inspect the bounded work queue first; producers can block while waiting for a full queue to drain.", dt("2026-01-05T13:10:00"), "s03"),
        R("M008", "A zero-length Matrix event body is valid for redactions; validation should inspect the event type before rejecting an empty body.", dt("2026-01-05T13:20:00"), "s03"),
        R("M009", "The macOS bridge host speaks newline-delimited JSON over stdin/stdout; stdout must contain protocol frames only.", dt("2026-01-06T08:00:00"), "s04"),
        R("M010", "Diagnostic logging for the bridge host belongs on stderr so it cannot corrupt NDJSON framing.", dt("2026-01-06T08:02:00"), "s04"),
        # Temporal corrections
        R("M011", "The build coordinator is strix03.", dt("2026-02-01T09:00:00"), "s05"),
        R("M012", "The build coordinator moved from strix03 to strix07; strix07 is now authoritative.", dt("2026-03-15T09:00:00"), "s06", supersedes_id="M011"),
        R("M013", "Production deploys use 'deployctl push --region west'.", dt("2026-02-02T10:00:00"), "s05"),
        R("M014", "After the deploy service migration, production deploys use 'shipit release --cluster pdx'; deployctl is obsolete.", dt("2026-04-10T10:00:00"), "s07", supersedes_id="M013"),
        R("M015", "The API rate limit was 120 requests per minute for service accounts.", dt("2026-02-10T12:00:00"), "s05"),
        R("M016", "The service-account API limit increased to 300 requests per minute on 2026-05-01.", dt("2026-05-01T12:00:00"), "s08", supersedes_id="M015"),
        # Multi-hop
        R("M017", "The invoice reconciler gets its database DSN from the secret named billing-db-dsn.", dt("2026-03-01T11:00:00"), "s09"),
        R("M018", "The billing-db-dsn secret is owned by the platform-secrets Terraform module.", dt("2026-03-01T11:03:00"), "s09"),
        R("M019", "Changes to platform-secrets require running the secrets-plan GitHub workflow before merge.", dt("2026-03-01T11:05:00"), "s09"),
        R("M020", "The thumbnail worker publishes failed jobs to the image-deadletter topic.", dt("2026-03-03T14:00:00"), "s10"),
        R("M021", "The image-deadletter topic is consumed by the media-repair service.", dt("2026-03-03T14:02:00"), "s10"),
        R("M022", "The media-repair service's replay command is 'media-repair replay --source deadletter'.", dt("2026-03-03T14:04:00"), "s10"),
        # Procedures and verified outcomes
        R("M023", "For stale generated Go code: edit the source schema, run the generator, inspect the generated diff, run package tests, then run the full suite.", dt("2026-04-01T10:00:00"), "s11", outcome="success", metadata={"procedure_family":"generated-code"}),
        R("M024", "Editing generated Go files directly made the immediate test pass but failed regeneration checks in CI.", dt("2026-04-01T10:20:00"), "s11", outcome="failure", metadata={"procedure_family":"generated-code"}),
        R("M025", "For flaky cache races: reproduce under -race, add synchronization at the ownership boundary, then rerun the focused race test before the whole package.", dt("2026-04-02T10:00:00"), "s12", outcome="success", metadata={"procedure_family":"race"}),
        R("M026", "Adding sleeps around the cache race reduced failures locally but hidden stress tests still failed; do not use timing sleeps as the fix.", dt("2026-04-02T10:20:00"), "s12", outcome="failure", metadata={"procedure_family":"race"}),
        R("M027", "For NDJSON protocol bugs: capture exact frames, validate one JSON object per line, and keep logs off stdout; this resolved the bridge desynchronization.", dt("2026-04-03T10:00:00"), "s13", outcome="success", metadata={"procedure_family":"ndjson"}),
        R("M028", "Pretty-printing outbound JSON across multiple lines made bridge framing failures worse and was reverted.", dt("2026-04-03T10:20:00"), "s13", outcome="failure", metadata={"procedure_family":"ndjson"}),
        # Scope/attribution collisions
        R("M029", "In repo atlas, the release branch is release/atlas-2.x.", dt("2026-04-05T09:00:00"), "s14", scope="repo:atlas"),
        R("M030", "In repo beacon, the release branch is stable.", dt("2026-04-05T09:01:00"), "s14", scope="repo:beacon"),
        R("M031", "Alice owns the Atlas deployment pipeline.", dt("2026-04-05T09:02:00"), "s14", scope="repo:atlas"),
        R("M032", "Bob owns the Beacon deployment pipeline.", dt("2026-04-05T09:03:00"), "s14", scope="repo:beacon"),
        R("M033", "In repo atlas, integration tests use PostgreSQL 17.", dt("2026-04-05T09:04:00"), "s14", scope="repo:atlas"),
        R("M034", "In repo beacon, integration tests use PostgreSQL 16.", dt("2026-04-05T09:05:00"), "s14", scope="repo:beacon"),
        # More distractors / near-neighbors
        R("M035", "The frontend preview environment uses Redis database number 2.", dt("2026-04-06T11:00:00"), "s15"),
        R("M036", "The development Redis database number is 3.", dt("2026-04-06T11:01:00"), "s15"),
        R("M037", "Human-readable audit logs are JSONL files compressed daily with zstd.", dt("2026-04-06T11:02:00"), "s15"),
        R("M038", "The telemetry collector uses protobuf over gRPC, not NDJSON.", dt("2026-04-06T11:03:00"), "s15"),
        R("M039", "The image service's normal work topic is image-jobs.", dt("2026-04-06T11:04:00"), "s15"),
        R("M040", "The billing web UI is deployed independently of the invoice reconciler.", dt("2026-04-06T11:05:00"), "s15"),
        # More correction / conflict
        R("M041", "The test fixture bucket is qa-fixtures-v1.", dt("2026-05-02T10:00:00"), "s16"),
        R("M042", "The test fixture bucket was renamed to qa-fixtures-v2; qa-fixtures-v1 is read-only for legacy runs.", dt("2026-06-10T10:00:00"), "s17", supersedes_id="M041"),
        R("M043", "The compatibility test still intentionally reads archived samples from qa-fixtures-v1.", dt("2026-06-10T10:05:00"), "s17"),
        # Extra procedures to make failure/success discrimination nontrivial
        R("M044", "A successful schema migration dry-run used a transaction plus EXPLAIN on the backfill query before applying the migration.", dt("2026-06-12T10:00:00"), "s18", outcome="success", metadata={"procedure_family":"migration"}),
        R("M045", "Running the backfill directly in production without EXPLAIN caused a lock spike and the change was rolled back.", dt("2026-06-12T10:20:00"), "s18", outcome="failure", metadata={"procedure_family":"migration"}),
        R("M046", "A successful dependency bump regenerated the lockfile and ran both unit tests and the license-policy check.", dt("2026-06-13T10:00:00"), "s19", outcome="success", metadata={"procedure_family":"dependency"}),
        R("M047", "Hand-editing the lockfile after a dependency bump produced an inconsistent graph and failed CI.", dt("2026-06-13T10:20:00"), "s19", outcome="failure", metadata={"procedure_family":"dependency"}),
        # Negative/distractor-only content
        R("M048", "The office coffee machine is descaled on the first Monday of each month.", dt("2026-06-14T10:00:00"), "s20"),
        R("M049", "The demo dashboard theme was changed from charcoal to slate.", dt("2026-06-14T10:01:00"), "s20"),
        R("M050", "The team's lunch order cutoff on Fridays is 11:15 AM.", dt("2026-06-14T10:02:00"), "s20"),
    ]

    Q = QueryCase
    cases = [
        Q("Q001", "exact", "What does E_SIG_47 mean and what fixed it?", ("M001",)),
        Q("Q002", "exact", "Which file is the generated payments client?", ("M002",)),
        Q("Q003", "exact", "Which Redis DB does staging use?", ("M005",), prohibited_ids=("M035","M036")),
        Q("Q004", "semantic", "Why can calling the invalidation callback while holding the cache lock deadlock or recurse?", ("M006",)),
        Q("Q005", "semantic", "The indexer isn't using CPU and seems frozen. What previously caused this?", ("M007",)),
        Q("Q006", "semantic", "Can a redaction event legitimately have no body text?", ("M008",)),
        Q("Q007", "temporal_current", "What machine is the current build coordinator?", ("M012",), prohibited_ids=("M011",)),
        Q("Q008", "temporal_current", "What is the current production deployment command?", ("M014",), prohibited_ids=("M013",)),
        Q("Q009", "temporal_current", "What is today's service-account request limit?", ("M016",), prohibited_ids=("M015",)),
        Q("Q010", "temporal_asof", "As of March 1, 2026, what production deployment command was in use?", ("M013",), prohibited_ids=("M014",), as_of=dt("2026-03-01T23:59:00")),
        Q("Q011", "temporal_asof", "As of February 20, 2026, which host coordinated builds?", ("M011",), prohibited_ids=("M012",), as_of=dt("2026-02-20T23:59:00")),
        Q("Q012", "multihop", "If I need to change the invoice reconciler's DB credentials, which secret/module/workflow chain matters?", ("M017","M018","M019")),
        Q("Q013", "multihop", "A thumbnail job landed in dead-letter. Which consumer and replay command handle it?", ("M020","M021","M022")),
        Q("Q014", "procedure", "Generated Go output is stale. What workflow previously succeeded?", ("M023",), prohibited_ids=("M024",)),
        Q("Q015", "procedure", "How should I attack a flaky cache race based on prior verified outcomes?", ("M025",), prohibited_ids=("M026",)),
        Q("Q016", "procedure", "What's the successful way to debug newline-delimited JSON framing?", ("M027",), prohibited_ids=("M028",)),
        Q("Q017", "procedure", "What is the safer proven approach for a database backfill migration?", ("M044",), prohibited_ids=("M045",)),
        Q("Q018", "procedure", "What did we learn about safely updating a dependency and lockfile?", ("M046",), prohibited_ids=("M047",)),
        Q("Q019", "scope", "For Atlas, what release branch should I target?", ("M029",), prohibited_ids=("M030",), scope="repo:atlas"),
        Q("Q020", "scope", "Who owns Beacon's deployment pipeline?", ("M032",), prohibited_ids=("M031",), scope="repo:beacon"),
        Q("Q021", "scope", "Which PostgreSQL version do Atlas integration tests use?", ("M033",), prohibited_ids=("M034",), scope="repo:atlas"),
        Q("Q022", "temporal_current", "Which bucket should new QA fixture runs use now?", ("M042",), prohibited_ids=("M041",)),
        Q("Q023", "conflict", "Does anything still intentionally use qa-fixtures-v1?", ("M043",), prohibited_ids=()),
        Q("Q024", "protocol", "Where should bridge diagnostic logs go, and why?", ("M009","M010"), prohibited_ids=("M037","M038")),
        Q("Q025", "negative", "What is the root password for the production database?", (), notes="No memory contains this fact."),
        Q("Q026", "negative", "Which engineer is on call tonight?", (), notes="No memory contains an on-call schedule."),
    ]
    if distractors:
        records.extend(stress_distractors(distractors))
    return records, cases


def stress_distractors(count: int = 450) -> list[MemoryRecord]:
    """Generate deterministic coding near-neighbors without changing ground truth.

    These are intentionally lexically/semantically adjacent to the core questions, but
    each contains qualifiers that make it a different system, environment, or historical
    incident. IDs continue after M050 so native provenance paths remain compatible.
    """
    if count < 0:
        raise ValueError("distractor count must be non-negative")
    repos = ["cedar", "delta", "ember", "fjord", "glint", "harbor", "ion", "juniper", "kestrel", "lumen"]
    services = ["catalog", "ledger", "search", "avatar", "mailer", "metrics", "archive", "gateway", "reporter", "scheduler"]
    owners = ["Carol", "Diego", "Erin", "Fatima", "Gus", "Hana", "Ivan", "Jules", "Kira", "Leo"]
    base = dt("2026-01-10T08:00:00")
    out: list[MemoryRecord] = []
    for i in range(count):
        rid = f"M{51+i:03d}"
        repo = repos[i % len(repos)]
        service = services[(i * 3) % len(services)]
        owner = owners[(i * 7) % len(owners)]
        n = (i * 11) % 19 + 1
        family = i % 12
        if family == 0:
            text = f"In repo {repo}, release rehearsals use branch release/{repo}-{(i%4)+1}.x; this is unrelated to Atlas releases."
        elif family == 1:
            text = f"A {repo} Redis migration fixture restored staging snapshot database {n % 8}; it does not define the platform staging Redis database."
        elif family == 2:
            text = f"The {service} canary deployment example uses deployctl preview --region test-{n}; it is not the production release command."
        elif family == 3:
            text = f"Repo {repo} generates internal/gen/{service}_client.go from api/{service}/v1/{service}.proto during its own codegen tests."
        elif family == 4:
            text = f"The {service} import utility reads newline-delimited JSON files from disk, while its diagnostic summary is written to a normal log file."
        elif family == 5:
            text = f"Failed {service} test jobs go to {service}-deadletter-{n}; the replay helper is {service}-repair replay --source test-deadletter."
        elif family == 6:
            text = f"The {repo} read-only database credential is secret {repo}-db-ro, managed by the {repo}-secrets Terraform module and checked by {repo}-plan."
        elif family == 7:
            text = f"Repo {repo} integration tests currently pin PostgreSQL {14 + (n % 4)} for the {service} compatibility matrix."
        elif family == 8:
            text = f"The {service} load-test account is capped at {100 + n*10} requests per minute; this quota applies only to synthetic traffic."
        elif family == 9:
            text = f"A {repo} generated-code incident was fixed by regenerating fixtures and running focused tests; direct edits were rejected during review."
        elif family == 10:
            text = f"A race in {service} was investigated with tracing and stress tests; adding arbitrary sleeps was documented as unreliable."
        else:
            text = f"{owner} maintains repo {repo}'s {service} pipeline; this ownership note applies only to {repo}."
        out.append(
            MemoryRecord(
                rid,
                text,
                base + timedelta(hours=i * 7),
                f"stress-{i//10:03d}",
                scope=f"repo:{repo}",
                outcome="neutral",
                metadata={"stress_distractor": True, "family": family},
            )
        )
    return out


def learning_stream() -> tuple[list[MemoryRecord], list[QueryCase]]:
    """Small procedural stream for testing verified feedback mechanics.

    Cases intentionally paraphrase the procedure family. A feedback-capable provider
    should be able to increase useful-before-harmful ranking over repeated episodes.
    """
    records, cases = build_corpus()
    proc_ids = {"M023","M024","M025","M026","M027","M028","M044","M045","M046","M047"}
    recs = [r for r in records if r.id in proc_ids]
    qs = [q for q in cases if q.category == "procedure"]
    return recs, qs


def learning_training_cases() -> list[QueryCase]:
    """Training-only paraphrases for verified-feedback diagnostics.

    These never appear in the reported learning curve. They carry the same objective
    success/failure labels as the held-out procedure queries, but use different wording
    so a feedback-capable provider must transfer what it learned to the evaluation query.
    """
    Q = QueryCase
    return [
        Q("LT001", "procedure_train", "A generated Go artifact drifted from its schema. Which prior approach should future runs favor?", ("M023",), prohibited_ids=("M024",)),
        Q("LT002", "procedure_train", "A concurrency bug only appears under stress. Which previously validated repair strategy should be preferred?", ("M025",), prohibited_ids=("M026",)),
        Q("LT003", "procedure_train", "The line-oriented bridge protocol is desynchronizing. Which past diagnostic method actually worked?", ("M027",), prohibited_ids=("M028",)),
        Q("LT004", "procedure_train", "Before a risky database backfill, what prior workflow earned a verified success receipt?", ("M044",), prohibited_ids=("M045",)),
        Q("LT005", "procedure_train", "A dependency graph changed. Which lockfile-update workflow succeeded rather than breaking CI?", ("M046",), prohibited_ids=("M047",)),
    ]
