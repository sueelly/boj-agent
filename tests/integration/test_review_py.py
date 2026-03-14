"""boj review 통합 테스트 -- subprocess로 실행.

Issue #67 -- Python 마이그레이션.
edge-cases RV1-RV4 커버리지 (integration 레벨).
"""

import shutil
from pathlib import Path

import pytest

from tests.conftest import run_boj, setup_problem_dir

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _setup_review_dir(tmp_path, fix, lang="java"):
    """리뷰 테스트용 문제 폴더를 구성한다."""
    prob_dir = setup_problem_dir(tmp_path, fix, lang=lang)

    # prompts/review.md 확인 (boj_env가 복사)
    prompts_dir = tmp_path / "prompts"
    assert prompts_dir.exists(), "prompts/ should be copied by boj_env"

    return prob_dir


# ---------------------------------------------------------------------------
# Happy Path
# ---------------------------------------------------------------------------

class TestReviewHappy:
    """정상 실행 시나리오."""

    def test_review_exits_zero_without_agent(self, boj_env, fixture_path):
        """RV3: 에이전트 미설정 시 fallback 모드로 exit 0."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        _setup_review_dir(tmp_path, fix, lang="java")

        # 에이전트 미설정 + 에디터를 true로 설정 (no-op)
        env["BOJ_EDITOR"] = "true"

        result = run_boj(env, "review", "99999")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )

    def test_review_with_echo_agent(self, boj_env, fixture_path):
        """RV1: echo 에이전트로 정상 리뷰 실행 + REVIEW.md 생성."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = _setup_review_dir(tmp_path, fix, lang="java")

        # echo를 에이전트로 설정 (config 파일)
        config_dir = Path(env["BOJ_CONFIG_DIR"])
        (config_dir / "agent").write_text("echo")

        # AGENT_COMMANDS에 echo가 없으므로 직접 에이전트 명령어로 인식됨
        # echo는 인수를 그대로 출력하므로 성공 exit 0
        result = run_boj(env, "review", "99999")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        # REVIEW.md 파일 생성 확인
        review_path = prob_dir / "submit" / "REVIEW.md"
        assert review_path.exists(), "submit/REVIEW.md should be created"
        assert len(review_path.read_text(encoding="utf-8").strip()) > 0


# ---------------------------------------------------------------------------
# Warning Paths
# ---------------------------------------------------------------------------

class TestReviewWarnings:
    """경고 시나리오."""

    def test_warns_when_solution_missing(self, boj_env):
        """RV2: Solution 파일 없으면 Warning 출력 후 계속 진행."""
        tmp_path, env = boj_env

        # 문제 폴더만 생성 (Solution 없이)
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        result = run_boj(env, "review", "99999")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "Warning" in result.stderr
        assert "Solution" in result.stderr


# ---------------------------------------------------------------------------
# Error Paths
# ---------------------------------------------------------------------------

class TestReviewErrors:
    """에러 경로 시나리오."""

    def test_exits_one_when_problem_dir_missing(self, boj_env):
        """RV3 (폴더 없음): 문제 폴더 없으면 exit 1."""
        _, env = boj_env

        result = run_boj(env, "review", "99999")

        assert result.returncode != 0
        assert "Error" in result.stderr

    def test_exits_one_when_agent_fails(self, boj_env, fixture_path):
        """RV4: 에이전트 실행 실패 시 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        _setup_review_dir(tmp_path, fix, lang="java")

        # 존재하지 않는 에이전트 설정
        config_dir = Path(env["BOJ_CONFIG_DIR"])
        (config_dir / "agent").write_text("nonexistent-agent-xyz")

        result = run_boj(env, "review", "99999")

        assert result.returncode != 0
        assert "Error" in result.stderr
