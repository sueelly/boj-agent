import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure helpers module in this directory is importable regardless of pytest rootdir
sys.path.insert(0, str(Path(__file__).parent))

from helpers import REPO_ROOT, FIXTURES_DIR, run_boj

FIXTURE_PROBLEMS = sorted(
    p.name for p in FIXTURES_DIR.iterdir()
    if p.is_dir() and (p / "raw.html").exists() and (p / "Solution.java").exists()
)

# Module-level parse.py template: test_runner.py expects a module-level
# parse_and_solve(sol, input) function. Fixtures use a Parse class with the
# same method. This shim bridges the two contracts.
_PARSE_PY_SHIM = """\
# Auto-generated shim: delegates to Parse class instance.
from test.parse_impl import Parse as _Parse
_parse_inst = _Parse()

def parse_and_solve(sol, input: str) -> str:
    return _parse_inst.parse_and_solve(sol, input)
"""


def setup_problem(tmp_path, env, fix_dir, problem_num):
    """make로 폴더 생성 후 픽스처에서 솔루션/테스트 복사."""
    env["BOJ_CLIENT_TEST_HTML"] = str(fix_dir / "raw.html")
    env["BOJ_AGENT_CMD"] = "echo MOCK"
    run_boj(env, "make", str(problem_num), "--no-open")
    prob_dir = next(tmp_path.glob(f"{problem_num}*"), None)
    assert prob_dir is not None, f"make failed for {problem_num}"

    # Copy solution and test files
    shutil.copy(fix_dir / "Solution.java", prob_dir)
    if (fix_dir / "solution.py").exists():
        shutil.copy(fix_dir / "solution.py", prob_dir)
    shutil.copytree(fix_dir / "test", prob_dir / "test", dirs_exist_ok=True)
    return prob_dir


def setup_problem_python(tmp_path, env, fix_dir, problem_num):
    """Python용 setup: parse.py를 test_runner.py 계약에 맞게 모듈 함수로 작성."""
    prob_dir = setup_problem(tmp_path, env, fix_dir, problem_num)

    # Rename the fixture's class-based parse.py to parse_impl.py so the shim
    # can import it, then write a module-level parse_and_solve shim as parse.py.
    parse_py = prob_dir / "test" / "parse.py"
    parse_impl_py = prob_dir / "test" / "parse_impl.py"
    if parse_py.exists():
        shutil.copy(parse_py, parse_impl_py)
        # Write module-level function that test_runner.py expects
        parse_py.write_text(
            "# Auto-generated shim for test_runner.py compatibility\n"
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).parent))\n"
            "from parse_impl import Parse as _Parse\n"
            "_parse_inst = _Parse()\n"
            "\n"
            "def parse_and_solve(sol, input: str) -> str:\n"
            "    return _parse_inst.parse_and_solve(sol, input)\n"
        )
    return prob_dir


class TestRunJavaHappy:
    """Java 정답 솔루션으로 run 실행 시 통과."""

    @pytest.mark.parametrize("problem_num", FIXTURE_PROBLEMS)
    def test_run_java_passes(self, boj_env, fixture_path, problem_num):
        """정답 Solution.java로 run 시 모든 테스트가 통과한다."""
        tmp_path, env = boj_env
        fix = fixture_path(problem_num)
        setup_problem(tmp_path, env, fix, problem_num)

        result = run_boj(env, "run", str(problem_num))
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"


class TestRunPythonHappy:
    """Python 정답 솔루션으로 run 실행 시 통과."""

    @pytest.mark.parametrize("problem_num", [
        p for p in FIXTURE_PROBLEMS
        if (FIXTURES_DIR / p / "solution.py").exists()
    ])
    def test_run_python_passes(self, boj_env, fixture_path, problem_num):
        """정답 solution.py로 run --lang python 시 통과한다."""
        tmp_path, env = boj_env
        fix = fixture_path(problem_num)
        setup_problem_python(tmp_path, env, fix, problem_num)

        result = run_boj(env, "run", str(problem_num), "--lang", "python")
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"


class TestRunErrors:
    """에러 케이스."""

    def test_exits_one_when_no_problem_dir(self, boj_env):
        """문제 폴더가 없으면 exit 1."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        result = run_boj(env, "run", "99999")
        assert result.returncode == 1
        assert "Error:" in result.stderr

    def test_exits_one_when_no_test_cases(self, boj_env, fixture_path):
        """test_cases.json이 없으면 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        shutil.copy(fix / "Solution.java", prob_dir)
        # Don't copy test/ — so test_cases.json is missing

        result = run_boj(env, "run", "99999")
        assert result.returncode == 1
        assert "test_cases.json" in result.stderr or "test/test_cases.json" in result.stderr

    def test_exits_one_when_no_solution(self, boj_env, fixture_path):
        """Solution.java가 없으면 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        shutil.copytree(fix / "test", prob_dir / "test", dirs_exist_ok=True)
        # Don't copy Solution.java

        result = run_boj(env, "run", "99999")
        assert result.returncode == 1
        assert "Solution" in result.stderr

    def test_compile_error_when_bad_java(self, boj_env, fixture_path):
        """문법 오류 Solution.java → 컴파일 에러."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        shutil.copytree(fix / "test", prob_dir / "test", dirs_exist_ok=True)
        # Write broken Solution.java
        (prob_dir / "Solution.java").write_text("public class Solution { INVALID SYNTAX }")

        result = run_boj(env, "run", "99999")
        assert result.returncode != 0

    def test_wrong_answer_when_bad_output(self, boj_env, fixture_path):
        """오답 출력 시 테스트 실패가 출력에 표시된다.

        Java Test.java는 테스트 실패 시 exit 0으로 종료하므로
        stdout에 실패 마커(❌ 또는 '실패')가 있는지 검증한다.
        """
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        shutil.copytree(fix / "test", prob_dir / "test", dirs_exist_ok=True)
        # Write wrong-answer Solution (always returns "0" instead of sum)
        (prob_dir / "Solution.java").write_text(
            "public class Solution {\n"
            "    public int solve(int a, int b) { return 0; }\n"
            "}\n"
        )

        result = run_boj(env, "run", "99999")
        # Java Test.java exits 0 even on wrong answers; verify failure is reported
        combined = result.stdout + result.stderr
        assert "실패" in combined or "\u274c" in combined, (
            f"Expected failure marker in output.\nstdout={result.stdout}\nstderr={result.stderr}"
        )
