#!/usr/bin/env python3
"""pstack의 작업 요청을 Herdr의 대화형 실행 담당에게 전달한다."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

# 프로젝트 동기화 대상으로 파이썬 캐시 파일이 들어가지 않도록 한다.
sys.dont_write_bytecode = True
from quota import ANTIGRAVITY_QUOTA_GROUPS, PROVIDERS, ROUTES, candidates, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--agent', choices=PROVIDERS)
    target.add_argument('--role', choices=ROUTES, help='할당량에 따라 조사 또는 구현 담당을 선택')
    parser.add_argument('--quota', type=Path, help='quota.py로 이번 작업에서 조회한 할당량 JSON')
    parser.add_argument(
        '--skip',
        choices=(*PROVIDERS, *ANTIGRAVITY_QUOTA_GROUPS),
        action='append',
        default=[],
        help='한도 오류가 확인된 실행 도구 또는 안티그래비티 모델을 이번 위임에서 제외',
    )
    parser.add_argument('--name', required=True)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--brief', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--parent', help='현재 터미널임을 확인한 hc 주소')
    parser.add_argument('--model', help='사용 가능 여부를 확인한 실제 모델 이름')
    parser.add_argument('--effort', choices=['low', 'medium', 'high', 'xhigh', 'max'])
    parser.add_argument('--read-only', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if not re.fullmatch(r'[a-z0-9_-]{1,32}', args.name):
        parser.error('이름은 영문 소문자·숫자·-·_ 1~32자로 적어주세요.')
    for label, path in [('작업 폴더', args.cwd), ('요청 파일', args.brief), ('보고 파일', args.report)]:
        if not path.is_absolute():
            parser.error(f'{label}은 절대 경로여야 합니다.')
    if not args.cwd.is_dir() or not args.brief.is_file():
        parser.error('작업 폴더와 요청 파일이 실제로 있어야 합니다.')
    if args.report.exists() or args.report.is_symlink():
        parser.error('오래된 결과와 혼동하지 않도록 새 보고 파일 경로를 정해주세요.')
    if not args.report.parent.is_dir():
        parser.error('보고 파일을 둘 폴더를 먼저 준비해주세요.')
    if args.role and (args.model or args.effort):
        parser.error('--model과 --effort를 직접 설정하려면 --agent를 사용해주세요.')
    if not args.role and (args.quota or args.skip):
        parser.error('--quota와 --skip은 --role과 함께 사용해주세요.')
    if args.agent == 'codex' and args.effort:
        parser.error('Codex의 추론 수준은 현재 세션 설정을 유지합니다. --effort를 빼주세요.')

    skill = Path(__file__).resolve().parents[1]
    mode = skill / 'vendor/pstack/skills/poteto-mode/SKILL.md'
    adapter = skill / 'references/herdr.md'
    if not mode.is_file() or not adapter.is_file():
        parser.error('함께 설치할 pstack 원본 또는 Herdr 연결 규칙이 없습니다.')

    agent, model = args.agent, args.model
    route = None
    if args.role:
        try:
            quotas = json.loads(args.quota.read_text()) if args.quota else snapshot(args.cwd)
            if not isinstance(quotas, dict) or not isinstance(quotas.get('checked_at'), str):
                raise ValueError('조회 시각이 없습니다.')
            options = candidates(args.role, quotas)
        except (OSError, ValueError, TypeError, AttributeError) as error:
            parser.error(f'할당량 JSON을 읽을 수 없습니다. {error}')
        eligible = [
            (provider, candidate_model, state)
            for provider, candidate_model, state in options
            if provider not in args.skip and candidate_model not in args.skip and state != '소진'
        ]
        if not eligible:
            parser.error(f'실행 가능한 후보가 없습니다. 후보 상태 {options}, 이번 작업에서 제외 {args.skip}')
        agent, model, state = eligible[0]
        route = {'agent': agent, 'model': model, 'quota_state': state, 'checked_at': quotas['checked_at']}
        print(f'위임 담당 {agent} / {model or "기본 모델"} / 할당량 {state}', file=sys.stderr)

    scope = ('프로젝트는 읽기 전용입니다. 지정한 보고 파일 외에는 파일·설정·Git·DB를 변경하지 마세요.'
             if args.read_only else '요청 파일에 명시된 담당 범위에서만 변경하고 다른 담당자의 변경을 보존하세요.')
    notify = (f'완료·차단 시 hc send {args.parent} 명령으로 보고 파일 경로와 결론을 전달하세요.'
              if args.parent else '완료·차단 시 마지막 응답에 보고 파일의 절대 경로와 결론을 적으세요.')
    prompt = f'''총괄에게 위임받은 실행 담당입니다. 한국어로 쉽게 답하고 시각은 KST로 기록하세요.
작업 폴더의 AGENTS.md와 연결된 작업 규칙을 먼저 읽으세요.
Herdr 연결 규칙 {adapter}와 원본 작업 방식 {mode}를 읽으세요.
별도 에이전트 지시 파일이 요청에 있으면 함께 읽으세요.
당신은 아래 범위만 맡습니다. 전체 작업 절차를 다시 실행하거나 추가 에이전트·패널을 만들지 마세요.
{scope}
권한 거절·신뢰 화면을 우회하거나 승인 상태를 바꾸지 마세요.
보고 파일 {args.report}에 확인한 사실·실행 근거·미확인 사항을 구분해 기록하세요.
실제 사용 모델을 확인할 수 있으면 출처와 함께 적고, 모르면 기본 모델·계열 미확인이라고 적으세요.
{notify}

요청 파일 {args.brief}의 내용입니다.
{args.brief.read_text(encoding='utf-8')}
'''

    binary = {'claude': 'claude', 'antigravity': 'agy', 'codex': 'codex'}[agent]
    program = [binary]
    if agent == 'codex':
        program.append('--no-daemon')
    if model:
        program.extend(['--model', model])
    if args.effort:
        program.extend(['--effort', args.effort])
    if agent == 'antigravity':
        program.extend(['--dangerously-skip-permissions', '--prompt-interactive'])
    program.append(prompt)
    command = ['hc', 'run', '--json', '--bg', '--name', args.name, '--cwd', str(args.cwd)]
    command.extend(['--parent', args.parent] if args.parent else ['--no-parent'])
    command.extend(program)

    if args.dry_run:
        preview = {'hc_argv': command, 'program_argv': program}
        if route:
            preview['route'] = route
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0
    if not shutil.which('hc') or not shutil.which(binary):
        parser.error(f'hc와 {binary} 실행 파일을 확인해주세요.')
    if args.parent:
        result = subprocess.run(['hc', 'get', '--json', args.parent], capture_output=True, text=True)
        if result.returncode:
            sys.stderr.write(result.stderr or result.stdout)
            return result.returncode
    return subprocess.run(command).returncode


if __name__ == '__main__':
    raise SystemExit(main())
