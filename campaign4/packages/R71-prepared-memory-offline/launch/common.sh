# R47 frozen launch settings (sourced). Claude Code 2.1.283, Max route (claude.ai, firstParty), no ANTHROPIC_* vars.
ENVI="env -i HOME=/var/home/bmosher PATH=/var/home/bmosher/.local/bin:/usr/bin:/bin"
BASE="--model claude-sonnet-5 --setting-sources project --strict-mcp-config --disable-slash-commands --output-format stream-json --verbose"
S1_TOOLS='--tools Read,Write,Edit --permission-mode acceptEdits'
S2_TOOLS='--tools Bash,Read,Write --permission-mode dontAsk'
S2_SETTINGS='{"permissions":{"allow":["Bash(./bench.sh --ctx:*)","Read","Write"]}}'   # R56 local amendment: only ./bench.sh --ctx N; no svc
