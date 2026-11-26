#!/usr/bin/env python3
"""등록된 Austin Skills 원본의 poteto-mode를 한 프로젝트에 동기화한다."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


def hashes(folder):
    if any(p.is_symlink() for p in folder.rglob('*')):
        raise ValueError('스킬 안의 심볼릭 링크는 동기화하지 않습니다.')
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file() and p.relative_to(folder).as_posix() != 'manifest.json'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    registry_root = source.parent.parent
    registry = registry_root / 'config/skills.json'
    if not registry.is_file() or 'poteto-mode' not in json.loads(registry.read_text()).get('project', []):
        parser.error('config/skills.json의 project에 poteto-mode를 먼저 등록해주세요.')
    if not args.project.is_absolute() or not (args.project / 'AGENTS.md').is_file():
        parser.error('AGENTS.md가 있는 프로젝트의 절대 경로를 지정해주세요.')
    manifest = json.loads((source / 'manifest.json').read_text())
    expected = manifest['files']
    if hashes(source) != expected:
        parser.error('원본 파일이 manifest.json과 다릅니다. 검증 후 파일 해시를 갱신해주세요.')
    target = args.project / '.agents/skills/poteto-mode'
    if target.is_symlink():
        parser.error('기존 poteto-mode가 심볼릭 링크여서 변경하지 않았습니다.')
    if target.exists():
        old_manifest = target / 'manifest.json'
        if not old_manifest.is_file():
            parser.error('기존 poteto-mode가 이 설치의 적용본인지 확인할 수 없습니다.')
        previous = json.loads(old_manifest.read_text())['files']
        if hashes(target) != previous:
            parser.error('기존 적용본에 직접 수정된 파일이 있어 덮어쓰지 않았습니다.')
    print(f'프로젝트 동기화: {source} -> {target}')
    if args.dry_run:
        return 0
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    for path in sorted(target.rglob('*'), reverse=True):
        if path.is_file() and path.relative_to(target).as_posix() != 'manifest.json' and str(path.relative_to(target)) not in expected:
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    if hashes(target) != expected:
        raise RuntimeError('프로젝트 적용본의 파일 해시가 원본과 다릅니다.')

    note = args.project / '.agents/PSTACK.md'
    marker = '<!-- pstack-herdr -->'
    if note.is_file():
        text = note.read_text()
        if marker not in text:
            update = (f'\n{marker}\n'
                      '> 2026-11-03 KST 추가: `poteto-mode`는 Herdr 연결 규칙과 원본 pstack 58개 스킬을 '
                      '포함하는 프로젝트 전용 묶음으로 설치했다. 사용은 '
                      '[진입점](skills/poteto-mode/SKILL.md)을 따른다. 아래 8개 스킬 설명은 '
                      '2026-10-23 개별 설치 이력이며 그대로 보존한다.\n\n')
            head, sep, tail = text.partition('\n')
            note.write_text(head + sep + update + tail)
    print('설치 확인: poteto-mode 원본·프로젝트 적용본 일치, 기존 개별 스킬 보존')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(f'동기화 실패: {error}', file=sys.stderr)
        raise SystemExit(1)
