---
name: obsidian-official-usage
description: 'Obsidian 공식 문서 기준의 기본 사용법과 CLI, 내부 링크, 커맨드 팔레트, 백링크, 속성 활용 원칙을 정리한 스킬. 트리거: "공식 obsidian 사용법", "obsidian official", "obsidian cli 공식", "위키링크", "백링크", "properties", "command palette"'
---

## 1. 목표

에이전트가 Obsidian을 "내가 아는 방식"이 아니라 "공식 문서 기준"으로 다루게 한다.

쉽게 말하면:

- 문서 연결은 공식 링크 방식으로
- 자동화는 공식 CLI 방식으로
- 탐색은 공식 Command palette, Backlinks, Properties 개념으로

움직이게 하는 스킬이다.

## 2. 공식 기준 핵심 요약

### 2.1 내부 링크

Obsidian 공식 도움말 기준으로 노트 연결은 두 방식이 있다.

- 위키링크: `[[노트명]]`
- 마크다운 링크: `[노트명](노트명.md)`

기본적으로 Obsidian은 위키링크를 더 자연스럽게 다룬다.
이 볼트도 제텔카스텐 연결성 때문에 위키링크를 우선 쓰는 편이 좋다.

### 2.2 링크 갱신

공식 설정의 `Automatically update internal links`가 켜져 있으면
파일 이름을 바꿔도 내부 링크가 자동 갱신된다.

그래서 에이전트는:

- 경로를 자주 바꾸는 대신
- 링크 구조를 먼저 안정화하는 것이 좋다.

### 2.3 Command Palette

공식 문서 기준 Command palette는 거의 모든 명령의 출입구다.

- macOS: `Cmd+P`
- 명령 이름을 몰라도 fuzzy matching으로 찾을 수 있다.

에이전트 관점에서는:

- 플러그인 명령 이름이 애매할 때
- 먼저 Command palette 명령으로 표현하는 것이 가장 공식적이다.

### 2.4 Hotkeys

자주 쓰는 명령은 공식적으로 Hotkeys에 연결할 수 있다.

즉, 나중에 Obsidian 운영이 안정되면:

- `Daily note 열기`
- `QuickAdd 실행`
- `Backlinks 열기`

같은 것을 단축키로 고정하는 게 맞다.

### 2.5 Backlinks

공식 Backlinks 플러그인은 "이 노트를 누가 참조하나"를 보여준다.

제텔카스텐 관점에서는 아주 중요하다.

에이전트는 노트를 새로 만들 때:

- 이 노트가 어디를 가리키는지(outgoing)
- 누가 이 노트를 다시 찾을 수 있는지(backlinks)

를 같이 생각해야 한다.

### 2.6 Properties

공식 Obsidian은 Properties를 파일 메타데이터 표준으로 본다.

그래서 에이전트는 반복적으로 쓰는 속성이 있으면:

- 본문에만 흩뿌리지 말고
- 필요 시 properties로 올릴 수 있다.

예:

- `project`
- `status`
- `type`
- `tags`

## 3. 공식 CLI 사용법

공식 Obsidian CLI 문서 기준 핵심은 이렇다.

### 3.1 시작

```bash
obsidian help
obsidian version
```

- CLI는 Obsidian 앱과 연결되어 동작한다.
- 앱이 꺼져 있으면 첫 명령이 앱을 띄울 수 있다.

### 3.2 볼트 지정

현재 작업 디렉터리가 vault면 그 vault를 기본 사용한다.
아니면 `vault=<name>` 또는 `vault=<id>`를 먼저 적는다.

이 저장소에서 특히 주의할 점:

- 코드 작업 `cwd`가 `/path/to/project` 같은 다른 프로젝트 루트일 수 있다.
- 그 경우 Obsidian CLI의 기본 vault 추론을 믿지 말고, 항상 `vault=obsidian` 을 명시하는 편이 안전하다.
- `path=` 값은 항상 vault root 기준 경로다. 즉 `daily/...`, `projects/...`, `issue/...` 는 현재 코드 프로젝트 상대경로가 아니다.

```bash
obsidian vault=obsidian daily
obsidian vault=obsidian search query="meeting"
```

### 3.3 파일 지정

공식 CLI는 보통 두 가지 지정 방식을 쓴다.

- `file=<name>`: 위키링크처럼 이름 기준 해석
- `path=<path>`: vault root 기준 정확한 경로

에이전트는 모호성이 있으면 `path=`를 우선한다.

### 3.4 공식 everyday 명령

공식 문서 예시 중 이 볼트에서 특히 중요한 것:

```bash
obsidian daily
obsidian daily:append content="- [ ] Buy groceries"
obsidian search query="meeting notes"
obsidian read
obsidian tasks daily
obsidian create name="Trip to Paris" template=Travel
obsidian tags counts
obsidian diff file=README from=1 to=3
```

이걸 이 저장소 스타일로 바꿔 생각하면:

- 오늘 노트 열기 -> `obsidian daily`
- 오늘 할일 추가 -> `obsidian daily:append ...`
- 특정 주제 찾기 -> `obsidian search query="..."`
- 현재 노트 읽기 -> `obsidian read`
- 태그 집계 -> `obsidian tags counts`

### 3.5 파일 조작 명령

공식 CLI는 파일 직접 조작도 지원한다.

```bash
obsidian open path="daily/2026-03-13.md"
obsidian create path="projects/new-project.md" content="# 새 프로젝트"
obsidian append path="daily/2026-03-13.md" content="- 추가 메모"
obsidian prepend path="daily/2026-03-13.md" content="> 상단 메모"
obsidian move path="projects/old.md" to="projects/new.md"
obsidian rename path="projects/old.md" name="new-name"
```

단, 이 저장소에서는 긴 구조 편집은 여전히 파일 직접 편집이 더 안전하다.
CLI는 짧은 자동화, 단순 append, 열기, 조회에 특히 좋다.

다시 한 번 쉽게 말하면:

- `vault=obsidian` -> 어떤 볼트인지 정하는 값
- `path="daily/2026-03-13.md"` -> 그 볼트 안 경로
- 현재 셸의 `cwd`가 어디든, `path=`는 vault 안 기준으로 해석해야 한다.

### 3.6 링크/구조 점검 명령

공식 CLI에는 제텔카스텐 점검에 도움이 되는 명령도 있다.

```bash
obsidian backlinks path="daily/2026-03-13.md"
obsidian links path="daily/2026-03-13.md"
obsidian unresolved
obsidian orphans
obsidian deadends
```

이 명령들은 각각:

- 누가 이 노트를 가리키는지
- 이 노트가 어디를 가리키는지
- 깨진 링크가 있는지
- 아무도 안 가리키는 노트가 있는지
- 어디도 안 가리키는 노트가 있는지

를 보는 데 좋다.

즉, 에이전트가 "연결이 잘 됐는지" 검사할 때 매우 유용하다.

### 3.7 Properties 명령

공식 CLI는 properties 읽기/수정도 지원한다.

```bash
obsidian properties path="daily/2026-03-13.md"
obsidian property:set path="daily/2026-03-13.md" name=project value="정보입력 플랫폼" type=text
obsidian property:read path="daily/2026-03-13.md" name=project
```

앞으로 메타데이터 규칙을 세우면 이 명령을 활용할 수 있다.

## 4. 에이전트용 사용 원칙

### 4.1 언제 CLI를 쓰면 좋은가

- 오늘 노트 열기
- 짧은 내용 append/prepend
- 검색/태그/링크 현황 조회
- 백링크/고아노트 점검
- properties 읽기/쓰기

### 4.2 언제 파일 직접 편집이 좋은가

- 긴 문단 구조 편집
- 여러 섹션 동시 재구성
- 정교한 보고서 생성
- 템플릿 기반 대형 문서 작성

### 4.3 언제 Command palette를 써야 하나

- 플러그인 명령이 공식 CLI에 없는 경우
- QuickAdd, Backlinks UI, workspace 전환 같은 UI 명령 중심 작업

## 5. 제텔카스텐 체크리스트

노트를 만들거나 고친 뒤 가능하면 확인한다.

- [ ] 이 노트에 최소 1개 이상의 내부 링크가 있는가?
- [ ] 관련 daily/weekly/monthly/plan 중 최소 1곳과 연결되는가?
- [ ] backlinks 관점에서 나중에 다시 발견 가능한가?
- [ ] unresolved link를 만들지 않았는가?
- [ ] orphan 또는 dead-end 노트가 되지 않는가?

## 6. 이 저장소에 바로 적용할 공식 패턴

### 6.1 daily

- `obsidian daily`
- `obsidian daily:append content="..."`
- 필요 시 `obsidian backlinks path="daily/YYYY-MM-DD.md"`

### 6.2 weekly/monthly

- 생성은 템플릿 + 파일 편집
- 검증은 `links`, `backlinks`, `unresolved`

### 6.3 plan 연결

- 관련 daily에 `[[agents-plan/MM-DD/<한 줄 요약>]]` 또는 `[[archive/agents-plan/YYYY/MM/<한 줄 요약>]]` 링크 추가
- weekly/monthly 프로젝트 섹션에도 관련 plan 링크 추가
- plan 스냅샷이 orphan가 되지 않게 daily 또는 review 쪽에서 재참조

### 6.4 프로젝트 허브 연결

- 프로젝트 기준 노트는 `reference/`보다 `projects/`를 우선한다.
- 프로젝트 표기는 저장소명보다 위키링크를 우선한다.
- 예: `claim-q-front` 대신 `[[프로젝트 A]]`
- 세부 트랙은 `[[프로젝트 A]] [[롯데구축]]`처럼 상위/하위 프로젝트를 함께 적는다.

## 7. 공식 문서에서 특히 중요한 뜻

- 내부 링크는 지식 네트워크를 만든다.
- Backlinks는 노트 발견성을 높인다.
- Command palette는 모든 명령의 공통 입구다.
- CLI는 자동화와 외부 도구 통합용이다.
- Unique note creator는 제텔카스텐식 UID 노트를 공식적으로 지원한다.

## 8. 참고 공식 문서

- Obsidian CLI
- Internal links
- Settings / Files and links
- Command palette
- Hotkeys
- Backlinks
- Core plugins
- Unique note creator
