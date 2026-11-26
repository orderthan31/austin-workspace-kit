---
name: obsidian-plan-reset
description: '현재 프로젝트의 plan.md를 Obsidian agents-plan에 스냅샷 반영한 뒤, 프로젝트의 plan.md를 초기 템플릿으로 리셋하는 스킬. 같은 플랜 사이클에서 `plan-register`가 만든 등록본 앵커가 있으면 그 파일을 갱신하고, 없으면 `MM-DD/{한 줄 요약}.md` 새 스냅샷을 만든다. 트리거: "플랜 백업", "플랜 종료", "플랜 리셋", "새 플랜 시작 전에 백업", "plan 백업 후 초기화", "plan 스냅샷", "obsidian-plan-reset", "plan reset"'
---

## 0. 공통 실행 원칙

- 이 스킬은 `obsidian-cli-guideline` 기준을 따른다.
- `PROJECT_ROOT`는 코드 프로젝트 루트다. `OBSIDIAN_ROOT`는 사용자가 지정한 볼트 루트다.
- `plan.md`는 `PROJECT_ROOT` 기준이고, `agents-plan/...` 스냅샷과 스크립트는 `OBSIDIAN_ROOT` 기준이다.
- 이 작업은 노트 직접 편집보다 저장소 스크립트 실행이 우선이다.
- 스크립트 실행 후 확인이 필요하면 생성된 `agents-plan` 스냅샷을 Obsidian에서 연다.
- 기본 동작은 "새 완료 스냅샷 추가"가 아니라 "같은 플랜의 등록본 최종 상태 갱신"이다.
- `deep-planning`이 `기존 플랜 백업 후 새 플랜 시작`으로 결정했을 때 이전 사이클을 닫는 기본 수단으로 본다.

## 1. 목표

현재 작업 프로젝트의 `plan.md`를 보존한 뒤 초기화해 새 계획 사이클을 시작한다.

- 스냅샷 대상: `<PROJECT_ROOT>/plan.md`
- 스냅샷 저장: `$OBSIDIAN_ROOT/agents-plan/MM-DD/<한 줄 요약>.md`
- 리셋 대상: `<PROJECT_ROOT>/plan.md`

## 2. 사용 스크립트

- `$OBSIDIAN_ROOT/scripts/obsidian-plan-reset.sh`

## 2.1 입력 계약

- 필수:
  - 현재 작업 디렉터리 또는 `project_root`
- 선택:
  - `OBSIDIAN_ROOT`는 설정에서 확인할 수 없을 때 지정한다.

여기서 현재 작업 디렉터리는 코드 프로젝트 루트를 뜻한다.
옵시디언 볼트 루트와 같은 뜻이 아니다.

## 2.2 출력 계약

- 생성 파일:
  - `$OBSIDIAN_ROOT/agents-plan/MM-DD/<한 줄 요약>.md`
- 수정 파일:
  - `<PROJECT_ROOT>/plan.md`
- 출력 메세지:
  - snapshot 경로
  - reset 완료 여부

## 3. 기본 실행

현재 디렉터리를 프로젝트 루트로 보고 실행:

```bash
OBSIDIAN_ROOT="${OBSIDIAN_ROOT:?볼트 경로를 지정하세요}"
bash "$OBSIDIAN_ROOT/scripts/obsidian-plan-reset.sh"
```

프로젝트 루트를 명시해서 실행:

```bash
OBSIDIAN_ROOT="${OBSIDIAN_ROOT:?볼트 경로를 지정하세요}"
bash "$OBSIDIAN_ROOT/scripts/obsidian-plan-reset.sh" "/path/to/project"
```

주의:

- 다른 프로젝트 디렉터리 안에서 실행해도 `scripts/...` 상대경로로 부르지 않는다.
- 항상 `"$OBSIDIAN_ROOT/scripts/obsidian-plan-reset.sh"`처럼 옵시디언 루트 기준 절대 경로로 호출한다.

## 4. 동작 규칙

1. `plan.md`가 없으면 실패로 종료한다.
2. `deep-planning`의 결정이 `기존 플랜 백업 후 새 플랜 시작`인지 먼저 확인한다.
3. 원본 `plan.md` 안에 `plan-register`가 남긴 등록 앵커가 있으면, 그 기존 등록본 파일을 최종 상태로 갱신한다.
4. 등록 앵커가 없을 때만 `MM-DD/<한 줄 요약>.md` 새 스냅샷을 만든다.
5. 새 스냅샷이 필요한 경우 파일명은 plan 안의 `## 한 줄 요약` 값을 1순위로 사용한다.
6. `한 줄 요약`이 없을 때만 짧은 정제 목표나 첫 의미 있는 제목을 fallback으로 사용한다.
7. 새 파일이 필요한데 같은 파일명이 이미 있으면 `(2)`, `(3)`처럼 뒤에 번호를 붙여 충돌을 피한다.
8. 원본 `plan.md`는 초기 템플릿으로 리셋한다.

## 4.1 파일명 규칙

- 파일명은 짧고 바로 이해돼야 한다.
- 사용자 원문 전체나 대화체 문장을 파일명으로 쓰지 않는다.
- 길게 설명하지 말고 "무슨 플랜인지"만 남긴다.

## 4.1 실패 시 처리

- `plan.md`가 없으면 절대 새로 만들지 말고 실패로 보고한다.
- 스냅샷 저장이 실패하면 리셋을 진행하지 않는다.

## 5. 출력 예시

```text
Snapshot saved: $OBSIDIAN_ROOT/agents-plan/03-17/목록-검색-개선.md
Reset completed: <PROJECT_ROOT>/plan.md
```
