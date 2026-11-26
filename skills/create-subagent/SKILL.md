---
name: create-subagent
description: '프로젝트 agents/*.md 기준 커스텀 subagent를 설계/생성/검증하는 스킬. 트리거: "subagent 만들어", "서브에이전트 생성", "custom agent", "agents frontmatter", "claude /agents"'
---

## 1. 목표

 Claude Code 스타일의 커스텀 subagent 문서를 안전하게 만든다.

- 기본 생성 위치(이 저장소 규칙): 프로젝트 범위 `agents/`
- Claude 기본 위치(참고): 프로젝트 `.claude/agents/` 또는 사용자 `~/.claude/agents/`
- 파일 형식: YAML frontmatter + Markdown 본문(system prompt)
- 최소 필수: `name`, `description`

## 2. 가장 쉬운 이해 (진짜 핵심만)

subagent 파일은 "설정 + 지시문" 2덩어리다.

1. 위쪽 `--- ... ---` = 설정값(frontmatter)
2. 아래쪽 본문 = 이 에이전트의 역할 설명(system prompt)

즉, "에이전트 명함 + 행동 매뉴얼"이다.

## 3. 생성 절차 (고정 루틴)

1. 에이전트 목적을 1문장으로 쓴다.
2. 범위를 정한다.
   - 이 저장소 기본: `agents/<agent-name>.md`
   - Claude 기본(참고): `.claude/agents/<agent-name>.md` 또는 `~/.claude/agents/<agent-name>.md`
3. frontmatter를 작성한다.
   - 필수: `name`, `description`
   - 권장: `tools`, `model`, `permissionMode`, `skills`, `memory`
4. 본문(system prompt)에 "해야 할 일/하지 말아야 할 일/출력 형식"을 적는다.
5. `/agents`에서 로드 확인 후 짧은 테스트 프롬프트로 검증한다.

## 4. 필드 선택 규칙 (헷갈리지 않게)

- `name`: 소문자 + 하이픈
  - 예: `report-orchestrator`
- `description`: Claude가 "언제" 이 에이전트에 위임해야 하는지 명확히 작성
- `tools`: 필요한 것만 허용 (최소권한)
- `model`:
  - 빠른 분류/탐색 중심: `haiku`
  - 균형형: `sonnet`
  - 기본값 유지: `inherit`
- `permissionMode`:
  - 기본은 `default`
  - 읽기전용 조사형은 `plan` 고려
  - `bypassPermissions`는 정말 필요할 때만
- `skills`: 이 에이전트 시작 시 미리 주입할 skill 목록
- `memory`: 반복 학습이 필요하면 `user`를 기본 추천

## 5. 기본 템플릿 (복붙용)

```markdown
---
name: my-agent
description: "특정 작업을 수행하는 커스텀 subagent"
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: default
skills:
  - my-skill-a
  - my-skill-b
memory: user
---

너는 <역할> 전용 subagent다.

반드시 할 일:
1) 입력 목표 재확인
2) 필요한 파일만 탐색
3) 근거 기반으로 결과 작성

금지:
- 근거 없는 추측
- 불필요한 대규모 수정

출력 형식:
- 요약 3줄
- 변경/분석 근거 목록
- 다음 액션 1~3개
```

## 6. 보고서/일정 오케스트레이터 템플릿 (당신 상황용)

```markdown
---
name: report-orchestrator
description: "일간/주간/월간 보고와 plan 백업/초기화 작업을 조건에 맞게 라우팅하는 서브에이전트"
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: default
skills:
  - obsidian-daily-ops
  - obsidian-report-ops
  - obsidian-plan-reset
memory: project
---

너는 보고서/일정 작업 총괄자다.

규칙:
1) 오늘 날짜 기준으로 필요한 작업만 선택한다.
2) daily -> weekly -> monthly 순서 의존성을 지킨다.
3) plan 관련 작업은 백업 완료를 확인한 뒤에만 초기화한다.
4) 이미 처리된 파일이 있으면 중복 실행하지 않는다.
5) 가능하면 daily/weekly/monthly/plan 문서 사이 위키링크를 남긴다.

출력:
- 오늘 실행한 작업
- 건너뛴 작업(이유 포함)
- 생성/수정 파일 경로
- 실패 시 재시도 방법
```

## 7. 테스트 프롬프트 (바로 실행)

- `Use the report-orchestrator agent and run today's reporting pipeline safely.`
- `Use my-agent to inspect this repo and return only actionable findings.`

## 8. 실패 줄이는 체크리스트

- [ ] `name`이 소문자-하이픈 규칙을 지켰는가?
- [ ] `description`에 "언제 위임할지"가 적혀 있는가?
- [ ] `description` 전체를 따옴표로 감쌌는가?
- [ ] `description` 안에 `트리거:` 같은 `콜론 + 공백`이 있으면 YAML이 깨지지 않는가?
- [ ] `tools`를 최소로 제한했는가?
- [ ] 본문에 금지사항과 출력 형식이 있는가?
- [ ] `/agents`에서 실제로 보이는가?

## 9. 공식 문서 기준 핵심 사실

- subagent는 Markdown 파일이며 frontmatter + 본문으로 구성된다.
- 필수 필드는 `name`, `description`이다.
- `tools`, `model`, `permissionMode`, `skills`, `memory` 등으로 동작을 제어한다.
- 범위는 `.claude/agents/`(프로젝트) 또는 `~/.claude/agents/`(사용자)로 나뉜다.
