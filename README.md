# Austin Workspace Kit

프로젝트를 시작할 때 쓰는 문서 구조, 개인 작업 규칙, 에이전트 스킬과 설치 도구를 관리합니다.

| 경로 | 내용 |
| --- | --- |
| [rules/](rules/) | 문서 정본·변경 이력·인계 관리, 개인 작업 기준 |
| [templates/project/](templates/project/) | 프로젝트 루트 규칙과 기능 명세·설계·스프린트·백로그·인계 양식 |
| [templates/obsidian/](templates/obsidian/) | 일간·주간·월간·프로젝트·이슈 보드 양식 |
| [skills/](skills/) · [agents/](agents/) | 수정하는 스킬 원본과 선택형 에이전트 |
| [config/](config/) · [scripts/](scripts/) | 설치 목록, 스킬 의존성, 생성·설치 스크립트 |

## 프로젝트 문서 시작하기

저장소를 클론한 폴더에서 실행합니다. 문서 생성에는 Python 3.10 이상이 필요합니다. 대상 폴더의 기존 파일은 유지합니다.

```bash
python3 scripts/init-project-docs.py /path/to/project --dry-run
python3 scripts/init-project-docs.py /path/to/project
```

설치 후 대상 프로젝트의 `AGENTS.md`에서 규칙을 확인합니다. 스프린트가 정해졌을 때 `docs/plans/sprint.md`의 기간·상태를 채우고, 미편성 일감은 `tasks.md`에 둡니다.

## 스킬 설치하기

Python 3.10 이상, Bash, rsync가 필요합니다. YAML 검증에 사용하는 PyYAML은 가상환경에 설치할 수 있습니다.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
bash scripts/sync-skills.sh --dry-run
bash scripts/sync-skills.sh
```

- 기본은 [공용 목록](config/global-skills.txt)만 설치합니다. 설치 위치는 `CLAUDE_SKILLS_DST`, `AGENTS_DST`, `ANTI_CLI_DST`, `ANTI_DST` 환경 변수로 바꿀 수 있습니다. 기본값은 각 CLI의 홈 경로입니다.
- `--include-obsidian`을 붙이면 [Obsidian 목록](config/obsidian-skills.txt)을 더합니다. 볼트 작업을 호출할 때 `OBSIDIAN_ROOT`에 사용할 폴더를 지정합니다. 일부 스킬이 사용하는 볼트 자동화는 해당 볼트에서 선택적으로 설정합니다. Obsidian 전용 에이전트는 `bash scripts/sync-obsidian-agent.sh`로 별도 설치합니다.
- 포테이토 모드는 프로젝트별로 설치합니다. 패키지와 함께 배포되는 외부 스킬의 버전 및 무결성은 [manifest.json](skills/poteto-mode/manifest.json)에서 확인합니다.

```bash
python3 skills/poteto-mode/scripts/sync_project.py --project /path/to/project
```

Herdr와 모델 CLI는 스킬을 실행할 때만 필요합니다. 모델 폴백은 [model-routes.json](skills/poteto-mode/config/model-routes.json)에서 관리합니다.

### 스킬 의존성

[skill-dependencies.json](config/skill-dependencies.json)의 `requires`에 스킬 이름을 넣으면 그 스킬과 하위 의존성을 먼저 설치합니다. 외부 스킬을 패키지에 포함할 때는 출처·버전·라이선스를 보존하고 `bundled`에 확인할 상대 경로를 적습니다. 설치는 저장소에 들어 있는 원본을 사용하므로 외부 스킬을 임의로 받아 실행하지 않습니다.

예를 들어 `obsidian-plan-reset`만 등록해도 `obsidian-plan-register`와 `obsidian-cli-guideline`이 같이 설치됩니다.

### 프로젝트 전용 설정

공용 템플릿을 프로젝트에 적용한 뒤 해당 프로젝트의 규칙과 업무 문서는 그 프로젝트에서 유지합니다. 한 컴퓨터에서만 쓰는 스킬은 Git에서 제외하는 `private/skills/`에 두고 `private/global-skills.txt`와 필요시 `private/skill-dependencies.json`에 등록합니다. 이 목록을 설치에 포함할 때는 `--include-private`을 붙입니다.
