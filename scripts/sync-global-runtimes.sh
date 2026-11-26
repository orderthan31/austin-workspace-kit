#!/usr/bin/env bash
set -euo pipefail

# 이미 설치한 Claude 스킬을 선택한 실행 환경으로 복사한다.
kit_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="${SRC:-$HOME/.claude/skills}"
for destination in "${AGENTS_DST:-$HOME/.agents/skills}" \
                   "${ANTI_CLI_DST:-$HOME/.gemini/config/skills}" \
                   "${ANTI_DST:-$HOME/.gemini/antigravity/skills}"; do
  SRC="$source_dir" DST="$destination" bash "$kit_root/scripts/sync-global-to-claude.sh" "$@"
done
