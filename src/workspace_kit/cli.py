import argparse
from importlib.metadata import PackageNotFoundError, version

from . import skills, templates


def main(argv=None):
    parser = argparse.ArgumentParser(prog="workspace-kit", description="프로젝트 스킬과 문서 템플릿 관리")
    try:
        parser.add_argument("--version", action="version", version=f"%(prog)s {version('austin-workspace-kit')}")
    except PackageNotFoundError:
        pass

    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("skills", help="설치된 스킬 조회 및 설치·갱신", add_help=False)
    commands.add_parser("templates", help="문서 템플릿 설치", add_help=False)
    args, rest = parser.parse_known_args(argv)
    handler = skills.main if args.command == "skills" else templates.main
    return handler(rest)
