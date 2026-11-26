---
name: obsidian-housekeeping-ops
description: '프롬프트 history/review 아카이브, 금일 daily 생성, 금요일 weekly 생성/갱신을 한 번에 다루는 Obsidian 운영 스킬. 트리거: "housekeeping", "vault housekeeping", "금일 일지 생성", "오늘 일지 만들어", "금요일 주간보고", "프롬프트 히스토리 아카이브", "review 끝난 history 정리"'
---

## 0. 공통 실행 원칙

- 이 스킬은 `obsidian-cli-guideline` 기준을 따른다.
- 이 스킬이 읽고 쓰는 `daily/...`, `weekly/...`, `prompt/...`, `archive/...` 는 모두 `OBSIDIAN_ROOT` 기준이다.
- 현재 코드 프로젝트 `cwd`가 어디든 vault 내부 경로를 현재 프로젝트 상대경로로 해석하지 않는다.
- 이 스킬은 새 문서를 "의미 없이 빈 파일로 만드는 것"보다, 필요한 링크와 최소 구조까지 같이 맞추는 것을 목표로 한다.
- 이미 있는 전용 스킬은 다시 설명하지 말고 조합해서 쓴다.
  - daily 생성/정리: `obsidian-daily-ops`
  - weekly 생성/갱신: `obsidian-report-ops`
  - 오래된 daily/weekly archive: `obsidian-archive-ops`
- `prompt/history`는 raw layer, `prompt/review`는 indexed layer에 가깝다. review가 끝난 raw history는 메인 폴더에 오래 쌓아두지 않는다.

## 1. 이 스킬이 하는 일

이 스킬은 아래 3가지를 한 번에 관리한다.

1. 오늘 날짜의 daily가 없으면 만든다.
2. 오늘이 금요일이면 이번 주 weekly를 만들거나 갱신한다.
3. review가 끝난 오래된 `prompt/history`와 대응 `prompt/review`를 archive로 이동한다.

쉽게 말하면:

- 아침에는 daily 준비
- 금요일에는 weekly까지 닫기
- 오래된 prompt 원문은 뒤로 치우기

를 한 번에 처리하는 운영 스킬이다.

## 1.1 운영 루틴

이 스킬은 기본적으로 아래 3가지 루틴을 지원한다.

### 업무 시작 루틴

- 오늘 날짜의 daily가 있는지 확인한다.
- 없으면 생성한다.
- 있으면 `이번 주` 링크와 기본 섹션 구조만 점검한다.

### 업무 마감 루틴

- 오늘 daily를 기준으로 금일 요약이 비어 있지 않은지 확인한다.
- 오래된 `prompt/history` / `prompt/review` 중 archive 조건을 만족하는 파일을 정리한다.

### 금요일 마감 루틴

- 업무 마감 루틴을 먼저 수행한다.
- 이번 주 weekly를 만들거나 갱신한다.
- prompt review가 끝난 history를 archive 한다.

쉽게 말하면:

- 시작할 때는 "오늘 일지 준비"
- 평일 마감 때는 "오늘 요약 + 오래된 파일 정리"
- 금요일 마감 때는 "오늘 요약 + 주간보고 + 프롬프트 정리"

순서로 본다.

## 2. 대상 경로

- daily:
  - `$OBSIDIAN_ROOT/daily/`
- weekly:
  - `$OBSIDIAN_ROOT/weekly/`
- prompt history:
  - `$OBSIDIAN_ROOT/prompt/history/`
- prompt review:
  - `$OBSIDIAN_ROOT/prompt/review/`
- archive:
  - `$OBSIDIAN_ROOT/archive/prompt/history/YYYY/MM/`
  - `$OBSIDIAN_ROOT/archive/prompt/review/YYYY/MM/`

## 3. 핵심 규칙

### 3.1 금일 daily 생성

- 오늘 날짜 파일 `daily/YYYY-MM-DD.md` 가 없으면 `daily/_template.md` 기준으로 생성한다.
- 만들 때 최소한 아래는 같이 맞춘다.
  - 제목 날짜
  - `이번 주` 링크
  - 기본 섹션 구조
- 이미 파일이 있으면 새로 덮어쓰지 말고 링크/빈 섹션만 보강한다.

### 3.2 금요일 weekly 생성/갱신

- 오늘이 로컬 시간 기준 금요일이면 이번 주 `weekly/YYYY-Www.md` 를 확인한다.
- 파일이 없으면 `weekly/_template.md` 기준으로 만든다.
- 파일이 있더라도 빈 껍데기면 그대로 두지 말고 갱신한다.
- weekly는 "생성만" 하지 말고, 그 주의 실제 daily를 읽어 아래를 채우는 것을 기본으로 본다.
  - `## 참조한 일간보고`
  - `## 이번 주 한눈에 보기`
  - `## 프로젝트별 진행 요약`
- weekly 요약층에는 `T1`, `Phase 2` 같은 내부 관리 번호를 올리지 않는다.

### 3.3 prompt history/review 아카이브

- 아카이브 대상은 날짜형 파일만 본다.
  - 예: `prompt/history/2026-03-17.md`
  - 예: `prompt/review/2026-03-17.md`, `prompt/review/2026-03-03_04.md`
- 아래 파일은 archive 대상이 아니다.
  - `prompt/history/history.md`
  - `prompt/review/review.md`
  - 숨김 상태 파일(`.codex_*`, `.space/*` 등)
- `prompt/history/YYYY-MM-DD.md` 는 아래 조건을 모두 만족할 때 archive 후보로 본다.
  1. 같은 날짜로 시작하는 review 파일이 `prompt/review/` 에 1개 이상 있다.
     - 예: history가 `2026-03-03.md` 면 review는 `2026-03-03.md`, `2026-03-03_04.md`, `2026-03-03_10.md` 모두 매칭
  2. 오늘 기준 7일 이상 지났다.
  3. 이번 주 파일은 아니다.
- archive 할 때는 해당 history 파일과 같은 날짜 prefix를 가진 review 파일들을 같이 옮긴다.
- 이동은 삭제가 아니라 archive 폴더로 이동이다.

## 4. 표준 절차

### 4.1 기본 루틴

1. 오늘 날짜와 이번 주 ID를 계산한다.
2. 오늘 daily가 있는지 본다.
3. 없으면 daily를 생성하고, 있으면 링크/기본 섹션만 보강한다.
4. 오늘이 금요일이면 이번 주 weekly를 만들거나 갱신한다.
5. `prompt/history` 의 날짜 파일들을 보고, review가 끝난 오래된 파일을 찾는다.
6. 대응하는 `prompt/review` 파일과 함께 archive로 이동한다.
7. 결과를 짧게 요약한다.

### 4.1.1 업무 시작 루틴

1. 오늘 날짜의 `daily/YYYY-MM-DD.md` 존재 여부를 확인한다.
2. 없으면 생성한다.
3. 있으면 `이번 주` 링크와 기본 섹션이 있는지만 본다.
4. 이 루틴에서는 weekly나 prompt archive를 강제로 수행하지 않는다.

### 4.1.2 업무 마감 루틴

1. 오늘 daily가 없으면 먼저 생성한다.
2. 오늘 daily의 `오늘 한일 Summary` 가 너무 비어 있지 않은지 확인한다.
3. review 완료 + 7일 경과 + 이번 주 아님 조건을 만족하는 `prompt/history` 를 찾는다.
4. 대응하는 `prompt/review` 와 함께 archive로 이동한다.
5. 오늘이 금요일이 아니면 여기서 종료한다.

### 4.1.3 금요일 마감 루틴

1. 업무 마감 루틴을 먼저 수행한다.
2. 이번 주 weekly를 만들거나 갱신한다.
3. 그 주 daily를 근거로 `한눈에 보기`, `참조한 일간보고`, `프로젝트별 진행 요약` 을 채운다.
4. 금요일 마감에서는 prompt review/history archive를 생략하지 않는다.

### 4.2 daily 생성 방식

- 기본 템플릿:
  - `$OBSIDIAN_ROOT/daily/_template.md`
- 생성 후 최소 확인:
  - 제목 날짜가 오늘과 일치하는가
  - `이번 주` 링크가 현재 week를 가리키는가
  - `연결 노트`, `오늘 할일`, `오늘 한일 Summary`, `Details` 섹션이 있는가

### 4.3 weekly 생성/갱신 방식

- 기본 템플릿:
  - `$OBSIDIAN_ROOT/weekly/_template.md`
- 생성/갱신 시:
  - 이번 주 daily 실제 파일만 `참조한 일간보고` 에 넣는다.
  - 상단 `한눈에 보기` 는 결과/진행/블로커 중심으로 쓴다.
  - 프로젝트명은 저장소명이 아니라 프로젝트 노트명 기준으로 정규화한다.

### 4.4 prompt archive 방식

- archive 대상 history의 날짜에서 `YYYY`, `MM` 을 읽는다.
- 이동 경로:
  - history -> `archive/prompt/history/YYYY/MM/`
  - review -> `archive/prompt/review/YYYY/MM/`
- review는 같은 날짜 prefix를 가진 파일을 전부 같이 이동한다.
- 이미 archive에 같은 파일이 있으면 덮어쓰기 전에 충돌 여부를 먼저 본다.

## 5. 판단 기준

- daily가 이미 잘 있으면 굳이 다시 만들지 않는다.
- 오늘이 금요일이 아니면 weekly는 자동 생성하지 않는다.
- review가 없으면 history를 archive 하지 않는다.
- 날짜는 오래됐어도 이번 주 문맥에 아직 직접 쓰는 review/history면 자동 이동보다 사용자 확인을 우선한다.

## 6. 출력 형식

- 생성/갱신한 daily 경로
- 생성/갱신한 weekly 경로
- archive로 이동한 prompt history/review 파일 목록
- 이번 실행에서 건너뛴 것과 이유

권장 실행 모드 이름:

- `업무 시작 루틴`
- `업무 마감 루틴`
- `금요일 마감 루틴`

## 7. 빠른 실행 예시

### 예시 1. 아침 루틴

- 오늘 daily가 없으면 생성
- 금요일이 아니면 weekly는 건너뜀
- review 끝난 오래된 prompt만 archive

### 예시 2. 금요일 마감 루틴

- 오늘 daily 확인/생성
- 이번 주 weekly 생성 또는 갱신
- review 끝난 prompt history/review archive
