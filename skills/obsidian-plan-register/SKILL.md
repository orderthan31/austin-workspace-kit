---
name: obsidian-plan-register
description: '프로젝트 루트 plan.md를 Obsidian agents-plan에 스냅샷 등록해 링크 가능한 plan 앵커를 먼저 만들고, 프로젝트 카드/일간 로그가 참조할 활성 plan 경로를 고정하는 스킬. 등록 경로는 `MM-DD/{한 줄 요약}.md` 형식이며, 같은 폴더에 같은 이름이 있으면 `(2)`처럼 뒤에 번호가 붙는다. 트리거: "플랜 등록", "플랜 앵커 만들기", "구현 전에 플랜 백업", "agents-plan 등록", "plan register"'
---

## 0. 공통 실행 원칙

- 이 스킬은 `obsidian-cli-guideline` 기준을 따른다.
- `PROJECT_ROOT`는 코드 프로젝트 루트다. `OBSIDIAN_ROOT`는 사용자가 지정한 볼트 루트다.
- `plan.md`는 `PROJECT_ROOT` 기준으로 읽고, `agents-plan/...` 등록본과 스크립트는 `OBSIDIAN_ROOT` 기준으로 다룬다.
- 구현 전에 먼저 실행해, daily와 project 카드가 참조할 안정적인 plan 링크를 확보한다.
- 이 스킬은 `plan reset`이 아니다. 원본 `plan.md`는 유지하고, Obsidian 쪽에 등록본만 만든다.
- 최초 등록 뒤에는 원본 `plan.md` 안에 숨은 앵커 주석을 남겨, 이후 같은 플랜의 reset이 기존 등록본을 갱신할 수 있게 한다.
- 같은 프로젝트에서 같은 날 여러 플랜이 생겨도 daily를 지저분하게 만들지 않도록, 대표 활성 플랜 1개만 노출하는 운영을 전제로 한다.
- `deep-planning`의 `## 플랜 처리 결정`이 `현재 플랜 확장`이면 기존 등록본을 계속 쓴다.
- `## 플랜 처리 결정`이 `기존 플랜 백업 후 새 플랜 시작`일 때만 새 등록본을 만든다.

## 1. 목표

프로젝트 루트의 `plan.md`를 Obsidian `agents-plan`에 먼저 등록해 링크 가능한 plan 앵커를 만든다.

- 원본 파일: `<PROJECT_ROOT>/plan.md`
- 등록 파일: `$OBSIDIAN_ROOT/agents-plan/MM-DD/<한 줄 요약>.md`
- 핵심 결과:
  - 구현 전에 참조 가능한 안정 링크 확보
  - 프로젝트 카드의 `현재 활성 plan` 링크 갱신 근거 확보
  - daily 로그에서 `관련 플랜`을 비우지 않게 함
  - 같은 날 여러 플랜 생성 시 `현재 활성 plan`과 `최근 대체된 plan`을 구분할 근거 확보

쉽게 말하면:

- `deep-planning`이 plan을 만들고
- `obsidian-plan-register`가 그 plan에 Obsidian 링크를 붙여주고
- `implement-from-plan`과 `obsidian-daily-ops`는 그 링크를 참조한다.

## 2. 사용 스크립트

- `$OBSIDIAN_ROOT/scripts/obsidian-plan-register.sh`

## 2.1 입력 계약

- 필수:
  - 현재 작업 디렉터리 또는 `project_root`
- 선택:
  - `OBSIDIAN_ROOT`는 설정에서 확인할 수 없을 때 지정한다.
  - `project_note`
  - `daily_note`

여기서 뜻은 아래와 같다.

- 현재 작업 디렉터리 또는 `project_root` -> 코드 프로젝트 루트
- `OBSIDIAN_ROOT` -> 옵시디언 볼트 루트

## 2.2 출력 계약

- 생성 파일:
  - `$OBSIDIAN_ROOT/agents-plan/MM-DD/<한 줄 요약>.md`
- 수정 가능 파일:
  - `projects/<project>.md` 의 `현재 활성 plan` 섹션
  - `daily/YYYY-MM-DD.md` 의 `관련 플랜` 참조
- 출력 메세지:
  - snapshot 경로
  - source plan 경로

## 3. 기본 실행

현재 디렉터리를 프로젝트 루트로 보고 실행:

```bash
OBSIDIAN_ROOT="${OBSIDIAN_ROOT:?볼트 경로를 지정하세요}"
bash "$OBSIDIAN_ROOT/scripts/obsidian-plan-register.sh"
```

프로젝트 루트를 명시해서 실행:

```bash
OBSIDIAN_ROOT="${OBSIDIAN_ROOT:?볼트 경로를 지정하세요}"
bash "$OBSIDIAN_ROOT/scripts/obsidian-plan-register.sh" "/path/to/project"
```

주의:

- 다른 프로젝트 디렉터리 안에서 실행해도 `scripts/...` 상대경로로 부르지 않는다.
- 항상 `"$OBSIDIAN_ROOT/scripts/obsidian-plan-register.sh"`처럼 옵시디언 루트 기준 절대 경로로 호출한다.

## 4. 표준 절차

1. `<PROJECT_ROOT>/plan.md`가 있는지 확인한다.
2. `## 플랜 처리 결정`이 `현재 플랜 확장`인지 `기존 플랜 백업 후 새 플랜 시작`인지 먼저 확인한다.
3. `현재 플랜 확장`이면 기존 등록 앵커를 유지하고 그 plan을 계속 쓴다.
4. `기존 플랜 백업 후 새 플랜 시작`이면 `agents-plan/MM-DD/` 폴더 아래에 `<한 줄 요약>.md` 형식 등록 파일을 만든다.
5. 파일명은 plan 안의 `## 한 줄 요약` 값을 1순위로 사용한다.
6. `한 줄 요약`이 없을 때만 짧은 정제 목표나 첫 의미 있는 제목을 fallback으로 사용한다.
7. 같은 파일명이 이미 있으면 시간 대신 `(2)`, `(3)`처럼 뒤에 번호를 붙여 충돌을 피한다.
8. 원본 `plan.md`에는 숨은 앵커 주석을 기록해, 같은 플랜 사이클의 reset이 기존 등록본을 갱신할 수 있게 한다.
9. 가능하면 관련 프로젝트 카드의 `플랜 관리` 섹션을 아래 기준으로 갱신한다.
   - `현재 활성 plan`: 새 등록본
   - `최근 대체된 plan`: 직전 active plan
   - `오늘 생성된 plan`: 같은 날 생성된 plan 목록
10. 이후 `implement-from-plan`과 `obsidian-daily-ops`는 이 등록본 링크를 우선 사용한다.

## 4.1 파일명 규칙

- 좋은 예:
  - `03-19/total-medication-days-정확도-개선.md`
  - `03-19/다회사-처리-리팩토링.md`
  - `03-19/테스트-누락-사례-조사.md`
- 나쁜 예:
  - 사용자 원문 전체를 그대로 넣은 긴 문장
  - "너가 제시한 방안으로 플래닝 부터" 같은 대화체
  - 설명이 너무 길어 파일 탐색기에서 잘리는 이름

## 5. 운영 규칙

### 5.1 언제 쓰는가

- `deep-planning` 직후
- 구현 시작 직전
- daily에 작업 로그를 남기기 전

### 5.2 언제 안 쓰는가

- plan을 종료하고 초기화할 때
  - 이때는 `obsidian-plan-reset`을 사용한다.

### 5.2.1 같은 날 여러 플랜이 생기면

1. 가장 마지막에 등록된 플랜을 기본 `active`로 본다.
2. 이전 플랜은 `superseded` 또는 `최근 대체된 plan`으로 본다.
3. daily에는 active 플랜 1개만 남긴다.
4. 상세 이력은 프로젝트 카드의 `플랜 관리`에서 다룬다.

### 5.3 관련 스킬 순서

정상 흐름:

1. `deep-planning`
2. `obsidian-plan-register`
3. `implement-from-plan`
4. `obsidian-daily-ops`
5. 필요 시 `obsidian-context-ingest`
6. 사이클 종료 시 `obsidian-plan-reset`

## 6. 링크 규칙

- daily의 `관련 플랜`은 가능하면 루트 `plan.md`가 아니라 등록된 `agents-plan` 링크를 우선한다.
- 프로젝트 카드의 `현재 활성 plan`도 등록된 `agents-plan` 링크를 우선한다.
- 원본 `plan.md`는 작업 파일이고, `agents-plan` 등록본은 기록 앵커다.
- 같은 플랜 사이클에서는 `plan-reset`이 새 파일을 만들기보다 이 등록본을 최종 상태로 갱신하는 것을 기본 동작으로 본다.
- 같은 날 여러 등록본이 있으면 daily에는 마지막 active 플랜만 노출한다.

## 7. 실패 시 처리

- `plan.md`가 없으면 새로 만들지 말고 실패로 보고한다.
- 등록 파일 생성이 실패하면 구현 단계로 넘어가지 않는 편이 안전하다.
- 프로젝트 문서/일간 노트 갱신은 선택 사항이므로, 등록 성공 후 링크 갱신이 실패하면 등록본 경로만 우선 보고한다.

## 8. 출력 예시

```text
Registered plan: $OBSIDIAN_ROOT/agents-plan/03-17/목록-필드-동기화.md
Source plan: /path/to/project/plan.md
```
