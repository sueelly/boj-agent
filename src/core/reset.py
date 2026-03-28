"""Solution 파일 초기화 모듈.

Issue #87 — boj reset 명령어.
Solution 파일을 git의 초기 커밋 상태로 되돌린다.
"""

import shutil
import subprocess
from pathlib import Path

from src.core.exceptions import BojError


def find_solution_file(problem_dir: Path, lang: str) -> Path | None:
    """문제 디렉터리에서 Solution 파일을 찾는다."""
    candidates = {
        "java": "Solution.java",
        "python": "solution.py",
        "cpp": "Solution.cpp",
        "c": "Solution.c",
        "kotlin": "Solution.kt",
    }
    filename = candidates.get(lang, f"Solution.{lang}")
    path = problem_dir / filename
    return path if path.exists() else None


def backup_solution(solution_path: Path) -> Path:
    """Solution 파일을 .bak으로 백업한다.

    Returns:
        백업 파일 경로.
    """
    bak_path = solution_path.with_suffix(solution_path.suffix + ".bak")
    shutil.copy2(solution_path, bak_path)
    return bak_path


def restore_solution(problem_dir: Path, solution_path: Path) -> None:
    """git checkout으로 Solution 파일을 초기 상태로 복원한다.

    Raises:
        BojError: git이 없거나 복원 실패 시.
    """
    rel_path = solution_path.relative_to(problem_dir.parent)
    result = subprocess.run(
        ["git", "checkout", "HEAD", "--", str(rel_path)],
        cwd=str(problem_dir.parent),
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise BojError(
            f"Solution 복원 실패: {result.stderr.strip() or 'git checkout 에러'}"
        )


def cleanup_submit(problem_dir: Path) -> bool:
    """submit/ 디렉터리를 삭제한다.

    Returns:
        삭제했으면 True, 없었으면 False.
    """
    submit_dir = problem_dir / "submit"
    if submit_dir.is_dir():
        shutil.rmtree(submit_dir)
        return True
    return False


def reset_problem(
    problem_dir: Path,
    lang: str,
    force: bool = False,
    no_backup: bool = False,
) -> dict:
    """Solution 파일을 초기 상태로 되돌린다.

    Args:
        problem_dir: 문제 폴더 경로.
        lang: 프로그래밍 언어.
        force: True면 확인 없이 진행.
        no_backup: True면 백업 생성 안 함.

    Returns:
        결과 딕셔너리 (backup_path, submit_cleaned 등).

    Raises:
        BojError: Solution 파일이 없을 때.
    """
    solution_path = find_solution_file(problem_dir, lang)
    if solution_path is None:
        raise BojError(
            f"Solution 파일을 찾을 수 없습니다: {problem_dir}"
        )

    result = {"backup_path": None, "submit_cleaned": False}

    # 백업
    if not no_backup:
        result["backup_path"] = backup_solution(solution_path)

    # 복원
    restore_solution(problem_dir, solution_path)

    # submit/ 정리
    result["submit_cleaned"] = cleanup_submit(problem_dir)

    return result
