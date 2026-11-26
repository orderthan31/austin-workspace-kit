#!/usr/bin/env bash
set -euo pipefail

KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$KIT_ROOT/agents/obsidian-orchestrator.md"
CLAUDE_DST="${CLAUDE_AGENT_DST:-$HOME/.claude/agents/obsidian-orchestrator.md}"
OPENCODE_DST="${OPENCODE_AGENT_DST:-$HOME/.config/opencode/agents/obsidian-orchestrator.md}"

if [[ ! -f "$SRC" ]]; then
  echo "Source agent not found: $SRC" >&2
  exit 1
fi

mkdir -p "$(dirname "$CLAUDE_DST")" "$(dirname "$OPENCODE_DST")"

sed 's/^model: .*/model: sonnet/' "$SRC" > "$CLAUDE_DST"

BODY="$(awk 'BEGIN{in_frontmatter=0; started=0} /^---$/ {if (!started) {started=1; in_frontmatter=1; next} if (in_frontmatter) {in_frontmatter=0; next}} !in_frontmatter {print}' "$SRC")"

cat > "$OPENCODE_DST" <<EOF
---
description: Obsidian related requests are routed to the right obsidian skills in sequence
mode: subagent
model: openai/gpt-5.4
skills:
  - obsidian-cli-guideline
  - obsidian-official-usage
  - obsidian-daily-ops
  - obsidian-report-ops
  - obsidian-review-agent-usage
  - obsidian-mermaid-visual-note
  - obsidian-plan-reset
  - obsidian-sync-skills-pipeline
tools:
  edit: true
  bash: true
  task: true
permission:
  edit: allow
  bash: allow
  task: allow
---

$BODY
EOF

echo "Synced Claude agent: $CLAUDE_DST"
echo "Synced OpenCode agent: $OPENCODE_DST"
