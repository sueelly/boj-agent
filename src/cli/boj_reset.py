"""boj reset CLI 래퍼.

Issue #87 — Solution 파일을 초기 스켈레톤 상태로 되돌린다.
"""

import argparse
import sys
from pathlib import Path

from src.core.config import config_get
from src.core.exceptions import BojError
from src.core.reset import reset_problem
from src.core.run import find_problem_dir

GREEN = "\033[32m"
BLUE = "\033[34m"
NC = "\033[0m"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="boj reset",
        description="Solution 파일을 초기 스켈레톤 상태로 되돌린다.",
    )
    parser.add_argument("problem_id", help="BOJ 문제 번호")
    parser.add_argument("--force", "-f", action="store_true", help="확인 없이 즉시 초기화")
    parser.add_argument("--no-backup", action="store_true", help="백업 없이 초기화")
    parser.add_argument("--lang", default=None, help="언어 override")
    parser.add_argument("--root", default=None, help="풀이 루트 디렉터리 override")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    lang = args.lang or config_get("prog_lang", "java")
    root_str = args.root or config_get("solution_root", "")
    solution_root = Path(root_str) if root_str else Path.cwd()

    problem_dir_str = find_problem_dir(str(solution_root), args.problem_id)
    if problem_dir_str is None:
        print(f"Error: '{args.problem_id}'로 시작하는 폴더를 찾을 수 없습니다.", file=sys.stderr)
        return 1

    problem_dir = Path(problem_dir_str)

    # 확인 프롬프트
    if not args.force:
        answer = input(f"정말 {problem_dir.name}의 Solution을 초기화하시겠습니까? (y/N): ")
        if answer.lower() not in ("y", "yes"):
            print("취소되었습니다.")
            return 0

    try:
        result = reset_problem(problem_dir, lang, force=args.force, no_backup=args.no_backup)
    except BojError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"{GREEN}Solution 초기화 완료: {problem_dir.name}{NC}")
    if result["backup_path"]:
        print(f"  백업: {result['backup_path']}")
    if result["submit_cleaned"]:
        print(f"  submit/ 디렉터리 삭제됨")

    return 0
