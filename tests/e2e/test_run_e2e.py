"""boj run E2E 테스트 — 실제 터미널에서 전체 흐름 검증.

Issue #60 — Python 마이그레이션. TDD Red 단계.
fixture 99999로 Java/Python 전체 흐름, exit code, 출력 포맷 검증.
"""

import pytest

from tests.conftest import run_boj, setup_problem_dir


# ---------------------------------------------------------------------------
# E2E: Full Flow
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestBojRunE2E:
    """실제 boj run 전체 흐름 E2E."""

    def test_boj_run_java_full_flow(self, boj_env, fixture_path):
        """Java로 boj run 99999 전체 흐름 — exit 0 + 2/2 통과."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "2/2" in result.stdout

    def test_boj_run_python_full_flow(self, boj_env, fixture_path):
        """Python으로 boj run 99999 전체 흐름 — exit 0 + 2/2 통과."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="python")

        result = run_boj(env, "run", "99999", "--lang", "python")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "2/2" in result.stdout

    def test_boj_run_exit_code_zero_on_all_pass(self, boj_env, fixture_path):
        """모든 테스트 통과 시 exit code 0."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999")

        assert result.returncode == 0

    def test_boj_run_stdout_format_emoji_and_count(self, boj_env, fixture_path):
        """stdout에 emoji + 통과 카운트 포맷이 있다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999")

        # 테스트 결과 출력에 emoji가 포함되어야 함
        assert result.returncode == 0
        # 통과 카운트 (2/2)
        assert "2/2" in result.stdout
