"""src/core/reset.py 단위 테스트.

Issue #87 — boj reset 명령어.
"""

import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

import pytest

from src.core.exceptions import BojError
from src.core.reset import (
    find_solution_file,
    backup_solution,
    restore_solution,
    cleanup_submit,
    reset_problem,
)


class TestFindSolutionFile:
    """Solution 파일 탐색."""

    def test_finds_java_solution(self, tmp_path):
        (tmp_path / "Solution.java").write_text("class Solution {}")
        assert find_solution_file(tmp_path, "java") is not None

    def test_finds_python_solution(self, tmp_path):
        (tmp_path / "solution.py").write_text("class Solution: pass")
        assert find_solution_file(tmp_path, "python") is not None

    def test_returns_none_when_missing(self, tmp_path):
        assert find_solution_file(tmp_path, "java") is None


class TestBackupSolution:
    """Solution 백업."""

    def test_creates_bak_file(self, tmp_path):
        sol = tmp_path / "Solution.java"
        sol.write_text("original code")
        bak = backup_solution(sol)
        assert bak.exists()
        assert bak.name == "Solution.java.bak"
        assert bak.read_text() == "original code"

    def test_preserves_original(self, tmp_path):
        sol = tmp_path / "Solution.java"
        sol.write_text("original code")
        backup_solution(sol)
        assert sol.read_text() == "original code"


class TestRestoreSolution:
    """git checkout 기반 복원."""

    def test_calls_git_checkout(self, tmp_path):
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        sol = problem_dir / "Solution.java"
        sol.write_text("modified")

        with patch("src.core.reset.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            restore_solution(problem_dir, sol)

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "git" in cmd
        assert "checkout" in cmd

    def test_raises_on_git_failure(self, tmp_path):
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        sol = problem_dir / "Solution.java"
        sol.write_text("modified")

        with patch("src.core.reset.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="error")
            with pytest.raises(BojError, match="복원 실패"):
                restore_solution(problem_dir, sol)


class TestCleanupSubmit:
    """submit/ 디렉터리 삭제."""

    def test_removes_submit_dir(self, tmp_path):
        submit = tmp_path / "submit"
        submit.mkdir()
        (submit / "Submit.java").write_text("code")
        assert cleanup_submit(tmp_path) is True
        assert not submit.exists()

    def test_returns_false_when_no_submit(self, tmp_path):
        assert cleanup_submit(tmp_path) is False


class TestResetProblem:
    """reset_problem 통합 로직."""

    def test_full_reset_with_backup(self, tmp_path):
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        sol = problem_dir / "Solution.java"
        sol.write_text("modified code")
        submit = problem_dir / "submit"
        submit.mkdir()
        (submit / "Submit.java").write_text("submit")

        with patch("src.core.reset.restore_solution"):
            result = reset_problem(problem_dir, "java", force=True)

        assert result["backup_path"] is not None
        assert result["backup_path"].exists()
        assert result["submit_cleaned"] is True

    def test_no_backup_flag(self, tmp_path):
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        sol = problem_dir / "Solution.java"
        sol.write_text("code")

        with patch("src.core.reset.restore_solution"):
            result = reset_problem(problem_dir, "java", force=True, no_backup=True)

        assert result["backup_path"] is None

    def test_raises_when_no_solution(self, tmp_path):
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        with pytest.raises(BojError, match="찾을 수 없습니다"):
            reset_problem(problem_dir, "java", force=True)
