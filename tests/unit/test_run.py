"""src/core/run.py 단위 테스트.

Issue #60 — boj run Python 마이그레이션. TDD Red 단계.
edge-cases R1-R17 커버리지.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# parse_resource_limits
# ---------------------------------------------------------------------------

class TestParseResourceLimits:
    """README.md에서 시간/메모리 제한을 파싱한다."""

    def test_parse_time_limit_extracts_seconds(self, tmp_path):
        """R13: '1 초' → 1.0초로 파싱한다."""
        from src.core.run import parse_resource_limits

        readme = tmp_path / "README.md"
        readme.write_text(
            '<p><strong>시간 제한:</strong> 1 초 | '
            '<strong>메모리 제한:</strong> 256 MB</p>'
        )

        time_sec, memory_mb = parse_resource_limits(readme)

        assert time_sec == 1.0

    def test_parse_memory_limit_extracts_mb(self, tmp_path):
        """R14: '256 MB' → 256으로 파싱한다."""
        from src.core.run import parse_resource_limits

        readme = tmp_path / "README.md"
        readme.write_text(
            '<p><strong>시간 제한:</strong> 2 초 | '
            '<strong>메모리 제한:</strong> 256 MB</p>'
        )

        time_sec, memory_mb = parse_resource_limits(readme)

        assert memory_mb == 256

    def test_parse_time_limit_decimal(self, tmp_path):
        """R13: '1.5 초' → 1.5초로 파싱한다."""
        from src.core.run import parse_resource_limits

        readme = tmp_path / "README.md"
        readme.write_text(
            '<p><strong>시간 제한:</strong> 1.5 초 | '
            '<strong>메모리 제한:</strong> 128 MB</p>'
        )

        time_sec, memory_mb = parse_resource_limits(readme)

        assert time_sec == 1.5
        assert memory_mb == 128

    def test_parse_time_limit_two_seconds(self, tmp_path):
        """R13: '2 초' → 2.0초로 파싱한다."""
        from src.core.run import parse_resource_limits

        readme = tmp_path / "README.md"
        readme.write_text(
            '<p><strong>시간 제한:</strong> 2 초 | '
            '<strong>메모리 제한:</strong> 512 MB</p>'
        )

        time_sec, memory_mb = parse_resource_limits(readme)

        assert time_sec == 2.0
        assert memory_mb == 512

    def test_parse_limits_returns_defaults_when_no_readme(self, tmp_path):
        """R15: README.md가 없으면 기본값(5초, 256MB)을 반환한다."""
        from src.core.run import parse_resource_limits

        time_sec, memory_mb = parse_resource_limits(tmp_path / "nonexistent.md")

        assert time_sec == 5.0
        assert memory_mb == 256

    def test_parse_limits_returns_defaults_when_no_match(self, tmp_path):
        """R15: README.md에 제한 정보가 없으면 기본값을 반환한다."""
        from src.core.run import parse_resource_limits

        readme = tmp_path / "README.md"
        readme.write_text("<h1>문제</h1><p>내용만 있는 README</p>")

        time_sec, memory_mb = parse_resource_limits(readme)

        assert time_sec == 5.0
        assert memory_mb == 256

    def test_parse_limits_from_real_fixture(self):
        """R13+R14: 실제 fixture readme.md에서 제한을 파싱한다."""
        from src.core.run import parse_resource_limits

        fixture_readme = (
            Path(__file__).parent.parent / "fixtures" / "99999" / "readme.md"
        )
        if not fixture_readme.exists():
            pytest.skip("fixture 99999/readme.md 없음")

        time_sec, memory_mb = parse_resource_limits(fixture_readme)

        assert time_sec == 5.0
        assert memory_mb == 256


# ---------------------------------------------------------------------------
# normalize_test_cases
# ---------------------------------------------------------------------------

class TestNormalizeTestCases:
    """test_cases.json 정규화 (id/description 자동 부여)."""

    def test_fills_missing_id_and_description(self, tmp_path):
        """R3: id/description 없는 케이스에 자동으로 값을 부여한다."""
        from src.core.run import normalize_test_cases

        tc_file = tmp_path / "test_cases.json"
        tc_file.write_text(json.dumps({
            "testCases": [
                {"input": "1 2", "expected": "3"},
                {"input": "10 20", "expected": "30"},
            ]
        }))

        result = normalize_test_cases(tc_file)

        assert result[0]["id"] == 1
        assert result[0]["description"] == "예제 1"
        assert result[1]["id"] == 2
        assert result[1]["description"] == "예제 2"

    def test_preserves_existing_id(self, tmp_path):
        """기존 id가 있으면 유지한다."""
        from src.core.run import normalize_test_cases

        tc_file = tmp_path / "test_cases.json"
        tc_file.write_text(json.dumps({
            "testCases": [
                {"id": 42, "description": "커스텀", "input": "1 2", "expected": "3"},
            ]
        }))

        result = normalize_test_cases(tc_file)

        assert result[0]["id"] == 42
        assert result[0]["description"] == "커스텀"

    def test_fills_only_missing_fields(self, tmp_path):
        """id만 있고 description 없으면 description만 자동 부여한다."""
        from src.core.run import normalize_test_cases

        tc_file = tmp_path / "test_cases.json"
        tc_file.write_text(json.dumps({
            "testCases": [
                {"id": 1, "input": "1 2", "expected": "3"},
            ]
        }))

        result = normalize_test_cases(tc_file)

        assert result[0]["id"] == 1
        assert result[0]["description"] == "예제 1"

    def test_handles_empty_test_cases(self, tmp_path):
        """빈 testCases 배열 → 빈 리스트 반환."""
        from src.core.run import normalize_test_cases

        tc_file = tmp_path / "test_cases.json"
        tc_file.write_text(json.dumps({"testCases": []}))

        result = normalize_test_cases(tc_file)

        assert result == []

    def test_handles_null_id(self, tmp_path):
        """id가 None이면 자동 부여한다."""
        from src.core.run import normalize_test_cases

        tc_file = tmp_path / "test_cases.json"
        tc_file.write_text(json.dumps({
            "testCases": [
                {"id": None, "input": "1 2", "expected": "3"},
            ]
        }))

        result = normalize_test_cases(tc_file)

        assert result[0]["id"] == 1

    def test_handles_empty_description(self, tmp_path):
        """description이 빈 문자열이면 자동 부여한다."""
        from src.core.run import normalize_test_cases

        tc_file = tmp_path / "test_cases.json"
        tc_file.write_text(json.dumps({
            "testCases": [
                {"id": 1, "description": "", "input": "1 2", "expected": "3"},
            ]
        }))

        result = normalize_test_cases(tc_file)

        assert result[0]["description"] == "예제 1"


# ---------------------------------------------------------------------------
# build_run_command
# ---------------------------------------------------------------------------

class TestBuildRunCommand:
    """언어별 실행 명령 조립."""

    def test_java_command(self, tmp_path):
        """R1: Java 실행 명령을 올바르게 생성한다."""
        from src.core.run import build_run_command

        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        cmd = build_run_command("java", problem_dir, template_dir)

        assert isinstance(cmd, list)
        assert len(cmd) > 0

    def test_python_command(self, tmp_path):
        """R2: Python 실행 명령을 올바르게 생성한다."""
        from src.core.run import build_run_command

        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        template_dir = tmp_path / "templates" / "python"
        template_dir.mkdir(parents=True)

        cmd = build_run_command("python", problem_dir, template_dir)

        assert isinstance(cmd, list)
        assert len(cmd) > 0


# ---------------------------------------------------------------------------
# validate_run_preconditions
# ---------------------------------------------------------------------------

class TestValidateRunPreconditions:
    """실행 전 사전 조건 검증."""

    def test_raises_when_problem_dir_missing(self, tmp_path):
        """R6: 문제 폴더가 없으면 에러를 발생시킨다."""
        from src.core.run import validate_run_preconditions
        from src.core.exceptions import BojError

        with pytest.raises(BojError, match="찾을 수 없습니다"):
            validate_run_preconditions(
                tmp_path / "nonexistent",
                "java",
                tmp_path / "templates" / "java",
            )

    def test_raises_when_test_cases_missing(self, tmp_path):
        """R8: test_cases.json이 없으면 에러를 발생시킨다."""
        from src.core.run import validate_run_preconditions
        from src.core.exceptions import BojError

        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        with pytest.raises(BojError, match="test_cases.json"):
            validate_run_preconditions(
                problem_dir,
                "java",
                tmp_path / "templates" / "java",
            )

    def test_raises_when_solution_missing_java(self, tmp_path):
        """R7: Java Solution.java가 없으면 에러를 발생시킨다."""
        from src.core.run import validate_run_preconditions
        from src.core.exceptions import BojError

        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        test_dir = problem_dir / "test"
        test_dir.mkdir()
        (test_dir / "test_cases.json").write_text('{"testCases": []}')

        with pytest.raises(BojError, match="Solution.java"):
            validate_run_preconditions(
                problem_dir,
                "java",
                tmp_path / "templates" / "java",
            )

    def test_raises_when_solution_missing_python(self, tmp_path):
        """R7: Python solution.py가 없으면 에러를 발생시킨다."""
        from src.core.run import validate_run_preconditions
        from src.core.exceptions import BojError

        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        test_dir = problem_dir / "test"
        test_dir.mkdir()
        (test_dir / "test_cases.json").write_text('{"testCases": []}')

        with pytest.raises(BojError, match="solution.py"):
            validate_run_preconditions(
                problem_dir,
                "python",
                tmp_path / "templates" / "python",
            )

    def test_raises_when_parse_java_missing(self, tmp_path):
        """R4(edge): Java test/Parse.java가 없으면 에러를 발생시킨다."""
        from src.core.run import validate_run_preconditions
        from src.core.exceptions import BojError

        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        (problem_dir / "Solution.java").write_text("class Solution {}")
        test_dir = problem_dir / "test"
        test_dir.mkdir()
        (test_dir / "test_cases.json").write_text('{"testCases": []}')

        with pytest.raises(BojError, match="Parse.java"):
            validate_run_preconditions(
                problem_dir,
                "java",
                tmp_path / "templates" / "java",
            )

    def test_raises_when_template_runner_missing(self, tmp_path):
        """R5(edge): 테스트 러너 템플릿이 없으면 에러를 발생시킨다."""
        from src.core.run import validate_run_preconditions
        from src.core.exceptions import BojError

        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        (problem_dir / "Solution.java").write_text("class Solution {}")
        test_dir = problem_dir / "test"
        test_dir.mkdir()
        (test_dir / "test_cases.json").write_text('{"testCases": []}')
        (test_dir / "Parse.java").write_text("class Parse {}")

        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)
        # Test.java 없음

        with pytest.raises(BojError, match="템플릿"):
            validate_run_preconditions(
                problem_dir,
                "java",
                template_dir,
            )


# ---------------------------------------------------------------------------
# execute_tests (리소스 제한)
# ---------------------------------------------------------------------------

class TestExecuteTests:
    """테스트 실행 + 리소스 제한 적용."""

    def test_timeout_raises_error(self):
        """R16: 시간 초과 시 TimeoutError를 발생시킨다."""
        from src.core.run import execute_tests
        from src.core.exceptions import RunTimeoutError

        # sleep 10을 0.1초 timeout으로 실행 → 시간 초과
        with pytest.raises(RunTimeoutError):
            execute_tests(
                cmd=["python3", "-c", "import time; time.sleep(10)"],
                timeout_sec=0.1,
                memory_mb=256,
                cwd=None,
            )

    def test_successful_execution(self, tmp_path):
        """정상 실행 시 stdout을 반환한다."""
        from src.core.run import execute_tests

        result = execute_tests(
            cmd=["python3", "-c", "print('hello')"],
            timeout_sec=5.0,
            memory_mb=256,
            cwd=str(tmp_path),
        )

        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_nonzero_exit_code_returned(self, tmp_path):
        """비정상 종료 시 returncode를 그대로 반환한다."""
        from src.core.run import execute_tests

        result = execute_tests(
            cmd=["python3", "-c", "import sys; sys.exit(1)"],
            timeout_sec=5.0,
            memory_mb=256,
            cwd=str(tmp_path),
        )

        assert result.returncode == 1


# ---------------------------------------------------------------------------
# run (통합 단위)
# ---------------------------------------------------------------------------

class TestRunFunction:
    """run() 함수 전체 흐름 (subprocess는 mock)."""

    def test_unsupported_lang_raises(self, tmp_path):
        """R12: 미지원 언어 → BojError."""
        from src.core.run import run
        from src.core.exceptions import BojError

        with pytest.raises(BojError, match="지원"):
            run(
                problem_num="99999",
                lang="fortran",
                solution_root=tmp_path,
                agent_root=tmp_path,
            )
