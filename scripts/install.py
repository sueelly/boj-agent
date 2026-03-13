#!/usr/bin/env python3
"""BOJ CLI 설치 스크립트.

Clone → python3 scripts/install.py → 설치 완료.
src/setup-boj-cli.sh를 대체하는 Python 구현 (Issue #47).

설치 경로:
    ~/bin/boj                      — CLI 명령어
    ~/.config/boj/                 — 설정 파일 (key-per-file)
    ~/.local/share/boj-agent/      — 에이전트 파일

사용법:
    python3 scripts/install.py               # 기본 설치
    python3 scripts/install.py --force       # 기존 설치 덮어쓰기
    python3 scripts/install.py --skip-setup  # boj setup 자동 실행 건너뛰기
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

IGNORE_PATTERNS = shutil.ignore_patterns(".git", "__pycache__", ".claude", ".venv")


def resolve_repo_root(script_path: Path | None = None) -> Path:
    """스크립트 위치 기준으로 boj-agent repo root를 찾는다.

    Args:
        script_path: install.py 파일 경로. None이면 __file__ 사용.

    Returns:
        repo root 경로 (src/boj가 존재하는 디렉터리).

    Raises:
        FileNotFoundError: src/boj를 찾을 수 없을 때.
    """
    if script_path is None:
        script_path = Path(__file__)

    current = script_path.resolve().parent
    # scripts/ → repo root (한 단계 위)
    # 최대 3단계까지 탐색
    for _ in range(4):
        if (current / "src" / "boj").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    raise FileNotFoundError(
        "Error: src/boj를 찾을 수 없습니다. boj-agent 저장소에서 실행하세요."
    )


def copy_agent_files(src: Path, dest: Path, *, force: bool = False) -> Path:
    """boj-agent 파일을 대상 경로로 복사한다.

    Args:
        src: 원본 repo 경로.
        dest: 복사 대상 경로 (~/.local/share/boj-agent/).
        force: True면 기존 dest를 덮어쓴다.

    Returns:
        실제 agent root 경로 (복사된 dest 또는 스킵 시 src).

    Raises:
        SystemExit: 사용자가 덮어쓰기를 거부했을 때.
    """
    src_resolved = src.resolve()
    dest_resolved = dest.resolve() if dest.exists() else dest.parent.resolve() / dest.name

    # self-move 방지
    if src_resolved == dest_resolved:
        print("  이미 설치 위치에서 실행 중입니다. 복사를 스킵합니다.")
        return src

    # dest 이미 존재 시 확인
    if dest.exists() and not force:
        answer = input(f"  {dest} 가 이미 존재합니다. 덮어쓰시겠습니까? (y/N): ")
        if answer.strip().lower() != "y":
            raise SystemExit(1)
        if dest.is_symlink():
            dest.unlink()
        else:
            shutil.rmtree(dest)

    if dest.exists() and force:
        if dest.is_symlink():
            dest.unlink()
        else:
            shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, ignore=IGNORE_PATTERNS)
    return dest


def install_cli(agent_root: Path, bin_dir: Path) -> Path:
    """boj CLI 스크립트를 bin_dir에 설치한다.

    Args:
        agent_root: boj-agent 설치 경로.
        bin_dir: CLI 설치 디렉터리 (~/bin).

    Returns:
        설치된 boj 명령어 경로.

    Raises:
        FileNotFoundError: agent_root/src/boj가 없을 때.
    """
    boj_src = agent_root / "src" / "boj"
    if not boj_src.exists():
        raise FileNotFoundError(f"Error: {boj_src}를 찾을 수 없습니다.")

    bin_dir.mkdir(parents=True, exist_ok=True)
    boj_dest = bin_dir / "boj"
    shutil.copy2(boj_src, boj_dest)
    boj_dest.chmod(0o755)
    return boj_dest


def save_config(agent_root: Path, config_dir: Path) -> None:
    """agent_root 경로를 config 파일에 저장한다.

    boj_agent_root: 새 키.
    root: src/boj 디스패처 하위호환용.

    Args:
        agent_root: boj-agent 설치 경로.
        config_dir: 설정 디렉터리 (~/.config/boj/).
    """
    config_dir.mkdir(parents=True, exist_ok=True)

    (config_dir / "boj_agent_root").write_text(str(agent_root) + "\n")
    (config_dir / "root").write_text(str(agent_root) + "\n")


def check_path(bin_dir: Path) -> bool:
    """PATH에 bin_dir가 포함되어 있는지 확인한다.

    Args:
        bin_dir: 확인할 디렉터리.

    Returns:
        포함 여부.
    """
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    bin_str = str(bin_dir)
    return any(os.path.normpath(p) == os.path.normpath(bin_str) for p in path_dirs)


def detect_shell_rc(home: Path) -> Path | None:
    """셸 설정 파일을 찾는다.

    .zshrc → .bashrc → .bash_profile 순서.

    Args:
        home: HOME 디렉터리.

    Returns:
        셸 rc 파일 경로 또는 None.
    """
    for name in (".zshrc", ".bashrc", ".bash_profile"):
        rc = home / name
        if rc.exists():
            return rc
    return None


def _rc_already_prepends_bin(content: str, bin_dir: Path) -> bool:
    """rc에 이미 «~/bin이 PATH 앞에 붙는» export가 있는지 본다.

    예전 구현은 \"$HOME/bin\" 문자열이 주석/문서에만 있어도 스킵해,
    실제 PATH에는 ~/bin이 없는데도 export를 안 넣는 버그가 있었다.
    """
    bin_s = str(bin_dir.resolve()) if bin_dir.exists() else str(bin_dir)
    for line in content.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if not re.match(r"export\s+PATH\s*=", s):
            continue
        rhs = s.split("=", 1)[1].strip()
        rhs = rhs.strip("\"'")
        first = rhs.split(":")[0].strip("\"'")
        if first == bin_s:
            return True
        if first in ("$HOME/bin", "${HOME}/bin"):
            return True
    return False


def add_to_path(bin_dir: Path, shell_rc: Path) -> bool:
    """shell rc에 PATH export를 추가한다. 이미 앞에 붙이는 줄이 있으면 스킵.

    Args:
        bin_dir: PATH에 추가할 디렉터리.
        shell_rc: 셸 설정 파일 경로.

    Returns:
        True면 추가됨, False면 이미 있어서 스킵.
    """
    export_line = f'export PATH="{bin_dir}:$PATH"'
    content = shell_rc.read_text() if shell_rc.exists() else ""
    if _rc_already_prepends_bin(content, bin_dir):
        return False
    with open(shell_rc, "a") as f:
        f.write(f"\n{export_line}\n")
    return True


def print_path_advice(bin_dir: Path, shell_rc: Path | None) -> None:
    """PATH 설정 안내 메시지를 출력한다.

    Args:
        bin_dir: CLI가 설치된 디렉터리.
        shell_rc: 셸 설정 파일 (None이면 일반 안내).
    """
    print(f"  PATH에 {bin_dir} 이(가) 없습니다. 셸 설정에 추가하세요:")
    print(f'    export PATH="$HOME/bin:$PATH"')
    if shell_rc:
        print(f"  위 내용을 {shell_rc.name}에 추가하면 됩니다.")


def run_setup(boj_cmd: Path) -> int:
    """boj setup을 subprocess로 실행한다.

    Args:
        boj_cmd: boj 명령어 경로.

    Returns:
        종료 코드 (0이면 성공).
    """
    try:
        result = subprocess.run(
            [str(boj_cmd), "setup"],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        return result.returncode
    except (FileNotFoundError, OSError):
        return 1


def main(argv: list[str] | None = None, *, script_path: Path | None = None) -> int:
    """설치 스크립트 메인 함수.

    Args:
        argv: CLI 인자. None이면 sys.argv 사용.
        script_path: install.py 경로 (테스트용 오버라이드).

    Returns:
        종료 코드 (0이면 성공).
    """
    parser = argparse.ArgumentParser(description="BOJ CLI 설치 스크립트")
    parser.add_argument(
        "--force", action="store_true", help="기존 설치 덮어쓰기"
    )
    parser.add_argument(
        "--skip-setup", action="store_true", help="boj setup 자동 실행 건너뛰기"
    )
    args = parser.parse_args(argv)

    # 1. repo root 탐지
    try:
        repo_root = resolve_repo_root(script_path)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    home = Path.home()
    bin_dir = home / "bin"
    config_dir = home / ".config" / "boj"
    agent_dest = home / ".local" / "share" / "boj-agent"

    print("BOJ CLI 설치를 시작합니다.")
    print()

    # 2. agent 파일 복사
    print("[1/4] boj-agent 파일 복사...")
    try:
        agent_root = copy_agent_files(repo_root, agent_dest, force=args.force)
    except SystemExit:
        print("설치를 중단합니다.")
        return 1
    except PermissionError as e:
        print(f"Error: 권한이 없습니다: {e}", file=sys.stderr)
        return 1
    print(f"  → {agent_root}")
    print()

    # 3. CLI 설치
    print("[2/4] boj 명령어 설치...")
    try:
        boj_cmd = install_cli(agent_root, bin_dir)
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"  → {boj_cmd}")
    print()

    # 4. config 저장
    print("[3/4] 설정 저장...")
    try:
        save_config(agent_root, config_dir)
    except PermissionError as e:
        print(f"Error: 설정을 저장할 수 없습니다: {e}", file=sys.stderr)
        return 1
    print(f"  → {config_dir}")
    print()

    # 5. PATH 확인
    print("[4/4] PATH 확인...")
    if check_path(bin_dir):
        print("  PATH에 포함되어 있습니다.")
    else:
        shell_rc = detect_shell_rc(home)
        if shell_rc:
            added = add_to_path(bin_dir, shell_rc)
            if added:
                print(f"  PATH 설정을 {shell_rc.name}에 추가했습니다.")
            else:
                print(f"  {shell_rc.name}에 PATH 설정이 이미 있습니다.")
            print(f"  현재 세션에 적용: source ~/{shell_rc.name}")
        else:
            print_path_advice(bin_dir, None)
    print()

    # 6. boj setup 실행
    if not args.skip_setup:
        print("boj setup을 실행합니다...")
        print()
        rc = run_setup(boj_cmd)
        if rc != 0:
            print()
            print("Warning: boj setup이 완료되지 않았습니다. 수동으로 실행하세요:")
            print(f"  {boj_cmd} setup")
    else:
        print("설치 완료! 다음 명령어로 초기 설정을 진행하세요:")
        print("  boj setup")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
