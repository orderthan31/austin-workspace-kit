---
name: frontend-feedback-fix-workflow
description: Use when the user gives concrete frontend UI feedback after seeing a screen and wants targeted fixes to layout, interaction, visual density, copy, or displayed data without broad refactors.
---

# Frontend Feedback Fix Workflow

## 목적

사용자가 실제 화면을 보고 준 피드백을 작은 수정 단위로 안정적으로 반영한다.

이 스킬은 특정 프로젝트 전용이 아니다. React, Vue, Svelte, HTML/CSS 기반 화면 등 대부분의 프론트엔드 작업에서 적용할 수 있다.

## 트리거

- “버튼이 안 보인다”
- “스크롤이 안 된다”
- “드롭다운이 뒤에 묻힌다”
- “폰트/패딩/너비를 줄여라”
- “이 정보는 빼라”
- “이 값은 API에 없으니 만들지 마라”
- “브라우저 테스트는 내가 할게”
- “방금 피드백 반영해”
- “화면 기준으로 수정해”

## 핵심 원칙

1. 사용자가 부르는 화면 용어를 먼저 고정한다.
2. 같은 단어가 코드에 없을 수 있으므로 UI 구조, 텍스트, class, component 이름을 같이 추적한다.
3. 피드백 하나를 여러 문제로 쪼개고, 영향 범위를 좁힌다.
4. 값이 안 보이는 문제와 값이 없는 문제를 구분한다.
5. 레이아웃 수정은 부모/자식 overflow, height, width, flex/grid 제약을 함께 확인한다.
6. API에 없는 표시값은 임의로 만들지 않는다.
7. 사용자가 브라우저 테스트를 직접 하겠다고 하면 자동 브라우저 검증을 하지 않는다.

## 작업 순서

### 1. 피드백 해석

사용자 피드백을 다음 형태로 정리한다.

| 항목 | 확인할 내용 |
|---|---|
| 화면 위치 | 어느 화면, 모달, 패널, 탭, 영역인지 |
| 증상 | 안 보임, 잘림, 겹침, 스크롤 불가, 값 불일치, 문구 오류 등 |
| 기대 동작 | 사용자가 원하는 최종 상태 |
| 데이터 출처 | API 응답, mock, store, props, 계산값 중 무엇인지 |
| 검증 방식 | lint/typecheck/unit test/browser test 중 무엇을 할지 |

피드백이 모호하면 바로 구현하지 말고 짧게 재정리해서 사용자에게 확인한다.

### 2. 코드 위치 찾기

우선순위:

1. 화면에 보이는 텍스트로 검색한다.
2. 컴포넌트명, 라우트명, 파일명으로 검색한다.
3. className, test id, icon, 버튼 문구로 검색한다.
4. 상태값이나 selector/store hook을 따라간다.
5. API/service/mock 데이터를 확인한다.

권장 명령:

```sh
rg -n "화면에 보이는 문구|버튼명|컬럼명" src
rg -n "컴포넌트명|route|service|mock" src
```

### 3. 수정 범위 결정

다음 중 어디를 고쳐야 하는지 분리한다.

| 유형 | 주 수정 위치 |
|---|---|
| 문구 오류 | label, i18n, formatter |
| 값 오류 | mapper, selector, service response, mock data |
| 표시하면 안 되는 값 | display schema, field filter, render 조건 |
| 스크롤 문제 | container height, min-height, overflow, flex child 제약 |
| 가로 잘림 | grid column, table width, min-width, font size, padding |
| 드롭다운 묻힘 | portal, z-index, overflow clipping, position context |
| 클릭/닫기 오류 | event handler, controlled state, modal lifecycle |
| 반응형 문제 | breakpoint, container query, wrap rule |

수정은 사용자가 지적한 범위를 넘기지 않는다. 관련 없는 리팩터링은 다음 태스크로 분리한다.

### 4. 데이터 표시 원칙

- 백엔드/API가 주지 않는 가공 표시값은 임의로 추가하지 않는다.
- 사용자가 볼 필요가 없는 내부 id, index, join key는 숨긴다.
- docId, orderNo, receiptNo처럼 사용자가 식별해야 하는 값은 화면 맥락에 맞게 그대로 쓴다.
- enum, code 값은 프로젝트의 기존 formatter/dictionary를 먼저 찾는다.
- mock 데이터는 실제 응답 interface와 맞춘다.

### 5. 레이아웃 수정 원칙

- “컴팩트”는 값을 빼는 뜻이 아니다. 필요한 값은 유지하고 밀도를 높인다.
- 패딩, gap, font size, row height를 줄일 때 읽을 수 있는 최소선을 지킨다.
- 스크롤이 필요한 영역은 독립적으로 스크롤되게 한다.
- flex/grid 자식에는 필요하면 `min-width: 0`, `min-height: 0`을 명시한다.
- table은 컬럼 너비, ellipsis, wrap 여부를 같이 조정한다.
- overlay/dropdown은 부모 overflow에 잘리지 않는지 확인한다.

### 6. 검증

프로젝트 관례를 따른다.

예시:

```sh
npx eslint {수정 파일}
npm run typecheck
npm test -- {관련 테스트}
```

브라우저 검증은 다음 기준으로 처리한다.

- 사용자가 직접 보겠다고 했으면 수행하지 않는다.
- 사용자가 요청했거나 로컬 화면 검증이 필수면 브라우저 도구로 확인한다.
- 브라우저를 열 수 없으면 어떤 검증을 못 했는지 명확히 보고한다.

### 7. 커밋

사용자가 작업 단위 커밋을 요구한 경우, 피드백 묶음이 끝날 때마다 커밋한다.

커밋 메시지는 프로젝트 언어와 관례를 따른다.

예시:

```sh
git add {수정 파일}
git commit -m "수정: 화면 피드백 반영"
```

## 완료 보고

완료 보고에는 다음만 간단히 담는다.

- 반영한 화면 피드백
- 주요 수정 파일
- 실행한 검증
- 하지 못한 검증이 있으면 그 이유
- 커밋 해시
