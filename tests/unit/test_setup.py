"""Python setup 명령어 단위 테스트 (src/cli/boj_setup.py).

Issue #46 — TDD Red 단계.
edge-cases.md S1~S15 + 대화형/비대화형 모드 커버.

엣지케이스 커버리지 매핑:
- S1  (최초 실행)       → TestEdgeCases.test_s1_*
- S2  (부분 설정)       → TestEdgeCases.test_s2_*
- S3  (쓰기 권한 없음)  → TestEdgeCases.test_s3_*
- S4  (git 미설치)      → TestInteractiveGit.test_git_not_installed
- S5  (clone 실패)      → TestEdgeCases.test_s5_*
- S6  (gh 미설치)       → TestInteractiveGit.test_gh_create_repo_without_gh
- S7  (--check)         → TestEdgeCases.test_s7_*
- S8  (재실행)          → TestEdgeCases.test_s8_*
- S9  (agent 미설정)    → TestInteractiveAgent.test_no_agent_recommends_gemini
- S10 (설정 완료)       → TestEdgeCases.test_s10_*
- S11 (Ctrl+C)          → TestMainIntegration.test_keyboard_interrupt_exits_gracefully
- S12 (알려진 agent)    → TestInteractiveAgent.test_select_known_agent
- S13 (기타 agent)      → TestInteractiveAgent.test_select_custom_agent
- S14 (에디터 미입력)   → TestInteractiveEditor.test_empty_editor_warns
- S15 (미지원 언어)     → TestInteractiveLang.test_unsupported_lang_shows_warning
"""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

from src.cli.boj_setup import (
    parse_args,
    run_check_mode,
    run_set_mode,
    step_root,
    step_lang,
    step_agent,
    step_git,
    step_username,
    step_editor,
    finish_setup,
    print_usage_guide,
    run_interactive,
    main,
)
from src.core.config import (
    config_get,
    config_set,
    is_setup_done,
    mark_setup_done,
    AGENT_COMMANDS,
    AGENT_INSTALL,
    DEFAULTS,
    SUPPORTED_LANGS,
)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def config_env(tmp_path, monkeypatch):
    """격리된 config 환경 (test_config.py와 동일 패턴)."""
    config_dir = tmp_path / ".config" / "boj"
    config_dir.mkdir(parents=True)

    monkeypatch.setenv("BOJ_CONFIG_DIR", str(config_dir))
    for key in (
        "BOJ_PROG_LANG", "BOJ_EDITOR", "BOJ_AGENT",
        "BOJ_USERNAME", "BOJ_SOLUTION_ROOT", "BOJ_AGENT_ROOT",
    ):
        monkeypatch.delenv(key, raising=False)

    return config_dir


def make_prompter(responses: list[str]):
    """미리 정의된 응답 리스트를 순서대로 반환하는 prompter.

    Args:
        responses: 각 input() 호출에 반환할 문자열 리스트.

    Returns:
        prompter callable. 호출될 때마다 다음 응답 반환.
    """
    it = iter(responses)

    def prompter(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise AssertionError(f"Prompter ran out of responses at prompt: {prompt!r}")

    return prompter


# ──────────────────────────────────────────────
# TestParseArgs — 옵션 파싱
# ──────────────────────────────────────────────

class TestParseArgs:
    """parse_args()가 CLI 인자를 올바르게 파싱한다."""

    def test_no_args_returns_interactive_mode(self):
        """인자 없으면 대화형 모드."""
        args = parse_args([])
        assert args.check is False
        assert args.root is None
        assert args.lang is None
        assert args.username is None
        assert args.editor is None
        assert args.agent is None

    def test_check_flag(self):
        """--check 플래그 인식."""
        args = parse_args(["--check"])
        assert args.check is True

    def test_root_option(self):
        """--root <path> 인식."""
        args = parse_args(["--root", "/tmp/test"])
        assert args.root == "/tmp/test"

    def test_lang_option(self):
        """--lang <lang> 인식."""
        args = parse_args(["--lang", "python"])
        assert args.lang == "python"

    def test_username_option(self):
        """--username <id> 인식."""
        args = parse_args(["--username", "testuser"])
        assert args.username == "testuser"

    def test_editor_option(self):
        """--editor <cmd> 인식."""
        args = parse_args(["--editor", "vim"])
        assert args.editor == "vim"

    def test_agent_option(self):
        """--agent <name> 인식."""
        args = parse_args(["--agent", "claude"])
        assert args.agent == "claude"

    def test_multiple_options(self):
        """복수 옵션 동시 사용."""
        args = parse_args(["--lang", "python", "--username", "user1"])
        assert args.lang == "python"
        assert args.username == "user1"


# ──────────────────────────────────────────────
# TestCheckMode — --check
# ──────────────────────────────────────────────

class TestCheckMode:
    """run_check_mode()가 check_config()를 호출한다."""

    def test_calls_check_config(self, config_env, capsys):
        """--check 실행 시 설정 상태를 출력한다."""
        run_check_mode()
        captured = capsys.readouterr()
        assert "BOJ CLI 설정 상태" in captured.out


# ──────────────────────────────────────────────
# TestSetMode — 비대화형 개별 키 설정
# ──────────────────────────────────────────────

class TestSetMode:
    """run_set_mode()가 개별 키를 올바르게 설정한다."""

    def test_set_lang_valid(self, config_env):
        """유효한 언어 설정."""
        args = parse_args(["--lang", "python"])
        result = run_set_mode(args)
        assert result == 0
        assert config_get("prog_lang", "") == "python"

    def test_set_lang_invalid(self, config_env, capsys):
        """유효하지 않은 언어 → 에러."""
        args = parse_args(["--lang", "ruby"])
        result = run_set_mode(args)
        assert result != 0
        captured = capsys.readouterr()
        assert "지원" in captured.err or "지원" in captured.out

    def test_set_root_valid(self, config_env, tmp_path):
        """유효한 경로 설정."""
        test_dir = tmp_path / "solutions"
        test_dir.mkdir()
        args = parse_args(["--root", str(test_dir)])
        result = run_set_mode(args)
        assert result == 0
        assert config_get("boj_solution_root", "") == str(test_dir)

    def test_set_root_invalid(self, config_env, capsys):
        """존재하지 않는 경로 → 에러."""
        args = parse_args(["--root", "/nonexistent/path/abc"])
        result = run_set_mode(args)
        assert result != 0

    def test_set_username(self, config_env):
        """username 설정."""
        args = parse_args(["--username", "testuser"])
        result = run_set_mode(args)
        assert result == 0
        assert config_get("username", "") == "testuser"

    def test_set_editor(self, config_env):
        """editor 설정."""
        args = parse_args(["--editor", "vim"])
        result = run_set_mode(args)
        assert result == 0
        assert config_get("editor", "") == "vim"

    def test_set_agent_known(self, config_env):
        """알려진 agent 설정 → 명령어 자동 매핑."""
        args = parse_args(["--agent", "claude"])
        result = run_set_mode(args)
        assert result == 0
        assert config_get("agent", "") == AGENT_COMMANDS["claude"]

    def test_set_agent_custom(self, config_env):
        """알 수 없는 agent → 직접 명령어로 저장."""
        args = parse_args(["--agent", "my-custom-agent -p"])
        result = run_set_mode(args)
        assert result == 0
        assert config_get("agent", "") == "my-custom-agent -p"


# ──────────────────────────────────────────────
# TestInteractiveRoot — step 1: 경로 입력
# ──────────────────────────────────────────────

class TestInteractiveRoot:
    """step_root()가 경로를 올바르게 설정한다."""

    def test_use_current_dir(self, config_env, tmp_path, monkeypatch):
        """현재 디렉터리 선택 (1 → 확인 y)."""
        monkeypatch.chdir(tmp_path)
        prompter = make_prompter(["1", "y"])
        result = step_root(prompter)
        assert result == str(tmp_path)
        assert config_get("boj_solution_root", "") == str(tmp_path)

    def test_enter_custom_path(self, config_env, tmp_path):
        """직접 경로 입력 (2 → 경로 → 확인 y)."""
        custom = tmp_path / "my_solutions"
        custom.mkdir()
        prompter = make_prompter(["2", str(custom), "y"])
        result = step_root(prompter)
        assert result == str(custom)

    def test_invalid_path_retries(self, config_env, tmp_path, monkeypatch):
        """유효하지 않은 경로 → 재입력 요청."""
        monkeypatch.chdir(tmp_path)
        prompter = make_prompter(["2", "/nonexistent", "1", "y"])
        result = step_root(prompter)
        assert result == str(tmp_path)

    def test_existing_root_keep(self, config_env, tmp_path):
        """기존 root가 있으면 유지 선택 가능 (N)."""
        config_set("boj_solution_root", str(tmp_path))
        prompter = make_prompter(["N"])
        result = step_root(prompter)
        assert result == str(tmp_path)

    def test_existing_root_change(self, config_env, tmp_path, monkeypatch):
        """기존 root 변경 선택 (y → 현재 디렉터리 → 확인)."""
        old_root = tmp_path / "old"
        old_root.mkdir()
        new_root = tmp_path / "new"
        new_root.mkdir()
        config_set("boj_solution_root", str(old_root))
        monkeypatch.chdir(new_root)
        prompter = make_prompter(["y", "1", "y"])
        result = step_root(prompter)
        assert result == str(new_root)


# ──────────────────────────────────────────────
# TestInteractiveLang — step 2: 언어 선택
# ──────────────────────────────────────────────

class TestInteractiveLang:
    """step_lang()가 언어를 올바르게 설정한다."""

    def test_select_java(self, config_env):
        """java 선택."""
        prompter = make_prompter(["java"])
        result = step_lang(prompter)
        assert result == "java"
        assert config_get("prog_lang", "") == "java"

    def test_select_python(self, config_env):
        """python 선택."""
        prompter = make_prompter(["python"])
        result = step_lang(prompter)
        assert result == "python"

    def test_unsupported_lang_shows_warning(self, config_env, capsys):
        """미지원 언어 → 경고 후 재입력 요청."""
        prompter = make_prompter(["cpp", "java"])
        result = step_lang(prompter)
        captured = capsys.readouterr()
        assert "미지원" in captured.out or "지원" in captured.out
        assert result == "java"

    def test_existing_lang_keep(self, config_env):
        """기존 언어 유지 (N)."""
        config_set("prog_lang", "python")
        prompter = make_prompter(["N"])
        result = step_lang(prompter)
        assert result == "python"


# ──────────────────────────────────────────────
# TestInteractiveAgent — step 3: agent 선택
# ──────────────────────────────────────────────

class TestInteractiveAgent:
    """step_agent()가 agent를 올바르게 설정한다."""

    def test_select_known_agent(self, config_env, capsys):
        """알려진 agent 선택 → 명령어 자동 매핑 + 설치 안내."""
        prompter = make_prompter(["claude"])
        result = step_agent(prompter)
        assert result == AGENT_COMMANDS["claude"]
        assert config_get("agent", "") == AGENT_COMMANDS["claude"]

    def test_select_custom_agent(self, config_env):
        """기타 선택 → 직접 명령어 입력."""
        prompter = make_prompter(["기타", "my-agent -p --"])
        result = step_agent(prompter)
        assert result == "my-agent -p --"

    def test_no_agent_recommends_gemini(self, config_env, capsys):
        """agent 없음 선택 → gemini 무료 추천."""
        prompter = make_prompter(["없음"])
        step_agent(prompter)
        captured = capsys.readouterr()
        assert "gemini" in captured.out.lower() or "추천" in captured.out

    def test_agent_install_info_shown(self, config_env, capsys):
        """agent 선택 시 설치 명령어 안내."""
        prompter = make_prompter(["claude"])
        step_agent(prompter)
        captured = capsys.readouterr()
        assert "install" in captured.out.lower() or "설치" in captured.out


# ──────────────────────────────────────────────
# TestInteractiveGit — step 4: git 연동
# ──────────────────────────────────────────────

class TestInteractiveGit:
    """step_git()가 git 설정을 올바르게 처리한다."""

    def test_already_linked(self, config_env, capsys):
        """이미 연동됨 선택."""
        prompter = make_prompter(["1"])
        with patch("src.cli.boj_setup.get_git_config", side_effect=["TestUser", "test@test.com"]):
            step_git(prompter)
        captured = capsys.readouterr()
        assert "TestUser" in captured.out or "이미" in captured.out

    def test_clone_repo(self, config_env, tmp_path):
        """repo URL clone 선택."""
        prompter = make_prompter(["2", "https://github.com/user/repo.git"])
        with patch("src.cli.boj_setup.get_git_config", side_effect=["User", "user@test.com"]), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            step_git(prompter)
            # git clone이 호출되었는지 확인
            clone_calls = [c for c in mock_run.call_args_list
                           if "clone" in str(c)]
            assert len(clone_calls) > 0

    def test_gh_create_repo_with_gh(self, config_env):
        """gh repo create 선택 (gh 설치됨)."""
        prompter = make_prompter(["3", "my-boj-solutions"])
        with patch("src.cli.boj_setup.get_git_config", side_effect=["User", "user@test.com"]), \
             patch("shutil.which", return_value="/usr/bin/gh"), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            step_git(prompter)

    def test_gh_create_repo_without_gh(self, config_env, capsys):
        """gh repo create 선택 (gh 미설치) → 설치 안내 후 선택만 재질문."""
        prompter = make_prompter(["3", "1"])  # 3=gh create, 1=이미연동으로 fallback
        with patch("src.cli.boj_setup.get_git_config", side_effect=["User", "user@test.com"]), \
             patch("shutil.which", return_value=None):
            step_git(prompter)
        captured = capsys.readouterr()
        assert "gh" in captured.out and ("설치" in captured.out or "install" in captured.out.lower())

    def test_git_name_email_setup(self, config_env):
        """git user.name/email 미설정 시 입력 요청."""
        prompter = make_prompter(["1"])
        with patch("src.cli.boj_setup.get_git_config", return_value=""), \
             patch("src.cli.boj_setup.set_git_config") as mock_set:
            # name과 email 입력을 위한 추가 prompter
            extended_prompter = make_prompter(["NewUser", "new@test.com", "1"])
            step_git(extended_prompter)
            assert mock_set.call_count >= 2

    def test_git_not_installed(self, config_env, capsys):
        """git 미설치 → 경고 표시."""
        prompter = make_prompter([])
        with patch("src.cli.boj_setup.get_git_config", side_effect=RuntimeError("git을 찾을 수 없습니다")):
            step_git(prompter)
        captured = capsys.readouterr()
        assert "git" in captured.out.lower()


# ──────────────────────────────────────────────
# TestInteractiveUsername — step 5
# ──────────────────────────────────────────────

class TestInteractiveUsername:
    """step_username()이 BOJ 사용자 ID를 설정한다."""

    def test_enter_username(self, config_env):
        """username 입력."""
        prompter = make_prompter(["myuser"])
        result = step_username(prompter)
        assert result == "myuser"
        assert config_get("username", "") == "myuser"

    def test_skip_username(self, config_env):
        """빈 입력 → 스킵."""
        prompter = make_prompter([""])
        result = step_username(prompter)
        assert result == ""

    def test_existing_username_keep(self, config_env):
        """기존 username 유지."""
        config_set("username", "existing")
        prompter = make_prompter(["N"])
        result = step_username(prompter)
        assert result == "existing"


# ──────────────────────────────────────────────
# TestInteractiveEditor — step 6
# ──────────────────────────────────────────────

class TestInteractiveEditor:
    """step_editor()가 에디터를 설정한다."""

    def test_enter_editor(self, config_env):
        """에디터 명령어 입력."""
        prompter = make_prompter(["vim"])
        result = step_editor(prompter)
        assert result == "vim"
        assert config_get("editor", "") == "vim"

    def test_empty_editor_warns(self, config_env, capsys):
        """빈 입력 → boj open 불가 안내."""
        prompter = make_prompter([""])
        step_editor(prompter)
        captured = capsys.readouterr()
        assert "open" in captured.out.lower() or "불가" in captured.out


# ──────────────────────────────────────────────
# TestFinishSetup — step 7-8: 완료
# ──────────────────────────────────────────────

class TestFinishSetup:
    """finish_setup()이 setup_done 플래그를 생성하고 사용법을 출력한다."""

    def test_marks_setup_done(self, config_env):
        """setup_done 파일 생성."""
        finish_setup()
        assert is_setup_done()

    def test_prints_usage_guide(self, config_env, capsys):
        """사용법 출력 포함."""
        finish_setup()
        captured = capsys.readouterr()
        # 전 명령어 소개 확인
        for cmd in ("setup", "make", "open", "run", "commit", "submit", "review"):
            assert cmd in captured.out


# ──────────────────────────────────────────────
# TestPrintUsageGuide — 사용법 출력
# ──────────────────────────────────────────────

class TestPrintUsageGuide:
    """print_usage_guide()가 명령어와 설정 옵션을 출력한다."""

    def test_all_commands_listed(self, capsys):
        """모든 명령어가 출력에 포함."""
        print_usage_guide()
        captured = capsys.readouterr()
        for cmd in ("setup", "make", "open", "run", "commit", "submit", "review"):
            assert cmd in captured.out

    def test_setup_options_listed(self, capsys):
        """setup 옵션이 출력에 포함."""
        print_usage_guide()
        captured = capsys.readouterr()
        for opt in ("--check", "--root", "--lang", "--username", "--editor", "--agent"):
            assert opt in captured.out


# ──────────────────────────────────────────────
# TestMainIntegration — main() end-to-end
# ──────────────────────────────────────────────

class TestMainIntegration:
    """main()이 모드를 올바르게 분기한다."""

    def test_check_mode(self, config_env, capsys):
        """main(["--check"]) → check_config 호출."""
        exit_code = main(["--check"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "BOJ CLI 설정 상태" in captured.out

    def test_set_mode_lang(self, config_env):
        """main(["--lang", "python"]) → lang 설정."""
        exit_code = main(["--lang", "python"])
        assert exit_code == 0
        assert config_get("prog_lang", "") == "python"

    def test_set_mode_invalid_lang(self, config_env):
        """main(["--lang", "invalid"]) → 에러 코드."""
        exit_code = main(["--lang", "ruby"])
        assert exit_code != 0

    def test_interactive_mode_full(self, config_env, tmp_path, monkeypatch):
        """대화형 모드 전체 흐름."""
        monkeypatch.chdir(tmp_path)
        # step_root: 현 위치(1) + 확인(y)
        # step_lang: java
        # step_agent: 없음
        # step_git: 이미 연동(1)
        # step_username: testuser
        # step_editor: code
        responses = ["1", "y", "java", "없음", "1", "testuser", "code"]
        prompter = make_prompter(responses)
        with patch("src.cli.boj_setup.get_git_config", return_value="TestUser"), \
             patch("src.cli.boj_setup.set_git_config"):
            exit_code = main([], prompter=prompter)
        assert exit_code == 0
        assert is_setup_done()

    def test_keyboard_interrupt_exits_gracefully(self, config_env):
        """Ctrl+C → 정상 종료."""
        def interrupt_prompter(prompt=""):
            raise KeyboardInterrupt()
        exit_code = main([], prompter=interrupt_prompter)
        assert exit_code == 130  # 표준 Ctrl+C 종료 코드


# ──────────────────────────────────────────────
# TestEdgeCases — edge-cases.md S1~S15
# ──────────────────────────────────────────────

class TestEdgeCases:
    """edge-cases.md S1~S15 엣지케이스.

    S4, S6, S9, S11~S15는 각 step 테스트 클래스에서 커버.
    이 클래스에서는 S1, S2, S3, S5, S7, S8, S10을 검증.
    """

    def test_s1_interactive_runs_when_no_config(self, config_env, tmp_path, monkeypatch):
        """S1: 최초 실행 (config 없음) → 대화형 실행."""
        monkeypatch.chdir(tmp_path)
        responses = ["1", "y", "java", "없음", "1", "user1", "code"]
        prompter = make_prompter(responses)
        with patch("src.cli.boj_setup.get_git_config", return_value="User"), \
             patch("src.cli.boj_setup.set_git_config"):
            exit_code = main([], prompter=prompter)
        assert exit_code == 0

    def test_s2_asks_only_missing_when_partial_config(self, config_env, tmp_path, monkeypatch, capsys):
        """S2: 부분 설정 → 기존 값 유지, 누락 항목만 물어봄."""
        config_set("boj_solution_root", str(tmp_path))
        config_set("prog_lang", "java")
        # root와 lang은 이미 있으므로 N(유지)
        # agent, git, username, editor은 누락 → 입력 필요
        responses = ["N", "N", "없음", "1", "user1", "code"]
        prompter = make_prompter(responses)
        with patch("src.cli.boj_setup.get_git_config", return_value="User"), \
             patch("src.cli.boj_setup.set_git_config"):
            exit_code = main([], prompter=prompter)
        assert exit_code == 0
        # 기존 값 유지 확인
        assert config_get("boj_solution_root", "") == str(tmp_path)
        assert config_get("prog_lang", "") == "java"

    def test_s3_errors_when_config_dir_not_writable(self, config_env, monkeypatch):
        """S3: config 디렉터리 쓰기 불가 → 에러."""
        monkeypatch.setenv("BOJ_CONFIG_DIR", "/root/no_write_access")
        args = parse_args(["--lang", "java"])
        result = run_set_mode(args)
        assert result != 0

    def test_s5_shows_error_when_clone_fails(self, config_env, capsys):
        """S5: git repo clone 실패 → 에러 메시지."""
        prompter = make_prompter(["2", "https://invalid.example.com/repo.git"])
        with patch("src.cli.boj_setup.get_git_config", side_effect=["User", "user@test.com"]), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=128, stderr="fatal: repository not found")
            step_git(prompter)
        captured = capsys.readouterr()
        assert "실패" in captured.out or "Error" in captured.out or "clone" in captured.out.lower()

    def test_s7_check_displays_state(self, config_env, capsys):
        """S7: --check → ok/missing/invalid 상태 표시."""
        config_set("prog_lang", "python")
        run_check_mode()
        captured = capsys.readouterr()
        assert "python" in captured.out

    def test_s8_shows_current_and_asks_change_when_rerun(self, config_env, tmp_path, monkeypatch, capsys):
        """S8: 재실행 → 현재 값 표시 + 변경 여부 질문."""
        config_set("boj_solution_root", str(tmp_path))
        config_set("prog_lang", "java")
        mark_setup_done()

        # 모든 step에서 N(유지)을 선택
        responses = ["N", "N", "N", "1", "N", "N"]
        prompter = make_prompter(responses)
        with patch("src.cli.boj_setup.get_git_config", return_value="User"), \
             patch("src.cli.boj_setup.set_git_config"):
            exit_code = main([], prompter=prompter)
        assert exit_code == 0

    def test_s10_creates_flag_when_setup_complete(self, config_env, tmp_path, monkeypatch):
        """S10: 설정 완료 → setup_done 파일 생성."""
        monkeypatch.chdir(tmp_path)
        responses = ["1", "y", "java", "없음", "1", "user1", "code"]
        prompter = make_prompter(responses)
        with patch("src.cli.boj_setup.get_git_config", return_value="User"), \
             patch("src.cli.boj_setup.set_git_config"):
            main([], prompter=prompter)
        assert is_setup_done()
