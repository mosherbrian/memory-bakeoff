# Inspected capability and sources (read-only, no model calls)
- `claude --version` -> 2.1.283; `claude --help`: -p/--print, --allowedTools, --disallowedTools, --permission-mode, --settings, --setting-sources, --model, --session-id, --no-session-persistence, --output-format.
- Auto-memory layout observed in this account: ~/.claude/projects/-var-home-bmosher/memory/ (297 entries incl. MEMORY.md index); fact files with frontmatter; index injected at session start in this session.
- R43 acceptance.json; R40 workflow order/protocol; R42 fixture and grader (hashes in protocol.json).
- RULE-CANDIDATES #4 and #6 sources verified earlier in R41 readiness.md.
- Not verified here: auto-memory default with a fresh CLAUDE_CONFIG_DIR; credential handling for isolated config dirs.
