#!/usr/bin/env python3
"""등록 스킬과 그 의존성을 설치 순서대로 출력한다."""

import argparse
import json
import os
from pathlib import Path
import re


KIT = Path(__file__).resolve().parents[1]
SKILL_NAME = re.compile(r"[a-z0-9][a-z0-9._-]*")


def resolve(registry, source, dependencies):
    selected = {}
    visiting = []

    def visit(name):
        if not isinstance(name, str) or not SKILL_NAME.fullmatch(name):
            raise ValueError(f"스킬 이름을 확인해주세요. {name}")
        if name in selected:
            return
        if name in visiting:
            raise ValueError(f"스킬 순환 의존성이 있습니다. {' → '.join([*visiting, name])}")
        skill = (source / name).resolve()
        if not skill.is_relative_to(source) or not (skill / "SKILL.md").is_file():
            raise ValueError(f"스킬 원본이 없습니다. {name}")
        visiting.append(name)
        settings = dependencies.get(name, {})
        for required in settings.get("requires", []):
            visit(required)
        for dependency in settings.get("bundled", []):
            bundled = (skill / dependency).resolve()
            if not bundled.is_relative_to(skill) or not bundled.is_file():
                raise ValueError(f"스킬에 포함된 의존성 파일을 확인해주세요. {name}/{dependency}")
        visiting.pop()
        selected[name] = None

    for line in registry.read_text(encoding="utf-8").splitlines():
        name = line.partition("#")[0].strip()
        if name:
            visit(name)
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    try:
        manifest = Path(os.environ.get("SKILL_DEPENDENCIES_FILE") or KIT / "config/skill-dependencies.json")
        dependencies = json.loads(manifest.read_text(encoding="utf-8"))
        selected = resolve(args.registry, args.source.resolve(), dependencies)
    except (OSError, AttributeError, TypeError, ValueError) as error:
        parser.error(str(error))
    for name in selected:
        print(name)


if __name__ == "__main__":
    main()
