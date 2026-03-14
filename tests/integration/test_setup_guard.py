"""setup_done 가드 통합 테스트 — 디스패처 레벨.

Issue #65 — C1: setup_done 없으면 안내 메시지 + boj setup 자동 실행.
디스패처(src/boj)에서 모든 명령어에 공통 적용.
"""

import shutil
from pathlib import Path

import pytest

from tests.conftest import run_boj, setup_problem_dir


class TestSetupGuard:
    """C1: setup_done 가드 동작 검증."""

    def test_shows_setup_message_when_no_setup_done(self, boj_env):
        """setup_done 없으면 설정 안내 메시지가 출력된다."""
        tmp_path, env = boj_env
        # setup_done 삭제
        setup_done = Path(env["BOJ_CONFIG_DIR"]) / "setup_done"
        setup_done.unlink()

        result = run_boj(env, "run", "99999")

        combined = result.stdout + result.stderr
        assert "설정이 완료되지 않았습니다" in combined

    def test_exits_nonzero_when_setup_not_completed(self, boj_env):
        """setup이 완료되지 않으면 (setup_done 생성 안 됨) exit 1."""
        tmp_path, env = boj_env
        setup_done = Path(env["BOJ_CONFIG_DIR"]) / "setup_done"
        setup_done.unlink()

        result = run_boj(env, "run", "99999")

        assert result.returncode != 0

    def test_make_works_when_setup_done_exists(self, boj_env):
        """setup_done 있으면 make 정상 진행 (에이전트 없어서 에러지만 가드는 통과)."""
        tmp_path, env = boj_env
        setup_done = Path(env["BOJ_CONFIG_DIR"]) / "setup_done"
        assert setup_done.exists()

        result = run_boj(env, "make", "99999")

        combined = result.stdout + result.stderr
        # setup 안내 메시지가 없어야 함
        assert "설정이 완료되지 않았습니다" not in combined

    def test_run_works_when_setup_done_exists(self, boj_env, fixture_path):
        """setup_done 있으면 run 정상 실행된다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999")

        combined = result.stdout + result.stderr
        assert "설정이 완료되지 않았습니다" not in combined

    def test_help_skips_guard(self, boj_env):
        """help 명령은 setup_done 가드를 건너뛴다."""
        tmp_path, env = boj_env
        setup_done = Path(env["BOJ_CONFIG_DIR"]) / "setup_done"
        setup_done.unlink()

        result = run_boj(env, "help")

        combined = result.stdout + result.stderr
        assert "설정이 완료되지 않았습니다" not in combined
        assert "사용법:" in combined

    def test_no_args_skips_guard(self, boj_env):
        """인자 없이 실행하면 usage 출력 (가드 건너뜀)."""
        tmp_path, env = boj_env
        setup_done = Path(env["BOJ_CONFIG_DIR"]) / "setup_done"
        setup_done.unlink()

        result = run_boj(env)

        combined = result.stdout + result.stderr
        assert "설정이 완료되지 않았습니다" not in combined
        assert "사용법:" in combined
