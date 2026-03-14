"""boj run 핵심 로직 — 테스트 실행 + 리소스 제한.

Issue #60 — run.sh Python 마이그레이션. TDD Green 단계.
"""

import json
import platform
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from src.core.config import config_get, find_problem_dir
from src.core.exceptions import BojError, RunError, RunMemoryError, RunTimeoutError

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

DEFAULT_TIME_LIMIT_SEC = 5.0
DEFAULT_MEMORY_LIMIT_MB = 256

# README.md에서 시간/메모리 제한을 파싱하는 정규식
_TIME_PATTERN = re.compile(r"시간\s*제한[:\s]*</strong>\s*(\d+(?:\.\d+)?)\s*초")
_MEMORY_PATTERN = re.compile(r"메모리\s*제한[:\s]*</strong>\s*(\d+)\s*MB")

# 지원 언어 (런타임 있는 것만)
SUPPORTED_RUN_LANGS = ("java", "python")


# ---------------------------------------------------------------------------
# 데이터 클래스
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    """테스트 실행 결과."""

    returncode: int
    stdout: str
    stderr: str


# ---------------------------------------------------------------------------
# parse_resource_limits
# ---------------------------------------------------------------------------

def parse_resource_limits(readme_path: Path) -> tuple[float, int]:
    """README.md에서 시간 제한(초)과 메모리 제한(MB)을 파싱한다.

    Args:
        readme_path: README.md 파일 경로.

    Returns:
        (time_limit_sec, memory_limit_mb) 튜플.
        파일이 없거나 파싱 실패 시 기본값 (5.0, 256) 반환.
    """
    if not readme_path.exists():
        return DEFAULT_TIME_LIMIT_SEC, DEFAULT_MEMORY_LIMIT_MB

    content = readme_path.read_text(encoding="utf-8")

    time_match = _TIME_PATTERN.search(content)
    time_sec = float(time_match.group(1)) if time_match else DEFAULT_TIME_LIMIT_SEC

    memory_match = _MEMORY_PATTERN.search(content)
    memory_mb = int(memory_match.group(1)) if memory_match else DEFAULT_MEMORY_LIMIT_MB

    return time_sec, memory_mb


# ---------------------------------------------------------------------------
# normalize_test_cases
# ---------------------------------------------------------------------------

def normalize_test_cases(test_cases_path: Path) -> list[dict]:
    """test_cases.json을 정규화한다 (id/description 자동 부여).

    원본 파일은 수정하지 않고, 정규화된 리스트를 반환한다.

    Args:
        test_cases_path: test_cases.json 파일 경로.

    Returns:
        정규화된 테스트 케이스 리스트.
    """
    raw = test_cases_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    cases = data.get("testCases", data.get("test_cases", []))

    for i, tc in enumerate(cases, 1):
        if "id" not in tc or tc["id"] is None:
            tc["id"] = i
        if "description" not in tc or not tc.get("description"):
            tc["description"] = f"예제 {i}"

    return cases


# ---------------------------------------------------------------------------
# build_run_command
# ---------------------------------------------------------------------------

def build_run_command(
    lang: str,
    problem_dir: Path,
    template_dir: Path,
) -> list[str]:
    """언어별 테스트 실행 명령을 생성한다.

    Args:
        lang: 프로그래밍 언어 ("java" 또는 "python").
        problem_dir: 문제 폴더 경로.
        template_dir: 템플릿 디렉터리 경로.

    Returns:
        실행할 명령어 리스트.
    """
    if lang == "java":
        return _build_java_command(problem_dir, template_dir)
    elif lang == "python":
        return _build_python_command(problem_dir, template_dir)
    else:
        raise RunError(f"'{lang}' 언어는 run 명령으로 지원되지 않습니다.")


def _build_java_command(problem_dir: Path, template_dir: Path) -> list[str]:
    """Java 컴파일 + 실행 명령을 생성한다."""
    pd = shlex.quote(str(problem_dir))
    td = shlex.quote(str(template_dir))
    return [
        "bash", "-c",
        (
            f'cd {pd} && '
            f'javac -cp ".:{td}" '
            f'{td}/ParseAndCallSolve.java '
            f'{td}/Test.java '
            f'Solution.java test/Parse.java 2>&1 && '
            f'java -cp ".:test:{td}" Test; '
            f'ret=$?; rm -f ./*.class test/*.class 2>/dev/null; exit $ret'
        ),
    ]


def _build_python_command(problem_dir: Path, template_dir: Path) -> list[str]:
    """Python 테스트 실행 명령을 생성한다."""
    return [
        "python3",
        str(template_dir / "test_runner.py"),
    ]


# ---------------------------------------------------------------------------
# validate_run_preconditions
# ---------------------------------------------------------------------------

def validate_run_preconditions(
    problem_dir: Path,
    lang: str,
    template_dir: Path,
) -> None:
    """실행 전 사전 조건을 검증한다.

    Args:
        problem_dir: 문제 폴더 경로.
        lang: 프로그래밍 언어.
        template_dir: 템플릿 디렉터리 경로.

    Raises:
        RunError: 사전 조건 위반 시.
    """
    # 문제 폴더 존재
    if not problem_dir.exists():
        raise RunError(
            f"문제 폴더를 찾을 수 없습니다: {problem_dir.name}"
        )

    # test_cases.json 존재
    test_cases = problem_dir / "test" / "test_cases.json"
    if not test_cases.exists():
        raise RunError(
            "test/test_cases.json이 없습니다. make를 먼저 실행하세요."
        )

    # 솔루션 파일 존재
    if lang == "java":
        if not (problem_dir / "Solution.java").exists():
            raise RunError("Solution.java를 찾을 수 없습니다.")
        if not (problem_dir / "test" / "Parse.java").exists():
            raise RunError("test/Parse.java를 찾을 수 없습니다.")
    elif lang == "python":
        has_solution = (
            (problem_dir / "solution.py").exists()
            or (problem_dir / "Solution.py").exists()
        )
        if not has_solution:
            raise RunError(
                "solution.py 또는 Solution.py를 찾을 수 없습니다."
            )

    # 템플릿 러너 존재
    if lang == "java":
        runner = template_dir / "Test.java"
    elif lang == "python":
        runner = template_dir / "test_runner.py"
    else:
        runner = None

    if runner and not runner.exists():
        raise RunError(
            f"테스트 러너 템플릿이 없습니다: {runner}"
        )


# ---------------------------------------------------------------------------
# execute_tests
# ---------------------------------------------------------------------------

def _make_preexec_fn(memory_mb: int):
    """메모리 제한을 적용하는 preexec_fn을 생성한다 (Unix only)."""
    if platform.system() == "Windows":
        return None

    def _set_limits():
        try:
            import resource
            memory_bytes = memory_mb * 1024 * 1024
            # macOS: RLIMIT_RSS, Linux: RLIMIT_AS
            limit_type = (
                resource.RLIMIT_RSS
                if platform.system() == "Darwin"
                else resource.RLIMIT_AS
            )
            resource.setrlimit(limit_type, (memory_bytes, memory_bytes))
        except (ValueError, OSError):
            # 제한 설정 실패 시 무시 (OS 제약)
            pass

    return _set_limits


def execute_tests(
    cmd: list[str],
    timeout_sec: float,
    memory_mb: int,
    cwd: str | None,
) -> RunResult:
    """테스트를 실행하고 결과를 반환한다.

    Args:
        cmd: 실행할 명령어 리스트.
        timeout_sec: 시간 제한 (초).
        memory_mb: 메모리 제한 (MB).
        cwd: 작업 디렉터리.

    Returns:
        RunResult 객체.

    Raises:
        RunTimeoutError: 시간 초과 시.
        RunMemoryError: 메모리 초과 시.
    """
    preexec_fn = _make_preexec_fn(memory_mb)

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            preexec_fn=preexec_fn,
        )
    except subprocess.TimeoutExpired as e:
        raise RunTimeoutError(
            f"시간 초과 (제한: {timeout_sec}초)"
        ) from e

    # 메모리 초과 감지: 시그널 또는 stderr 패턴
    if result.returncode < 0 or (
        result.returncode != 0
        and _is_memory_error(result.stderr)
    ):
        if _is_memory_error(result.stderr):
            raise RunMemoryError(
                f"메모리 초과 (제한: {memory_mb} MB)"
            )

    return RunResult(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def _is_memory_error(stderr: str) -> bool:
    """stderr에서 메모리 초과 패턴을 감지한다."""
    patterns = [
        "MemoryError",
        "OutOfMemoryError",
        "Cannot allocate memory",
        "std::bad_alloc",
        "ENOMEM",
        "mmap",
    ]
    return any(p in stderr for p in patterns)


# ---------------------------------------------------------------------------
# run (메인 함수)
# ---------------------------------------------------------------------------

def run(
    problem_num: str,
    lang: str | None = None,
    solution_root: Path | None = None,
    agent_root: Path | None = None,
) -> RunResult:
    """boj run의 핵심 로직.

    Args:
        problem_num: 문제 번호 (예: "99999").
        lang: 언어 override. None이면 config에서 읽음.
        solution_root: 풀이 루트 디렉터리. None이면 config에서 읽음.
        agent_root: 에이전트 루트 디렉터리. None이면 config에서 읽음.

    Returns:
        RunResult 객체.

    Raises:
        RunError: 사전 조건 위반 시.
        RunTimeoutError: 시간 초과 시.
        RunMemoryError: 메모리 초과 시.
    """
    # 언어 결정
    prog_lang = lang or config_get("prog_lang", "java")

    # 언어 유효성 검사
    if prog_lang not in SUPPORTED_RUN_LANGS:
        raise RunError(
            f"'{prog_lang}' 언어는 현재 run 명령으로 지원되지 않습니다. "
            f"지원 언어: {' '.join(SUPPORTED_RUN_LANGS)}"
        )

    # 루트 경로 결정
    if solution_root is None:
        root_str = config_get("solution_root", "")
        solution_root = Path(root_str) if root_str else Path.cwd()

    if agent_root is None:
        root_str = config_get("boj_agent_root", "")
        agent_root = Path(root_str) if root_str else Path.cwd()

    # 문제 폴더 찾기
    problem_dir = find_problem_dir(str(solution_root), problem_num)
    if problem_dir is None:
        raise RunError(
            f"'{problem_num}'로 시작하는 폴더를 찾을 수 없습니다."
        )
    problem_dir = Path(problem_dir)

    # 템플릿 디렉터리
    template_dir = agent_root / "templates" / prog_lang

    # 사전 조건 검증
    validate_run_preconditions(problem_dir, prog_lang, template_dir)

    # README.md에서 리소스 제한 파싱
    readme_path = problem_dir / "README.md"
    time_limit, memory_limit = parse_resource_limits(readme_path)

    # test_cases.json 정규화 (원본 비파괴)
    test_cases_path = problem_dir / "test" / "test_cases.json"
    normalized = normalize_test_cases(test_cases_path)

    # 정규화된 내용으로 임시 교체
    original_content = test_cases_path.read_text(encoding="utf-8")
    data = json.loads(original_content)
    data["testCases"] = normalized
    test_cases_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    try:
        # 실행 명령 조립
        cmd = build_run_command(prog_lang, problem_dir, template_dir)

        # 테스트 실행
        cwd = str(problem_dir)
        result = execute_tests(cmd, time_limit, memory_limit, cwd)

        return result

    finally:
        # 원본 복구
        test_cases_path.write_text(original_content, encoding="utf-8")
