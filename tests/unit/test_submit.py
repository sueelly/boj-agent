"""src/core/submit.py 단위 테스트.

Issue #69 — boj submit Python 마이그레이션.
edge-cases SB1-SB10 커버리지.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.exceptions import BojError
from src.core.submit import (
    compile_check,
    extract_imports,
    generate_c_submit,
    generate_cpp_submit,
    generate_java_submit,
    generate_python_submit,
    generate_submit,
    strip_class_modifiers,
    strip_parse_decorators,
)


# ---------------------------------------------------------------------------
# extract_imports
# ---------------------------------------------------------------------------


class TestExtractImports:
    """Java 소스에서 import 문을 추출한다."""

    def test_extract_basic_imports(self):
        """기본 import 추출."""
        source = (
            "import java.util.*;\n"
            "\n"
            "public class Solution {\n"
            "    public int solve(int a) { return a; }\n"
            "}\n"
        )
        result = extract_imports(source)
        assert result == {"import java.util.*;"}

    def test_extract_multiple_imports(self):
        """여러 import 추출."""
        source = (
            "import java.util.*;\n"
            "import java.io.*;\n"
            "import java.math.BigInteger;\n"
            "\n"
            "public class Solution {}\n"
        )
        result = extract_imports(source)
        assert result == {
            "import java.util.*;",
            "import java.io.*;",
            "import java.math.BigInteger;",
        }

    def test_extract_no_imports(self):
        """import 없는 소스."""
        source = "public class Solution {}\n"
        result = extract_imports(source)
        assert result == set()

    def test_extract_duplicates_returns_set(self):
        """중복 import는 set으로 제거."""
        source = (
            "import java.util.*;\n"
            "import java.util.*;\n"
            "public class Solution {}\n"
        )
        result = extract_imports(source)
        assert result == {"import java.util.*;"}


# ---------------------------------------------------------------------------
# strip_class_modifiers
# ---------------------------------------------------------------------------


class TestStripClassModifiers:
    """public class -> class 변환, import/package 제거."""

    def test_public_class_to_class(self):
        """public class Solution -> class Solution."""
        source = (
            "import java.util.*;\n"
            "package com.example;\n"
            "\n"
            "public class Solution {\n"
            "    public int solve(int a) { return a; }\n"
            "}\n"
        )
        result = strip_class_modifiers(source)
        assert "class Solution {" in result
        assert "public class Solution" not in result

    def test_removes_import_lines(self):
        """import 라인 제거."""
        source = (
            "import java.util.*;\n"
            "public class Solution {}\n"
        )
        result = strip_class_modifiers(source)
        assert "import" not in result

    def test_removes_package_lines(self):
        """package 라인 제거."""
        source = (
            "package com.example;\n"
            "public class Solution {}\n"
        )
        result = strip_class_modifiers(source)
        assert "package" not in result

    def test_preserves_inner_class(self):
        """SB6: inner class는 보존."""
        source = (
            "public class Solution {\n"
            "    static class Node {\n"
            "        int val;\n"
            "    }\n"
            "    public int solve(int a) { return a; }\n"
            "}\n"
        )
        result = strip_class_modifiers(source)
        assert "static class Node" in result
        assert "int val;" in result


# ---------------------------------------------------------------------------
# strip_parse_decorators
# ---------------------------------------------------------------------------


class TestStripParseDecorators:
    """Parse implements ParseAndCallSolve, @Override 제거."""

    def test_removes_implements(self):
        """implements ParseAndCallSolve 제거."""
        source = (
            "import java.util.*;\n"
            "\n"
            "public class Parse implements ParseAndCallSolve {\n"
            "    @Override\n"
            "    public String parseAndCallSolve(Solution sol, String input) {\n"
            "        return \"\";\n"
            "    }\n"
            "}\n"
        )
        result = strip_parse_decorators(source)
        assert "implements ParseAndCallSolve" not in result
        assert "class Parse {" in result

    def test_removes_override(self):
        """@Override 제거."""
        source = (
            "public class Parse implements ParseAndCallSolve {\n"
            "    @Override\n"
            "    public String parseAndCallSolve(Solution sol, String input) {\n"
            "        return \"\";\n"
            "    }\n"
            "}\n"
        )
        result = strip_parse_decorators(source)
        assert "@Override" not in result

    def test_public_class_to_class(self):
        """public class Parse -> class Parse."""
        source = "public class Parse implements ParseAndCallSolve {}\n"
        result = strip_parse_decorators(source)
        assert "class Parse {" in result
        assert "public class Parse" not in result

    def test_removes_import_and_package(self):
        """import/package 라인 제거."""
        source = (
            "import java.util.*;\n"
            "package test;\n"
            "public class Parse {}\n"
        )
        result = strip_parse_decorators(source)
        assert "import" not in result
        assert "package" not in result


# ---------------------------------------------------------------------------
# generate_java_submit
# ---------------------------------------------------------------------------


class TestGenerateJavaSubmit:
    """Java Submit 파일 생성."""

    def test_with_parse(self, tmp_path):
        """Parse 있을 때 parseAndCallSolve 호출 포함."""
        sol = tmp_path / "Solution.java"
        sol.write_text(
            "import java.util.*;\n"
            "\n"
            "public class Solution {\n"
            "    public int solve(int a, int b) {\n"
            "        return a + b;\n"
            "    }\n"
            "}\n"
        )
        parse = tmp_path / "Parse.java"
        parse.write_text(
            "import java.util.*;\n"
            "\n"
            "public class Parse implements ParseAndCallSolve {\n"
            "    @Override\n"
            "    public String parseAndCallSolve("
            "Solution sol, String input) {\n"
            "        return \"\";\n"
            "    }\n"
            "}\n"
        )
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        result = generate_java_submit(sol, parse, template_dir)

        assert "public class Main {" in result
        assert "class Solution {" in result
        assert "class Parse {" in result
        assert "parser.parseAndCallSolve(sol, input)" in result
        assert "import java.util.*;" in result
        assert "import java.io.*;" in result
        # import/package 제거 확인 (Solution/Parse 블록 내)
        assert "// ===== Solution =====" in result
        assert "// ===== Parse =====" in result
        # @Override, implements 제거 확인
        assert "@Override" not in result
        assert "implements ParseAndCallSolve" not in result

    def test_without_parse(self, tmp_path):
        """Parse 없을 때 TODO 스텁 포함."""
        sol = tmp_path / "Solution.java"
        sol.write_text(
            "public class Solution {\n"
            "    public int solve(int n) {\n"
            "        return n;\n"
            "    }\n"
            "}\n"
        )
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        result = generate_java_submit(sol, None, template_dir)

        assert "public class Main {" in result
        assert "class Solution {" in result
        assert "// TODO:" in result
        assert "Parse" not in result.split("// ===== Solution =====")[1]

    def test_with_fixture(self, tmp_path):
        """실제 fixture 파일로 생성."""
        fixtures = Path(__file__).resolve().parent.parent / "fixtures" / "99999"
        sol = fixtures / "Solution.java"
        parse = fixtures / "test" / "Parse.java"
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        result = generate_java_submit(sol, parse, template_dir)

        assert "public class Main {" in result
        assert "class Solution {" in result
        assert "class Parse {" in result
        assert "parser.parseAndCallSolve" in result

    def test_inner_classes_preserved(self, tmp_path):
        """SB6: inner class가 있는 Solution."""
        sol = tmp_path / "Solution.java"
        sol.write_text(
            "import java.util.*;\n"
            "\n"
            "public class Solution {\n"
            "    static class Node {\n"
            "        int val;\n"
            "        Node next;\n"
            "    }\n"
            "    public int solve(int a) { return a; }\n"
            "}\n"
        )
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        result = generate_java_submit(sol, None, template_dir)

        assert "static class Node" in result
        assert "int val;" in result

    def test_duplicate_imports_deduplicated(self, tmp_path):
        """Solution과 Parse의 중복 import 제거."""
        sol = tmp_path / "Solution.java"
        sol.write_text(
            "import java.util.*;\n"
            "import java.io.*;\n"
            "\n"
            "public class Solution {}\n"
        )
        parse = tmp_path / "Parse.java"
        parse.write_text(
            "import java.util.*;\n"
            "import java.io.*;\n"
            "\n"
            "public class Parse implements ParseAndCallSolve {}\n"
        )
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        result = generate_java_submit(sol, parse, template_dir)

        # 중복 없이 각 import 한 번만
        assert result.count("import java.util.*;") == 1
        assert result.count("import java.io.*;") == 1


# ---------------------------------------------------------------------------
# generate_python_submit
# ---------------------------------------------------------------------------


class TestGeneratePythonSubmit:
    """Python Submit 파일 생성."""

    def test_basic_generation(self, tmp_path):
        """기본 Python submit 생성."""
        sol = tmp_path / "solution.py"
        sol.write_text(
            "class Solution:\n"
            "    def solve(self, a: int, b: int) -> int:\n"
            "        return a + b\n"
        )

        result = generate_python_submit(sol)

        assert "#!/usr/bin/env python3" in result
        assert "import sys" in result
        assert "input = sys.stdin.readline" in result
        assert "class Solution:" in result
        assert 'if __name__ == "__main__":' in result

    def test_with_fixture(self):
        """실제 fixture 파일로 생성."""
        fixtures = Path(__file__).resolve().parent.parent / "fixtures" / "99999"
        sol = fixtures / "solution.py"

        result = generate_python_submit(sol)

        assert "class Solution:" in result
        assert "def solve" in result


# ---------------------------------------------------------------------------
# generate_cpp_submit
# ---------------------------------------------------------------------------


class TestGenerateCppSubmit:
    """C++ Submit 파일 생성."""

    def test_removes_existing_includes(self, tmp_path):
        """기존 #include 제거."""
        sol = tmp_path / "Solution.cpp"
        sol.write_text(
            "#include <iostream>\n"
            "#include <vector>\n"
            "\n"
            "class Solution {\n"
            "public:\n"
            "    int solve(int n) { return n; }\n"
            "};\n"
        )

        result = generate_cpp_submit(sol)

        assert "#include <bits/stdc++.h>" in result
        assert "using namespace std;" in result
        assert "#include <iostream>" not in result
        assert "#include <vector>" not in result
        assert "class Solution" in result
        assert "int main()" in result

    def test_preserves_non_include_code(self, tmp_path):
        """#include 아닌 코드는 보존."""
        sol = tmp_path / "Solution.cpp"
        sol.write_text(
            "#include <vector>\n"
            "\n"
            "int custom_func() { return 42; }\n"
        )

        result = generate_cpp_submit(sol)

        assert "int custom_func()" in result


# ---------------------------------------------------------------------------
# generate_c_submit
# ---------------------------------------------------------------------------


class TestGenerateCSubmit:
    """C Submit 파일 생성."""

    def test_basic_generation(self, tmp_path):
        """기본 C submit 생성."""
        sol = tmp_path / "Solution.c"
        sol.write_text(
            "#include <math.h>\n"
            "\n"
            "int solve(int n) { return n; }\n"
        )

        result = generate_c_submit(sol)

        assert "#include <stdio.h>" in result
        assert "#include <stdlib.h>" in result
        assert "#include <string.h>" in result
        assert "#include <math.h>" not in result
        assert "int solve(int n)" in result
        assert "int main()" in result


# ---------------------------------------------------------------------------
# generate_submit (통합)
# ---------------------------------------------------------------------------


class TestGenerateSubmit:
    """Submit 파일 생성 통합 함수."""

    def test_missing_solution_raises_error(self, tmp_path):
        """SB2: Solution 없으면 BojError."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        with pytest.raises(BojError, match="Solution 파일이 없습니다"):
            generate_submit(problem_dir, "java", template_dir)

    def test_existing_submit_no_force_raises_error(self, tmp_path):
        """SB5: 기존 Submit + force=False → BojError."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        # Solution 생성
        sol = problem_dir / "Solution.java"
        sol.write_text("public class Solution {}\n")

        # 기존 Submit 파일
        submit_dir = problem_dir / "submit"
        submit_dir.mkdir()
        (submit_dir / "Submit.java").write_text("existing\n")

        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        with pytest.raises(BojError, match="이미 있습니다"):
            generate_submit(problem_dir, "java", template_dir, force=False)

    def test_existing_submit_with_force_overwrites(self, tmp_path):
        """SB5: force=True면 덮어쓰기."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        sol = problem_dir / "Solution.java"
        sol.write_text("public class Solution {}\n")

        submit_dir = problem_dir / "submit"
        submit_dir.mkdir()
        (submit_dir / "Submit.java").write_text("old content\n")

        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        result = generate_submit(
            problem_dir, "java", template_dir, force=True,
        )

        assert result.exists()
        assert result.read_text() != "old content\n"

    def test_creates_submit_directory(self, tmp_path):
        """SB4: submit/ 폴더 자동 생성."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        sol = problem_dir / "Solution.java"
        sol.write_text("public class Solution {}\n")

        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        result = generate_submit(problem_dir, "java", template_dir)

        assert result.parent.name == "submit"
        assert result.parent.exists()

    def test_unsupported_language_raises_error(self, tmp_path):
        """미지원 언어 BojError."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        template_dir = tmp_path / "templates" / "rust"
        template_dir.mkdir(parents=True)

        with pytest.raises(BojError, match="지원합니다"):
            generate_submit(problem_dir, "rust", template_dir)

    def test_java_submit_end_to_end(self, tmp_path):
        """Java submit 전체 흐름."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        sol = problem_dir / "Solution.java"
        sol.write_text(
            "import java.util.*;\n"
            "\n"
            "public class Solution {\n"
            "    public int solve(int a, int b) {\n"
            "        return a + b;\n"
            "    }\n"
            "}\n"
        )

        test_dir = problem_dir / "test"
        test_dir.mkdir()
        parse = test_dir / "Parse.java"
        parse.write_text(
            "import java.util.*;\n"
            "\n"
            "public class Parse implements ParseAndCallSolve {\n"
            "    @Override\n"
            "    public String parseAndCallSolve("
            "Solution sol, String input) {\n"
            "        return \"\";\n"
            "    }\n"
            "}\n"
        )

        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        result = generate_submit(problem_dir, "java", template_dir)

        assert result.name == "Submit.java"
        content = result.read_text()
        assert "public class Main" in content
        assert "class Solution" in content

    def test_python_submit_end_to_end(self, tmp_path):
        """Python submit 전체 흐름."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        sol = problem_dir / "solution.py"
        sol.write_text(
            "class Solution:\n"
            "    def solve(self, a: int, b: int) -> int:\n"
            "        return a + b\n"
        )

        template_dir = tmp_path / "templates" / "python"
        template_dir.mkdir(parents=True)

        result = generate_submit(problem_dir, "python", template_dir)

        assert result.name == "Submit.py"
        content = result.read_text()
        assert "#!/usr/bin/env python3" in content
        assert "class Solution:" in content

    def test_python_solution_py_found(self, tmp_path):
        """Python은 solution.py 파일을 찾는다."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        (problem_dir / "solution.py").write_text(
            "class Solution:\n    def solve(self): pass\n"
        )

        template_dir = tmp_path / "templates" / "python"
        template_dir.mkdir(parents=True)

        result = generate_submit(problem_dir, "python", template_dir)
        content = result.read_text()

        assert "class Solution:" in content
        assert "def solve" in content

    def test_cpp_submit_end_to_end(self, tmp_path):
        """C++ submit 전체 흐름."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        sol = problem_dir / "Solution.cpp"
        sol.write_text(
            "#include <iostream>\n"
            "\n"
            "class Solution {\n"
            "public:\n"
            "    int solve(int n) { return n; }\n"
            "};\n"
        )

        template_dir = tmp_path / "templates" / "cpp"
        template_dir.mkdir(parents=True)

        result = generate_submit(problem_dir, "cpp", template_dir)

        assert result.name == "Submit.cpp"

    def test_c_submit_end_to_end(self, tmp_path):
        """C submit 전체 흐름."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()

        sol = problem_dir / "Solution.c"
        sol.write_text("int solve(int n) { return n; }\n")

        template_dir = tmp_path / "templates" / "c"
        template_dir.mkdir(parents=True)

        result = generate_submit(problem_dir, "c", template_dir)

        assert result.name == "Submit.c"


# ---------------------------------------------------------------------------
# compile_check
# ---------------------------------------------------------------------------


class TestCompileCheck:
    """Java 컴파일 검증."""

    def test_compile_success(self, tmp_path):
        """SB9: 컴파일 성공."""
        submit = tmp_path / "Submit.java"
        submit.write_text(
            "import java.io.*;\n"
            "import java.util.*;\n"
            "\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"hello\");\n"
            "    }\n"
            "}\n"
        )
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        assert compile_check(submit, template_dir) is True

    def test_compile_failure(self, tmp_path):
        """SB9: 컴파일 실패 시 False (non-fatal)."""
        submit = tmp_path / "Submit.java"
        submit.write_text("this is not valid java code\n")
        template_dir = tmp_path / "templates" / "java"
        template_dir.mkdir(parents=True)

        assert compile_check(submit, template_dir) is False
