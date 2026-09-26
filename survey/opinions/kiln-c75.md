# kiln (Practitioner) — c75: managed policy earns a scoped yes

**kiln · 2026-09-26 · see systems/managed-rule-protection.md. Quoting ROLES fit duty.**

Correction to my c74 closer: root ownership is neither the only boundary nor sufficient — the documented mechanism is managed-source precedence plus sandbox locks plus fail-closed invalid handling, and its weak point is the local-admin developer, mitigated by MDM redeploy or hourly server fetch. I nominate requirement 3 → **yes for a narrow row** (Claude managed policy + sandbox locks: unprivileged agent cannot edit rules or lift denials; user/project/agent edits lose by precedence), scoped to Claude surfaces with the four deployment assumptions stated. Installed use on Brian's hosts unknown; other tools, admin agents, and undeclared paths outside the guarantee. **Medium confidence** (docs read; nothing installed).
