"""boj review 핵심 로직 -- 에이전트 리뷰 또는 클립보드 fallback.

Issue #67 -- review.sh Python 마이그레이션.

edge-cases:
    RV1: 정상 (에이전트 + Solution) -> agent 실행
    RV2: Solution 없음 -> Warning, agent 계속 실행
    RV3: 폴더 없음 -> BojError
    RV4: 에이전트 실행 에러 -> BojError
"""

import shlex
import subprocess
import sys
from pathlib import Path

from src.core.config import config_get, find_problem_dir
from src.core.exceptions import BojError


# ---------------------------------------------------------------------------
# Solution 파일 탐색
# ---------------------------------------------------------------------------

# 지원하는 Solution 파일명 (우선순위 순서)
_SOLUTION_NAMES = (
    "Solution.java",
    "Solution.py",
    "solution.py",
    "Solution.kt",
    "Solution.cpp",
    "Solution.c",
)


def find_solution_file(
    problem_dir: Path, lang: str | None = None,
) -> Path | None:
    """문제 폴더에서 Solution 파일을 찾는다.

    lang이 지정되면 해당 언어의 Solution 파일만 찾고,
    미지정이면 모든 Solution.* 파일 중 첫 번째를 반환한다.

    Args:
        problem_dir: 문제 폴더 경로.
        lang: 프로그래밍 언어 (예: "java", "python"). None이면 전체 탐색.

    Returns:
        Solution 파일 경로. 없으면 None.
    """
    if lang == "java":
        candidates = ("Solution.java",)
    elif lang == "python":
        candidates = ("solution.py", "Solution.py")
    else:
        candidates = _SOLUTION_NAMES

    for name in candidates:
        path = problem_dir / name
        if path.exists():
            return path

    return None


# ---------------------------------------------------------------------------
# 프롬프트 빌드
# ---------------------------------------------------------------------------

def build_review_prompt(
    problem_dir: Path,
    prompt_template_path: Path,
) -> str:
    """리뷰 프롬프트를 조립한다.

    review.md 템플릿을 읽고, Solution 파일 내용이 있으면 포함한다.

    Args:
        problem_dir: 문제 폴더 경로.
        prompt_template_path: prompts/review.md 파일 경로.

    Returns:
        조립된 프롬프트 문자열.
    """
    # 프롬프트 템플릿 읽기
    if prompt_template_path.exists():
        template = prompt_template_path.read_text(encoding="utf-8")
    else:
        template = ""

    # Solution 파일 탐색 (언어 무관)
    solution_file = find_solution_file(problem_dir)

    parts = []
    if template:
        parts.append(template)

    # Solution 내용 포함
    if solution_file and solution_file.exists():
        content = solution_file.read_text(encoding="utf-8")
        parts.append(
            f"\n---\n\n"
            f"## Solution ({solution_file.name})\n\n"
            f"```\n{content}\n```"
        )

    parts.append("\n---\n리뷰해줘")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# 에이전트 실행
# ---------------------------------------------------------------------------

def run_review(
    problem_dir: Path,
    agent_cmd: str,
    prompt: str,
) -> subprocess.CompletedProcess:
    """에이전트로 리뷰를 실행한다.

    Args:
        problem_dir: 문제 폴더 경로 (cwd로 사용).
        agent_cmd: 에이전트 실행 명령어 (예: "claude -p --").
        prompt: 리뷰 프롬프트 문자열.

    Returns:
        CompletedProcess 결과.

    Raises:
        BojError: 에이전트 실행 실패 시 (RV4).
    """
    cmd = shlex.split(agent_cmd)
    try:
        result = subprocess.run(
            [*cmd, prompt],
            cwd=str(problem_dir),
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError) as e:
        raise BojError(
            f"에이전트 실행 실패: {e}"
        ) from e

    if result.returncode != 0:
        detail = ""
        if result.stderr and result.stderr.strip():
            detail = f" ({result.stderr.strip()[:200]})"
        raise BojError(
            f"에이전트 실행 실패. 수동으로 리뷰를 요청하세요.{detail}"
        )

    return result


# ---------------------------------------------------------------------------
# REVIEW.md 파일 저장
# ---------------------------------------------------------------------------

def write_review_file(problem_dir: Path, content: str) -> Path:
    """리뷰 내용을 submit/REVIEW.md에 저장한다.

    Args:
        problem_dir: 문제 폴더 경로.
        content: 리뷰 내용 문자열.

    Returns:
        생성된 REVIEW.md 파일 경로.
    """
    submit_dir = problem_dir / "submit"
    submit_dir.mkdir(parents=True, exist_ok=True)
    review_path = submit_dir / "REVIEW.md"
    review_path.write_text(content, encoding="utf-8")
    return review_path


# ---------------------------------------------------------------------------
# 클립보드 fallback
# ---------------------------------------------------------------------------

def clipboard_fallback(prompt: str) -> bool:
    """프롬프트를 클립보드에 복사한다.

    pbcopy(macOS) 또는 xclip(Linux)을 시도한다.

    Args:
        prompt: 클립보드에 복사할 문자열.

    Returns:
        True면 복사 성공, False면 클립보드 도구 없음.
    """
    for tool in ("pbcopy", "xclip"):
        try:
            subprocess.run(
                [tool] if tool == "pbcopy" else [tool, "-selection", "clipboard"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    return False


# ---------------------------------------------------------------------------
# review (메인 함수)
# ---------------------------------------------------------------------------

def review(
    problem_num: str,
    lang: str | None = None,
    solution_root: Path | None = None,
    agent_root: Path | None = None,
) -> subprocess.CompletedProcess | None:
    """boj review의 핵심 로직.

    Args:
        problem_num: 문제 번호 (예: "99999").
        lang: 언어 override. None이면 config에서 읽음.
        solution_root: 풀이 루트 디렉터리. None이면 config에서 읽음.
        agent_root: 에이전트 루트 디렉터리. None이면 config에서 읽음.

    Returns:
        에이전트 실행 시 CompletedProcess, fallback 시 None.

    Raises:
        BojError: 문제 폴더 없음(RV3) 또는 에이전트 실행 실패(RV4).
    """
    # 루트 경로 결정
    if solution_root is None:
        root_str = config_get("solution_root", "")
        solution_root = Path(root_str) if root_str else Path.cwd()

    if agent_root is None:
        root_str = config_get("boj_agent_root", "")
        if root_str:
            agent_root = Path(root_str)

    # 문제 폴더 찾기 (RV3)
    problem_dir_str = find_problem_dir(str(solution_root), problem_num)
    if problem_dir_str is None:
        raise BojError(
            f"'{problem_num}'로 시작하는 문제 폴더가 없습니다."
        )
    problem_dir = Path(problem_dir_str)

    # Solution 파일 확인 (RV2: 없어도 Warning만)
    solution_file = find_solution_file(problem_dir, lang)
    if solution_file is None:
        print(
            "Warning: Solution 파일이 없습니다. "
            "리뷰할 코드가 없을 수 있습니다.",
            file=sys.stderr,
        )

    # 프롬프트 빌드
    if agent_root is not None:
        prompt_template = agent_root / "prompts" / "review.md"
    else:
        from src.core.resources import get_prompt_file
        prompt_template = get_prompt_file("review")
    prompt = build_review_prompt(problem_dir, prompt_template)

    # 에이전트 명령어 확인 (RV3: 없으면 fallback)
    agent_cmd = config_get("agent", "")
    if agent_cmd:
        # 에이전트 이름 -> 실행 명령어 매핑
        from src.core.config import AGENT_COMMANDS
        agent_cmd = AGENT_COMMANDS.get(agent_cmd, agent_cmd)

    if agent_cmd:
        # RV1/RV4: 에이전트 실행
        result = run_review(problem_dir, agent_cmd, prompt)
        # stdout 내용을 submit/REVIEW.md로 저장
        if result.stdout and result.stdout.strip():
            write_review_file(problem_dir, result.stdout)
        return result
    else:
        # RV3: fallback -- 클립보드 + 에디터
        clipboard_fallback("리뷰해줘")
        editor = config_get("editor", "code")
        if editor:
            try:
                cmd = [*shlex.split(editor), str(problem_dir)]
                subprocess.Popen(cmd, cwd=str(problem_dir))
            except (FileNotFoundError, OSError):
                pass
        return None
