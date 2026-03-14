"""boj submit 통합 테스트 — CLI 경유 전체 흐름.

Issue #69 — submit.sh Python 마이그레이션.
fixture 99999를 사용하여 전체 파이프라인을 검증한다.
"""

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.conftest import FIXTURES_DIR, run_boj, setup_problem_dir


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _setup_java_problem(tmp_path):
    """Java 픽스처 기반 문제 폴더를 구성한다."""
    fix = FIXTURES_DIR / "99999"
    return setup_problem_dir(tmp_path, fix, lang="java")


def _setup_python_problem(tmp_path):
    """Python 픽스처 기반 문제 폴더를 구성한다."""
    fix = FIXTURES_DIR / "99999"
    return setup_problem_dir(tmp_path, fix, lang="python")


# ---------------------------------------------------------------------------
# CLI 통합 테스트
# ---------------------------------------------------------------------------


class TestSubmitPyIntegration:
    """CLI 경유 submit 통합 테스트."""

    def test_java_submit_generates_file(self, boj_env):
        """Java submit 파일이 생성된다."""
        tmp_path, env = boj_env
        fix = FIXTURES_DIR / "99999"
        prob_dir = _setup_java_problem(tmp_path)

        result = run_boj(env, "submit", "99999", "--lang", "java")

        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        submit_file = prob_dir / "submit" / "Submit.java"
        assert submit_file.exists()

        content = submit_file.read_text()
        assert "public class Main" in content
        assert "class Solution" in content

    def test_python_submit_generates_file(self, boj_env):
        """Python submit 파일이 생성된다."""
        tmp_path, env = boj_env
        fix = FIXTURES_DIR / "99999"
        prob_dir = _setup_python_problem(tmp_path)

        result = run_boj(env, "submit", "99999", "--lang", "python")

        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        submit_file = prob_dir / "submit" / "Submit.py"
        assert submit_file.exists()

        content = submit_file.read_text()
        assert "#!/usr/bin/env python3" in content
        assert "class Solution:" in content

    def test_missing_solution_returns_error(self, boj_env):
        """Solution 없으면 에러."""
        tmp_path, env = boj_env

        # 빈 문제 폴더 생성
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        result = run_boj(env, "submit", "99999", "--lang", "java")

        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_missing_problem_dir_returns_error(self, boj_env):
        """SB1: 문제 폴더 없으면 에러."""
        _tmp_path, env = boj_env

        result = run_boj(env, "submit", "99999", "--lang", "java")

        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_force_flag_overwrites(self, boj_env):
        """--force로 기존 파일 덮어쓰기."""
        tmp_path, env = boj_env
        prob_dir = _setup_java_problem(tmp_path)

        # 첫 번째 생성
        result1 = run_boj(env, "submit", "99999", "--lang", "java")
        assert result1.returncode == 0

        # 두 번째 생성 (force 없이) → 에러
        result2 = run_boj(env, "submit", "99999", "--lang", "java")
        assert result2.returncode == 1

        # --force로 덮어쓰기
        result3 = run_boj(
            env, "submit", "99999", "--lang", "java", "--force",
        )
        assert result3.returncode == 0

    def test_open_flag_accepted(self, boj_env):
        """SB10: --open 플래그가 CLI에서 허용된다 (core 레벨에서 mock)."""
        from src.core.submit import open_submit_page

        with patch("src.core.submit.subprocess.Popen") as mock_popen:
            open_submit_page("99999")

        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert "99999" in call_args[1]
        assert "acmicpc.net" in call_args[1]


# ---------------------------------------------------------------------------
# core 레벨 통합 테스트 (CLI 거치지 않음)
# ---------------------------------------------------------------------------


class TestSubmitCoreIntegration:
    """core 함수 직접 호출 통합 테스트."""

    def test_java_with_parse_fixture(self, tmp_path):
        """실제 fixture로 Java submit 생성 (Parse 포함)."""
        from src.core.submit import generate_submit

        fix = FIXTURES_DIR / "99999"
        prob_dir = setup_problem_dir(tmp_path, fix, lang="java")
        template_dir = tmp_path / "templates" / "java"

        submit_path = generate_submit(prob_dir, "java", template_dir)

        content = submit_path.read_text()
        assert "public class Main" in content
        assert "class Solution" in content
        assert "class Parse" in content
        assert "parser.parseAndCallSolve" in content

    def test_java_without_parse(self, tmp_path):
        """SB3: Parse 없을 때 TODO 스텁."""
        from src.core.submit import generate_submit

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        sol = prob_dir / "Solution.java"
        sol.write_text(
            "public class Solution {\n"
            "    public int solve(int n) { return n; }\n"
            "}\n"
        )

        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        submit_path = generate_submit(prob_dir, "java", template_dir)

        content = submit_path.read_text()
        assert "// TODO:" in content
        assert "Parse" not in content.split("// ===== Solution =====")[1]

    def test_python_with_fixture(self, tmp_path):
        """실제 fixture로 Python submit 생성."""
        from src.core.submit import generate_submit

        fix = FIXTURES_DIR / "99999"
        prob_dir = setup_problem_dir(tmp_path, fix, lang="python")
        template_dir = tmp_path / "templates" / "python"

        submit_path = generate_submit(prob_dir, "python", template_dir)

        content = submit_path.read_text()
        assert "#!/usr/bin/env python3" in content
        assert "class Solution:" in content
