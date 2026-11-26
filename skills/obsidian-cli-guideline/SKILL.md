---
name: obsidian-cli-guideline
description: '에이전트가 Obsidian을 다룰 때 어떤 방법을 우선 써야 하는지 정리한 공통 가이드 스킬. 트리거: "obsidian cli", "옵시디언 cli", "Obsidian guideline", "obsidian://", "Advanced URI", "커맨드 팔레트"'
---

## 1. 목표

에이전트 기준으로 Obsidian 작업을 할 때 헷갈리지 않게 "무엇을 어떤 순서로 써야 하는지" 고정 기준을 준다.

추가로 이 가이드는 "에이전트가 한 일을 옵시디언에 어떻게 남길지"에 대한 공통 운영 헌장도 함께 제공한다.

가장 중요한 생각:

1. 노트 내용 수정은 에이전트가 파일을 직접 편집한다.
2. Obsidian 앱 열기/포커스/특정 노트 이동은 `obsidian://` URI 또는 Obsidian 명령으로 처리한다.
3. 복잡한 반복 작업은 이 저장소의 `$OBSIDIAN_ROOT/scripts/`를 호출한다.
4. 공식 동작 원칙이 필요하면 `obsidian-official-usage`를 함께 따른다.

즉, "내용 수정"과 "앱 조작"을 분리해서 생각하면 쉽다.

## 1.1 공통 운영 헌장

이 부분은 모든 `obsidian-*` 스킬과, Obsidian을 건드리는 상위 작업 스킬이 같이 따라야 하는 최상위 규칙이다.

핵심 원칙 3개:

1. 에이전트가 수행한 모든 의미 있는 작업은 `daily`에 기록한다.
2. 작업의 상태 변화는 `issue` 또는 `project` 카드에도 반영한다.
3. `plan`은 왜 이 작업을 했는지 보여주는 기준 문서로 연결한다.

쉽게 말하면:

- daily = 오늘 실제로 무슨 일이 있었는지 남기는 원장
- issue = 이슈 상태가 어떻게 바뀌었는지 남기는 보드
- project = 지금 프로젝트 상태가 어떤지 남기는 요약 카드
- plan = 이번 작업의 이유와 기준을 보여주는 실행 문서

여기서 "의미 있는 작업"은 아래를 모두 포함한다.

- 코드 수정
- 버그 조사
- 로그 분석
- 플래닝
- 구현
- 검증
- 실패
- 차단
- 이슈 triage
- 수동 확인 결과 정리

즉, "코드를 바꿨을 때만 기록"이 아니라 "에이전트가 판단과 행동을 했으면 기록"이 기본이다.

## 1.2 공통 완료 루프

어떤 스킬이든 작업을 끝낼 때 아래 순서로 생각한다.

1. 이번 작업을 `daily`에 남겼는가?
2. 이슈 상태가 바뀌었으면 `issue` 보드에 반영했는가?
3. 프로젝트의 현재 상태/결정/리스크가 바뀌었으면 `project` 카드에 반영했는가?
4. 관련 `plan`이 있으면 `daily`와 `project`에서 링크할 수 있게 연결했는가?

기본 원칙:

- `daily` 기록은 기본값이다.
- `issue` / `project` 반영은 상태 변화가 있을 때 추가한다.
- 애매하면 `daily`에는 남기고, `project` 승격은 신중하게 판단한다.

## 2. 제일 쉬운 규칙

### 2.1 무엇으로 할지 먼저 고르기

- 노트 내용을 읽고 수정해야 한다 -> 저장소 파일을 직접 읽고 편집
- Obsidian 화면에서 특정 노트를 열어야 한다 -> `obsidian://open...`
- 오늘 일간노트를 열어야 한다 -> `obsidian://daily?...` 또는 `Periodic Notes: Open daily note`
- 플러그인 명령을 실행해야 한다 -> Command Palette 또는 QuickAdd
- 프로젝트 전용 자동화가 이미 있다 -> `$OBSIDIAN_ROOT/scripts/*.sh`

### 2.2 우선순위

1. 파일 직접 편집
2. Obsidian URI
3. Command Palette / QuickAdd / Periodic Notes
4. 저장소 스크립트

앱 화면을 굳이 조작할 이유가 없으면 1번이 제일 단순하고 안정적이다.

## 3. 에이전트 기준 표준 운영 방식

### 3.0 경로 기준

이 부분이 제일 중요하다.

- `OBSIDIAN_ROOT`: 이 옵시디언 볼트 루트다. 사용자가 지정한 볼트 경로를 사용한다.
- `PROJECT_ROOT`: 지금 코드 작업 중인 프로젝트 루트다. 예: `/path/to/project`
- vault 상대경로: `daily/2026-03-30.md` 같은 경로다. 항상 `OBSIDIAN_ROOT` 기준이다.

헷갈리지 않게 아래처럼 고정해서 생각한다.

1. 코드 분석/테스트/`plan.md`는 `PROJECT_ROOT` 기준이다.
2. 옵시디언 노트 읽기/수정/스크립트 호출은 `OBSIDIAN_ROOT` 기준이다.
3. 다른 프로젝트 디렉터리 안에서 실행 중이어도 `daily/...`, `issue/...`, `projects/...` 는 현재 프로젝트 상대경로가 아니라 vault 상대경로다.
4. 쉘에서 옵시디언 스크립트를 부를 때는 `scripts/...` 상대경로 대신 `"$OBSIDIAN_ROOT/scripts/..."` 절대 기준으로 호출한다.

### 3.0 시간대 기준

- Obsidian 노트에 쓰는 날짜/시간은 기본적으로 항상 `Asia/Seoul`, 즉 KST 기준으로 적는다.
- 특히 `daily`, `weekly`, `monthly`, `plan.md`, `agents-plan`, `Details (Agent Log)`, `구현 로그`는 모두 KST를 기준으로 해석한다.
- 에이전트 실행 환경이나 외부 도구가 UTC/미국 시간으로 시간을 주더라도, 노트에 적기 전에 KST로 변환해서 쓴다.
- `오늘`, `어제`, `방금`, `현재` 같은 상대 표현도 KST 날짜 기준으로 판단한다.
- 시간이 중요한 로그라면 가능하면 `KST`를 같이 적어 오해를 막는다.

### 3.1 노트 수정

- 대상 파일 경로를 찾는다.
- markdown 파일을 직접 편집한다.
- 템플릿이 필요하면 `templates/` 기준으로 만든다.
- 여기서 `daily/...`, `weekly/...`, `projects/...`, `issue/...`, `templates/...` 는 모두 vault 상대경로다.

예:

- 일간 로그 추가 -> `daily/YYYY-MM-DD.md` 수정
- 주간 보고 생성 -> `weekly/YYYY-[W]WW.md` 생성/수정
- 월간 보고 생성 -> `monthly/YYYY-MM.md` 생성/수정

### 3.2 Obsidian 앱에서 열기

맥 기준으로는 보통 아래처럼 생각하면 된다.

```bash
open "obsidian://open?vault=obsidian&file=daily%2F2026-03-13"
```

- `vault=`: 볼트 이름
- `file=`: 볼트 내부 상대 경로
- `/` 는 `%2F`, 공백은 `%20` 으로 인코딩

노트를 "보여주는 것"이 목적이면 URI가 맞고,
노트를 "고치는 것"이 목적이면 파일 편집이 먼저다.

### 3.3 오늘 일간노트 빠르게 열기

```bash
open "obsidian://daily?vault=obsidian"
```

또는 Obsidian 안에서:

- `Periodic Notes: Open daily note`

### 3.4 새 노트 만들기

```bash
open "obsidian://new?vault=obsidian&file=projects%2Fnew-project&content=hello"
```

하지만 이 저장소에서는 새 노트 내용이 길거나 형식이 중요하면 URI보다 직접 파일 생성/편집이 더 낫다.

## 4. 이 저장소 기준으로 자주 쓰는 기능

### 4.1 Daily / Weekly / Monthly

- daily 열기: `Periodic Notes: Open daily note`
- weekly 열기: `Periodic Notes: Open weekly note`
- monthly 열기: `Periodic Notes: Open monthly note`

템플릿 연결 기준:

- `templates/daily-template.md`
- `templates/weekly-template.md`
- `templates/monthly-template.md`

### 4.2 QuickAdd

이 볼트에서 이미 전제로 잡는 QuickAdd 흐름:

- `Daily Log`
- `Prompt Review`
- `Plan Reset`

QuickAdd는 "Obsidian UI 안에서 1번 실행"이 강점이고,
Claude Code는 "파일을 정확히 고치는 것"이 강점이다.
둘 중 하나만 고집하지 말고 목적에 맞게 쓴다.

### 4.3 Advanced URI

Advanced URI는 "특정 노트/설정/위치로 점프"할 때 유용하다.

쉽게 말하면:

- 기본 `obsidian://` = 열기/생성/검색
- Advanced URI = 더 세밀한 점프/명령

그래서 스킬에서는 아래처럼 생각하면 된다.

- 노트 내용 수정이 핵심 -> 직접 파일 편집
- Obsidian 앱을 특정 위치로 열어주면 좋은 작업 -> Advanced URI 고려

## 5. 스킬 작성 공통 규칙

Obsidian 관련 스킬은 아래 규칙을 기본으로 둔다.

1. 파일 경로를 먼저 확정한다.
2. 노트 본문 변경은 markdown 파일 편집으로 처리한다.
3. 사용자가 Obsidian 앱 포커싱/오픈까지 원할 때만 URI나 플러그인 명령을 제안한다.
4. 자동화가 이미 스크립트로 있으면 스크립트를 우선 재사용한다.
5. 결과 경로는 항상 절대경로와 vault 상대경로를 함께 의식한다.
6. 날짜/시간이 들어가는 모든 기록은 기본적으로 KST로 적는다.
7. 작업이 끝나면 `daily` 반영 여부를 먼저 확인한다.
8. 상태 변화가 있으면 `issue` / `project` 반영 여부까지 이어서 확인한다.

## 5.1 스킬 문서 최소 구성

앞으로 `obsidian-*` 스킬은 가능하면 아래 순서를 맞춘다.

1. 목표
2. 입력 계약
3. 출력 계약
4. 대상 파일/폴더
5. 표준 절차
6. 실패 시 처리
7. 빠른 예시

이렇게 해야 나중에 Claude Code든 OpenCode든 같은 문서를 재사용하기 쉽다.

## 5.2 제텔카스텐 연결 규칙

Obsidian 관련 스킬은 "문서를 하나 잘 쓰는 것"보다 "다른 문서와 잘 이어지게 쓰는 것"이 더 중요하다.

최소 연결 규칙:

1. daily는 관련 plan 또는 project note를 가진다.
2. weekly는 참조한 daily를 가진다.
3. monthly는 참조한 weekly를 가진다.
4. plan 스냅샷은 가능한 한 관련 daily/weekly에서 다시 찾을 수 있어야 한다.
5. project note는 `reference/`보다 `projects/` 구조를 우선한다.
6. 프로젝트 이름은 저장소명이 아니라 프로젝트 문서 제목을 우선한다.

링크는 가능하면 일반 경로보다 위키링크를 우선 쓴다.

## 6. 스킬에 넣기 좋은 문장 템플릿

### 6.1 공통 선행 문구

```markdown
## 0. 공통 실행 원칙

- 이 스킬은 `obsidian-cli-guideline` 기준을 따른다.
- 노트 본문 수정은 에이전트가 markdown 파일을 직접 편집한다.
- Obsidian 앱 열기/포커스가 필요할 때만 `obsidian://` URI 또는 Command Palette를 쓴다.
```

### 6.2 노트 열기 예시

```markdown
- daily 노트를 Obsidian에서 바로 열고 싶으면 `Periodic Notes: Open daily note` 또는 `obsidian://daily`를 사용한다.
```

### 6.3 스크립트 우선 예시

```markdown
- 이미 저장소 스크립트가 있으면 수동 절차보다 스크립트를 먼저 사용한다.
```

## 7. 언제 어떤 방식을 쓰는지 한 줄 요약

- 읽고/쓰고/정리한다 -> 파일 편집
- 보여주고/이동한다 -> `obsidian://`
- 플러그인 기능을 누른다 -> Command Palette / QuickAdd
- 반복 자동화한다 -> `$OBSIDIAN_ROOT/scripts/*.sh`

## 8. 이 가이드가 기대하는 최종 모습

앞으로 `obsidian-*` 스킬들은 모두:

- "무슨 파일을 바꾸는지"
- "언제 Obsidian 앱을 여는지"
- "언제 스크립트를 쓰는지"
- "입력과 출력이 무엇인지"
- "실패하면 어디서 멈추는지"

이 3가지를 분리해서 설명해야 한다.

## 9. 참고 기준

- 이 저장소의 `OBSIDIAN_DEV_SETUP_GUIDE.md`
- `obsidian-official-usage`
- Obsidian URI 공식 문서
- Advanced URI 문서
