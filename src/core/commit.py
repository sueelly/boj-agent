"""boj commit 핵심 로직 -- BOJ 통계 + git 자동 커밋.

Issue #68 -- commit.sh Python 마이그레이션.
edge-cases CT1-CT9 커버리지.
"""

import subprocess
import sys
from pathlib import Path

from src.core.config import config_get, find_problem_dir
from src.core.exceptions import BojError

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

USER_AGENT = "Mozilla/5.0 (compatible; boj-agent/1.0)"
BOJ_STATUS_URL = "https://www.acmicpc.net/status"
STATS_TIMEOUT_SEC = 5

# 화이트리스트: 문제 폴더에서 staging할 파일 패턴
_WHITELIST_FILES = [
    "README.md",
    "Solution.java",
    "solution.py",
    "Solution.py",
    "Solution.cpp",
    "Solution.c",
    "Solution.kt",
    "Solution.go",
    "test/test_cases.json",
    "test/Parse.java",
    "test/Parse.py",
    "test/Parse.cpp",
    "test/Parse.c",
    "test/Parse.kt",
    "test/Parse.go",
    "submit/REVIEW.md",
    "submit/Submit.java",
    "submit/Submit.py",
    "submit/Submit.cpp",
    "submit/Submit.c",
    "submit/Submit.kt",
    "submit/Submit.go",
]


# ---------------------------------------------------------------------------
# check_git_repo
# ---------------------------------------------------------------------------

def check_git_repo(cwd: Path | None = None) -> None:
    """git repo인지 확인한다. 아니면 BojError.

    Args:
        cwd: 확인할 디렉터리. None이면 현재 디렉터리.

    Raises:
        BojError: git 저장소가 아닌 경우 (CT2).
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise BojError("git 저장소가 아닙니다.")
    except FileNotFoundError:
        raise BojError("git을 찾을 수 없습니다.")


# ---------------------------------------------------------------------------
# check_git_email
# ---------------------------------------------------------------------------

def check_git_email(cwd: Path | None = None) -> None:
    """git user.email 설정을 확인한다. 없으면 BojError.

    Args:
        cwd: 확인할 디렉터리. None이면 현재 디렉터리.

    Raises:
        BojError: git user.email이 설정되지 않은 경우 (CT8).
    """
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        email = result.stdout.strip()
        if not email:
            raise BojError(
                "git user.email이 설정되지 않았습니다. "
                "boj setup 또는 git config --global user.email 실행."
            )
    except FileNotFoundError:
        raise BojError("git을 찾을 수 없습니다.")


# ---------------------------------------------------------------------------
# fetch_boj_stats
# ---------------------------------------------------------------------------

def fetch_boj_stats(
    problem_id: str,
    session: str,
    username: str,
) -> str:
    """BOJ 통계(메모리/시간)를 조회한다.

    실패 시 실패 사유 문자열을 반환한다 (non-fatal).

    Args:
        problem_id: 문제 번호.
        session: BOJ 세션 쿠키 값.
        username: BOJ 사용자 ID.

    Returns:
        "[v Nms NKB]" 또는 "[BOJ 통계: 실패 사유]" 형태의 문자열.
    """
    if not session:
        return "[BOJ 통계: 세션 없음]"

    if not username:
        return "[BOJ 통계: 사용자 ID 없음]"

    url = (
        f"{BOJ_STATUS_URL}"
        f"?problem_id={problem_id}"
        f"&user_id={username}"
        f"&result_id=4"
    )

    try:
        import requests  # lazy import: CI에서 미설치 가능
    except ImportError:
        return "[BOJ 통계: requests 모듈 없음]"

    try:
        resp = requests.get(
            url,
            headers={
                "Cookie": f"OnlineJudge={session}; bojautologin={session}",
                "User-Agent": USER_AGENT,
            },
            timeout=STATS_TIMEOUT_SEC,
        )
    except requests.exceptions.RequestException:
        return "[BOJ 통계: 네트워크 오류]"

    if not resp.text:
        return "[BOJ 통계: 응답 없음]"

    try:
        from bs4 import BeautifulSoup  # lazy import: CI에서 미설치 가능
    except ImportError:
        return "[BOJ 통계: bs4 모듈 없음]"

    # BeautifulSoup으로 메모리/시간 파싱
    soup = BeautifulSoup(resp.text, "html.parser")

    # status 테이블에서 메모리(KB)와 시간(ms) td 추출
    memory = _parse_stat_td(soup, "KB")
    time_ms = _parse_stat_td(soup, "ms")

    if memory is not None and time_ms is not None:
        return f"[✓ {time_ms}ms {memory}KB]"

    # Accepted 결과 확인
    if "맞았습니다" in resp.text or "Accepted" in resp.text:
        return "[BOJ 통계: 파싱 실패]"

    return "[BOJ 통계: Accepted 없음]"


def _parse_stat_td(soup: "BeautifulSoup", unit: str) -> str | None:
    """BeautifulSoup에서 특정 단위의 td 값을 추출한다.

    Args:
        soup: BeautifulSoup 객체.
        unit: 단위 문자열 (예: "KB", "ms").

    Returns:
        숫자 문자열 또는 None.
    """
    for td in soup.find_all("td"):
        text = td.get_text(strip=True)
        if text.endswith(f" {unit}"):
            val = text[: -len(f" {unit}")]
            if val.isdigit():
                return val
    return None


# ---------------------------------------------------------------------------
# build_commit_message
# ---------------------------------------------------------------------------

def build_commit_message(
    problem_name: str,
    stats: str,
    custom_message: str | None = None,
) -> str:
    """커밋 메시지를 생성한다.

    Args:
        problem_name: 문제 폴더 이름 (예: "99999-두수의합").
        stats: BOJ 통계 문자열.
        custom_message: 사용자 지정 커밋 메시지. None이면 자동 생성.

    Returns:
        커밋 메시지 문자열.
    """
    if custom_message:
        return custom_message

    return f"{problem_name} 풀이 완료 {stats}"


# ---------------------------------------------------------------------------
# stage_problem_files
# ---------------------------------------------------------------------------

def stage_problem_files(
    problem_dir: Path,
    cwd: Path | None = None,
) -> list[str]:
    """화이트리스트 파일을 staging한다. 존재하는 파일만.

    Args:
        problem_dir: 문제 폴더 절대 경로.
        cwd: git 명령 실행 디렉터리 (repo root). None이면 현재 디렉터리.

    Returns:
        staging된 파일의 상대 경로 리스트.
    """
    problem_name = problem_dir.name
    files_to_add = []

    for rel_path in _WHITELIST_FILES:
        full_path = problem_dir / rel_path
        if full_path.exists():
            files_to_add.append(f"{problem_name}/{rel_path}")

    if not files_to_add:
        return []

    try:
        subprocess.run(
            ["git", "add"] + files_to_add,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except subprocess.CalledProcessError:
        # 일부 파일 스테이징 실패 -- Warning만 출력
        print(
            "Warning: 일부 파일 스테이징 실패. 수동으로 git add를 확인하세요.",
            file=sys.stderr,
        )

    return files_to_add


# ---------------------------------------------------------------------------
# has_staged_changes
# ---------------------------------------------------------------------------

def has_staged_changes(cwd: Path | None = None) -> bool:
    """staging area에 변경사항이 있는지 확인한다.

    Args:
        cwd: git 명령 실행 디렉터리. None이면 현재 디렉터리.

    Returns:
        변경사항이 있으면 True.
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=cwd,
        capture_output=True,
        timeout=5,
    )
    # returncode 0 = no diff (clean), 1 = has diff
    return result.returncode != 0


# ---------------------------------------------------------------------------
# git_commit
# ---------------------------------------------------------------------------

def git_commit(message: str, cwd: Path | None = None) -> None:
    """git commit을 실행한다.

    Args:
        message: 커밋 메시지.
        cwd: git 명령 실행 디렉터리. None이면 현재 디렉터리.

    Raises:
        BojError: git commit 실패 시.
    """
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise BojError(
            f"git commit 실패: {result.stderr.strip()}"
        )


# ---------------------------------------------------------------------------
# commit (메인 함수)
# ---------------------------------------------------------------------------

def commit(
    problem_num: str,
    custom_message: str | None = None,
    no_stats: bool = False,
    solution_root: Path | None = None,
    cwd: Path | None = None,
) -> str:
    """boj commit의 핵심 로직.

    Args:
        problem_num: 문제 번호.
        custom_message: 사용자 지정 커밋 메시지.
        no_stats: True이면 BOJ 통계 조회를 건너뛴다.
        solution_root: 풀이 루트 디렉터리. None이면 config에서 읽음.
        cwd: git 명령 실행 디렉터리. None이면 solution_root 사용.

    Returns:
        커밋 메시지 문자열.

    Raises:
        BojError: git repo가 아니거나, email 미설정이거나,
                  문제 폴더를 찾을 수 없는 경우.
    """
    # 루트 경로 결정
    if solution_root is None:
        root_str = config_get("solution_root", "")
        solution_root = Path(root_str) if root_str else Path.cwd()

    if cwd is None:
        cwd = solution_root

    # CT2: git repo 확인
    check_git_repo(cwd)

    # CT8: git email 확인
    check_git_email(cwd)

    # CT1: 문제 폴더 찾기
    problem_dir_str = find_problem_dir(str(solution_root), problem_num)
    if problem_dir_str is None:
        raise BojError(
            f"'{problem_num}'로 시작하는 폴더를 찾을 수 없습니다."
        )
    problem_dir = Path(problem_dir_str)
    problem_name = problem_dir.name

    # BOJ 통계 조회
    if no_stats:
        stats = "[BOJ 통계: 스킵]"
    else:
        session = config_get("session", "")
        username = config_get("username", "")
        stats = fetch_boj_stats(problem_num, session, username)

    # 커밋 메시지 생성
    msg = build_commit_message(problem_name, stats, custom_message)

    # 파일 staging
    stage_problem_files(problem_dir, cwd)

    # CT3: 변경사항 확인
    if not has_staged_changes(cwd):
        print(
            "Warning: 커밋할 변경사항이 없습니다.",
            file=sys.stderr,
        )
        return msg

    # 커밋 실행
    git_commit(msg, cwd)

    return msg
