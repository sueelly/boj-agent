"""boj make CLI — core.make 위 얇은 래퍼.

Usage:
    python -m src.cli.boj_make 1000
    python -m src.cli.boj_make 1000 --lang python --image-mode skip
    python -m src.cli.boj_make 1000 -f --keep-artifacts
"""

import argparse
import sys
from pathlib import Path

from src.core.config import config_get, DEFAULTS
from src.core.exceptions import BojError
from src.core.make import (
    ensure_setup,
    fetch_problem,
    generate_readme,
    generate_spec,
    generate_skeleton,
    open_editor,
    cleanup_artifacts,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        prog="boj make",
        description="BOJ 문제 풀이 환경을 자동 생성한다.",
    )
    parser.add_argument(
        "problem_id",
        help="BOJ 문제 번호 (예: 1000)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        help="프로그래밍 언어 (기본: config 설정값)",
    )
    parser.add_argument(
        "--image-mode",
        default="download",
        choices=["download", "reference", "skip"],
        help="이미지 처리 모드 (기본: download)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="에디터 자동 열기 비활성화",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="artifacts 정리 비활성화",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="기존 폴더 덮어쓰기",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI 진입점.

    Args:
        argv: CLI 인자 리스트. None이면 sys.argv[1:].

    Returns:
        종료 코드. 0=성공, 1=실패.
    """
    args = parse_args(argv)

    try:
        return _run_pipeline(args)
    except BojError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _run_pipeline(args: argparse.Namespace) -> int:
    """파이프라인 실행 (예외는 main()에서 처리).

    Returns:
        종료 코드. 0=성공, 1=실패.
    """
    # Step 사전 조건 (COMMAND-SPEC: setup 완료 시 에이전트 필수, fallback 없음)
    ensure_setup()
    agent_cmd = (config_get("agent") or DEFAULTS.get("agent", "") or "").strip()
    if not agent_cmd:
        print("Error: 에이전트가 설정되지 않았습니다. boj setup을 실행한 뒤 에이전트를 선택하세요.", file=sys.stderr)
        return 1

    # 언어 결정
    lang = args.lang or config_get("prog_lang", DEFAULTS["prog_lang"])

    # solution_root 기반 problem_dir 결정
    solution_root = config_get("solution_root", "")
    if solution_root:
        base_dir = Path(solution_root)
    else:
        base_dir = Path.cwd()

    # Step 0: BOJ fetch → problem.json
    print(f"[1/6] 문제 {args.problem_id} 가져오는 중...", file=sys.stderr)
    problem_dir = fetch_problem(
        args.problem_id,
        image_mode=args.image_mode,
        base_dir=base_dir,
        force=args.force,
    )

    # Step 1: README.md 생성
    print("[2/6] README.md 생성 중...", file=sys.stderr)
    problem_json = problem_dir / "artifacts" / "problem.json"
    generate_readme(problem_json)

    # Step 2: spec 생성 (에이전트 필수)
    print("[3/6] problem.spec.json 생성 중...", file=sys.stderr)
    generate_spec(problem_dir, agent_cmd)

    # Step 3: Solution + Parse 생성 (에이전트)
    print("[4/6] Solution/Parse 생성 중...", file=sys.stderr)
    generate_skeleton(problem_dir, lang, agent_cmd)

    # Step 4: 에디터 오픈
    editor_cmd = config_get("editor", DEFAULTS.get("editor", "")) if not args.no_open else ""
    if editor_cmd:
        print("[5/6] 에디터 열기...", file=sys.stderr)
        open_editor(problem_dir, editor_cmd)
    elif not args.no_open:
        print("[5/6] 에디터 미설정 — 스킵", file=sys.stderr)

    # Step 5: artifacts 정리
    print("[6/6] 정리 중...", file=sys.stderr)
    cleanup_artifacts(problem_dir, keep=args.keep_artifacts, lang=lang)

    print(f"✓ {problem_dir.name} 생성 완료", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
