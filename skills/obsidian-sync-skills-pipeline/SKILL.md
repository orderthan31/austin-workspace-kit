---
name: obsidian-sync-skills-pipeline
description: Austin Workspace Kit의 등록 스킬과 의존성을 Claude Code·Codex·Gemini CLI·Antigravity에 동기화한다. 스킬 배포, 설치 미리보기, Obsidian 스킬 동기화 요청에 사용한다.
---

# 스킬 동기화

- 이 스킬은 기존 호출 이름을 유지한다. 스킬 설치는 Austin Workspace Kit 저장소에서 실행하고 Obsidian 볼트는 설치에 필요하지 않다.
- 저장소는 사용자가 알려준 경로 또는 `AUSTIN_WORKSPACE_KIT_ROOT`로 확인한다. 그 안의 `README.md`와 `config/` 등록 목록을 읽는다.
- 스킬 원본은 저장소의 `skills/`에서 수정한다. 설치 경로는 스크립트로 갱신한다.
- 설치 대상부터 확인할 때는 아래 명령을 실행한다.

```bash
bash "${AUSTIN_WORKSPACE_KIT_ROOT:?저장소 경로를 지정하세요}/scripts/sync-skills.sh" --dry-run
```

- 실제 설치 요청이면 같은 명령에서 `--dry-run`을 뺀다. Obsidian 스킬은 `--include-obsidian`으로, 사용자가 따로 등록한 로컬 스킬은 `--include-private`으로 추가한다.
- `config/skill-dependencies.json`의 필수 스킬과 포함된 외부 스킬을 확인한다. 새 외부 스킬은 출처·버전·라이선스를 확인한 뒤 원본을 함께 관리한다.
- Obsidian 전용 에이전트는 필요할 때 `scripts/sync-obsidian-agent.sh`로 설치한다. 볼트 자동화를 실행할 때만 `OBSIDIAN_ROOT`를 사용한다.
- 설치 뒤 요청한 적용 위치를 확인하고 실패한 위치와 이유를 보고한다.
