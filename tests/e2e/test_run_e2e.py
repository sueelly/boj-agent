"""boj run E2E 테스트 — 실제 터미널에서 전체 흐름 검증.

Issue #60 — Python 마이그레이션. TDD Red 단계.
fixture 99999로 Java/Python 전체 흐름, exit code, 출력 포맷 검증.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


@pytest.fixture
def boj_env(tmp_path):
    """격리된 BOJ 환경을 생성한다."""
    for d in ("src", "templates", "prompts"):
        src = REPO_ROOT / d
        if src.exists():
            shutil.copytree(src, tmp_path / d)

    # 실행 권한
    for sh in (tmp_path / "src").rglob("*.sh"):
        sh.chmod(0o755)
    (tmp_path / "src" / "boj").chmod(0o755)

    # git init (일부 명령에 필요)
    subprocess.run(
        ["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=tmp_path, check=True, capture_output=True,
    )

    env = os.environ.copy()
    env.update({
        "BOJ_ROOT": str(tmp_path),
        "HOME": str(tmp_path),
        "BOJ_CONFIG_DIR": str(tmp_path / ".config" / "boj"),
        "BOJ_EDITOR": "true",
    })

    return tmp_path, env


@pytest.fixture
def fixture_path():
    """픽스처 경로 헬퍼."""
    def _get(problem_num: int | str) -> Path:
        p = FIXTURES_DIR / str(problem_num)
        assert p.exists(), f"Fixture not found: {p}"
        return p
    return _get


def run_boj(env, *args) -> subprocess.CompletedProcess:
    """격리 환경에서 boj CLI를 실행한다."""
    tmp_path = Path(env["BOJ_ROOT"])
    return subprocess.run(
        [str(tmp_path / "src" / "boj"), *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def setup_problem(tmp_path, fix, lang="java"):
    """픽스처에서 문제 폴더를 구성한다."""
    prob_dir = tmp_path / "99999-두수의합"
    prob_dir.mkdir(exist_ok=True)

    if (fix / "readme.md").exists():
        shutil.copy(fix / "readme.md", prob_dir / "README.md")

    if lang == "java":
        if (fix / "Solution.java").exists():
            shutil.copy(fix / "Solution.java", prob_dir)
    elif lang == "python":
        if (fix / "solution.py").exists():
            shutil.copy(fix / "solution.py", prob_dir)

    if (fix / "test").exists():
        shutil.copytree(fix / "test", prob_dir / "test", dirs_exist_ok=True)

    return prob_dir


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
        setup_problem(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "2/2" in result.stdout

    def test_boj_run_python_full_flow(self, boj_env, fixture_path):
        """Python으로 boj run 99999 전체 흐름 — exit 0 + 2/2 통과."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem(tmp_path, fix, lang="python")

        result = run_boj(env, "run", "99999", "--lang", "python")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "2/2" in result.stdout

    def test_boj_run_exit_code_zero_on_all_pass(self, boj_env, fixture_path):
        """모든 테스트 통과 시 exit code 0."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999")

        assert result.returncode == 0

    def test_boj_run_stdout_format_emoji_and_count(self, boj_env, fixture_path):
        """stdout에 emoji + 통과 카운트 포맷이 있다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999")

        # 테스트 결과 출력에 emoji가 포함되어야 함
        assert result.returncode == 0
        # 통과 카운트 (2/2)
        assert "2/2" in result.stdout
