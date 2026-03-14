"""boj open 핵심 로직 — 문제 폴더를 에디터로 열기.

Issue #66 — open.sh Python 마이그레이션.
"""

import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from src.core.config import config_get, find_problem_dir
from src.core.exceptions import BojError


# ---------------------------------------------------------------------------
# find_or_create_problem_dir
# ---------------------------------------------------------------------------

def find_or_create_problem_dir(
    problem_id: str,
    base_dir: Path | None = None,
) -> Path:
    """문제 번호로 시작하는 폴더를 찾아 경로를 반환한다.

    Args:
        problem_id: 문제 번호 (예: "99999").
        base_dir: 풀이 루트 디렉터리. None이면 config에서 읽음.

    Returns:
        찾은 문제 폴더 경로.

    Raises:
        BojError: 문제 폴더를 찾을 수 없을 때 (O1).
    """
    if base_dir is None:
        root_str = config_get("solution_root", "")
        base_dir = Path(root_str) if root_str else Path.cwd()

    result = find_problem_dir(str(base_dir), problem_id)
    if result is None:
        raise BojError(
            f"'{problem_id}' 문제 폴더가 없습니다. "
            f"먼저 boj make {problem_id} 를 실행하세요."
        )

    return Path(result)


# ---------------------------------------------------------------------------
# open_in_editor
# ---------------------------------------------------------------------------

def open_in_editor(problem_dir: Path, editor_cmd: str | None) -> None:
    """에디터로 문제 폴더를 연다 (non-blocking).

    Popen으로 실행하여 CLI가 에디터 종료를 기다리지 않는다.

    Args:
        problem_dir: 문제 폴더 경로.
        editor_cmd: 에디터 명령어 (예: "code", "cursor", "vim").

    Raises:
        BojError: 에디터가 설정되지 않았을 때 (O2).
        BojError: 에디터를 PATH에서 찾을 수 없을 때 (O4).
    """
    if not (editor_cmd or "").strip():
        raise BojError(
            "에디터가 설정되지 않았습니다. "
            "--editor 옵션 또는 boj setup에서 에디터를 설정하세요."
        )

    editor_name = shlex.split(editor_cmd.strip())[0]
    if shutil.which(editor_name) is None:
        raise BojError(
            f"설정된 에디터 '{editor_name}'을(를) "
            f"찾을 수 없습니다. PATH를 확인하세요."
        )

    cmd = [*shlex.split(editor_cmd.strip()), str(problem_dir)]
    subprocess.Popen(cmd, cwd=str(problem_dir))


# ---------------------------------------------------------------------------
# open_problem (메인 함수)
# ---------------------------------------------------------------------------

def open_problem(
    problem_id: str,
    editor: str | None = None,
    base_dir: Path | None = None,
) -> Path:
    """boj open의 핵심 로직.

    Args:
        problem_id: 문제 번호 (예: "99999").
        editor: 에디터 override. None이면 config에서 읽음.
        base_dir: 풀이 루트 디렉터리. None이면 config에서 읽음.

    Returns:
        열린 문제 폴더 경로.

    Raises:
        BojError: 문제 폴더 없음 (O1), 에디터 미설정 (O2),
                  에디터 PATH 없음 (O4).
    """
    # 에디터 결정 (O3: --editor flag override)
    editor_cmd = editor or config_get("editor", "")

    # 문제 폴더 찾기
    problem_dir = find_or_create_problem_dir(problem_id, base_dir)

    # 에디터로 열기
    open_in_editor(problem_dir, editor_cmd)

    print(
        f"문제 폴더를 에디터로 열었습니다: {problem_dir.name}",
        file=sys.stderr,
    )

    return problem_dir
