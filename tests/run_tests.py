#!/usr/bin/env python3
"""BOJ CLI 테스트 러너.

Python pytest 테스트를 실행한다.
Issue #50 — run_tests.sh 대체. Issue #56 — bash 테스트 디스커버리 제거.

사용법:
    python tests/run_tests.py [--unit|--integration|--e2e|--all] [--skip-live]
    ./tests/run_tests.py [--unit|--integration|--e2e|--all] [--skip-live]
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent


@dataclass
class Results:
    passed: int = 0
    failed: int = 0


def run_pytest(paths: list[Path], results: Results, extra_args: list[str] | None = None) -> bool:
    """pytest로 Python 테스트 파일들을 실행하고 성공 여부를 반환한다."""
    if not paths:
        return True

    str_paths = [str(p) for p in paths]
    cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"] + (extra_args or []) + str_paths
    print(f"--- pytest {' '.join(p.name for p in paths)} ---")
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    ok = result.returncode == 0
    if ok:
        results.passed += 1
    else:
        results.failed += 1
    print()
    return ok


def collect_pytest(directory: Path, pattern: str = "test_*.py") -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(f for f in directory.glob(pattern) if f.is_file())


def run_unit(results: Results, extra_args: list[str] | None = None) -> None:
    print("=== 단위 테스트 ===")

    unit_dir = TESTS_DIR / "unit"

    py_files = collect_pytest(unit_dir, "test_*.py")
    if py_files:
        run_pytest(py_files, results, extra_args=extra_args)


def run_integration(results: Results, extra_args: list[str] | None = None) -> None:
    print("=== 통합 테스트 ===")

    int_dir = TESTS_DIR / "integration"

    py_files = collect_pytest(int_dir, "test_*.py")
    if py_files:
        run_pytest(py_files, results, extra_args=extra_args)


def run_e2e(results: Results, extra_args: list[str] | None = None) -> None:
    print("=== E2E 테스트 ===")

    e2e_dir = TESTS_DIR / "e2e"

    py_files = collect_pytest(e2e_dir, "test_*.py")
    if py_files:
        run_pytest(py_files, results, extra_args=extra_args)


def main() -> int:
    parser = argparse.ArgumentParser(description="BOJ CLI 테스트 러너")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unit", action="store_true", help="단위 테스트만")
    group.add_argument("--integration", action="store_true", help="통합 테스트만")
    group.add_argument("--e2e", action="store_true", help="E2E 테스트만")
    group.add_argument("--all", action="store_true", help="전체 (기본)")
    parser.add_argument("--skip-live", action="store_true",
                        help="실제 BOJ 서버 라이브 테스트 스킵 (CI용)")
    args = parser.parse_args()

    results = Results()
    extra: list[str] = []
    if args.skip_live:
        extra.append("--skip-live")

    print("==========================================")
    print("BOJ CLI 테스트 실행")
    print("==========================================")
    print()

    if args.unit:
        run_unit(results, extra_args=extra)
    elif args.integration:
        run_integration(results, extra_args=extra)
    elif args.e2e:
        run_e2e(results, extra_args=extra)
    else:
        run_unit(results, extra_args=extra)
        run_integration(results, extra_args=extra)
        run_e2e(results, extra_args=extra)

    print()
    print("==========================================")
    print(f"최종 결과: {results.passed}개 통과, {results.failed}개 실패")
    print("==========================================")

    return 1 if results.failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
