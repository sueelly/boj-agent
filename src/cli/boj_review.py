#!/usr/bin/env python3
"""boj review CLI 래퍼 -- 인수 파싱 + 출력 포매팅.

Issue #67 -- review.sh Python 마이그레이션.

사용법:
    python -m src.cli.boj_review <문제번호> [--lang java|python]
    또는 boj 디스패처에서 호출.
"""

import argparse
import sys
from pathlib import Path

from src.core.config import BLUE, GREEN, NC, YELLOW
from src.core.exceptions import BojError
from src.core.review import review


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 인수를 파싱한다.

    Args:
        argv: 인수 리스트. None이면 sys.argv[1:] 사용.

    Returns:
        파싱된 Namespace.
    """
    parser = argparse.ArgumentParser(
        prog="boj review",
        description="에이전트로 리뷰 요청 (또는 에디터+클립보드 fallback)",
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
    """boj review 메인 진입점.

    Args:
        argv: CLI 인수. None이면 sys.argv[1:].

    Returns:
        exit code (0=성공, 1=에러).
    """
    args = parse_args(argv)

    solution_root = Path(args.root) if args.root else None
    agent_root = Path(args.agent_root) if args.agent_root else None

    try:
        result = review(
            problem_num=args.problem_num,
            lang=args.lang,
            solution_root=solution_root,
            agent_root=agent_root,
        )

        if result is not None:
            # 에이전트 실행 성공
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
            if result.stdout and result.stdout.strip():
                print(
                    f"\n{GREEN}submit/REVIEW.md 저장 완료{NC}",
                    file=sys.stderr,
                )
        else:
            # fallback 모드
            print(
                f"{YELLOW}에이전트가 설정되지 않았습니다. "
                f"에디터에서 '리뷰해줘'를 요청하세요.{NC}",
                file=sys.stderr,
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
