#!/usr/bin/env python3
"""등록된 스킬과 의존성을 각 실행 환경에 동기화한다."""

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory

import yaml

from .locations import kit_root, project_root, project_skill_roots

STATE_FILE = ".austin-workspace-kit.json"
TARGETS = {
    "claude": ".claude/skills",
    "agents": ".agents/skills",
    "antigravity-cli": ".gemini/config/skills",
    "antigravity-app": ".gemini/antigravity/skills",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def skill_name(name):
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"스킬 이름을 확인해주세요. {name}")
    return name


def read_catalog(kit, scope, include_private):
    roots = [kit, kit / "private"] if include_private else [kit]
    sources, dependencies, selected = {}, {}, []
    for root in roots:
        path = root / ("config/skills.json" if root == kit else "skills.json")
        manifest = read_json(path)
        for name in manifest[scope]:
            selected.append(skill_name(name))
        for name, settings in manifest.get("dependencies", {}).items():
            dependencies[skill_name(name)] = settings
        for folder in (root / "skills").iterdir():
            if (folder / "SKILL.md").is_file():
                if folder.name in sources:
                    raise ValueError(f"공용과 비공개에 중복 등록된 스킬입니다. {folder.name}")
                sources[folder.name] = folder
    return selected, sources, dependencies


def ignored(_directory, names):
    return {name for name in names if name in {".DS_Store", "__pycache__"} or name.endswith(".pyc")}


def file_hashes(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"스킬 폴더를 확인해주세요. {root}")
    files = {}
    for directory, folders, names in os.walk(root):
        skip = ignored(directory, [*folders, *names])
        folders[:] = [name for name in folders if name not in skip]
        for name in [*folders, *(name for name in names if name not in skip)]:
            path = Path(directory) / name
            if path.is_symlink():
                raise ValueError(f"스킬 폴더 안에 심볼릭 링크가 있습니다. {path}")
            if path.is_file():
                files[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
            elif not path.is_dir():
                raise ValueError(f"일반 파일이 아닌 항목이 있습니다. {path}")
    return files


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def validate_source(folder, name, bundled):
    files = file_hashes(folder)
    header = (folder / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)
    metadata = yaml.safe_load(header[1]) if len(header) == 3 and not header[0] else None
    if not isinstance(metadata, dict) or metadata.get("name") != name:
        raise ValueError(f"SKILL.md의 이름을 확인해주세요. {folder}")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"SKILL.md에 설명이 필요합니다. {folder}")
    for path in bundled:
        if path not in files:
            raise ValueError(f"포함된 의존성 파일이 없습니다. {name}/{path}")
    if "manifest.json" in files:
        manifest = read_json(folder / "manifest.json")
        if "files" in manifest and manifest["files"] != {k: v for k, v in files.items() if k != "manifest.json"}:
            raise ValueError(f"패키지 파일이 manifest.json과 다릅니다. {folder}")
    return fingerprint(files)


def resolve(selected, sources, dependencies):
    packages, visiting = {}, []

    def visit(name):
        name = skill_name(name)
        if name in packages:
            return
        if name in visiting:
            raise ValueError(f"스킬 순환 의존성입니다. {' → '.join([*visiting, name])}")
        if name not in sources:
            raise ValueError(f"스킬 원본이 없습니다. {name}")
        visiting.append(name)
        config = dependencies.get(name, {})
        for requirement in config.get("requires", []):
            visit(requirement)
        folder = sources[name]
        packages[name] = (folder, validate_source(folder, name, config.get("bundled", [])))
        visiting.pop()

    for name in selected:
        visit(name)
    return packages


@dataclass
class Change:
    destination: Path
    name: str
    action: str
    before: str | None
    source: Path | None = None
    digest: str | None = None


def state_at(destination):
    path = destination / STATE_FILE
    if path.is_symlink():
        raise ValueError(f"관리 기록이 심볼릭 링크입니다. {path}")
    state = read_json(path) if path.exists() else {}
    if not isinstance(state, dict):
        raise ValueError(f"관리 기록 형식을 확인해주세요. {path}")
    return state


def present(path):
    return path.exists() or path.is_symlink()


def installed_at(destination):
    if not destination.is_dir():
        return []
    return sorted(path for path in destination.iterdir()
                  if not path.name.startswith(".") and (path / "SKILL.md").is_file())


def show_installed(roots, names):
    count = 0
    for root in roots:
        managed = state_at(root)
        for path in installed_at(root):
            if names and path.name not in names:
                continue
            if path.is_symlink() or path.name not in managed:
                status = "별도 설치"
            else:
                try:
                    before = fingerprint(file_hashes(path))
                except ValueError:
                    before = None
                status = "관리 중" if before == managed[path.name] else "수정됨"
            print(f"{path.name}\t{status}\t{path}")
            count += 1
    if count == 0:
        print("설치된 스킬이 없습니다.")


def verified_previous_package(target, source, files):
    if "manifest.json" not in files or not (source / "manifest.json").is_file():
        return False
    try:
        previous = read_json(target / "manifest.json")
        current = read_json(source / "manifest.json")
        upstream = current.get("upstream", {}).get("repository")
        return (previous.get("name") == source.name == current.get("name")
                and bool(upstream) and previous.get("upstream", {}).get("repository") == upstream
                and previous.get("files") == {k: v for k, v in files.items() if k != "manifest.json"})
    except (AttributeError, OSError, ValueError):
        return False


def plan_at(destination, packages, removals, *, migrating=False):
    managed = state_at(destination)
    for name in removals or packages:
        if not present(destination / name):
            if not removals:
                source, digest = packages[name]
                yield Change(destination, name, "설치", None, source, digest)
            elif name in managed:
                yield Change(destination, name, "기록 정리", None)
            else:
                yield Change(destination, name, "없음", None)
            continue
        try:
            files = file_hashes(destination / name)
            before = fingerprint(files)
        except ValueError:
            yield Change(destination, name, "보류", None)
            continue
        if removals:
            action = "제거" if managed.get(name) == before else "보류"
            yield Change(destination, name, action, before)
        else:
            source, digest = packages[name]
            if before == digest:
                action = "동일" if managed.get(name) == digest else "등록"
            elif migrating and name not in managed and verified_previous_package(destination / name, source, files):
                action = "이전 패키지 갱신"
            else:
                action = "갱신" if managed.get(name) == before else "보류"
            yield Change(destination, name, action, before, source, digest)


def apply_change(change):
    if change.action in {"동일", "없음"}:
        return
    destination = change.destination
    target = destination / change.name
    before = fingerprint(file_hashes(target)) if present(target) else None
    if before != change.before:
        raise ValueError(f"미리보기 이후 파일이 바뀌었습니다. {target}")
    managed = state_at(destination)
    if change.action in {"갱신", "제거"} and managed.get(change.name) != before:
        raise ValueError(f"미리보기 이후 관리 기록이 바뀌었습니다. {target}")
    with TemporaryDirectory(prefix=".skill-sync-", dir=destination) as folder:
        stage = Path(folder)
        incoming, backup = stage / "incoming", stage / "backup"
        if change.action in {"설치", "갱신", "이전 패키지 갱신"}:
            shutil.copytree(change.source, incoming, symlinks=True, ignore=ignored)
            if fingerprint(file_hashes(incoming)) != change.digest:
                raise ValueError(f"설치 준비 중 원본이 바뀌었습니다. {change.source}")
        if change.digest:
            managed[change.name] = change.digest
        else:
            managed.pop(change.name, None)
        record = stage / STATE_FILE
        record.write_text(json.dumps(managed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if change.action in {"갱신", "이전 패키지 갱신", "제거"}:
            target.rename(backup)
        moved = False
        try:
            if incoming.exists():
                incoming.rename(target)
                moved = True
            os.replace(record, destination / STATE_FILE)
        except OSError:
            if moved:
                target.rename(incoming)
            if backup.exists():
                backup.rename(target)
            raise


def apply_changes(changes):
    pending = {}
    for change in changes:
        if change.action not in {"동일", "없음"}:
            pending.setdefault(change.destination, []).append(change)
    for destination, operations in pending.items():
        destination.mkdir(parents=True, exist_ok=True)
        lock = destination / ".austin-workspace-kit.lock"
        try:
            lock.mkdir()
        except FileExistsError as error:
            raise ValueError(f"다른 동기화가 진행 중이거나 잠금이 남아 있습니다. {lock}") from error
        try:
            for change in operations:
                apply_change(change)
        finally:
            lock.rmdir()


def update_candidates(roots, names, sources, dependencies):
    by_root = {root: [path.name for path in installed_at(root)] for root in roots}
    installed = {name for names_at_root in by_root.values() for name in names_at_root}
    if names:
        missing = set(names) - installed
        if missing:
            raise ValueError(f"설치되지 않은 스킬입니다. {', '.join(sorted(missing))}")
        missing_source = set(names) - sources.keys()
        if missing_source:
            raise ValueError(f"갱신할 스킬 원본이 없습니다. {', '.join(sorted(missing_source))}")
    for root, names_at_root in by_root.items():
        selected = [name for name in names_at_root if name in sources and (not names or name in names)]
        yield from plan_at(root, resolve(selected, sources, dependencies), [], migrating=True)


def main(argv=None, *, legacy=False):
    parser = argparse.ArgumentParser(prog=None if legacy else "workspace-kit skills", description=__doc__)
    commands = ("list", "plan", "apply", "remove") if legacy else (
        "list", "catalog", "plan", "install", "update", "remove",
    )
    parser.add_argument("command", choices=commands)
    parser.add_argument("skills", nargs="*", help="대상 스킬 이름")
    destinations = parser.add_mutually_exclusive_group()
    destinations.add_argument("--project", type=Path, help="대상 프로젝트 폴더")
    destinations.add_argument("--global", dest="global_scope", action="store_true", help="사용자 홈 스킬 사용")
    destinations.add_argument("--target", choices=TARGETS, action="append")
    destinations.add_argument("--dest", type=Path, help="사용자가 지정한 스킬 폴더")
    parser.add_argument("--kit", type=Path, help="별도 킷 저장소의 원본 사용")
    parser.add_argument("--include-private", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="설치·갱신 예정 항목만 확인")
    parser.add_argument("--apply", action="store_true", help="remove에서 제거를 실제 적용")
    args = parser.parse_intermixed_args(argv)
    if args.apply and args.command != "remove":
        parser.error("--apply는 remove 명령에서 사용해주세요.")

    try:
        current_project = not (legacy or args.global_scope or args.target or args.dest)
        project = project_root(args.project) if args.project or current_project else None
        scope = "project" if project else "global"
        if project:
            roots = project_skill_roots(project, args.command in {"list", "update", "remove"} and not legacy)
        elif args.dest:
            roots = [args.dest.expanduser().resolve()]
        else:
            names = args.target or TARGETS
            roots = list(dict.fromkeys((Path.home() / TARGETS[name]).resolve() for name in names))
        if args.command == "list" and not legacy:
            show_installed(roots, args.skills)
            return 0

        kit = kit_root(args.kit)
        source_roots = [kit / "skills", kit / "private/skills"]
        for root in roots:
            if any(root.is_relative_to(source.resolve()) for source in source_roots):
                raise ValueError(f"스킬 원본 폴더는 설치 대상으로 사용할 수 없습니다. {root}")

        if args.command == "remove":
            if not args.skills:
                parser.error("제거할 스킬 이름을 지정해주세요.")
            removals = list(dict.fromkeys(skill_name(name) for name in args.skills))
            changes = [change for root in roots for change in plan_at(root, {}, removals)]
        else:
            registered, sources, dependencies = read_catalog(kit, scope, args.include_private)
            if args.command == "update":
                changes = list(update_candidates(roots, args.skills, sources, dependencies))
                if not changes:
                    print("현재 킷에서 갱신할 설치 스킬이 없습니다.")
            else:
                if args.skills and any(name not in registered for name in args.skills):
                    raise ValueError("선택한 범위의 JSON 목록에 등록된 스킬을 지정해주세요.")
                packages = resolve(args.skills or registered, sources, dependencies)
                if args.command in {"catalog", "list"}:
                    for name, (source, _) in packages.items():
                        print(f"{name}\t{source.relative_to(kit)}")
                    return 0
                changes = [change for root in roots for change in plan_at(root, packages, [])]
        for change in changes:
            print(f"{change.action}\t{change.destination / change.name}")
        if any(change.action == "보류" for change in changes):
            raise ValueError("수정되거나 관리 대상이 아닌 설치본이 있습니다. 해당 경로를 먼저 확인해주세요.")
        if not args.dry_run and (args.command in {"apply", "install", "update"} or args.apply):
            apply_changes(changes)
        return 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
