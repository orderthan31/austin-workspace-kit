---
name: obsidian-report-ops
description: 'daily, weekly, monthly 보고 생성과 프로젝트 이력 조회를 함께 다루는 통합 스킬. 트리거: "주간보고", "월간보고", "프로젝트 보고서 조회", "report ops", "weekly report", "monthly report"'
---

## 0. 공통 실행 원칙

- 이 스킬은 `obsidian-cli-guideline` 기준을 따른다.
- 보고서는 markdown 파일 직접 편집 또는 조회로 처리한다.
- daily -> weekly -> monthly 흐름을 끊지 않고 링크로 이어준다.
- 활성 폴더만 보지 말고, 대상 기간에 해당하는 `archive/` 노트도 함께 확인한다.

## 1. 목표

보고 노트들을 "집계 문서"가 아니라 서로 연결된 리뷰 체인으로 유지한다.

- daily는 weekly로 올라간다.
- weekly는 monthly로 올라간다.
- project query는 이 체인을 따라 근거를 찾는다.

## 2. 제텔카스텐 연결 원칙

보고 문서는 위아래 연결이 있어야 한다.

필수 연결:

1. weekly는 참조한 daily를 위키링크로 가진다.
2. monthly는 참조한 weekly를 위키링크로 가진다.
3. 각 프로젝트 섹션은 가능하면 관련 plan/project note를 같이 적는다.
4. 조회 결과를 만들 때는 "어느 노트에서 왔는지" 추적 가능해야 한다.
5. 프로젝트 이름은 저장소명이 아니라 프로젝트 문서 제목 기준으로 모은다.

쉽게 말하면:

- daily = 원재료
- weekly = 중간 정리
- monthly = 큰 그림

세 문서가 따로 놀면 안 된다.

## 3. 입력 계약

### 3.1 weekly 생성

- 필수:
  - `week_id` 또는 현재 주차
- 선택:
  - `date_range`
  - `project_filter[]`

### 3.2 monthly 생성

- 필수:
  - `month_id` 또는 현재 월
- 선택:
  - `weekly_files[]`
  - `project_filter[]`

### 3.3 프로젝트 조회

- 필수:
  - `project_name`
- 선택:
  - `parent_project`
  - `scope=daily|weekly|monthly|all`
  - `start_date`
  - `end_date`
  - `week_id`
  - `month_id`

## 4. 출력 계약

- weekly 생성/수정:
  - `$OBSIDIAN_ROOT/weekly/YYYY-[W]WW.md`
- monthly 생성/수정:
  - `$OBSIDIAN_ROOT/monthly/YYYY-MM.md`
- 프로젝트 조회:
  - 텍스트 요약 + 근거 파일 목록

## 5. 표준 절차

### 5.1 weekly 만들기

1. 대상 주차의 daily 파일을 수집한다.
2. 메인 `daily/`에 없는 날짜가 있거나 이미 archive 된 기간이면 `archive/daily/YYYY/MM/`도 함께 확인한다.
3. 관련 plan 링크를 적을 때는 `agents-plan/MM-DD/...` 뿐 아니라 `archive/agents-plan/YYYY/MM/...`도 후보에 넣는다.
4. 프로젝트별 `Summary`와 `Details` 근거를 모은다.
5. weekly 파일을 생성/갱신한다.
6. `## 연결 노트`에 `[[projects/projects]]`를 포함한다.
7. `## 참조한 일간보고`에 실제로 사용한 daily 위키링크를 적는다.
8. 각 프로젝트 섹션에 가능하면 관련 plan 또는 project note 링크를 붙인다.

### 5.2 monthly 만들기

1. 대상 월의 weekly 파일을 수집한다.
2. 메인 `weekly/`만 보지 말고, 해당 월 주차가 archive 된 경우 `archive/weekly/YYYY/MM/`도 함께 확인한다.
3. 프로젝트별 완료/진행/이월/리스크를 집계한다.
4. monthly 파일을 생성/갱신한다.
5. `## 연결 노트`에 `[[projects/projects]]`를 포함한다.
6. `## 참조한 주간보고`에 실제로 사용한 weekly 위키링크를 적는다.
7. 다음 달 계획이 관련 플랜 또는 프로젝트 축적 노트와 이어지게 쓴다.

### 5.3 프로젝트 조회

1. 기간과 범위를 확정한다.
2. `daily/weekly/monthly`뿐 아니라 기간에 해당하는 `archive/daily`, `archive/weekly`, `archive/agents-plan`도 같이 찾는다.
3. 저장소명/워크트리명이 아니라 프로젝트 문서 제목 기준으로 병합한다.
4. 하위 프로젝트가 있으면 상위 프로젝트 아래에 묶어 보여준다.
5. 결과와 근거 파일을 같이 출력한다.

## 6. 출력 형식

### 6.1 weekly

```markdown
# YYYY-[W]WW 주간보고

## 연결 노트
- 프로젝트 허브: [[projects/projects]]

## 참조한 일간보고
- [[daily/YYYY-MM-DD]]

## 프로젝트별 진행 요약

### Project: [[<project-name>]]
- 관련 플랜: [[agents-plan/MM-DD/<한 줄 요약>]]
- 완료:
- 진행 중:
- 다음 주 계획:
- 이슈/리스크:
```

### 6.2 monthly

```markdown
# YYYY-MM 월간보고

## 연결 노트
- 프로젝트 허브: [[projects/projects]]

## 참조한 주간보고
- [[weekly/YYYY-[W]WW]]

## 프로젝트별 월간 리뷰

### Project: [[<project-name>]]
- 관련 플랜:
- 주요 완료:
- 주요 진행:
- 미완료/이월:
- 다음 달 계획:
- 이슈/리스크:
```

### 6.3 project query

```markdown
## 프로젝트 보고서 조회 결과: <project-name>

상위 프로젝트: [[<parent-project>]]

### 완료
- ...

### 진행 중
- ...

### 이슈/리스크
- ...

### 다음 계획
- ...

### 근거 파일
- [[daily/YYYY-MM-DD]]
- [[weekly/YYYY-[W]WW]]
- [[monthly/YYYY-MM]]
```

## 7. 집계 규칙

- 근거 없는 문장은 추가하지 않는다.
- 같은 항목은 최신의 더 구체적인 기록 기준으로 병합한다.
- `claim-q-front` 같은 저장소명은 가능하면 `[[프로젝트 A]]` 같은 프로젝트 노트명으로 정규화한다.
- `롯데구축` 같은 하위 프로젝트가 보이면 `[[프로젝트 A]]` 아래로 함께 묶는다.
- weekly/monthly의 참조 링크는 실제 사용한 문서만 남긴다.
- archive 문서를 읽었으면 `[[archive/...]]` 링크를 숨기지 말고 그대로 남긴다.
- 같은 기간에 활성 폴더와 archive 폴더 둘 다 있으면, 더 구체적인 내용을 가진 쪽을 우선 근거로 쓴다.
- 다음 계획은 이전 미완료와 연결되는 문장으로 쓴다.
- 보고서 상단 요약(`이번 주 목표`, `완료`, `진행 중`, `핵심 완료`)에는 `T1`, `Phase 2`, `P0-T3` 같은 내부 관리 ID를 쓰지 않는다.
- 내부 관리 ID가 꼭 필요하면 `관련 플랜` 링크나 `Details` 성격의 하단 설명으로 내린다.
- 상단 요약은 "무엇이 좋아졌는지/무엇이 끝났는지/무엇이 막혔는지"를 사람이 바로 읽을 수 있는 문장으로 쓴다.

## 8. 실패 시 처리

- 대상 daily/weekly가 없으면 빈 보고서를 억지로 만들지 않는다.
- 프로젝트 분류가 애매하면 추측보다 제외를 우선한다.
- 조회 결과가 빈약하면 `관련 기록을 찾지 못함`으로 마무리한다.

## 9. 빠른 실행 예시

```text
입력:
- week_id: 2026-W11

결과:
- $OBSIDIAN_ROOT/weekly/2026-W11.md 갱신
```
