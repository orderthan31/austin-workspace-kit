---
name: obsidian-archive-ops
description: '오래된 daily와 weekly를 archive 폴더로 이동하고, archive 대상 daily와 같은 월-일(`MM-DD`) 폴더의 활성 agents-plan도 함께 archive로 보내는 스킬. 트리거: "archive ops", "daily archive", "오래된 daily 정리", "weekly archive", "archive로 이동"'
---

## 공통 경로 기준

- 이 스킬은 `obsidian-cli-guideline` 기준을 따른다.
- `daily/...`, `weekly/...`, `agents-plan/...`, `archive/...` 는 모두 `OBSIDIAN_ROOT` 기준이다.
- 다른 코드 프로젝트 안에서 실행하더라도 현재 `cwd` 상대경로로 해석하지 않는다.

## 언제 쓰나
- `daily/`에 최근 문서만 남기고 싶을 때
- 오래된 `weekly/`를 메인 폴더에서 치우고 싶을 때
- 오래된 `daily`와 연결된 `agents-plan/MM-DD/` 활성 플랜을 같이 archive로 보내고 싶을 때

## 핵심 규칙
- `daily`는 오늘 기준 20일이 지나면 archive 후보다.
- `weekly`는 오늘 기준 60일이 지나면 archive 후보다.
- `monthly`는 자동 archive 하지 않는다.
- `daily`를 옮길 때는 같은 월-일(`MM-DD`) 폴더의 활성 `agents-plan/MM-DD/*.md`도 같이 archive로 이동한다.
- archive는 삭제가 아니라 이동이다.

## 대상 경로
- 원본
  - `$OBSIDIAN_ROOT/daily/`
  - `$OBSIDIAN_ROOT/weekly/`
  - `$OBSIDIAN_ROOT/agents-plan/`
- 보관
  - `$OBSIDIAN_ROOT/archive/daily/YYYY/MM/`
  - `$OBSIDIAN_ROOT/archive/weekly/YYYY/MM/`
  - `$OBSIDIAN_ROOT/archive/agents-plan/YYYY/MM/`

## 처리 방식
1. archive 대상 `daily`를 찾는다.
2. 각 daily 파일명에서 날짜를 읽는다.
3. 같은 월-일 폴더인 `agents-plan/MM-DD/`를 찾는다.
4. 그 안의 `.md` 파일들을 `archive/agents-plan/YYYY/MM/`로 이동한다.
5. archive 대상 `weekly`를 찾고, 수정 시각 기준으로 archive로 이동한다.
6. 이동 결과를 요약해 사용자에게 알려준다.

## 주의
- 프로젝트 카드의 `현재 활성 plan`이 archive 대상 파일을 가리키고 있으면, 먼저 최신 활성 plan이 맞는지 확인한다.
- archive는 원문을 지우는 작업이 아니지만, 링크 경로는 바뀔 수 있으므로 `현재 활성 plan`처럼 메인 문맥에서 자주 쓰는 링크는 최신 문서만 유지하는 것이 좋다.
- `monthly`, `projects`, `prompt/review`는 기본적으로 메인 폴더에 둔다.

## 실행
- 스크립트:
  - `$OBSIDIAN_ROOT/scripts/obsidian-archive-notes.sh`
- 기본 실행:
```bash
OBSIDIAN_ROOT="${OBSIDIAN_ROOT:?볼트 경로를 지정하세요}"
bash "$OBSIDIAN_ROOT/scripts/obsidian-archive-notes.sh"
```
- 미리보기:
```bash
OBSIDIAN_ROOT="${OBSIDIAN_ROOT:?볼트 경로를 지정하세요}"
bash "$OBSIDIAN_ROOT/scripts/obsidian-archive-notes.sh" --dry-run
```

## 기대 결과
- `daily/`에는 최근 20일 노트만 남는다.
- `weekly/`에는 최근 60일 노트만 남는다.
- 오래된 `daily`와 같은 월-일 폴더의 활성 `agents-plan`은 같이 archive로 이동한다.
- `monthly/`와 `projects/`는 계속 메인 폴더에서 문맥 허브 역할을 한다.
