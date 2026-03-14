"""boj open 통합 테스트 — subprocess로 실행.

Issue #66 — open.sh Python 마이그레이션.
edge-cases O1-O4 커버리지 (integration 레벨).
"""

import shutil
from pathlib import Path

import pytest

from tests.conftest import run_boj, setup_problem_dir

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


# ---------------------------------------------------------------------------
# Happy Path
# ---------------------------------------------------------------------------

class TestOpenHappy:
    """정상 실행 시나리오."""

    def test_open_existing_problem_dir(self, boj_env, fixture_path):
        """문제 폴더가 존재하면 에디터를 열고 exit 0."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        # BOJ_EDITOR=true (boj_env 기본값) → 항상 성공하는 에디터
        result = run_boj(env, "open", "99999")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "에디터로 열었습니다" in result.stderr

    def test_open_with_editor_flag(self, boj_env, fixture_path):
        """O3: --editor 플래그로 에디터를 override한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        # "true"는 어디서든 사용 가능한 명령어
        result = run_boj(env, "open", "99999", "--editor", "true")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )


# ---------------------------------------------------------------------------
# Error Paths
# ---------------------------------------------------------------------------

class TestOpenErrors:
    """에러 경로 시나리오."""

    def test_exits_one_when_problem_dir_missing(self, boj_env):
        """O1: 문제 폴더 없으면 exit 1 + boj make 안내."""
        _, env = boj_env

        result = run_boj(env, "open", "99999")

        assert result.returncode != 0
        assert "Error:" in result.stderr
        assert "boj make" in result.stderr

    def test_exits_one_when_editor_not_in_path(self, boj_env, fixture_path):
        """O4: 에디터가 PATH에 없으면 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        # 존재하지 않는 에디터
        result = run_boj(env, "open", "99999", "--editor", "nonexistent-editor-xyz")

        assert result.returncode != 0
        assert "Error:" in result.stderr
        assert "찾을 수 없습니다" in result.stderr

    def test_exits_one_when_editor_empty(self, boj_env, fixture_path):
        """O2: 에디터 미설정 시 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        # BOJ_EDITOR를 빈 문자열로 설정
        env["BOJ_EDITOR"] = ""

        result = run_boj(env, "open", "99999")

        assert result.returncode != 0
        assert "Error:" in result.stderr
