"""boj run 통합 테스트 — subprocess로 실행.

Issue #60 — Python 마이그레이션 + 리소스 제한. TDD Red 단계.
edge-cases R1-R17 커버리지 (integration 레벨).
"""

import platform
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.conftest import run_boj, setup_problem_dir

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


# ---------------------------------------------------------------------------
# Happy Path
# ---------------------------------------------------------------------------

class TestRunHappy:
    """정상 실행 시나리오."""

    def test_run_java_passes_two_of_two(self, boj_env, fixture_path):
        """R1: Java 정답으로 run 실행 시 2/2 통과한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "2/2" in result.stdout

    def test_run_python_passes_two_of_two(self, boj_env, fixture_path):
        """R2: Python 정답으로 run 실행 시 2/2 통과한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="python")

        result = run_boj(env, "run", "99999", "--lang", "python")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "2/2" in result.stdout


# ---------------------------------------------------------------------------
# Branches
# ---------------------------------------------------------------------------

class TestRunBranches:
    """분기 시나리오."""

    def test_run_lang_override_flag(self, boj_env, fixture_path):
        """R4: --lang 플래그로 언어를 override한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = setup_problem_dir(tmp_path, fix, lang="python")

        result = run_boj(env, "run", "99999", "--lang", "python")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "2/2" in result.stdout

    def test_run_partial_pass_shows_count(self, boj_env, fixture_path):
        """R5: 일부 테스트만 통과하면 카운트를 보여준다."""
        import json

        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = setup_problem_dir(tmp_path, fix, lang="java")

        # 하나를 틀리게 수정
        tc_file = prob_dir / "test" / "test_cases.json"
        data = json.loads(tc_file.read_text())
        data["testCases"][1]["expected"] = "999"  # 틀린 답
        tc_file.write_text(json.dumps(data, ensure_ascii=False))

        result = run_boj(env, "run", "99999")

        assert "1/2" in result.stdout

    def test_run_warns_when_readme_missing(self, boj_env, fixture_path):
        """R15: README.md 없으면 Warning 출력 후 기본 제한으로 실행한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = setup_problem_dir(tmp_path, fix, lang="python")

        # README.md 삭제
        readme = prob_dir / "README.md"
        if readme.exists():
            readme.unlink()

        result = run_boj(env, "run", "99999", "--lang", "python")

        assert result.returncode == 0, (
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert "Warning" in result.stderr
        assert "README.md" in result.stderr


# ---------------------------------------------------------------------------
# Error Paths
# ---------------------------------------------------------------------------

class TestRunErrors:
    """에러 경로 시나리오."""

    def test_exits_one_when_problem_dir_missing(self, boj_env):
        """R6: 문제 폴더 없으면 exit 1."""
        _, env = boj_env

        result = run_boj(env, "run", "99999")

        assert result.returncode != 0
        assert "Error:" in result.stderr or "Error:" in result.stdout

    def test_exits_one_when_solution_missing(self, boj_env, fixture_path):
        """R7: Solution 파일 없으면 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)

        prob_dir = tmp_path / "99999-두수의합"
        prob_dir.mkdir()
        shutil.copytree(fix / "test", prob_dir / "test")
        if (fix / "readme.md").exists():
            shutil.copy(fix / "readme.md", prob_dir / "README.md")
        # Solution.java 없음

        result = run_boj(env, "run", "99999")

        assert result.returncode != 0

    def test_exits_one_when_test_cases_missing(self, boj_env, fixture_path):
        """R8: test_cases.json 없으면 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)

        prob_dir = tmp_path / "99999-두수의합"
        prob_dir.mkdir()
        shutil.copy(fix / "Solution.java", prob_dir)
        if (fix / "readme.md").exists():
            shutil.copy(fix / "readme.md", prob_dir / "README.md")
        # test/ 폴더 없음

        result = run_boj(env, "run", "99999")

        assert result.returncode != 0

    def test_exits_one_when_unsupported_lang(self, boj_env, fixture_path):
        """R9/R12: 미지원 언어 → exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        setup_problem_dir(tmp_path, fix, lang="java")

        result = run_boj(env, "run", "99999", "--lang", "fortran")

        assert result.returncode != 0

    def test_exits_one_when_compile_error(self, boj_env, fixture_path):
        """R10: 컴파일 에러 → exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = setup_problem_dir(tmp_path, fix, lang="java")

        # Solution.java를 깨진 코드로 교체
        (prob_dir / "Solution.java").write_text("class Solution { BROKEN }")

        result = run_boj(env, "run", "99999")

        assert result.returncode != 0


# ---------------------------------------------------------------------------
# Resource Limits
# ---------------------------------------------------------------------------

class TestRunResourceLimits:
    """리소스 제한 시나리오."""

    def test_reports_timeout_when_exceeded(self, boj_env, fixture_path):
        """R16: 시간 초과 시 타임아웃 메시지를 출력한다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = setup_problem_dir(tmp_path, fix, lang="python")

        # README에 매우 짧은 시간 제한 설정 (1초)
        (prob_dir / "README.md").write_text(
            '<p><strong>시간 제한:</strong> 1 초 | '
            '<strong>메모리 제한:</strong> 256 MB</p>'
        )

        # solution.py를 import 시 무한 대기로 교체 (subprocess 전체 timeout)
        (prob_dir / "solution.py").write_text(
            "import time\n"
            "time.sleep(60)  # subprocess timeout 유발\n"
            "class Solution:\n"
            "    def solve(self, a, b):\n"
            "        return a + b\n"
        )

        result = run_boj(env, "run", "99999", "--lang", "python")

        # 시간 초과 에러 메시지가 있어야 함
        combined = result.stdout + result.stderr
        assert "시간 초과" in combined or "Timeout" in combined or "timeout" in combined

    @pytest.mark.skipif(
        platform.system() == "Darwin",
        reason="macOS RLIMIT_RSS는 advisory only — 메모리 제한 미강제",
    )
    def test_reports_memory_error_when_exceeded(self, boj_env, fixture_path):
        """R17: 메모리 초과 시 메모리 에러 메시지를 출력한다 (Linux only)."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = setup_problem_dir(tmp_path, fix, lang="python")

        # README에 매우 작은 메모리 제한
        (prob_dir / "README.md").write_text(
            '<p><strong>시간 제한:</strong> 5 초 | '
            '<strong>메모리 제한:</strong> 4 MB</p>'
        )

        # solution.py를 큰 메모리 사용으로 교체
        (prob_dir / "solution.py").write_text(
            "class Solution:\n"
            "    def solve(self, a, b):\n"
            "        x = [0] * (100 * 1024 * 1024)\n"
            "        return a + b\n"
        )

        result = run_boj(env, "run", "99999", "--lang", "python")

        # 메모리 초과 관련 에러
        combined = result.stdout + result.stderr
        assert (
            "메모리 초과" in combined
            or "Memory" in combined
            or "memory" in combined
            or result.returncode != 0
        )
