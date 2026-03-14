"""boj commit 통합 테스트 -- CLI 디스패처 경유.

Issue #68 -- commit.sh Python 마이그레이션.
edge-cases CT1-CT9 커버리지 (integration 레벨).
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from tests.conftest import run_boj, setup_problem_dir

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


def _init_git(tmp_path, env):
    """git init + empty initial commit으로 커밋 가능한 상태를 만든다.

    문제 폴더 파일은 staging하지 않는다 (boj commit이 staging할 수 있도록).
    """
    subprocess.run(
        ["git", "commit", "-m", "initial", "--allow-empty"],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
    )


# ---------------------------------------------------------------------------
# Happy Path
# ---------------------------------------------------------------------------

class TestCommitHappy:
    """정상 커밋 시나리오."""

    def test_commit_with_no_stats(self, boj_env, fixture_path):
        """--no-stats로 통계 조회 없이 커밋한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")
        _init_git(tmp_path, env)

        result = run_boj(env, "commit", "99999", "--no-stats", "--no-push")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "커밋 메시지" in result.stdout

        # git log 확인
        log = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert "풀이 완료" in log.stdout

    def test_commit_with_custom_message(self, boj_env, fixture_path):
        """--message로 커밋 메시지를 직접 지정한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")
        _init_git(tmp_path, env)

        result = run_boj(
            env, "commit", "99999",
            "--no-stats", "--no-push",
            "-m", "my custom msg",
        )

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )

        log = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert "my custom msg" in log.stdout


# ---------------------------------------------------------------------------
# Error Cases
# ---------------------------------------------------------------------------

class TestCommitErrors:
    """에러 시나리오."""

    def test_error_when_problem_not_found(self, boj_env):
        """CT1: 문제 폴더가 없으면 에러를 반환한다."""
        tmp_path, env = boj_env
        _init_git(tmp_path, env)

        result = run_boj(env, "commit", "88888", "--no-stats", "--no-push")

        assert result.returncode == 1
        assert "찾을 수 없습니다" in result.stderr

    def test_error_when_not_git_repo(self, boj_env, fixture_path):
        """CT2: git repo가 아니면 에러를 반환한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        # .git 디렉터리 삭제
        git_dir = tmp_path / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)

        result = run_boj(env, "commit", "99999", "--no-stats", "--no-push")

        assert result.returncode == 1
        assert "git" in result.stderr.lower()

    def test_warning_when_nothing_to_commit(self, boj_env, fixture_path):
        """CT3: 변경사항이 없으면 Warning을 출력하고 정상 종료한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")
        _init_git(tmp_path, env)

        # 먼저 한 번 커밋하여 변경사항 소진
        run_boj(env, "commit", "99999", "--no-stats", "--no-push")

        # 다시 커밋 시도 -- 변경사항 없음
        result = run_boj(env, "commit", "99999", "--no-stats", "--no-push")

        assert result.returncode == 0
        assert "변경사항이 없습니다" in result.stderr


# ---------------------------------------------------------------------------
# CT9: pre-staged 변경사항
# ---------------------------------------------------------------------------

class TestCommitPreStaged:
    """CT9: 기존 staged 변경사항과 함께 커밋."""

    def test_preserves_pre_staged_changes(self, boj_env, fixture_path):
        """기존 staged 파일 + 문제 폴더 파일이 함께 커밋된다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")
        _init_git(tmp_path, env)

        # 문제 폴더 외부에 파일 추가 후 staging
        (tmp_path / "extra.txt").write_text("extra content")
        subprocess.run(
            ["git", "add", "extra.txt"],
            cwd=tmp_path,
            env=env,
            check=True,
            capture_output=True,
        )

        result = run_boj(env, "commit", "99999", "--no-stats", "--no-push")

        assert result.returncode == 0

        # extra.txt가 커밋에 포함되었는지 확인
        show = subprocess.run(
            ["git", "show", "--stat", "HEAD"],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert "extra.txt" in show.stdout
