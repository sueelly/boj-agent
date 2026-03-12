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
from src.core.make import (
    ensure_setup,
    check_existing,
    fetch_problem,
    generate_readme,
    generate_spec,
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

    # Step 사전 조건
    ensure_setup()

    # 언어 결정
    lang = args.lang or config_get("prog_lang", DEFAULTS["prog_lang"])

    # solution_root 기반 problem_dir 결정
    # 신규 키 "boj_solution_root"를 우선 사용하고,
    # 과거 설정과의 호환성을 위해 "solution_root"도 fallback으로 조회한다.
    solution_root = config_get("boj_solution_root") or config_get("solution_root")
    if solution_root:
        base_dir = Path(solution_root)
    else:
        base_dir = Path.cwd()

    # Step 0: BOJ fetch → problem.json
    print(f"[1/5] 문제 {args.problem_id} 가져오는 중...", file=sys.stderr)
    problem_dir = fetch_problem(
        args.problem_id,
        image_mode=args.image_mode,
        base_dir=base_dir,
        force=args.force,
    )

    # Step 1: README.md 생성
    print("[2/5] README.md 생성 중...", file=sys.stderr)
    problem_json = problem_dir / "artifacts" / "problem.json"
    generate_readme(problem_json)

    # Step 2: spec 생성 (에이전트)
    agent_cmd = config_get("agent") or DEFAULTS.get("agent", "")
    if agent_cmd:
        print("[3/5] problem.spec.json 생성 중...", file=sys.stderr)
        generate_spec(problem_dir, agent_cmd)
    else:
        print("[3/5] 에이전트 미설정 — spec 생성 건너뜀", file=sys.stderr)

    # Step 5: artifacts 정리
    print("[5/5] 정리 중...", file=sys.stderr)
    cleanup_artifacts(problem_dir, keep=args.keep_artifacts)

    print(f"✓ {problem_dir.name} 생성 완료", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
