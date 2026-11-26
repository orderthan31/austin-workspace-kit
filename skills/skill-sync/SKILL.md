---
name: skill-sync
description: Austin Workspace Kit에서 커스텀 스킬 목록과 의존성을 확인하고, 공용 또는 지정한 프로젝트 설치본을 동기화하거나 제거한다. 스킬 배포, 설치 상태 확인, 여러 실행 환경의 스킬 정리 요청에 사용한다.
---

# 스킬 동기화

설치된 `workspace-kit` CLI를 사용한다. 사용자 지정 로컬 원본은 `--kit <저장소>` 또는 `AUSTIN_WORKSPACE_KIT_ROOT`로 연결한다.

- `workspace-kit skills list`는 실제 설치 상태, `skills catalog`는 설치 가능한 목록을 보여준다. 기존 스킬은 `skills update`, 새 스킬은 `skills install`을 사용하고 필요하면 `--dry-run`으로 먼저 확인한다.
- 기본 범위는 현재 프로젝트다. 다른 프로젝트는 `--project`, 공용은 `--global`, 개별 CLI의 공용 경로는 `--target`으로 선택한다.
- 지정한 설치본을 지울 때는 `skills remove <이름>`으로 확인한 뒤 `--apply`로 적용한다. 문서 양식은 `workspace-kit templates install`로 설치한다.
- 로컬 전용 목록은 요청받았을 때 `--include-private`로 더한다. 원본과 의존성은 킷 저장소의 `skills/`와 `skills.json`에서 관리한다.
- 이미 설치되어 있는 수정본이나 외부 설치본이 보류로 표시되면 경로와 이유를 확인한다. 비공개 원본과 설정은 해당 컴퓨터에서 관리한다.
