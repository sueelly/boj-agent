"""boj add-test CLI 래퍼.

Issue #88 — AI 기반 테스트 케이스 자동 생성.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from src.core.config import config_get
from src.core.exceptions import BojError
from src.core.add_test import (
    load_existing_test_cases,
    merge_test_cases,
    save_test_cases,
    parse_agent_response,
    build_add_test_prompt,
)
from src.core.run import find_problem_dir

GREEN = "\033[32m"
BLUE = "\033[34m"
NC = "\033[0m"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="boj add-test",
        description="AI 기반 테스트 케이스 자동 생성",
    )
    parser.add_argument("problem_id", help="BOJ 문제 번호")
    parser.add_argument("--edge", action="store_true", help="엣지 케이스 생성")
    parser.add_argument("--extreme", action="store_true", help="극한 케이스 생성")
    parser.add_argument("--count", type=int, default=3, help="생성 개수 (기본 3)")
    parser.add_argument("--root", default=None, help="풀이 루트 디렉터리 override")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    mode = "extreme" if args.extreme else ("edge" if args.edge else "basic")

    root_str = args.root or config_get("solution_root", "")
    solution_root = Path(root_str) if root_str else Path.cwd()

    agent_cmd = config_get("agent", "")
    if not agent_cmd:
        print("Error: 에이전트가 설정되지 않았습니다. boj setup을 실행하세요.", file=sys.stderr)
        return 1

    problem_dir_str = find_problem_dir(str(solution_root), args.problem_id)
    if problem_dir_str is None:
        print(f"Error: '{args.problem_id}'로 시작하는 폴더를 찾을 수 없습니다.", file=sys.stderr)
        return 1

    problem_dir = Path(problem_dir_str)

    print(f"{BLUE}[1/3] 기존 테스트 케이스 로드...{NC}", file=sys.stderr)
    existing = load_existing_test_cases(problem_dir)
    print(f"  기존 {len(existing)}개 케이스", file=sys.stderr)

    print(f"{BLUE}[2/3] {mode} 모드 테스트 케이스 {args.count}개 생성 중...{NC}", file=sys.stderr)
    prompt = build_add_test_prompt(problem_dir, mode, args.count, existing)

    import shlex
    cmd = shlex.split(agent_cmd)
    try:
        result = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True,
            cwd=str(problem_dir),
        )
    except FileNotFoundError:
        print(f"Error: 에이전트 명령어를 찾을 수 없습니다: {agent_cmd}", file=sys.stderr)
        return 1

    try:
        new_cases = parse_agent_response(result.stdout)
    except BojError as e:
        print(f"Error: {e}", file=sys.stderr)
        if result.stderr:
            print(f"  stderr: {result.stderr[:200]}", file=sys.stderr)
        return 1

    print(f"{BLUE}[3/3] 테스트 케이스 병합...{NC}", file=sys.stderr)
    merged, added = merge_test_cases(existing, new_cases, mode=mode)

    if added == 0:
        print("Warning: 모든 케이스가 중복입니다. 추가된 케이스 없음.", file=sys.stderr)
        return 0

    tc_path = save_test_cases(problem_dir, merged)

    print(f"{GREEN}완료! {added}개 테스트 케이스 추가 (총 {len(merged)}개){NC}")
    print(f"  저장: {tc_path}")

    return 0
