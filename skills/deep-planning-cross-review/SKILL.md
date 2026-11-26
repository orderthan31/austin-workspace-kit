---
name: deep-planning-cross-review
description: '기존 deep-planning 흐름 위에 교차 리뷰 단계를 얹어, 현재 플래닝을 수행하는 엔진을 제외한 다른 엔진들(Claude Code, OpenCode, Gemini CLI)에게 초안 계획을 검토받고 수용 여부를 판단해 최종 계획을 구체화하는 스킬. 트리거: "플랜 교차 리뷰", "다른 모델들에게 계획 검토", "자기 자신 제외 리뷰", "cross review planning"'
---

# deep-planning 교차 리뷰

이 스킬은 기존 [deep-planning]($AUSTIN_WORKSPACE_KIT_ROOT/skills/deep-planning/SKILL.md)을 대체하지 않는다.
대신 초안 `plan.md`가 있을 때, 현재 플래닝 실행 주체를 제외한 다른 CLI 에이전트들에게 리뷰를 요청하고
그 결과를 한곳에 모아 최종 계획 구체화에 쓰도록 돕는다.

## 1. 목표

기존 `deep-planning`의 강점은 유지한다.

- 프로젝트 분석
- 작업 명세 정제
- `plan.md` 작성
- task context pack 구성

여기에 아래 단계를 추가한다.

- 초안 계획 작성
- 실행 주체 식별
- 자기 자신 제외 리뷰어 선정
- 외부 모델 리뷰 요청
- 피드백 수용 여부 판단
- 최종 계획 구체화

핵심 원칙:

- 계획 작성자는 리뷰어가 아니다.
- 리뷰어는 초안을 통째로 다시 쓰지 말고 비평만 한다.
- 최종 결정권은 실행 중인 planner에게 있다.
- 리뷰를 받았다는 사실보다, 어떤 피드백을 왜 받거나 거절했는지가 더 중요하다.

## 2. 실행 주체와 리뷰 대상 규칙

이 스킬은 Claude Code, OpenCode, Gemini CLI 중 누가 실행하더라도 동일한 구조로 동작해야 한다.

실행 주체별 리뷰 매트릭스:

| 플래닝 실행 주체 | 제외 대상 | 리뷰 요청 대상 |
|---|---|---|
| Claude Code | Claude Code | OpenCode, Gemini CLI |
| OpenCode | OpenCode | Claude Code, Gemini CLI |
| Gemini CLI | Gemini CLI | Claude Code, OpenCode |

기본 규칙:

1. 현재 플래닝을 실제로 수행 중인 에이전트를 `planner`로 본다.
2. `planner` 자신에게는 리뷰를 요청하지 않는다.
3. 가능한 경우 나머지 2개 엔진 모두에게 리뷰를 요청한다.
4. 하나만 사용 가능한 환경이면, 사용 가능한 나머지 1개에게만 리뷰를 요청한다.
5. 아무 리뷰어도 사용할 수 없으면, 리뷰 단계는 생략하되 그 사실을 `plan.md`에 남긴다.

## 3. planner identity 판별 규칙

스킬 본문에는 아래처럼 "현재 내가 누구인지 먼저 판별하라"는 규칙이 들어가야 한다.

판별 순서:

1. 현재 세션/도구가 Claude Code인지 확인
2. 아니면 OpenCode인지 확인
3. 아니면 Gemini CLI인지 확인
4. 명확하지 않으면 사용자에게 묻기 전에 현재 실행 컨텍스트, 사용 가능한 CLI, 기존 동기화 위치를 근거로 가장 보수적으로 추정

표현 예시:

```text
현재 플래닝 실행 주체를 먼저 식별한다.
식별 결과를 planner identity로 기록한다.
planner identity와 같은 엔진은 리뷰 대상에서 제외한다.
```

권장 기록 필드:

- `planner_identity: claude-code | opencode | gemini-cli`
- `reviewers_selected: [...]`
- `reviewers_skipped: [...]`
- `review_skipped_reason: ...`

## 4. 실행 방법

실제 CLI 호출은 이 옵시디언 프로젝트의 `scripts/`에 둔다.
동기화된 스킬이 다른 환경에서 실행되더라도, 아래 스크립트는 항상 옵시디언 원본 경로를 바라보게 한다.

- 메인 실행기:
  - `$OBSIDIAN_ROOT/scripts/deep-planning-cross-review.sh`
- 리뷰어별 래퍼:
  - `$OBSIDIAN_ROOT/scripts/review-plan-with-claude.sh`
  - `$OBSIDIAN_ROOT/scripts/review-plan-with-opencode.sh`
  - `$OBSIDIAN_ROOT/scripts/review-plan-with-gemini.sh`

중요 규칙:

- 스크립트 파일은 옵시디언 프로젝트에 있다.
- 하지만 리뷰 실행 `cwd`는 항상 현재 planner가 보고 있는 프로젝트 루트여야 한다.
- 즉 스크립트 경로와 작업 대상 프로젝트 경로는 분리해서 다룬다.

기본 실행 예시:

```bash
OBSIDIAN_ROOT="${OBSIDIAN_ROOT:?볼트 경로를 지정하세요}"
PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"

bash "$OBSIDIAN_ROOT/scripts/deep-planning-cross-review.sh" \
  --project-root "$PROJECT_ROOT" \
  --plan-file "$PROJECT_ROOT/plan.md" \
  --planner claude-code
```

중요:

- `--planner`는 항상 명시한다.
- 자동 판별은 보조 수단일 뿐이고, 애매하면 스크립트가 실패하도록 둔다.
- 특히 OpenCode에서 실행할 때는 `--planner opencode`를 꼭 준다.

리뷰 결과 산출물은 기본적으로 현재 프로젝트 아래 `.cross-review/<timestamp>/`에 저장한다.

## 5. 권장 워크플로

기존 `deep-planning` 절차를 유지하면서, 초안 완성 직후 교차 리뷰 단계를 넣는다.

### 4.1 초안 작성

먼저 기존 방식대로 진행한다.

- 사용자 요청 정제
- 프로젝트 구조 스캔
- 영향 범위 파악
- 작업 분해
- 리스크 정리
- 검증 계획 수립
- 초안 `plan.md` 작성

이 단계에서는 아직 최종본으로 확정하지 않는다.

### 4.2 리뷰 요청 준비

초안에서 리뷰어가 읽어야 할 최소 정보만 추린다.

- 목표
- 범위
- 주요 단계
- 리스크
- 검증 계획
- 열려 있는 가정

리뷰어에게는 다음 원칙을 준다.

- 계획을 새로 쓰지 말 것
- 누락, 순서 문제, 리스크, 검증 부족만 지적할 것
- 중요도 순으로 정리할 것
- 유지해야 할 장점도 알려줄 것

### 4.3 자기 자신 제외 리뷰 실행

`planner_identity`에 따라 리뷰어를 자동 선택한다.

예시:

- Claude Code가 실행 중이면 OpenCode와 Gemini CLI에 보낸다.
- OpenCode가 실행 중이면 Claude Code와 Gemini CLI에 보낸다.
- Gemini CLI가 실행 중이면 Claude Code와 OpenCode에 보낸다.

리뷰 요청은 가능하면 병렬로 보내되, 둘 다 실패해도 플래닝 전체가 중단되지는 않게 한다.

### 4.4 리뷰 수집 및 정규화

리뷰 결과를 자유서술 그대로 두지 말고 항목화한다.

각 피드백을 아래 형태로 정리한다.

```text
- id:
- source:
- severity: critical | important | optional
- category: missing-step | ordering | risk | validation | scope | clarity
- feedback:
- suggested_change:
```

여러 리뷰어가 비슷한 지적을 하면 중복 항목으로 두지 말고 묶는다.

### 4.5 수용 여부 판단

planner가 각 피드백마다 아래 셋 중 하나를 결정한다.

- `accept`
- `partial`
- `reject`

판단 기준:

- 실제 요구사항과 더 잘 맞는가
- 범위를 불필요하게 키우지 않는가
- 실행 순서를 더 안전하게 만드는가
- 검증 가능성을 높이는가
- 이미 초안에 반영된 내용의 중복은 아닌가

각 결정에는 한 줄 이유를 남긴다.

### 4.6 최종 계획 구체화

수용된 피드백만 반영해 `plan.md`를 더 구체화한다.

최종본에는 최소한 아래가 남아야 한다.

- 최종 실행 단계
- 선행 조건
- 단계별 산출물
- 검증 방법
- 주요 리스크와 대응
- 외부 리뷰 반영 결과

## 6. 리뷰 프롬프트 초안

아래 프롬프트는 어느 리뷰어에게 보내도 큰 틀은 같게 유지하는 것이 좋다.

```text
You are reviewing an implementation plan.

Do not rewrite the whole plan.
Do not produce a replacement roadmap.
Critique the draft.

Focus on:
1. missing steps
2. bad sequencing
3. hidden risks
4. weak validation
5. scope confusion
6. places that are too vague to execute

Return:
- Critical issues
- Important improvements
- Optional suggestions
- Things that should remain unchanged
```

한국어 버전으로 고정해도 되지만, 외부 CLI 모델마다 영어 프롬프트 안정성이 더 좋다면 영어 템플릿을 기본으로 두는 편이 안전하다.

## 7. `plan.md`에 추가할 수 있는 임시 섹션

기존 템플릿을 크게 깨지 않고 아래 섹션만 덧붙일 수 있다.

```markdown
## 8.5) 외부 리뷰 반영 결과
- planner identity:
- 요청한 리뷰어:
- 응답한 리뷰어:
- 리뷰 실패/생략:

### Feedback R1
- source:
- category:
- decision: accept | partial | reject
- reason:
- applied change:

### Feedback R2
- source:
- category:
- decision: accept | partial | reject
- reason:
- applied change:
```

## 8. 스킬 문구로 바꿀 때의 핵심 포인트

기존 `deep-planning`에 나중에 섞게 된다면 아래 원칙을 유지한다.

- 기존 목적은 유지한다.
- "계획 초안 작성"과 "최종 계획 확정" 사이에 `교차 리뷰` 단계를 추가한다.
- 실행 주체 식별 규칙을 명시한다.
- 자기 자신 제외 규칙을 명시한다.
- 리뷰는 비평 중심으로 제한한다.
- 수용 여부 판단 기록을 남기게 한다.
- 스킬 본문은 실행기를 설명하고, 실제 CLI 차이는 `scripts/`에서 처리한다.

## 9. 권장 문장 초안

실제 스킬 본문에 넣기 쉬운 문장만 따로 적어 두면 아래와 같다.

```text
초안 plan.md를 작성한 뒤, 현재 플래닝을 수행 중인 엔진을 planner identity로 기록한다.
planner identity와 같은 엔진은 리뷰 대상에서 제외한다.
가능하면 나머지 엔진 모두에게 초안 계획 리뷰를 요청한다.
리뷰어에게는 전체 재작성 대신 누락, 순서, 리스크, 검증 부족을 비평하게 한다.
수집된 피드백은 항목별로 정규화한 뒤, 각 항목에 대해 accept, partial, reject 중 하나를 결정한다.
최종 plan.md에는 외부 리뷰 반영 결과와 결정 이유를 함께 남긴다.
```

## 10. 장점과 주의점

장점:

- 특정 모델 하나의 시각에 갇히지 않는다.
- 계획 품질을 올리면서도 최종 책임은 planner에게 남긴다.
- Claude/OpenCode/Gemini 어느 쪽에서 시작해도 같은 규칙으로 움직인다.

주의점:

- 모든 환경에서 모든 CLI가 항상 사용 가능하진 않다.
- 리뷰어에게 계획 재작성을 허용하면 결과가 흔들린다.
- 리뷰 항목 정규화 없이 자유서술만 쌓이면 오히려 plan이 지저분해진다.
- 응답 실패를 예외가 아니라 정상 시나리오로 다뤄야 한다.

## 11. 현재 구현 상태

현재는 파이프라인 메모를 따로 두지 않고 아래 한 덩어리로 구현한다.

1. 스킬 문서: 이 파일
2. 실행기: `scripts/deep-planning-cross-review.sh`
3. 리뷰어별 CLI 래퍼: `scripts/review-plan-with-*.sh`

즉 `pipeline`과 `review`를 스킬 파일 두 개로 쪼개지 않는다.
