"""대상 프로젝트에 없는 문서만 채운다."""

import argparse
from pathlib import Path

from .locations import kit_root, project_root


def document_sources(kit, preset):
    template = kit / "templates" / preset
    if preset == "obsidian":
        return {Path("templates") / path.name: path for path in sorted(template.glob("*.md"))}
    documents = {path.relative_to(template): path for path in sorted(template.rglob("*.md"))}
    for path in sorted((kit / "rules").glob("*.md")):
        documents[Path("docs/rules") / path.name] = path
    for name in ("sprint.md", "tasks.md"):
        documents[Path("docs/plans") / name] = template / "docs/templates" / name
    return documents


def install_documents(root, documents, dry_run):
    if not documents:
        raise ValueError("설치할 문서 템플릿이 없습니다.")
    pending = {}
    for relative, original in documents.items():
        target = root / relative
        if target.exists() or target.is_symlink():
            print(f"보존 {relative}")
            continue
        if not target.resolve().is_relative_to(root):
            raise ValueError(f"프로젝트 밖을 가리키는 경로입니다. {relative}")
        pending[relative] = original.read_bytes()
    for relative, content in pending.items():
        if not dry_run:
            target = root / relative
            if not target.resolve().is_relative_to(root):
                raise ValueError(f"프로젝트 밖을 가리키는 경로입니다. {relative}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as destination:
                destination.write(content)
        print(f"{'생성 예정' if dry_run else '생성'} {relative}")


def main(argv=None, *, legacy=False):
    parser = argparse.ArgumentParser(prog=None if legacy else "workspace-kit templates", description=__doc__)
    if legacy:
        parser.add_argument("project", type=Path, help="적용할 프로젝트 폴더")
    else:
        parser.add_argument("command", choices=("install",))
        parser.add_argument("--project", type=Path, help="대상 프로젝트 또는 옵시디언 볼트")
    parser.add_argument("--preset", choices=("project", "obsidian"), default="project")
    parser.add_argument("--kit", type=Path, help="별도 킷 저장소의 템플릿 원본 사용")
    parser.add_argument("--dry-run", action="store_true", help="생성 예정 경로만 확인")
    args = parser.parse_args(argv)
    try:
        root = project_root(args.project)
        install_documents(root, document_sources(kit_root(args.kit), args.preset), args.dry_run)
    except (OSError, ValueError) as error:
        parser.error(str(error))
