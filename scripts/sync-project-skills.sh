#!/usr/bin/env bash
set -euo pipefail

# Project skill sync: source is always Claude Code project skills.
PROJECT_ROOT="${1:-$(pwd)}"
if [[ "${PROJECT_ROOT:-}" == "--help" || "${PROJECT_ROOT:-}" == "-h" ]]; then
  cat <<USAGE
Usage: $(basename "$0") [PROJECT_ROOT] [--mirror] [--dry-run]

Sync project-local skills from Claude source to Codex project skills and .agent skills.
Claude source: <PROJECT_ROOT>/.claude/skills

Options:
  --mirror   Make destinations exactly match source (uses rsync --delete)
  --dry-run  Show what would change without writing
  -h, --help Show this help
USAGE
  exit 0
fi

shift || true

MIRROR=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mirror) MIRROR=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      cat <<USAGE
Usage: $(basename "$0") [PROJECT_ROOT] [--mirror] [--dry-run]
USAGE
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
  shift
done

SRC="$PROJECT_ROOT/.claude/skills"
CODEX_DST="$PROJECT_ROOT/.codex/skills"
AGENT_DST="$PROJECT_ROOT/.agent/skills"

if [[ ! -d "$SRC" ]]; then
  echo "Source directory not found: $SRC" >&2
  exit 1
fi

RSYNC_FLAGS=( -a --checksum --human-readable )
if [[ $MIRROR -eq 1 ]]; then
  RSYNC_FLAGS+=( --delete )
fi
if [[ $DRY_RUN -eq 1 ]]; then
  RSYNC_FLAGS+=( --dry-run --itemize-changes )
fi

sync_one() {
  local dst="$1"
  if [[ $DRY_RUN -eq 1 && ! -d "$dst" ]]; then
    echo "[dry-run] create $dst"
    return
  fi
  mkdir -p "$dst"
  echo "Sync: $SRC/ -> $dst/"
  rsync "${RSYNC_FLAGS[@]}" "$SRC/" "$dst/"
}

sync_one "$CODEX_DST"
sync_one "$AGENT_DST"

echo "Done."
