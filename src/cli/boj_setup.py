"""BOJ CLI setup 명령어 — 대화형 설정 마법사 + 비대화형 옵션.

Issue #46: src/commands/setup.sh를 Python으로 재구현.
세션 쿠키 관련 로직은 이슈 스코프 외 → 제외.

사용법:
    python -m src.cli.boj_setup                  # 대화형 8단계
    python -m src.cli.boj_setup --check          # 설정 상태 조회
    python -m src.cli.boj_setup --lang python    # 개별 키 설정
"""

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import NoReturn

from src.core.config import (
    config_get,
    config_set,
    is_setup_done,
    mark_setup_done,
    validate_lang,
    validate_path,
    get_git_config,
    set_git_config,
    check_config,
    get_agent_command,
    AGENT_COMMANDS,
    AGENT_INSTALL,
    DEFAULTS,
    SUPPORTED_LANGS,
    RED,
    GREEN,
    YELLOW,
    BLUE,
    NC,
)


# ──────────────────────────────────────────────
# 인자 파싱
# ──────────────────────────────────────────────

def parse_args(argv: list[str]) -> argparse.Namespace:
    """CLI 인자를 파싱한다.

    Args:
        argv: sys.argv[1:] 에 해당하는 인자 리스트.

    Returns:
        파싱된 Namespace 객체.
    """
    parser = argparse.ArgumentParser(
        prog="boj setup",
        description="BOJ CLI 초기 설정 마법사",
    )
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="현재 설정 표시",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="레포 루트 경로 설정",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        help="기본 언어 설정 (java, python)",
    )
    parser.add_argument(
        "--username",
        type=str,
        default=None,
        help="BOJ 사용자 ID 설정",
    )
    parser.add_argument(
        "--editor",
        type=str,
        default=None,
        help="에디터 명령어 설정",
    )
    parser.add_argument(
        "--agent",
        type=str,
        default=None,
        help="에이전트 이름 또는 명령어 설정",
    )
    return parser.parse_args(argv)


# ──────────────────────────────────────────────
# --check 모드
# ──────────────────────────────────────────────

def run_check_mode() -> None:
    """설정 상태를 출력한다 (config.check_config 위임)."""
    check_config()


# ──────────────────────────────────────────────
# 비대화형 set 모드
# ──────────────────────────────────────────────

def run_set_mode(args: argparse.Namespace) -> int:
    """비대화형으로 개별 키를 설정한다.

    Args:
        args: parse_args() 결과.

    Returns:
        종료 코드. 0=성공, 1=실패.
    """
    if args.root is not None:
        if not validate_path(args.root):
            print(
                f"{RED}Error: 경로가 존재하지 않습니다: {args.root}{NC}",
                file=sys.stderr,
            )
            return 1
        try:
            config_set("solution_root", args.root)
            print(f"{GREEN}✓ root 저장됨: {args.root}{NC}")
        except (PermissionError, OSError) as e:
            print(f"{RED}Error: 설정 저장 실패 — {e}{NC}", file=sys.stderr)
            return 1

    if args.lang is not None:
        if not validate_lang(args.lang):
            supported = ", ".join(SUPPORTED_LANGS)
            print(
                f"{RED}Error: 지원하지 않는 언어입니다: {args.lang} "
                f"(지원: {supported}){NC}",
                file=sys.stderr,
            )
            return 1
        try:
            config_set("prog_lang", args.lang)
            print(f"{GREEN}✓ lang 저장됨: {args.lang}{NC}")
        except (PermissionError, OSError) as e:
            print(f"{RED}Error: 설정 저장 실패 — {e}{NC}", file=sys.stderr)
            return 1

    if args.username is not None:
        try:
            config_set("username", args.username)
            print(f"{GREEN}✓ username 저장됨: {args.username}{NC}")
        except (PermissionError, OSError) as e:
            print(f"{RED}Error: 설정 저장 실패 — {e}{NC}", file=sys.stderr)
            return 1

    if args.editor is not None:
        try:
            config_set("editor", args.editor)
            print(f"{GREEN}✓ editor 저장됨: {args.editor}{NC}")
        except (PermissionError, OSError) as e:
            print(f"{RED}Error: 설정 저장 실패 — {e}{NC}", file=sys.stderr)
            return 1

    if args.agent is not None:
        # 알려진 agent 이름이면 명령어 자동 매핑, 아니면 입력값을 그대로 사용
        mapped = get_agent_command(args.agent)
        agent_cmd = mapped if mapped else args.agent
        try:
            config_set("agent", agent_cmd)
            print(f"{GREEN}✓ agent 저장됨: {agent_cmd}{NC}")
        except (PermissionError, OSError) as e:
            print(f"{RED}Error: 설정 저장 실패 — {e}{NC}", file=sys.stderr)
            return 1

    return 0


# ──────────────────────────────────────────────
# 대화형 step 함수들
# ──────────────────────────────────────────────

def step_root(prompter: Callable[[str], str]) -> str:
    """[Step 1] 레포 루트 경로를 설정한다.

    Args:
        prompter: input() 대체 callable.

    Returns:
        설정된 경로 문자열.
    """
    print(f"\n{YELLOW}[1/6] 레포 루트 경로 (BOJ_SOLUTION_ROOT){NC}")

    current = config_get("solution_root", "")
    if current and validate_path(current):
        print(f"  현재: {current}")
        change = prompter(f"  변경하시겠습니까? (y/N): ")
        if not change.strip().lower().startswith("y"):
            print(f"  유지: {current}")
            return current

    while True:
        cwd = os.getcwd()
        print(f"  경로를 선택하세요:")
        print(f"    1) 현재 디렉터리 ({cwd})")
        print(f"    2) 직접 입력")
        choice = prompter("  선택 [1/2]: ").strip()

        if choice == "1":
            path = cwd
        elif choice == "2":
            path = prompter("  경로: ").strip()
        else:
            path = cwd

        if not validate_path(path):
            print(f"  {RED}경로가 존재하지 않습니다: {path}{NC}")
            print(f"  다시 선택하세요.")
            continue

        confirm = prompter(f"  '{path}'(으)로 설정하시겠습니까? (y/N): ")
        if confirm.strip().lower().startswith("y"):
            config_set("solution_root", path)
            print(f"  {GREEN}✓ 저장: {path}{NC}")
            return path


def step_lang(prompter: Callable[[str], str]) -> str:
    """[Step 2] 기본 언어를 설정한다.

    Args:
        prompter: input() 대체 callable.

    Returns:
        설정된 언어 문자열.
    """
    print(f"\n{YELLOW}[2/6] 기본 언어 (make/run/submit 기본값){NC}")

    current = config_get("prog_lang", "")
    if current and validate_lang(current):
        print(f"  현재: {current}")
        change = prompter(f"  변경하시겠습니까? (y/N): ")
        if not change.strip().lower().startswith("y"):
            print(f"  유지: {current}")
            return current

    supported = ", ".join(SUPPORTED_LANGS)
    while True:
        print(f"  지원 언어: {supported}")
        lang = prompter(f"  기본 언어 [java]: ").strip()
        if not lang:
            lang = "java"

        if validate_lang(lang):
            config_set("prog_lang", lang)
            print(f"  {GREEN}✓ 저장: {lang}{NC}")
            return lang
        else:
            print(f"  {YELLOW}'{lang}'은(는) 현재 미지원입니다. "
                  f"지원 언어: {supported}{NC}")


def step_agent(prompter: Callable[[str], str]) -> str:
    """[Step 3] 에이전트를 설정한다.

    Args:
        prompter: input() 대체 callable.

    Returns:
        설정된 에이전트 명령어 문자열 (빈 문자열 = 미설정).
    """
    print(f"\n{YELLOW}[3/6] 에이전트 (make/review에 사용){NC}")

    current = config_get("agent", "")
    if current:
        print(f"  현재: {current}")
        change = prompter(f"  변경하시겠습니까? (y/N): ")
        if not change.strip().lower().startswith("y"):
            print(f"  유지: {current}")
            return current

    print(f"  사용할 에이전트를 선택하세요:")
    agents = list(AGENT_COMMANDS.keys())
    for i, name in enumerate(agents, 1):
        print(f"    {i}) {name} → {AGENT_COMMANDS[name]}")
    print(f"    {len(agents) + 1}) 기타 (직접 입력)")
    print(f"    0) 없음")

    choice = prompter(f"  선택: ").strip().lower()

    # "없음" 또는 "0"
    if choice in ("없음", "0", ""):
        print(f"  {YELLOW}에이전트 미설정.{NC}")
        print(f"  {BLUE}추천: gemini (무료, Google AI)")
        if "gemini" in AGENT_INSTALL:
            print(f"  설치: {AGENT_INSTALL['gemini']}{NC}")
        return ""

    # "기타" 또는 해당 번호
    if choice in ("기타", str(len(agents) + 1)):
        cmd = prompter(f"  에이전트 명령어: ").strip()
        if cmd:
            config_set("agent", cmd)
            print(f"  {GREEN}✓ 저장: {cmd}{NC}")
            return cmd
        return ""

    # 알려진 에이전트 이름 또는 번호
    selected_name = None
    if choice in AGENT_COMMANDS:
        selected_name = choice
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(agents):
                selected_name = agents[idx]
        except ValueError:
            pass

    if selected_name:
        cmd = AGENT_COMMANDS[selected_name]
        config_set("agent", cmd)
        print(f"  {GREEN}✓ 저장: {cmd}{NC}")
        if selected_name in AGENT_INSTALL:
            print(f"  설치 명령어: {AGENT_INSTALL[selected_name]}")
        return cmd

    # 입력을 직접 명령어로 취급
    config_set("agent", choice)
    print(f"  {GREEN}✓ 저장: {choice}{NC}")
    return choice


def step_git(prompter: Callable[[str], str]) -> None:
    """[Step 4] Git 연동을 설정한다.

    Args:
        prompter: input() 대체 callable.
    """
    print(f"\n{YELLOW}[4/6] Git 연동{NC}")

    # git 설치 확인
    try:
        git_name = get_git_config("user.name")
        git_email = get_git_config("user.email")
    except RuntimeError:
        print(f"  {RED}git이 설치되어 있지 않습니다.{NC}")
        print(f"  git 설치 후 다시 실행하세요: https://git-scm.com/downloads")
        return

    # user.name / user.email 미설정 시 입력 요청
    if not git_name:
        git_name = prompter(f"  git user.name: ").strip()
        if git_name:
            set_git_config("user.name", git_name)
            print(f"  {GREEN}✓ user.name 저장됨{NC}")

    if not git_email:
        git_email = prompter(f"  git user.email: ").strip()
        if git_email:
            set_git_config("user.email", git_email)
            print(f"  {GREEN}✓ user.email 저장됨{NC}")

    if git_name and git_email:
        print(f"  {GREEN}✓{NC} {git_name} <{git_email}>")

    # git 연동 옵션 (gh 미설치 시 선택만 다시 묻기)
    while True:
        print(f"\n  Git 레포 연동 방법을 선택하세요:")
        print(f"    1) 이미 연동됨 (현재 디렉터리가 git repo)")
        print(f"    2) repo URL clone")
        print(f"    3) gh repo create (새 레포 생성)")

        choice = prompter(f"  선택 [1/2/3]: ").strip()

        if choice == "2":
            url = prompter(f"  repo URL: ").strip()
            if url:
                try:
                    subprocess.run(
                        ["git", "clone", url],
                        check=True, timeout=60,
                    )
                    print(f"  {GREEN}✓ clone 완료{NC}")
                except subprocess.CalledProcessError:
                    print(f"  {RED}clone 실패. URL을 확인하세요.{NC}")
                except FileNotFoundError:
                    print(f"  {RED}git이 설치되어 있지 않습니다.{NC}")
            break

        if choice == "3":
            gh_path = shutil.which("gh")
            if not gh_path:
                print(f"  {YELLOW}gh CLI가 설치되어 있지 않습니다.{NC}")
                print(f"  설치 방법:")
                print(f"    macOS: brew install gh")
                print(f"    Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md")
                print(f"  설치 후 다시 실행하세요.")
                # 선택만 다시 묻기 (step 전체 재실행 아님)
                continue

            repo_name = prompter(f"  레포 이름: ").strip()
            if repo_name:
                try:
                    subprocess.run(
                        ["gh", "repo", "create", repo_name, "--public", "--clone"],
                        check=True, timeout=30,
                    )
                    print(f"  {GREEN}✓ 레포 생성 및 clone 완료{NC}")
                except subprocess.CalledProcessError:
                    print(f"  {RED}레포 생성 실패. gh auth login을 확인하세요.{NC}")
            break

        # 1) 이미 연동됨 또는 기타
        print(f"  확인.")
        break


def step_username(prompter: Callable[[str], str]) -> str:
    """[Step 5] BOJ 사용자 ID를 설정한다.

    Args:
        prompter: input() 대체 callable.

    Returns:
        설정된 username 문자열 (빈 문자열 = 스킵).
    """
    print(f"\n{YELLOW}[5/6] BOJ 사용자 ID (통계 조회용){NC}")

    current = config_get("username", "")
    if current:
        print(f"  현재: {current}")
        change = prompter(f"  변경하시겠습니까? (y/N): ")
        if not change.strip().lower().startswith("y"):
            print(f"  유지: {current}")
            return current

    username = prompter(f"  BOJ 사용자 ID (없으면 Enter 스킵): ").strip()
    if username:
        config_set("username", username)
        print(f"  {GREEN}✓ 저장: {username}{NC}")
    else:
        print(f"  스킵 (나중에 boj setup --username 으로 설정 가능)")

    return username


def step_editor(prompter: Callable[[str], str]) -> str:
    """[Step 6] 에디터를 설정한다.

    Args:
        prompter: input() 대체 callable.

    Returns:
        설정된 에디터 명령어 문자열.
    """
    print(f"\n{YELLOW}[6/6] 에디터 (boj open에 사용){NC}")

    current = config_get("editor", "")
    if current:
        print(f"  현재: {current}")
        change = prompter(f"  변경하시겠습니까? (y/N): ")
        if not change.strip().lower().startswith("y"):
            print(f"  유지: {current}")
            return current

    print(f"  에디터 실행 명령어를 입력하세요.")
    print(f"  예: code (VS Code), vim, nano, idea")
    editor = prompter(f"  에디터 [code]: ").strip()
    if not editor:
        editor = ""
        print(f"  {YELLOW}에디터 미설정. boj open 명령어를 사용할 수 없습니다.{NC}")
    else:
        config_set("editor", editor)
        print(f"  {GREEN}✓ 저장: {editor}{NC}")

    return editor


# ──────────────────────────────────────────────
# 완료 + 사용법 출력
# ──────────────────────────────────────────────

def finish_setup() -> None:
    """setup_done 플래그를 생성하고 사용법을 출력한다."""
    mark_setup_done()
    print(f"\n{BLUE}========================================{NC}")
    print(f"{GREEN}✅ 설정 완료!{NC}")
    print()
    print_usage_guide()


def print_usage_guide() -> None:
    """전체 명령어 및 setup 옵션을 출력한다."""
    print(f"{BLUE}=== BOJ CLI 명령어 ==={NC}")
    print(f"  boj setup          초기 설정 마법사")
    print(f"  boj make <번호>    문제 디렉터리 생성 + 스켈레톤 코드")
    print(f"  boj open <번호>    에디터로 문제 열기")
    print(f"  boj run <번호>     테스트 케이스 실행")
    print(f"  boj commit <번호>  풀이 커밋")
    print(f"  boj submit <번호>  BOJ에 제출")
    print(f"  boj review <번호>  코드 리뷰 요청")
    print()
    print(f"{BLUE}=== setup 옵션 ==={NC}")
    print(f"  boj setup --check       현재 설정 상태 조회")
    print(f"  boj setup --root <경로>  레포 루트 경로 설정")
    print(f"  boj setup --lang <언어>  기본 언어 설정")
    print(f"  boj setup --username <ID> BOJ 사용자 ID 설정")
    print(f"  boj setup --editor <cmd>  에디터 명령어 설정")
    print(f"  boj setup --agent <name>  에이전트 설정")
    print()
    print(f"확인: boj setup --check")
    print(f"시작: boj make 4949")


# ──────────────────────────────────────────────
# 대화형 모드
# ──────────────────────────────────────────────

def run_interactive(prompter: Callable[[str], str]) -> int:
    """대화형 8단계 설정 마법사를 실행한다.

    Args:
        prompter: input() 대체 callable.

    Returns:
        종료 코드. 0=성공.
    """
    print(f"{BLUE}========================================{NC}")
    print(f"{BLUE}  BOJ CLI 초기 설정{NC}")
    print(f"{BLUE}========================================{NC}")

    if is_setup_done():
        print(f"\n  {GREEN}✓{NC} 이미 설정이 완료되었습니다.")
        print(f"  각 항목을 확인하고 변경할 수 있습니다.")

    step_root(prompter)
    step_lang(prompter)
    step_agent(prompter)
    step_git(prompter)
    step_username(prompter)
    step_editor(prompter)
    finish_setup()

    return 0


# ──────────────────────────────────────────────
# 진입점
# ──────────────────────────────────────────────

def main(
    argv: list[str] | None = None,
    prompter: Callable[[str], str] | None = None,
) -> int:
    """CLI 진입점.

    Args:
        argv: CLI 인자 리스트. None이면 sys.argv[1:].
        prompter: input() 대체 callable. None이면 builtin input.

    Returns:
        종료 코드. 0=성공, 1=실패, 130=Ctrl+C.
    """
    if argv is None:
        argv = sys.argv[1:]
    if prompter is None:
        prompter = input

    args = parse_args(argv)

    try:
        # --check 모드
        if args.check:
            run_check_mode()
            return 0

        # 비대화형 set 모드 (하나 이상의 옵션이 지정된 경우)
        has_set_option = any([
            args.root is not None,
            args.lang is not None,
            args.username is not None,
            args.editor is not None,
            args.agent is not None,
        ])
        if has_set_option:
            return run_set_mode(args)

        # 대화형 모드
        return run_interactive(prompter)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}설정이 중단되었습니다.{NC}")
        return 130


if __name__ == "__main__":
    sys.exit(main())
