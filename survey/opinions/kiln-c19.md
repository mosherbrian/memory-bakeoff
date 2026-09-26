# kiln (Practitioner) — c19: native recovery is grep-to-expand, glue is a loop

**kiln · 2026-09-26 · see systems/native-failed-attempt-recovery.md. Quoting ROLES.md: "maintenance, fit for Brian's stack".**

Pi/pi-lcm recovers a failed attempt without any ID today: `lcm_grep` (FTS/regex/summary scopes) → IDs → `lcm_expand` or seq-window read, with originals stored verbatim beside derived summaries. Mechanism verdict: **deploy** — it ships, it is local, it costs nothing extra. The remaining glue is concrete and small: a cross-conversation sweep loop (all calls are per-conversation scoped) and a failure-note convention, since nothing marks pass/fail. Hindsight's pull-route and version-replacement limits from c18 stand unrepaired; native wins failed-attempt recovery on verifiability, loses it on cross-session reach — which is exactly the loop to build.
