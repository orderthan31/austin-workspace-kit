import os
from pathlib import Path


PROJECT_SKILLS = (".agents/skills", ".claude/skills", ".codex/skills", ".agent/skills", ".cursor/skills")


def kit_root(path=None):
    explicit = path or os.environ.get("AUSTIN_WORKSPACE_KIT_ROOT")
    module = Path(__file__).resolve()
    bundled = module.parent / "assets"
    root = Path(explicit).expanduser().resolve() if explicit else bundled
    if not explicit and not root.is_dir():
        root = module.parents[2]
    if not (root / "config/skills.json").is_file():
        raise ValueError(f"킷의 config/skills.json을 찾을 수 없습니다. {root}")
    return root


def project_root(path=None):
    if path is None:
        working = Path.cwd().resolve()
        path = next((parent for parent in (working, *working.parents)
                     if (parent / ".git").exists() or (parent / "AGENTS.md").is_file()), working)
    root = path.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"프로젝트 폴더를 먼저 만들어 주세요. {root}")
    return root


def project_skill_roots(project, include_alternatives):
    paths = PROJECT_SKILLS if include_alternatives else PROJECT_SKILLS[:1]
    roots = []
    for relative in paths:
        local = (project / relative).resolve()
        if local == project or not local.is_relative_to(project):
            raise ValueError(f"프로젝트 밖을 가리키는 스킬 경로입니다. {project / relative}")
        if local not in roots:
            roots.append(local)
    return roots
