#!/usr/bin/env python3
"""boj open CLI 래퍼 — 인수 파싱 + 에디터 실행.

Issue #66 — open.sh Python 마이그레이션.

사용법:
    python -m src.cli.boj_open <문제번호> [--editor code|cursor|vim]
    또는 boj 디스패처에서 호출.
"""

import argparse
import sys
from pathlib import Path

from src.core.exceptions import BojError
from src.core.open import open_problem


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 인수를 파싱한다.

    Args:
        argv: 인수 리스트. None이면 sys.argv[1:] 사용.

    Returns:
        파싱된 Namespace.
    """
    parser = argparse.ArgumentParser(
        prog="boj open",
        description="문제 폴더를 에디터로 열기",
    )
    parser.add_argument(
        "problem_id",
        help="문제 번호 (예: 99999)",
    )
    parser.add_argument(
        "--editor",
        default=None,
        help="에디터 override (code|cursor|vim). 미지정 시 config 사용.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="풀이 루트 디렉터리 override.",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """boj open 메인 진입점.

    Args:
        argv: CLI 인수. None이면 sys.argv[1:].

    Returns:
        exit code (0=성공, 1=에러).
    """
    args = parse_args(argv)

    base_dir = Path(args.root) if args.root else None

    try:
        open_problem(
            problem_id=args.problem_id,
            editor=args.editor,
            base_dir=base_dir,
        )
        return 0

    except BojError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n중단되었습니다.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
