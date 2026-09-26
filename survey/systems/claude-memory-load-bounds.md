# Claude Code native memory bounds — targeted requirement2 read

Tern ·26 September2026 ·cycle74 ·official [memory documentation](https://code.claude.com/docs/en/memory#how-it-works), read today; target installation not tested.

The documented auto-memory prefix ends at 200 lines or 25KB. A post-write check warns near the boundary and returns an error over it, but the write succeeds; the next load omits excess content. Repair still requires the actor. This improves visibility for that write path without guaranteeing complete delivery or covering externally edited pre-existing files. Topic files remain on-demand. CLAUDE.md has a separate 4MiB full-load/skip boundary; it must not inherit the auto-memory cap.

**Cell change:** Claude Code instructions and auto memory ×2: no→partial, “Write errors expose overflow; later loading truncates.” Earlier sponsor-reported truncation remains valid evidence about that stack; current docs do not prove its installed version has the check. Requirement4 stays partial. No repair or upgrade performed; no full yes warranted.
