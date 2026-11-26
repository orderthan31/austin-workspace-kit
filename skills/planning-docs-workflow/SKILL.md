---
name: planning-docs-workflow
description: Use when a feature must be planned through separate product/spec, screen/design, and implementation-plan documents, especially when requirements evolve through multiple feedback rounds and the user wants the documents kept consistent.
---

# Planning Docs Workflow

## 목적

기능을 바로 구현하지 않고 문서를 역할별로 나눠 정리한다.

프로젝트가 이미 쓰는 파일명이 있으면 그 이름을 따른다. 아래 이름은 기본 예시다.

| 문서 | 역할 |
|---|---|
| `architect.md` | 기능정의서. 업무 목적, 용어, 플로우, 데이터/API 방향, 판단 룰을 정의한다. |
| `design.md` | 화면기획서. 화면 구조, 영역, 버튼, 상태 UI, 문구, 인터랙션을 정의한다. |
| `plan.md` | 구현계획서. atomic task, 의존성, 완료 기준, 검증 방법을 정의한다. |

## 트리거

- “기획안 작성”
- “화면기획서 작성”
- “구현계획서 작성”
- “architect/design/plan 갱신”
- “PRD/디자인/구현계획 갱신”
- “보강사항 반영”
- “외부 공유용으로 정리”
- “취소선 없애고 현행 문서로 정리”

## 기본 순서

1. 사용자 요구사항을 정리한다.
2. 사용자가 승인하면 기능정의 문서를 먼저 갱신한다.
3. 화면 영향이 있으면 화면기획 문서를 갱신한다.
4. 구현 영향이 있으면 구현계획 문서를 갱신한다.
5. Obsidian, Notion, Google Docs, Markdown board 등 외부 동기화가 요구되면 대상 문서를 맞춘다.
6. 문서 변경을 커밋한다.

## 문서별 작성 기준

### 기능정의 문서

포함할 것:

- 기능 목적
- 진입점
- 핵심 용어
- 사용자 플로우
- 데이터 구조
- API/service 방향
- 자동화 원칙
- 완료 조건
- 제외 범위
- 추후 확장

포함하지 않을 것:

- CSS 수준의 화면 배치
- 구현 태스크 목록
- 과거 보강 이력

### 화면기획 문서

포함할 것:

- 화면 구조
- 영역 정의
- 버튼 문구
- 표시 정보
- 상태 UI
- 드로어/모달/이미지 보기
- 빈 상태와 오류 상태
- 사용자가 볼 문구

포함하지 않을 것:

- API 계약 상세
- 코드 수정 파일 목록
- 구현 순서

### 구현계획 문서

포함할 것:

- atomic task
- task id
- 의존성
- 주요 파일
- 제외 범위
- 완료 기준
- 검증 방법

포함하지 않을 것:

- 긴 기능 설명
- 화면 문구 원본 정의
- 히스토리성 보강 본문

## 보강 처리 규칙

사용자가 “기존 내용은 지우지 말고 취소선 처리”라고 하면 기존 문장을 취소선으로 남기고 하단에 보강 섹션을 추가한다.

사용자가 “외부 공유용”, “진짜 문서처럼”, “취소선 삭제”라고 하면 취소선, 보강 날짜, 폐기 태스크, 내부 작업 로그를 모두 제거하고 현행 기준만 남긴다.

사용자가 특정 문서만 수정하라고 하면 다른 문서는 건드리지 않는다.

프로젝트가 `architect.md`, `design.md`, `plan.md`가 아닌 파일명을 쓰면 그 이름을 그대로 사용한다.

## 완료 전 검증

- `rg -n "~~|보강|폐기|히스토리|위 본문|충돌하는 경우" {공유용 문서}`
- `git diff --check`
- 외부 문서 동기화 시 가능한 방식으로 동일성 확인

## 완료 보고

간단히 보고한다.

```md
완료했습니다.

반영:
- architect.md: ...
- design.md: ...
- plan.md: ...
- Obsidian 동기화: ...

검증:
- ...

커밋:
- ...
```
