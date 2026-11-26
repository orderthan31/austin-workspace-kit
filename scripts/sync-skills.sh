#!/usr/bin/env bash
set -euo pipefail

kit_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
claude_dst="${CLAUDE_SKILLS_DST:-$HOME/.claude/skills}"
agents_dst="${AGENTS_DST:-$HOME/.agents/skills}"
anti_cli_dst="${ANTI_CLI_DST:-$HOME/.gemini/config/skills}"
anti_app_dst="${ANTI_DST:-$HOME/.gemini/antigravity/skills}"
dry_run=0
include_obsidian=0
include_private=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --include-obsidian) include_obsidian=1 ;;
    --include-private) include_private=1 ;;
    -h|--help)
      echo "사용법: $0 [--dry-run] [--include-obsidian] [--include-private]"
      exit 0
      ;;
    *) echo "알 수 없는 옵션입니다. $arg" >&2; exit 2 ;;
  esac
done

if [[ $include_private -eq 1 && ! -f "$kit_root/private/global-skills.txt" ]]; then
  echo "private/global-skills.txt에 설치할 로컬 스킬을 등록해주세요." >&2
  exit 1
fi

sync_scope() {
  local source="$1" registry="$2" exclusions="$3" dependencies="$4" destination
  local options=()
  if [[ $dry_run -eq 1 ]]; then
    options=(--dry-run)
  fi
  for destination in "$claude_dst" "$agents_dst" "$anti_cli_dst" "$anti_app_dst"; do
    SRC="$source" DST="$destination" GLOBAL_SKILLS_FILE="$registry" EXCLUDE_FILE="$exclusions" \
      SKILL_DEPENDENCIES_FILE="$dependencies" \
      bash "$kit_root/scripts/sync-global-to-claude.sh" ${options[@]+"${options[@]}"}
  done
}

public_deps="$kit_root/config/skill-dependencies.json"
sync_scope "$kit_root/skills" "$kit_root/config/global-skills.txt" "$kit_root/config/global-excludes.txt" "$public_deps"
if [[ $include_obsidian -eq 1 ]]; then
  sync_scope "$kit_root/skills" "$kit_root/config/obsidian-skills.txt" "$kit_root/config/global-excludes.txt" "$public_deps"
fi
if [[ $include_private -eq 1 ]]; then
  private_deps="$kit_root/private/skill-dependencies.json"
  if [[ ! -f "$private_deps" ]]; then
    private_deps="$public_deps"
  fi
  sync_scope "$kit_root/private/skills" "$kit_root/private/global-skills.txt" "$kit_root/private/global-excludes.txt" "$private_deps"
fi
