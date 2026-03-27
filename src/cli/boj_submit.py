#!/usr/bin/env python3
"""boj submit CLI 래퍼 — 인수 파싱 + 출력 포매팅.

Issue #69 — submit.sh Python 마이그레이션.
Issue #86 — submit 시 제출 페이지 자동 열기를 기본값으로 변경 + config 설정 지원.

사용법:
    python -m src.cli.boj_submit <문제번호> [--lang java|python|cpp|c] [--open] [--no-open] [--force]
    또는 boj 디스패처에서 호출.

브라우저 열기 우선순위: --no-open > --open > submit_open config > 기본값(true)
"""

import argparse
import sys
from pathlib import Path

from src.core.config import BLUE, GREEN, NC, YELLOW, config_get, find_problem_dir
from src.core.exceptions import BojError
from src.core.submit import compile_check, generate_submit, open_submit_page


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 인수를 파싱한다.

    Args:
        argv: 인수 리스트. None이면 sys.argv[1:] 사용.

    Returns:
        파싱된 Namespace.
    """
    parser = argparse.ArgumentParser(
        prog="boj submit",
        description="Submit 파일 생성 (BOJ 제출용)",
    )
    parser.add_argument(
        "problem_id",
        help="BOJ 문제 번호 (예: 99999)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        help="언어 override (java|python|cpp|c). 미지정 시 config 사용.",
    )
    open_group = parser.add_mutually_exclusive_group()
    open_group.add_argument(
        "--open",
        action="store_true",
        default=False,
        dest="open_browser",
        help="제출 페이지 브라우저 열기 (config 무시하고 강제 열기)",
    )
    open_group.add_argument(
        "--no-open",
        action="store_true",
        default=False,
        dest="no_open_browser",
        help="제출 페이지 브라우저 열기 안 함 (config 무시)",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="기존 Submit 파일 덮어쓰기",
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
    """boj submit 메인 진입점.

    Args:
        argv: CLI 인수. None이면 sys.argv[1:].

    Returns:
        exit code (0=성공, 1=에러).
    """
    args = parse_args(argv)

    # 언어 결정
    lang = args.lang or config_get("prog_lang", "java")

    # 루트 경로 결정
    if args.root:
        solution_root = Path(args.root)
    else:
        root_str = config_get("solution_root", "")
        solution_root = Path(root_str) if root_str else Path.cwd()

    if args.agent_root:
        agent_root = Path(args.agent_root)
    else:
        root_str = config_get("boj_agent_root", "")
        agent_root = Path(root_str) if root_str else Path.cwd()

    try:
        # 문제 폴더 찾기
        problem_dir_str = find_problem_dir(str(solution_root), args.problem_id)
        if problem_dir_str is None:
            print(
                f"Error: '{args.problem_id}'로 시작하는 폴더를 찾을 수 없습니다.",
                file=sys.stderr,
            )
            return 1

        problem_dir = Path(problem_dir_str)
        problem_name = problem_dir.name
        template_dir = agent_root / "templates" / lang

        print(f"{BLUE}Submit 생성: {problem_name} ({lang}){NC}")

        # Submit 파일 생성
        submit_path = generate_submit(
            problem_dir=problem_dir,
            lang=lang,
            template_dir=template_dir,
            force=args.force,
        )

        print(f"{GREEN}Submit 생성 완료{NC}")

        # Java 컴파일 검증
        if lang == "java":
            print(f"{BLUE}컴파일 검증 중...{NC}")
            if compile_check(submit_path, template_dir):
                print(f"{GREEN}컴파일 성공{NC}")
            else:
                print(
                    f"{YELLOW}Warning: Submit.java 컴파일 확인 실패. "
                    f"수동으로 확인하세요.{NC}",
                    file=sys.stderr,
                )

        print()
        print(f"{BLUE}생성된 파일: {submit_path}{NC}")
        print()

        # 브라우저 열기 여부 결정: --no-open > --open > submit_open config > 기본값(true)
        if args.no_open_browser:
            should_open = False
        elif args.open_browser:
            should_open = True
        else:
            should_open = config_get("submit_open", "true").lower() not in ("false", "0", "no")

        # 제출 페이지 브라우저 오픈
        if should_open:
            url = f"https://www.acmicpc.net/submit/{args.problem_id}"
            print(f"{BLUE}제출 페이지 오픈: {url}{NC}")
            open_submit_page(args.problem_id)

        print()
        print(f"{GREEN}Submit 완료!{NC}")
        print()
        print("다음 단계:")
        print(f"  1. {submit_path} 내용 확인")
        print(
            f"  2. https://www.acmicpc.net/submit/{args.problem_id} "
            "에서 제출"
        )
        print(
            f"  또는: boj submit {args.problem_id} --no-open  "
            "(브라우저 자동 열기 끄기)"
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
