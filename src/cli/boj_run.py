#!/usr/bin/env python3
"""boj run CLI 래퍼 — 인수 파싱 + 출력 포매팅.

Issue #60 — run.sh Python 마이그레이션.

사용법:
    python -m src.cli.boj_run <문제번호> [--lang java|python]
    또는 boj 디스패처에서 호출.
"""

import argparse
import sys
from pathlib import Path

from src.core.exceptions import BojError, RunMemoryError, RunTimeoutError
from src.core.run import run


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 인수를 파싱한다.

    Args:
        argv: 인수 리스트. None이면 sys.argv[1:] 사용.

    Returns:
        파싱된 Namespace.
    """
    parser = argparse.ArgumentParser(
        prog="boj run",
        description="테스트 실행 (test_cases.json 기반)",
    )
    parser.add_argument(
        "problem_num",
        help="문제 번호 (예: 99999)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        help="언어 override (java|python). 미지정 시 config 사용.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="풀이 루트 디렉터리 override.",
    )
    parser.add_argument(
        "--agent-root",
        default=None,
        help="에이전트 루트 디렉터리 override.",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """boj run 메인 진입점.

    Args:
        argv: CLI 인수. None이면 sys.argv[1:].

    Returns:
        exit code (0=성공, 1=에러).
    """
    args = parse_args(argv)

    solution_root = Path(args.root) if args.root else None
    agent_root = Path(args.agent_root) if args.agent_root else None

    try:
        result = run(
            problem_num=args.problem_num,
            lang=args.lang,
            solution_root=solution_root,
            agent_root=agent_root,
        )

        # stdout/stderr 출력
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)

        return result.returncode

    except RunTimeoutError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except RunMemoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except BojError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n중단되었습니다.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
