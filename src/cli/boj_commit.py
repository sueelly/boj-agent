#!/usr/bin/env python3
"""boj commit CLI 래퍼 -- 인수 파싱 + 출력 포매팅.

Issue #68 -- commit.sh Python 마이그레이션.

사용법:
    python -m src.cli.boj_commit <문제번호> [--message MSG] [--no-stats] [--no-push]
    또는 boj 디스패처에서 호출.
"""

import argparse
import sys

from src.core.commit import commit
from src.core.exceptions import BojError


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 인수를 파싱한다.

    Args:
        argv: 인수 리스트. None이면 sys.argv[1:] 사용.

    Returns:
        파싱된 Namespace.
    """
    parser = argparse.ArgumentParser(
        prog="boj commit",
        description="문제 폴더 파일을 git commit (BOJ 통계 포함)",
    )
    parser.add_argument(
        "problem_num",
        help="문제 번호 (예: 99999)",
    )
    parser.add_argument(
        "--message", "-m",
        default=None,
        help="커밋 메시지 직접 지정",
    )
    parser.add_argument(
        "--no-stats",
        action="store_true",
        default=False,
        help="BOJ 통계 조회 스킵",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        default=False,
        help="push 프롬프트 스킵",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """boj commit 메인 진입점.

    Args:
        argv: CLI 인수. None이면 sys.argv[1:].

    Returns:
        exit code (0=성공, 1=에러).
    """
    args = parse_args(argv)

    try:
        msg = commit(
            problem_num=args.problem_num,
            custom_message=args.message,
            no_stats=args.no_stats,
        )

        print(f"커밋 메시지: {msg}")

        # push 프롬프트: TTY이고 --no-push가 아닌 경우에만
        if not args.no_push and sys.stdin.isatty():
            try:
                answer = input("GitHub에 푸시하시겠습니까? (y/N): ")
                if answer.strip().lower() in ("y", "yes"):
                    import subprocess
                    result = subprocess.run(
                        ["git", "push"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        print("푸시 완료!")
                    else:
                        print(
                            f"푸시 실패: {result.stderr.strip()}",
                            file=sys.stderr,
                        )
                else:
                    print(
                        "푸시를 건너뛰었습니다. "
                        "나중에 'git push'로 푸시하세요."
                    )
            except (EOFError, KeyboardInterrupt):
                print("\n푸시를 건너뛰었습니다.")

        return 0

    except BojError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n중단되었습니다.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
