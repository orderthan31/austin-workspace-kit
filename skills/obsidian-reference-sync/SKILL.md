---
name: obsidian-reference-sync
description: Use when local project documents, planning documents, reference notes, plan snapshots, or issue boards must be synchronized to an Obsidian vault without directly editing installed runtime skill copies.
---

# Obsidian Reference Sync

## 목적

프로젝트 문서와 Obsidian vault 문서를 같은 상태로 맞춘다.

프로젝트마다 vault 위치와 폴더 구조가 다르므로 경로를 하드코딩하지 않는다. 먼저 현재 프로젝트의 설정, 기존 문서, 사용자 지시를 확인한다.

## 대상 유형

| 프로젝트 파일 유형 | Obsidian 대상 예시 |
|---|---|
| 기능정의/요구사항 문서 | `reference/`, `projects/`, `specs/` |
| 화면기획/설계 문서 | `reference/`, `design/`, `projects/` |
| 구현계획 문서 | `agents-plan/`, `plans/`, `projects/` |
| 칸반/이슈 보드 | `issues/`, `issue/`, `kanban/` |
| 스킬 원본 | `skills/` |

## 작업 순서

1. 사용자 지시 또는 프로젝트 설정에서 vault root를 확인한다.
2. 기존 Obsidian 대상 파일이 있는지 찾는다.
3. 프로젝트 파일을 먼저 수정한다.
4. Obsidian target 경로를 확정한다.
5. 파일 복사, 전용 sync script, CLI 중 프로젝트 관례에 맞는 방법으로 동기화한다.
6. 가능한 경우 동일성 또는 핵심 내용 반영 여부를 확인한다.
7. 필요한 경우 Obsidian issue board도 갱신한다.
8. 프로젝트 repo 변경분을 커밋한다.

## 검증 명령 예시

```sh
diff -q {프로젝트 문서} {Obsidian 대상 문서}
rg -n "반영해야 할 핵심 문구" {Obsidian 대상 문서}
```

## 주의사항

- Obsidian의 실제 스킬 적용본은 직접 수정하지 않는다.
- 스킬 원본 경로는 사용자 지시나 vault 관례를 따른다.
- reference 문서는 프로젝트 문서와 동일해야 하는지, 요약본이어야 하는지 먼저 확인한다.
- plan snapshot은 사용자가 요구했거나 현재 plan cycle이 유지되는 경우에만 갱신한다.
- 절대경로가 필요한 경우에도 다른 사용자 환경에 그대로 복붙될 수 있다고 가정하지 않는다.
