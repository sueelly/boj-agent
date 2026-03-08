import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


def run_boj(env, *args, input_text=None):
    tmp_path = Path(env["BOJ_ROOT"])
    return subprocess.run(
        [str(tmp_path / "src" / "boj"), *args],
        cwd=tmp_path, env=env, capture_output=True, text=True,
        input=input_text, timeout=30,
    )


class TestReviewMocking:
    """모킹 테스트 (CI용): BOJ_AGENT_CMD=echo MOCK"""

    def test_review_runs_agent_successfully(self, boj_env, fixture_path):
        """에이전트 설정 시 review가 성공한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        # Create problem dir with make
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        shutil.copy(fix / "Solution.java", prob_dir)

        result = run_boj(env, "review", "99999")
        assert result.returncode == 0

    def test_review_agent_receives_prompt(self, boj_env, fixture_path):
        """에이전트에 리뷰 프롬프트가 전달된다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo"  # echo will print the prompt
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        shutil.copy(fix / "Solution.java", prob_dir)

        result = run_boj(env, "review", "99999")
        assert result.returncode == 0
        # The echo command prints the review prompt
        assert "리뷰" in result.stdout

    def test_review_exits_one_when_no_problem_dir(self, boj_env):
        """문제 폴더가 없으면 exit 1."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"

        result = run_boj(env, "review", "99999")
        assert result.returncode == 1
        assert "Error:" in result.stderr

    def test_review_warns_when_no_solution(self, boj_env, fixture_path):
        """Solution 파일이 없으면 Warning을 출력하지만 계속 진행한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")
        # Don't copy Solution — no Solution.* files

        result = run_boj(env, "review", "99999")
        # Should still succeed (warning only)
        assert result.returncode == 0
        assert "Warning:" in result.stderr or "Solution" in result.stderr


class TestReviewFallback:
    """에이전트 미설정 시 fallback 동작."""

    def test_fallback_when_no_agent(self, boj_env, fixture_path):
        """BOJ_AGENT_CMD 미설정 시 에디터 fallback."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")

        # Now remove agent cmd
        env.pop("BOJ_AGENT_CMD", None)
        # Also make sure no config file for agent
        config_dir = Path(env["BOJ_CONFIG_DIR"])
        config_dir.mkdir(parents=True, exist_ok=True)

        result = run_boj(env, "review", "99999")
        # Fallback uses boj_open_editor which is BOJ_EDITOR=true (noop)
        assert result.returncode == 0
        # Should mention editor or clipboard fallback
        combined = result.stdout + result.stderr
        assert "에디터" in combined or "클립보드" in combined or "리뷰" in combined


class TestReviewAgentFailure:
    """에이전트 실행 실패 시 에러."""

    def test_exits_one_when_agent_fails(self, boj_env, fixture_path):
        """에이전트가 실패(exit 1)하면 review도 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "false"  # `false` command always exits 1
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        shutil.copy(fix / "Solution.java", prob_dir)

        result = run_boj(env, "review", "99999")
        assert result.returncode == 1
        assert "Error:" in result.stderr
