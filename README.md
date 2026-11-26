# Austin Workspace Kit

프로젝트를 시작할 때 쓰는 문서 구조, 개인 작업 규칙, 에이전트 스킬과 설치 도구를 관리합니다.

| 경로 | 내용 |
| --- | --- |
| [rules/](rules/) | 문서 정본·변경 이력·인계 관리, 개인 작업 기준 |
| [templates/project/](templates/project/) | 프로젝트 루트 규칙과 기능 명세·설계·스프린트·백로그·인계 양식 |
| [templates/obsidian/](templates/obsidian/) | 일간·주간·월간·프로젝트·이슈 보드 양식 |
| [skills/](skills/) | 수정하는 스킬 원본 |
| [config/](config/) · [src/workspace_kit/](src/workspace_kit/) | 설치 목록, 스킬 의존성, 관리 CLI |

## 관리 CLI 설치

Python 3.10 이상이 필요합니다. 저장소를 받은 뒤 아래 명령으로 `workspace-kit`을 한 번 설치합니다. 그다음부터 대상 프로젝트에서 바로 실행할 수 있습니다.

```bash
uv tool install /path/to/austin-workspace-kit
workspace-kit --version
```

공용 스킬과 템플릿은 CLI에 포함됩니다. 킷 저장소를 수정한 버전으로 다시 설치하려면 같은 경로에 `uv tool install --reinstall`을 실행합니다.

## 프로젝트에서 사용
```bash
workspace-kit skills list
workspace-kit skills catalog
workspace-kit skills install poteto-mode --dry-run
workspace-kit skills install poteto-mode
workspace-kit skills update --dry-run
workspace-kit skills update
workspace-kit templates install --dry-run
workspace-kit templates install
```

- 현재 폴더부터 올라가며 `.git` 또는 `AGENTS.md`가 있는 폴더를 프로젝트 루트로 사용합니다. 다른 프로젝트나 새 폴더에 적용하려면 `--project /path/to/project`를 붙입니다.
- `skills list`는 프로젝트의 `.agents`, `.claude`, `.codex`, `.agent`, `.cursor` 아래에 실제 설치된 스킬과 관리 상태를 보여줍니다. `skills catalog`는 킷에서 제공하는 설치 목록입니다.
- `skills install`은 프로젝트에서 공용으로 쓸 `.agents/skills`에 설치합니다. `skills update`는 이미 설치된 스킬 중 원본을 확인할 수 있는 것만 갱신합니다. `update poteto-mode`처럼 이름을 주면 대상 하나만 갱신합니다.
- 설치본에서 수동 수정이 확인되면 경로와 함께 보류로 표시합니다. 이전 포테이토 설치본은 패키지 이름·출처·파일 해시가 확인되면 그대로 이어서 갱신합니다.
- `templates install`은 빠진 `AGENTS.md`, 문서 규칙, 스프린트·백로그 등만 채웁니다. 옵시디언 양식은 `templates install --preset obsidian --project /path/to/vault`로 볼트의 `templates/`에 설치합니다.

## 공용 스킬 관리

공용 [설치 목록](config/skills.json)은 `--global`로 선택합니다. 사용자 홈의 특정 실행 환경은 `--target claude`, `--target agents`, `--target antigravity-cli`, `--target antigravity-app`으로 선택하고, 직접 정한 설치 위치는 `--dest /path/to/skills`로 지정합니다.

```bash
workspace-kit skills install skill-sync --global
workspace-kit skills remove skill-sync --target agents
workspace-kit skills remove skill-sync --target agents --apply
```

포테이토를 실제로 실행할 때 Herdr와 모델 CLI가 필요합니다. 외부 스킬의 버전·해시는 [manifest.json](skills/poteto-mode/manifest.json), 모델 폴백은 [model-routes.json](skills/poteto-mode/config/model-routes.json)에서 확인합니다.

기존 `scripts/skills.py`와 `scripts/init-project-docs.py` 호출도 저장소에서 사용할 수 있습니다.

### 스킬 의존성

[skills.json](config/skills.json)의 `dependencies.<스킬 이름>.requires`에 다른 스킬 이름을 넣으면 해당 스킬과 하위 의존성을 먼저 설치합니다. 외부 스킬을 패키지에 포함할 때는 출처·버전·라이선스를 보존하고 같은 항목의 `bundled`에 확인할 상대 경로를 적습니다. 포함된 파일은 패키지와 함께 복사됩니다.

### 프로젝트 전용 설정

공용 템플릿을 적용한 뒤 프로젝트별 규칙과 업무 문서는 각 프로젝트에서 유지합니다. 로컬 전용 스킬은 킷 저장소의 `private/skills/`와 `private/skills.json`에 둡니다. 로컬 원본이나 비공개 목록을 사용할 때는 `--kit /path/to/austin-workspace-kit`을 지정하고 비공개 목록에는 `--include-private`을 추가합니다.
