---
name: document-to-implementation-workflow
description: Use when implementation should proceed from approved planning/spec/design documents and an implementation plan, with atomic task completion, verification, and per-task commits.
---

# Document To Implementation Workflow

## 목적

확정된 기획/설계/구현계획 문서를 기준으로 실제 코드를 구현한다.

프로젝트가 쓰는 문서명이 다르면 그 이름을 따른다. `architect.md`, `design.md`, `plan.md`는 예시다.

## 적용 상황

- “플랜대로 구현”
- “구현계획 기준으로 이어서”
- “접수된 태스크 처리”
- “마저 하던 태스크 진행”

## 작업 순서

1. 구현계획 문서에서 미완료 태스크를 확인한다.
2. 현재 태스크와 관련된 기획/설계 문서 부분만 읽는다.
3. 관련 코드 파일을 찾는다.
4. 좁은 범위로 구현한다.
5. 필요한 테스트 또는 정적 검증을 돌린다.
6. 구현계획 문서의 체크 상태를 갱신한다.
7. 외부 노트/칸반 동기화가 요구된 경우 반영한다.
8. 태스크 단위로 커밋한다.

## 태스크 완료 기준

태스크는 다음 조건을 만족해야 완료다.

- 요구사항이 코드에 반영됨
- 정적 검증 통과
- 관련 문서/plan 상태가 맞음
- 사용자 변경을 되돌리지 않음
- 커밋 완료

## 금지

- 문서와 충돌하는 구현을 임의로 진행하지 않는다.
- 보류된 범위를 몰래 구현하지 않는다.
- 전체 리팩토링으로 번지지 않는다.
- 사용자가 브라우저 테스트를 하지 말라고 했는데 Playwright/browser를 돌리지 않는다.
- 사용자가 특정 파일, 문서, 테스트를 제외하면 그 범위를 지킨다.

## 완료 보고

```md
태스크 완료했습니다.

반영:
- ...

검증:
- ...

커밋:
- ...
```
