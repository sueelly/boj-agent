import json
import os
import shutil
from pathlib import Path

import pytest

from helpers import REPO_ROOT, FIXTURES_DIR, run_boj

FIXTURE_PROBLEMS = sorted(
    p.name for p in FIXTURES_DIR.iterdir()
    if p.is_dir() and (p / "raw.html").exists()
)


class TestMakeHappy:
    """Happy path: make로 폴더 구조가 생성된다."""

    @pytest.mark.parametrize("problem_num", FIXTURE_PROBLEMS)
    def test_creates_problem_dir(self, boj_env, problem_num):
        """make 실행 시 문제 디렉터리가 생성된다."""
        tmp_path, env = boj_env
        fix_dir = FIXTURES_DIR / problem_num
        env["BOJ_CLIENT_TEST_HTML"] = str(fix_dir / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"

        result = run_boj(env, "make", problem_num, "--no-open")

        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
        prob_dir = next(tmp_path.glob(f"{problem_num}*"), None)
        assert prob_dir is not None, "문제 디렉터리 미생성"

    @pytest.mark.parametrize("problem_num", FIXTURE_PROBLEMS)
    def test_creates_problem_json(self, boj_env, problem_num):
        """make 실행 시 artifacts/problem.json이 생성된다."""
        tmp_path, env = boj_env
        fix_dir = FIXTURES_DIR / problem_num
        env["BOJ_CLIENT_TEST_HTML"] = str(fix_dir / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"

        run_boj(env, "make", problem_num, "--no-open")

        prob_dir = next(tmp_path.glob(f"{problem_num}*"))
        pj = prob_dir / "artifacts" / "problem.json"
        assert pj.exists()
        data = json.loads(pj.read_text())
        assert data["problem_num"] == problem_num
        assert data["title"] != ""

    @pytest.mark.parametrize("problem_num", FIXTURE_PROBLEMS)
    def test_creates_readme(self, boj_env, problem_num):
        """make 실행 시 README.md가 생성된다."""
        tmp_path, env = boj_env
        fix_dir = FIXTURES_DIR / problem_num
        env["BOJ_CLIENT_TEST_HTML"] = str(fix_dir / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"

        run_boj(env, "make", problem_num, "--no-open")

        prob_dir = next(tmp_path.glob(f"{problem_num}*"))
        assert (prob_dir / "README.md").exists()
        content = (prob_dir / "README.md").read_text()
        assert len(content) > 0


class TestMakeAgentFallback:
    """에이전트 미설정 시 fallback 동작."""

    def test_fallback_warning_when_no_agent(self, boj_env, fixture_path):
        """BOJ_AGENT_CMD 미설정 시 Warning 출력."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env.pop("BOJ_AGENT_CMD", None)
        # Also ensure no config file agent
        config_dir = Path(env["BOJ_CONFIG_DIR"])
        config_dir.mkdir(parents=True, exist_ok=True)

        result = run_boj(env, "make", "99999", "--no-open")

        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert (
            "Warning:" in result.stderr
            or "fallback" in result.stdout.lower()
            or "에이전트 미설정" in combined
        )


class TestMakeErrors:
    """에러 케이스."""

    def test_exits_one_when_invalid_lang(self, boj_env, fixture_path):
        """잘못된 언어 옵션 시 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"

        result = run_boj(env, "make", "99999", "--lang", "brainfuck", "--no-open")
        assert result.returncode != 0

    def test_exits_one_when_bad_html(self, boj_env):
        """제목 없는 HTML → exit 1."""
        tmp_path, env = boj_env
        bad_html = tmp_path / "bad.html"
        bad_html.write_text("<html><body></body></html>")
        env["BOJ_CLIENT_TEST_HTML"] = str(bad_html)
        env["BOJ_AGENT_CMD"] = "echo MOCK"

        result = run_boj(env, "make", "99999", "--no-open")
        assert result.returncode != 0
        assert "Error:" in result.stderr


class TestMakeOptions:
    """옵션 테스트."""

    def test_help_flag(self, boj_env):
        """--help 시 사용법을 출력하고 exit 0."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        result = run_boj(env, "make", "99999", "--help")
        assert result.returncode == 0
        assert "사용법" in result.stdout or "Usage" in result.stdout
