import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.characterization.conftest import REPO_ROOT, FIXTURES_DIR, run_boj


def setup_problem_for_submit(tmp_path, env, fix_dir, problem_num):
    """make로 폴더 생성 후 Solution.java + test/Parse.java 복사."""
    env["BOJ_CLIENT_TEST_HTML"] = str(fix_dir / "raw.html")
    env["BOJ_AGENT_CMD"] = "echo MOCK"
    run_boj(env, "make", str(problem_num), "--no-open")
    prob_dir = next(tmp_path.glob(f"{problem_num}*"), None)
    assert prob_dir is not None
    shutil.copy(fix_dir / "Solution.java", prob_dir)
    if (fix_dir / "test" / "Parse.java").exists():
        (prob_dir / "test").mkdir(exist_ok=True)
        shutil.copy(fix_dir / "test" / "Parse.java", prob_dir / "test")
    return prob_dir


FIXTURE_PROBLEMS_WITH_JAVA = sorted(
    p.name for p in FIXTURES_DIR.iterdir()
    if p.is_dir() and (p / "Solution.java").exists() and (p / "raw.html").exists()
)


class TestSubmitJavaHappy:
    """Java Submit.java 생성 + 컴파일."""

    @pytest.mark.parametrize("problem_num", FIXTURE_PROBLEMS_WITH_JAVA)
    def test_submit_creates_submit_java(self, boj_env, fixture_path, problem_num):
        """submit 실행 시 submit/Submit.java가 생성된다."""
        tmp_path, env = boj_env
        fix = fixture_path(problem_num)
        prob_dir = setup_problem_for_submit(tmp_path, env, fix, problem_num)

        result = run_boj(env, "submit", str(problem_num), "--force")
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
        assert (prob_dir / "submit" / "Submit.java").exists()

    @pytest.mark.parametrize("problem_num", FIXTURE_PROBLEMS_WITH_JAVA)
    def test_submit_java_compiles(self, boj_env, fixture_path, problem_num):
        """생성된 Submit.java가 javac로 컴파일 된다."""
        tmp_path, env = boj_env
        fix = fixture_path(problem_num)
        prob_dir = setup_problem_for_submit(tmp_path, env, fix, problem_num)

        run_boj(env, "submit", str(problem_num), "--force")
        submit_java = prob_dir / "submit" / "Submit.java"
        assert submit_java.exists()

        # Compile separately to verify — javac requires public class Main in Main.java
        import tempfile
        with tempfile.TemporaryDirectory() as compile_dir:
            main_java = Path(compile_dir) / "Main.java"
            shutil.copy(submit_java, main_java)
            compile_result = subprocess.run(
                ["javac", str(main_java)],
                capture_output=True, text=True, timeout=15,
            )
        assert compile_result.returncode == 0, f"Compile error: {compile_result.stderr}"


class TestSubmitJavaContent:
    """Submit.java 내용 검증."""

    def test_submit_contains_main_class(self, boj_env, fixture_path):
        """Submit.java에 public class Main이 포함된다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = setup_problem_for_submit(tmp_path, env, fix, "99999")

        run_boj(env, "submit", "99999", "--force")

        content = (prob_dir / "submit" / "Submit.java").read_text()
        assert "public class Main" in content
        assert "class Solution" in content  # public 제거됨

    def test_submit_with_parse_includes_parse_class(self, boj_env, fixture_path):
        """Parse.java가 있으면 Submit.java에 Parse 클래스가 포함된다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        prob_dir = setup_problem_for_submit(tmp_path, env, fix, "99999")

        run_boj(env, "submit", "99999", "--force")

        content = (prob_dir / "submit" / "Submit.java").read_text()
        assert "class Parse" in content


class TestSubmitErrors:
    """에러 케이스."""

    def test_exits_one_when_no_problem_dir(self, boj_env):
        """문제 폴더가 없으면 exit 1."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        result = run_boj(env, "submit", "99999", "--force")
        assert result.returncode == 1
        assert "Error:" in result.stderr

    def test_exits_one_when_no_solution(self, boj_env, fixture_path):
        """Solution.java가 없으면 exit 1."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")
        # Don't copy Solution.java

        result = run_boj(env, "submit", "99999", "--force")
        assert result.returncode == 1
        assert "Error:" in result.stderr

    def test_submit_without_parse(self, boj_env, fixture_path):
        """Parse.java 없이 submit 시에도 Submit.java가 생성된다."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        shutil.copy(fix / "Solution.java", prob_dir)
        # Don't copy Parse.java

        result = run_boj(env, "submit", "99999", "--force")
        assert result.returncode == 0
        assert (prob_dir / "submit" / "Submit.java").exists()


class TestSubmitXfail:
    """알려진 취약 동작 문서화."""

    @pytest.mark.xfail(reason="submit.sh sed 기반 Java 접합이 inner class에서 깨질 수 있음")
    def test_submit_with_inner_class(self, boj_env, fixture_path):
        """inner class가 있는 Solution → Submit.java 컴파일 성공."""
        tmp_path, env = boj_env
        fix = fixture_path(99999)
        env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        run_boj(env, "make", "99999", "--no-open")
        prob_dir = next(tmp_path.glob("99999*"))
        # Write Solution with inner class
        (prob_dir / "Solution.java").write_text("""
import java.util.*;

public class Solution {
    private static class Pair {
        int a, b;
        Pair(int a, int b) { this.a = a; this.b = b; }
    }

    public String solve(int a, int b) {
        Pair p = new Pair(a, b);
        return String.valueOf(p.a + p.b);
    }
}
""")
        # Copy Parse
        (prob_dir / "test").mkdir(exist_ok=True)
        shutil.copy(fix / "test" / "Parse.java", prob_dir / "test")

        run_boj(env, "submit", "99999", "--force")
        submit_java = prob_dir / "submit" / "Submit.java"
        assert submit_java.exists()

        import tempfile
        with tempfile.TemporaryDirectory() as compile_dir:
            main_java = Path(compile_dir) / "Main.java"
            shutil.copy(submit_java, main_java)
            compile_result = subprocess.run(
                ["javac", str(main_java)],
                capture_output=True, text=True, timeout=15,
            )
        assert compile_result.returncode == 0, f"Compile error: {compile_result.stderr}"
