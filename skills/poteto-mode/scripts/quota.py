#!/usr/bin/env python3
"""각 CLI의 기본 계정 한도를 조회하고 단일 위임에 쓸 모델을 선택한다."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os
from pathlib import Path
import re
import select
import subprocess
from time import monotonic
from zoneinfo import ZoneInfo


PROVIDERS = ('claude', 'antigravity', 'codex')
MODEL_CONFIG = Path(__file__).resolve().parents[1] / 'config/model-routes.json'


def load_model_routes():
    try:
        config = json.loads(MODEL_CONFIG.read_text(encoding='utf-8'))
        quota_groups = config['antigravity_quota_groups']
        routes = {}
        for role, entries in config['routes'].items():
            route = []
            for entry in entries:
                provider, model = entry['provider'], entry['model']
                if provider not in PROVIDERS:
                    raise ValueError(f'{role}에 지원하지 않는 실행 도구가 있습니다. {provider}')
                uses_default = provider == 'codex' and model is None
                if not uses_default and (not isinstance(model, str) or not model.strip()):
                    raise ValueError(f'{role}의 {provider} 모델 이름을 확인해주세요.')
                if provider == 'antigravity' and not quota_groups.get(model):
                    raise ValueError(f'{model}의 안티그래비티 할당량 그룹이 없습니다.')
                route.append((provider, model))
            if not route:
                raise ValueError(f'{role}에 실행 후보가 없습니다.')
            routes[role] = tuple(route)
        if not {'investigate', 'implement'} <= routes.keys():
            raise ValueError('investigate와 implement의 실행 후보가 모두 필요합니다.')
    except (AttributeError, OSError, KeyError, TypeError, ValueError) as error:
        raise SystemExit(f'모델 폴백 설정을 읽을 수 없습니다. {MODEL_CONFIG} ({error})') from error
    return routes, quota_groups


ROUTES, ANTIGRAVITY_QUOTA_GROUPS = load_model_routes()
KST = ZoneInfo('Asia/Seoul')
ANSI = re.compile(r'\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|$)|[78])')


def claude_quota(cwd):
    # Claude Code의 내장 /usage는 대화형 화면을 사용한다. 새 조회용 터미널에서만 입력한다.
    probe = r'''
set timeout 6
spawn -noecho claude --strict-mcp-config --settings {{"disableAllHooks":true,"tui":"default"}}
stty rows 60 columns 130 < $spawn_out(slave,name)
expect {
    -re {❯} {send -- "/usage"; after 240; send -- "\r"}
    timeout {exit 2}
    eof {exit 2}
}
expect {
    -re {%.*used} {expect -timeout 1 {eof {} timeout {}}}
    timeout {exit 2}
    eof {exit 2}
}
'''
    result = subprocess.run(['expect', '-c', probe], cwd=cwd, capture_output=True, text=True, timeout=15, check=True)
    return parse_claude(result.stdout)


def parse_claude(output):
    output = ANSI.sub('', output)
    # 화면 갱신 방식에 따라 단어 사이 공백이 터미널 제어 문자로 표시된다.
    lines = [re.sub(r'\s+', '', line).lower() for line in output.splitlines() if line.strip()]
    windows = {}
    for title, meter in zip(lines, lines[1:]):
        match = re.fullmatch(r'[\u2580-\u259f]*(\d{1,3})%used', meter)
        if not match or int(match[1]) > 100:
            continue
        # 화면이 일부 글자를 그대로 둘 때 Currnt session처럼 갱신된 글자만 기록된다.
        title = re.sub(r'^curre?n?t?(?=se|week\()', 'current', title)
        if title.startswith('currentse'):
            title = 'currentsession'
        if title in {'currentsession', '5-hourlimit'} or title.startswith(('currentweek(', 'weeklylimit(')):
            windows[title] = 100 - int(match[1])
    return windows


def antigravity_quota(cwd):
    # 이 조회는 CLI에서 처리하며 모델로 프롬프트를 보내지 않는다.
    result = subprocess.run(
        ['agy', '--dangerously-skip-permissions', '--print', '/usage'],
        cwd=cwd, capture_output=True, text=True, timeout=12, check=True,
    )
    return parse_antigravity(result.stdout)


def parse_antigravity(output):
    windows = {}
    for line in output.splitlines():
        columns = line.split('\t')
        if len(columns) < 3:
            continue
        group, limit, percent = columns[:3]
        match = re.fullmatch(r'(\d{1,3})%', percent.strip())
        if 'limit' in limit.lower() and match and int(match[1]) <= 100:
            windows.setdefault(group.strip(), {})[limit.strip()] = int(match[1])
    return windows


def codex_quota(cwd):
    requests = [
        {'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'pstack-quota', 'version': '1.0'}}},
        {'method': 'initialized'},
        {'id': 2, 'method': 'account/rateLimits/read', 'params': {'excludeResetCreditDetails': True}},
    ]
    with subprocess.Popen(
        ['codex', 'app-server', '--listen', 'stdio://'],
        cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    ) as server:
        try:
            server.stdin.write(('\n'.join(map(json.dumps, requests)) + '\n').encode())
            server.stdin.flush()
            deadline = monotonic() + 8
            pending = b''
            while (seconds := deadline - monotonic()) > 0 and select.select([server.stdout], [], [], seconds)[0]:
                chunk = os.read(server.stdout.fileno(), 65536)
                if not chunk:
                    break
                pending += chunk
                while b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    response = json.loads(line)
                    if response.get('id') == 2:
                        return parse_codex(response.get('result') or {})
            return {}
        finally:
            server.terminate()
            try:
                server.wait(timeout=2)
            except subprocess.TimeoutExpired:
                server.kill()


def parse_codex(result):
    limits = result.get('rateLimits') or {}
    windows = {}
    for key in ('primary', 'secondary'):
        window = limits.get(key) or {}
        used = window.get('usedPercent')
        if isinstance(used, int) and 0 <= used <= 100:
            minutes = window.get('windowDurationMins')
            label = f'{minutes}분' if minutes else key
            windows[label] = 100 - used
    return {
        'windows': windows,
        'ordinary_usage_allowed': result.get('ordinaryUsageAllowed'),
        'spend_control_reached': limits.get('spendControlReached') is True,
    }


def probe_quota(probe, cwd):
    try:
        return probe(cwd)
    except (OSError, ValueError, subprocess.SubprocessError):
        return {}


def snapshot(cwd=None):
    with ThreadPoolExecutor(max_workers=3) as pool:
        checks = pool.map(probe_quota, (claude_quota, antigravity_quota, codex_quota), (cwd,) * 3)
        usage = dict(zip(PROVIDERS, checks))
    return {'checked_at': datetime.now(KST).isoformat(timespec='seconds'), **usage}


def quota_state(provider, model, usage):
    if provider == 'codex':
        if usage.get('spend_control_reached') or usage.get('ordinary_usage_allowed') is False:
            return '소진'
        if usage.get('ordinary_usage_allowed') is True:
            return '여유'
        remaining = list(usage.get('windows', {}).values())
    elif provider == 'claude':
        family = model.split('[')[0]
        remaining = [
            percent for label, percent in usage.items()
            if '(' not in label or 'allmodels' in label or family in label
        ]
        if 0 not in remaining and not (
            {'currentsession', '5-hourlimit'} & usage.keys()
            and {'currentweek(allmodels)', 'weeklylimit(allmodels)'} & usage.keys()
        ):
            return '확인 필요'
    else:
        family = ANTIGRAVITY_QUOTA_GROUPS[model]
        remaining = [
            percent for group in ('Gemini Models', family)
            for percent in usage.get(group, {}).values()
        ]
    if 0 in remaining:
        return '소진'
    return '여유' if remaining else '확인 필요'


def candidates(role, quotas):
    return [
        (provider, model, quota_state(provider, model, quotas.get(provider, {})))
        for provider, model in ROUTES[role]
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    quotas = snapshot()
    print(json.dumps(quotas, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
