"""BOJ CLI 설정 관리 모듈.

설정값 우선순위: 환경변수 (BOJ_<KEY>) > 설정 파일 (~/.config/boj/<key>) > 기본값.
Bash config.sh를 대체하는 Python 구현.
"""

import os
import subprocess
import sys
from pathlib import Path


# ──────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────

DEFAULTS: dict[str, str] = {
    "prog_lang": "java",
    "editor": "code",
    "agent": "",
    "username": "",
    "boj_solution_root": "",
    "boj_agent_root": "",
}

# 환경변수 매핑: config key → BOJ_<ENV_KEY>
_ENV_MAP: dict[str, str] = {
    "prog_lang": "BOJ_PROG_LANG",
    "editor": "BOJ_EDITOR",
    "agent": "BOJ_AGENT",
    "username": "BOJ_USERNAME",
    "boj_solution_root": "BOJ_SOLUTION_ROOT",
    "boj_agent_root": "BOJ_AGENT_ROOT",
}

AGENT_COMMANDS: dict[str, str] = {
    "claude": "claude -p --",
    "copilot": "copilot -p",
    "cursor": "agent -p",
    "gemini": "gemini -p",
    "opencode": "opencode -p",
}

# 에이전트 설치 명령어 (macOS/Linux 기준)
AGENT_INSTALL: dict[str, str] = {
    "claude": "curl -fsSL https://claude.ai/install.sh | bash",
    "copilot": "brew install copilot-cli",
    "cursor": "brew install --cask cursor",
    "gemini": "npm install -g @google/gemini-cli",
    "opencode": "curl -fsSL https://raw.githubusercontent.com/opencode-ai/opencode/refs/heads/main/install | bash",
}

# 지원 언어 (현재 런타임 지원)
SUPPORTED_LANGS = ("java", "python")

# ANSI 색상 (NO_COLOR 환경변수 존중)
_NO_COLOR = os.environ.get("NO_COLOR") is not None
RED = "" if _NO_COLOR else "\033[0;31m"
GREEN = "" if _NO_COLOR else "\033[0;32m"
YELLOW = "" if _NO_COLOR else "\033[1;33m"
BLUE = "" if _NO_COLOR else "\033[0;34m"
NC = "" if _NO_COLOR else "\033[0m"


# ──────────────────────────────────────────────
# 설정 디렉터리
# ──────────────────────────────────────────────

def _config_dir() -> Path:
    """설정 디렉터리 경로를 반환한다. BOJ_CONFIG_DIR 환경변수로 오버라이드 가능."""
    return Path(os.environ.get("BOJ_CONFIG_DIR", os.path.expanduser("~/.config/boj")))


# ──────────────────────────────────────────────
# 설정값 read / write
# ──────────────────────────────────────────────

def config_get(key: str, default: str = "") -> str:
    """설정값을 읽는다. 우선순위: 환경변수 > 파일 > default.

    Args:
        key: 설정 키 (예: "prog_lang", "editor")
        default: 환경변수와 파일 모두 없을 때 반환할 기본값

    Returns:
        설정값 문자열. 빈 문자열은 미설정으로 취급하여 default 반환.
    """
    # 1. 환경변수 확인
    env_var = _ENV_MAP.get(key, f"BOJ_{key.upper()}")
    env_val = os.environ.get(env_var, "")
    if env_val.strip():
        return env_val.strip()

    # 2. 파일 확인
    config_file = _config_dir() / key
    if config_file.is_file():
        try:
            val = config_file.read_text().strip()
            if val:
                return val
        except OSError:
            pass

    # 3. 기본값
    return default


def config_set(key: str, value: str) -> None:
    """설정값을 파일에 저장한다. 디렉터리가 없으면 자동 생성.

    Args:
        key: 설정 키
        value: 저장할 값

    Raises:
        PermissionError: 디렉터리/파일 쓰기 권한이 없을 때
        OSError: 기타 파일시스템 오류
    """
    config_dir = _config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / key).write_text(value + "\n")


# ──────────────────────────────────────────────
# setup_done 플래그
# ──────────────────────────────────────────────

def is_setup_done() -> bool:
    """설정 완료 여부를 반환한다. setup_done 파일 존재 여부로 판단."""
    return (_config_dir() / "setup_done").exists()


def mark_setup_done() -> None:
    """setup_done 플래그 파일을 생성한다."""
    config_dir = _config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "setup_done").touch()


# ──────────────────────────────────────────────
# 경로 검증
# ──────────────────────────────────────────────

def validate_path(path: str) -> bool:
    """경로가 존재하는 디렉터리인지 검증한다."""
    if not path:
        return False
    return Path(path).is_dir()


# ──────────────────────────────────────────────
# 언어 검증
# ──────────────────────────────────────────────

def validate_lang(lang: str) -> bool:
    """언어가 지원 목록에 포함되는지 검증한다."""
    if not lang:
        return False
    return lang in SUPPORTED_LANGS


# ──────────────────────────────────────────────
# agent 커맨드 매핑
# ──────────────────────────────────────────────

def get_agent_command(agent_name: str) -> str | None:
    """agent 이름에 대한 실행 명령어를 반환한다. 알 수 없으면 None."""
    return AGENT_COMMANDS.get(agent_name)


# ──────────────────────────────────────────────
# git config 연동
# ──────────────────────────────────────────────

def get_git_config(key: str) -> str:
    """git config --global 값을 읽는다. 미설정/에러 시 빈 문자열."""
    try:
        result = subprocess.run(
            ["git", "config", "--global", key],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ""


def set_git_config(key: str, value: str) -> None:
    """git config --global 값을 설정한다.

    Raises:
        FileNotFoundError: git이 설치되지 않은 경우
        subprocess.CalledProcessError: git config 실행 실패
    """
    subprocess.run(
        ["git", "config", "--global", key, value],
        capture_output=True, text=True, check=True, timeout=5,
    )


# ──────────────────────────────────────────────
# 설정 상태 조회
# ──────────────────────────────────────────────

def check_config() -> None:
    """전체 설정 상태를 포맷팅하여 출력한다."""
    print(f"{BLUE}=== BOJ CLI 설정 상태 ==={NC}")
    print()

    # solution_root
    sol_root = config_get("boj_solution_root", "")
    if sol_root and validate_path(sol_root):
        print(f"  solution_root: {GREEN}✓{NC} {sol_root}")
    else:
        print(f"  solution_root: {RED}✗ 미설정{NC} (boj setup 실행)")

    # agent_root
    agent_root = config_get("boj_agent_root", "")
    if agent_root and validate_path(agent_root):
        print(f"  agent_root:    {GREEN}✓{NC} {agent_root}")
    else:
        print(f"  agent_root:    {RED}✗ 미설정{NC} (boj setup 실행)")

    # prog_lang
    lang = config_get("prog_lang", DEFAULTS["prog_lang"])
    print(f"  prog_lang:     {GREEN}✓{NC} {lang}")

    # editor
    editor = config_get("editor", DEFAULTS["editor"])
    print(f"  editor:        {GREEN}✓{NC} {editor}")

    # agent
    agent = config_get("agent", "")
    if agent:
        print(f"  agent:         {GREEN}✓{NC} {agent}")
    else:
        print(f"  agent:         {YELLOW}미설정{NC} (make/review는 에디터+클립보드 fallback)")

    # username
    username = config_get("username", "")
    if username:
        print(f"  username:      {GREEN}✓{NC} {username}")
    else:
        print(f"  username:      {YELLOW}미설정{NC}")

    # git
    print()
    git_name = get_git_config("user.name")
    git_email = get_git_config("user.email")
    if git_name and git_email:
        print(f"  git:           {GREEN}✓{NC} {git_name} <{git_email}>")
    else:
        print(f"  git:           {YELLOW}미설정{NC} (git config --global user.name/email 필요)")

    # setup_done
    print()
    if is_setup_done():
        print(f"  setup:         {GREEN}✓ 완료{NC}")
    else:
        print(f"  setup:         {RED}✗ 미완료{NC} (boj setup 실행)")
