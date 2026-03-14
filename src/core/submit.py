"""boj submit 핵심 로직 — Submit 파일 생성.

Issue #69 — submit.sh Python 마이그레이션.
"""

import platform
import re
import subprocess
import tempfile
from pathlib import Path

from src.core.config import config_get, find_problem_dir
from src.core.exceptions import BojError


# ── 지원 언어 및 파일명 매핑 ──

_LANG_EXT: dict[str, str] = {
    "java": "java",
    "python": "py",
    "cpp": "cpp",
    "c": "c",
    "kotlin": "kt",
    "go": "go",
}

_SUBMIT_LANGS = frozenset(_LANG_EXT.keys())


# ── Java Submit 생성 ──


def extract_imports(source: str) -> set[str]:
    """Java 소스에서 import 문을 추출한다.

    Args:
        source: Java 소스 코드 문자열.

    Returns:
        import 문 집합 (각 줄 전체, 예: "import java.util.*;").
    """
    return {
        line
        for line in source.splitlines()
        if line.startswith("import ")
    }


def strip_class_modifiers(source: str) -> str:
    """public class → class 변환, import/package 라인 제거.

    Args:
        source: Java 소스 코드 문자열.

    Returns:
        변환된 소스 코드.
    """
    lines = []
    for line in source.splitlines():
        if line.startswith("import ") or line.startswith("package "):
            continue
        line = re.sub(r"^public class Solution", "class Solution", line)
        lines.append(line)
    return "\n".join(lines)


def strip_parse_decorators(source: str) -> str:
    """Parse 클래스에서 implements ParseAndCallSolve, @Override 제거.

    public class Parse → class Parse 변환도 수행한다.
    import/package 라인도 제거한다.

    Args:
        source: Parse.java 소스 코드 문자열.

    Returns:
        변환된 소스 코드.
    """
    lines = []
    for line in source.splitlines():
        if line.startswith("import ") or line.startswith("package "):
            continue
        if re.match(r"^\s*@Override\s*$", line):
            continue
        line = re.sub(r"^public class Parse", "class Parse", line)
        line = re.sub(r"\s+implements\s+ParseAndCallSolve", "", line)
        lines.append(line)
    return "\n".join(lines)


def generate_java_submit(
    solution_path: Path,
    parse_path: Path | None,
    template_dir: Path,
) -> str:
    """Java Submit 파일 내용을 생성한다.

    1. Solution + Parse의 import를 합산하고 중복 제거
    2. public class Main { main() } 생성
    3. Parse 있으면 parseAndCallSolve 호출, 없으면 TODO 스텁
    4. Solution: public class → class, import/package 제거
    5. Parse: implements/Override 제거, import/package 제거

    Args:
        solution_path: Solution.java 파일 경로.
        parse_path: Parse.java 파일 경로. None이면 Parse 없는 모드.
        template_dir: 템플릿 디렉터리 경로 (컴파일 검증 시 사용).

    Returns:
        생성된 Submit.java 파일 내용 문자열.
    """
    solution_src = solution_path.read_text(encoding="utf-8")

    # import 합산 (기본 import + Solution + Parse)
    imports: set[str] = {"import java.util.*;", "import java.io.*;"}
    imports |= extract_imports(solution_src)

    has_parse = parse_path is not None and parse_path.exists()
    parse_src = ""
    if has_parse:
        parse_src = parse_path.read_text(encoding="utf-8")
        imports |= extract_imports(parse_src)

    # import 정렬
    sorted_imports = sorted(imports)

    # Main 클래스 본문
    if has_parse:
        main_body = (
            "        Parse parser = new Parse();\n"
            "        String result = parser.parseAndCallSolve(sol, input);\n"
            "        System.out.println(result);\n"
            "    }\n"
            "}"
        )
    else:
        main_body = (
            "        // TODO: 입력 파싱 후 sol.solve(...) 호출\n"
            "        // StringTokenizer st = new StringTokenizer(input);\n"
            "        // int n = Integer.parseInt(st.nextToken());\n"
            "        // System.out.println(sol.solve(n));\n"
            "    }\n"
            "}"
        )

    main_class = (
        "public class Main {\n"
        "    public static void main(String[] args) throws Exception {\n"
        "        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        String line;\n"
        "        while ((line = br.readLine()) != null) {\n"
        "            sb.append(line).append('\\n');\n"
        "        }\n"
        "        String input = sb.toString().trim();\n"
        "        Solution sol = new Solution();\n"
        + main_body
    )

    # Solution 클래스 변환
    solution_block = strip_class_modifiers(solution_src)

    # 최종 결합
    parts = ["\n".join(sorted_imports), ""]
    parts.append("")
    parts.append(main_class)
    parts.append("")
    parts.append("// ===== Solution =====")
    parts.append(solution_block)

    if has_parse:
        parse_block = strip_parse_decorators(parse_src)
        parts.append("")
        parts.append("// ===== Parse =====")
        parts.append(parse_block)

    return "\n".join(parts) + "\n"


# ── Python Submit 생성 ──


def generate_python_submit(solution_path: Path) -> str:
    """Python Submit 파일 내용을 생성한다.

    #!/usr/bin/env python3 + import sys + solution 내용 + __main__ block.

    Args:
        solution_path: solution.py 파일 경로.

    Returns:
        생성된 Submit.py 파일 내용 문자열.
    """
    solution_src = solution_path.read_text(encoding="utf-8")

    parts = [
        "#!/usr/bin/env python3",
        "import sys",
        "input = sys.stdin.readline",
        "",
        solution_src,
        "",
        "",
        'if __name__ == "__main__":',
        "    data = sys.stdin.read().strip()",
        "    sol = Solution()",
        "    # Parse가 있으면 from test.parse import parse_and_solve 활용 가능",
        "    # result = parse_and_solve(sol, data)",
        "    # print(result)",
        "",
    ]
    return "\n".join(parts)


# ── C/C++ Submit 생성 ──


def generate_cpp_submit(solution_path: Path) -> str:
    """C++ Submit 파일을 생성한다.

    bits/stdc++.h + solution (기존 #include 제거) + main() TODO.

    Args:
        solution_path: Solution.cpp 파일 경로.

    Returns:
        생성된 Submit.cpp 파일 내용 문자열.
    """
    solution_src = solution_path.read_text(encoding="utf-8")

    # 기존 #include 제거
    filtered = [
        line for line in solution_src.splitlines()
        if not line.startswith("#include")
    ]

    parts = [
        "#include <bits/stdc++.h>",
        "using namespace std;",
        "",
        "\n".join(filtered),
        "",
        "int main() {",
        "    ios_base::sync_with_stdio(false);",
        "    cin.tie(NULL);",
        "    // TODO: 입력 파싱 후 solve() 호출",
        "    return 0;",
        "}",
        "",
    ]
    return "\n".join(parts)


def generate_c_submit(solution_path: Path) -> str:
    """C Submit 파일을 생성한다.

    stdio/stdlib/string.h + solution (기존 #include 제거) + main() TODO.

    Args:
        solution_path: Solution.c 파일 경로.

    Returns:
        생성된 Submit.c 파일 내용 문자열.
    """
    solution_src = solution_path.read_text(encoding="utf-8")

    # 기존 #include 제거
    filtered = [
        line for line in solution_src.splitlines()
        if not line.startswith("#include")
    ]

    parts = [
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <string.h>",
        "",
        "\n".join(filtered),
        "",
        "int main() {",
        "    // TODO: 입력 파싱 후 solve() 호출",
        "    return 0;",
        "}",
        "",
    ]
    return "\n".join(parts)


# ── 공통 ──


def _find_solution_file(problem_dir: Path, lang: str) -> Path | None:
    """언어별 Solution 파일을 찾는다.

    Python은 solution.py 우선, Solution.py 차선.

    Args:
        problem_dir: 문제 폴더 경로.
        lang: 프로그래밍 언어.

    Returns:
        Solution 파일 경로. 없으면 None.
    """
    ext = _LANG_EXT[lang]

    if lang == "python":
        # solution.py 우선 (run.sh와 동일)
        lower = problem_dir / "solution.py"
        upper = problem_dir / "Solution.py"
        if lower.exists():
            return lower
        if upper.exists():
            return upper
        return None

    sol = problem_dir / f"Solution.{ext}"
    return sol if sol.exists() else None


def generate_submit(
    problem_dir: Path,
    lang: str,
    template_dir: Path,
    force: bool = False,
) -> Path:
    """Submit 파일 생성 통합 함수.

    Args:
        problem_dir: 문제 폴더 경로.
        lang: 프로그래밍 언어.
        template_dir: 템플릿 디렉터리 경로.
        force: True면 기존 Submit 파일 덮어쓰기.

    Returns:
        생성된 submit 파일 경로.

    Raises:
        BojError: Solution 파일 없음, 미지원 언어, 기존 파일 존재(force=False).
    """
    if lang not in _SUBMIT_LANGS:
        raise BojError(
            f"'submit' 명령은 현재 {'/'.join(sorted(_SUBMIT_LANGS))}만 "
            f"지원합니다."
        )

    # 1. Solution 파일 확인
    solution_path = _find_solution_file(problem_dir, lang)
    if solution_path is None:
        ext = _LANG_EXT[lang]
        if lang == "python":
            raise BojError(
                f"Solution 파일이 없습니다 (solution.py 또는 Solution.{ext}). "
                "먼저 풀이를 작성하세요."
            )
        raise BojError(
            f"Solution 파일이 없습니다 (Solution.{ext}). "
            "먼저 풀이를 작성하세요."
        )

    # 2. submit/ 디렉터리 생성
    submit_dir = problem_dir / "submit"
    submit_dir.mkdir(parents=True, exist_ok=True)

    # 3. Submit 파일 경로 결정
    ext = _LANG_EXT[lang]
    submit_path = submit_dir / f"Submit.{ext}"

    # 4. 기존 파일 존재 + not force → BojError
    if submit_path.exists() and not force:
        raise BojError(
            f"submit/Submit.{ext} 이 이미 있습니다. "
            "덮어쓰려면 --force 옵션을 사용하세요."
        )

    # 5. 언어별 생성 함수 호출
    if lang == "java":
        parse_path = problem_dir / "test" / "Parse.java"
        if not parse_path.exists():
            parse_path = None
        content = generate_java_submit(solution_path, parse_path, template_dir)
    elif lang == "python":
        content = generate_python_submit(solution_path)
    elif lang == "cpp":
        content = generate_cpp_submit(solution_path)
    elif lang == "c":
        content = generate_c_submit(solution_path)
    else:
        # kotlin, go — 에이전트 활용 안내 (submit.sh와 동일)
        raise BojError(
            f"{lang} Submit 생성은 에이전트를 통해 진행하세요."
        )

    # 6. submit 파일 쓰기
    submit_path.write_text(content, encoding="utf-8")

    return submit_path


def compile_check(submit_path: Path, template_dir: Path) -> bool:
    """Java Submit 파일의 컴파일을 검증한다.

    실패해도 Warning만 출력하고 False를 반환한다 (non-fatal).

    Args:
        submit_path: Submit.java 파일 경로.
        template_dir: 템플릿 디렉터리 (사용하지 않지만 인터페이스 일관성).

    Returns:
        True면 컴파일 성공, False면 실패.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        main_java = tmp / "Main.java"
        main_java.write_text(
            submit_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        result = subprocess.run(
            ["javac", str(main_java)],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0


def open_submit_page(problem_id: str) -> None:
    """브라우저에서 BOJ 제출 페이지를 연다.

    플랫폼에 따라 open(macOS) 또는 xdg-open(Linux)을 사용한다.

    Args:
        problem_id: BOJ 문제 번호.
    """
    url = f"https://www.acmicpc.net/submit/{problem_id}"

    system = platform.system()
    if system == "Darwin":
        cmd = "open"
    elif system == "Linux":
        cmd = "xdg-open"
    else:
        # Windows 또는 기타 — 경고만 출력
        return

    subprocess.Popen(
        [cmd, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
