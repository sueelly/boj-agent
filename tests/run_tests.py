#!/usr/bin/env python3
"""BOJ CLI 통합 테스트 러너.

Bash 단위/통합 테스트와 Python pytest 테스트를 모두 실행한다.
Issue #50 — run_tests.sh 대체.

사용법:
    python tests/run_tests.py [--unit|--integration|--e2e|--all]
    ./tests/run_tests.py [--unit|--integration|--e2e|--all]
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent


@dataclass
class Results:
    passed: int = 0
    failed: int = 0


def run_bash(path: Path, results: Results) -> bool:
    """bash 스크립트를 실행하고 성공 여부를 반환한다."""
    print(f"--- {path.name} ---")
    result = subprocess.run(["bash", str(path)], cwd=REPO_ROOT)
    ok = result.returncode == 0
    if ok:
        results.passed += 1
    else:
        print(f"FAILED: {path.name}")
        results.failed += 1
    print()
    return ok


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


def collect_bash(directory: Path, pattern: str = "*.sh") -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(f for f in directory.glob(pattern) if f.is_file())


def collect_pytest(directory: Path, pattern: str = "test_*.py") -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(f for f in directory.glob(pattern) if f.is_file())


def run_unit(results: Results) -> None:
    print("=== 단위 테스트 ===")

    unit_dir = TESTS_DIR / "unit"
    cmd_dir = unit_dir / "commands"

    # Bash 단위 테스트
    for f in collect_bash(unit_dir, "test_*.sh"):
        run_bash(f, results)
    for f in collect_bash(cmd_dir, "*.sh"):
        run_bash(f, results)

    # Python 단위 테스트
    py_files = collect_pytest(unit_dir, "test_*.py")
    if py_files:
        run_pytest(py_files, results)


def run_integration(results: Results) -> None:
    print("=== 통합 테스트 ===")

    int_dir = TESTS_DIR / "integration"

    # Bash 통합 테스트
    for f in collect_bash(int_dir, "test_*.sh"):
        run_bash(f, results)

    # Python 통합 테스트
    py_files = collect_pytest(int_dir, "test_*.py")
    if py_files:
        run_pytest(py_files, results)


def run_e2e(results: Results) -> None:
    print("=== E2E 테스트 ===")

    e2e_dir = TESTS_DIR / "e2e"

    for f in collect_bash(e2e_dir, "test_*.sh"):
        run_bash(f, results)

    py_files = collect_pytest(e2e_dir, "test_*.py")
    if py_files:
        run_pytest(py_files, results)


def main() -> int:
    parser = argparse.ArgumentParser(description="BOJ CLI 테스트 러너")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unit", action="store_true", help="단위 테스트만")
    group.add_argument("--integration", action="store_true", help="통합 테스트만")
    group.add_argument("--e2e", action="store_true", help="E2E 테스트만")
    group.add_argument("--all", action="store_true", help="전체 (기본)")
    args = parser.parse_args()

    results = Results()

    print("==========================================")
    print("BOJ CLI 테스트 실행")
    print("==========================================")
    print()

    if args.unit:
        run_unit(results)
    elif args.integration:
        run_integration(results)
    elif args.e2e:
        run_e2e(results)
    else:
        run_unit(results)
        run_integration(results)
        run_e2e(results)

    print()
    print("==========================================")
    print(f"최종 결과: {results.passed}개 통과, {results.failed}개 실패")
    print("==========================================")

    return 1 if results.failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
