#!/usr/bin/env python3
"""대상 프로젝트에 없는 문서만 채운다."""

import argparse
from pathlib import Path


KIT = Path(__file__).resolve().parents[1]
TEMPLATE = KIT / "templates/project"


def add_document(root, relative, original, dry_run):
    target = root / relative
    if target.exists() or target.is_symlink():
        print(f"보존 {relative}")
        return
    if not target.resolve().is_relative_to(root):
        raise ValueError(f"프로젝트 밖을 가리키는 경로입니다. {relative}")
    content = original.read_bytes()
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as destination:
            destination.write(content)
    print(f"{'생성 예정' if dry_run else '생성'} {relative}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="적용할 프로젝트 폴더")
    parser.add_argument("--dry-run", action="store_true", help="생성 예정 경로만 확인")
    args = parser.parse_args()
    root = args.project.resolve()
    if not root.is_dir():
        parser.error("대상 프로젝트 폴더를 먼저 만들어 주세요.")

    documents = {path.relative_to(TEMPLATE): path for path in sorted(TEMPLATE.rglob("*.md"))}
    for path in sorted((KIT / "rules").glob("*.md")):
        documents[Path("docs/rules") / path.name] = path
    for name in ("sprint.md", "tasks.md"):
        documents[Path("docs/plans") / name] = TEMPLATE / "docs/templates" / name
    try:
        for relative, original in documents.items():
            add_document(root, relative, original, args.dry_run)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
