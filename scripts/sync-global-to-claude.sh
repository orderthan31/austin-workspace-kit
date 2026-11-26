#!/usr/bin/env bash
set -euo pipefail

kit_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="${SRC:-$kit_root/skills}"
destination="${DST:-$HOME/.claude/skills}"
registry="${GLOBAL_SKILLS_FILE:-$kit_root/config/global-skills.txt}"
exclusions="${EXCLUDE_FILE:-$kit_root/config/global-excludes.txt}"
dry_run=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    -h|--help)
      echo "사용법: $0 [--dry-run]"
      echo "환경 변수: SRC, DST, GLOBAL_SKILLS_FILE, EXCLUDE_FILE, SKILL_DEPENDENCIES_FILE"
      exit 0
      ;;
    *) echo "알 수 없는 옵션입니다. $arg" >&2; exit 2 ;;
  esac
done

selected="$(python3 "$kit_root/scripts/resolve-skill-dependencies.py" "$registry" "$source_dir")"
excluded="|"
if [[ -f "$exclusions" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    name="$(printf '%s' "${line%%#*}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [[ -n "$name" ]] || continue
    excluded+="$name|"
  done < "$exclusions"
fi

validate_frontmatter() {
  local src_file="$1"
  local expected_name="$2"

  python3 - "$src_file" "$expected_name" <<'PY'
import sys
from pathlib import Path

import yaml

path = Path(sys.argv[1])
expected_name = sys.argv[2]
text = path.read_text()

if not text.startswith("---\n"):
    print(f"[ERROR] {path}: frontmatter 시작 구분자(---)가 없습니다.", file=sys.stderr)
    sys.exit(1)

parts = text.split("\n---\n", 1)
if len(parts) != 2:
    print(f"[ERROR] {path}: frontmatter 종료 구분자(---)가 없습니다.", file=sys.stderr)
    sys.exit(1)

frontmatter = parts[0][4:]

try:
    data = yaml.safe_load(frontmatter)
except yaml.YAMLError as exc:
    print(f"[ERROR] {path}: frontmatter YAML 파싱 실패: {exc}", file=sys.stderr)
    print("[HINT] description에 콜론(:)이 들어가면 전체 값을 따옴표로 감싸세요.", file=sys.stderr)
    sys.exit(1)

if not isinstance(data, dict):
    print(f"[ERROR] {path}: frontmatter는 YAML 객체여야 합니다.", file=sys.stderr)
    sys.exit(1)

for required_key in ("name", "description"):
    if required_key not in data:
        print(f"[ERROR] {path}: frontmatter 필수 키 '{required_key}'가 없습니다.", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data[required_key], str) or not data[required_key].strip():
        print(f"[ERROR] {path}: frontmatter '{required_key}'는 비어 있지 않은 문자열이어야 합니다.", file=sys.stderr)
        sys.exit(1)

if data["name"] != expected_name:
    print(
        f"[ERROR] {path}: frontmatter name({data['name']})과 폴더명({expected_name})이 다릅니다.",
        file=sys.stderr,
    )
    sys.exit(1)
PY
}

while IFS= read -r name; do
  [[ -n "$name" ]] || continue
  if [[ "$excluded" == *"|$name|"* ]]; then
    echo "설치할 스킬이 제외 목록에 있습니다. $name" >&2
    exit 1
  fi
  validate_frontmatter "$source_dir/$name/SKILL.md" "$name"
done <<< "$selected"

while IFS= read -r name; do
  [[ -n "$name" ]] || continue
  from="$source_dir/$name"
  to="$destination/$name"
  if [[ -L "$to" ]]; then
    echo "심볼릭 링크 보존 $to"
    continue
  fi
  if [[ -d "$to" ]] && diff -qr "$from" "$to" >/dev/null; then
    echo "동일 $to"
  elif [[ $dry_run -eq 1 ]]; then
    echo "설치 예정 $to"
  else
    mkdir -p "$to"
    rsync -a --delete "$from/" "$to/"
    echo "설치 $to"
  fi
done <<< "$selected"
