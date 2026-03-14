#!/usr/bin/env python3
"""boj CLI 통합 디스패처.

Bash 디스패처(src/boj)를 대체하는 Python 진입점.
pyproject.toml [project.scripts] 에서 boj = "src.cli.main:main" 으로 등록.

사용법:
    boj <command> [args...]
    boj make 4949 --lang python
    boj run 4949
    boj commit 4949
"""

import sys


COMMANDS = {
    "make": "src.cli.boj_make",
    "run": "src.cli.boj_run",
    "open": "src.cli.boj_open",
    "commit": "src.cli.boj_commit",
    "review": "src.cli.boj_review",
    "submit": "src.cli.boj_submit",
    "setup": "src.cli.boj_setup",
}


def _print_usage() -> None:
    print("사용법: boj <명령> [문제번호] [옵션]")
    print()
    print("명령:")
    print("  boj setup              — 초기 설정 (git, BOJ 세션, 에이전트)")
    print("  boj setup --check      — 현재 설정 상태 확인")
    print("  boj make 4949          — 에이전트로 환경 생성")
    print("  boj open 4949          — 해당 문제 폴더를 에디터로 열기")
    print("  boj run 4949           — 테스트 실행")
    print("  boj submit 4949        — Submit 파일 생성 (BOJ 제출용)")
    print("  boj commit 4949 [msg]  — 해당 문제 폴더 커밋")
    print("  boj review 4949        — 에이전트로 리뷰 요청")
    print()
    print("공통 옵션:")
    print("  -h, --help             — 명령별 도움말")
    print()
    print("예시:")
    print("  boj make 4949 --lang python")
    print("  boj run 4949 --lang java")
    print("  boj submit 4949 --open")
    print("  boj commit 4949 --no-stats")
    print("  boj open 4949 --editor cursor")


def main() -> None:
    """CLI 메인 진입점. sys.argv 기반으로 서브커맨드를 라우팅한다."""
    argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help", "help"):
        _print_usage()
        sys.exit(0)

    command = argv[0]
    sub_argv = argv[1:]

    if command not in COMMANDS:
        print(f"Unknown subcommand: {command}", file=sys.stderr)
        _print_usage()
        sys.exit(1)

    module_path = COMMANDS[command]

    # lazy import: 해당 서브커맨드 모듈만 로드
    from importlib import import_module

    module = import_module(module_path)
    sys.exit(module.main(sub_argv))


if __name__ == "__main__":
    main()
