"""Python config 모듈 단위 테스트 (src/core/config.py).

Issue #45 — TDD Red 단계: 모든 테스트는 config.py 구현 전까지 실패한다.
edge-cases.md CF1~CF21 기준.
"""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# 구현 후 import 경로 — 현재는 ImportError 발생 예상
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
    GIT_NOT_FOUND_MSG,
    AGENT_COMMANDS,
    AGENT_INSTALL,
    DEFAULTS,
)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def config_env(tmp_path, monkeypatch):
    """격리된 config 환경.

    - ~/.config/boj/ 를 tmp_path로 격리
    - BOJ_* 환경변수 초기화
    """
    config_dir = tmp_path / ".config" / "boj"
    config_dir.mkdir(parents=True)

    monkeypatch.setenv("BOJ_CONFIG_DIR", str(config_dir))
    for key in (
        "BOJ_PROG_LANG", "BOJ_EDITOR", "BOJ_AGENT",
        "BOJ_USERNAME", "BOJ_SOLUTION_ROOT", "BOJ_AGENT_ROOT",
    ):
        monkeypatch.delenv(key, raising=False)

    return config_dir


# ──────────────────────────────────────────────
# 우선순위: env > file > default (CF1, CF2, CF3)
# ──────────────────────────────────────────────

class TestConfigPriority:
    """설정값 우선순위 검증."""

    def test_returns_env_over_file_when_both_set(self, config_env, monkeypatch):
        """CF1: 환경변수와 파일 모두 있을 때 환경변수 값을 반환한다."""
        (config_env / "prog_lang").write_text("java")
        monkeypatch.setenv("BOJ_PROG_LANG", "python")

        result = config_get("prog_lang", "java")
        assert result == "python"

    def test_returns_file_when_no_env(self, config_env):
        """CF2: 환경변수 없고 파일만 있으면 파일 값을 반환한다."""
        (config_env / "prog_lang").write_text("python")

        result = config_get("prog_lang", "java")
        assert result == "python"

    def test_returns_default_when_no_env_no_file(self, config_env):
        """CF3: 환경변수도 파일도 없으면 기본값을 반환한다."""
        result = config_get("prog_lang", "java")
        assert result == "java"


# ──────────────────────────────────────────────
# read/write 라운드트립 (CF4)
# ──────────────────────────────────────────────

class TestConfigReadWrite:
    """설정값 저장/읽기 검증."""

    def test_set_then_get_roundtrip(self, config_env):
        """CF4: set 후 get으로 동일 값을 읽는다."""
        config_set("prog_lang", "python")
        assert config_get("prog_lang", "java") == "python"

    def test_set_creates_config_dir_when_missing(self, tmp_path, monkeypatch):
        """CF4: 설정 디렉터리가 없으면 자동 생성 후 저장한다."""
        config_dir = tmp_path / "new_config"
        monkeypatch.setenv("BOJ_CONFIG_DIR", str(config_dir))

        config_set("prog_lang", "python")

        assert (config_dir / "prog_lang").read_text().strip() == "python"

    def test_set_overwrites_existing_value(self, config_env):
        """기존 값을 덮어쓴다."""
        config_set("editor", "vim")
        config_set("editor", "code")
        assert config_get("editor", "vim") == "code"


# ──────────────────────────────────────────────
# 파일시스템 엣지케이스 (CF5, CF6, CF7)
# ──────────────────────────────────────────────

class TestConfigFilesystem:
    """파일시스템 관련 엣지케이스."""

    def test_set_raises_when_dir_not_writable(self, config_env):
        """CF5: 쓰기 권한 없으면 에러를 발생시킨다."""
        config_env.chmod(0o444)
        try:
            with pytest.raises((PermissionError, OSError)):
                config_set("prog_lang", "python")
        finally:
            config_env.chmod(0o755)

    def test_get_returns_default_when_file_empty(self, config_env):
        """CF6: 파일 내용이 빈 문자열이면 기본값을 반환한다."""
        (config_env / "prog_lang").write_text("")

        result = config_get("prog_lang", "java")
        assert result == "java"

    def test_get_strips_trailing_whitespace(self, config_env):
        """CF7: trailing whitespace/newline을 strip한다."""
        (config_env / "prog_lang").write_text("python  \n")

        result = config_get("prog_lang", "java")
        assert result == "python"


# ──────────────────────────────────────────────
# setup_done 플래그 (CF8, CF9)
# ──────────────────────────────────────────────

class TestSetupDone:
    """setup_done 플래그 검증."""

    def test_is_setup_done_returns_true_when_flag_exists(self, config_env):
        """CF8: setup_done 파일이 있으면 True를 반환한다."""
        (config_env / "setup_done").touch()
        assert is_setup_done() is True

    def test_is_setup_done_returns_false_when_no_flag(self, config_env):
        """CF9: setup_done 파일이 없으면 False를 반환한다."""
        assert is_setup_done() is False

    def test_mark_setup_done_creates_flag(self, config_env):
        """mark_setup_done 호출 시 파일이 생성된다."""
        mark_setup_done()
        assert (config_env / "setup_done").exists()


# ──────────────────────────────────────────────
# 경로 검증 (CF10, CF11)
# ──────────────────────────────────────────────

class TestPathValidation:
    """경로 존재 여부 검증."""

    def test_validate_path_returns_true_when_exists(self, tmp_path):
        """CF10/CF11: 경로가 존재하면 True를 반환한다."""
        assert validate_path(str(tmp_path)) is True

    def test_validate_path_returns_false_when_missing(self):
        """CF10/CF11: 경로가 존재하지 않으면 False를 반환한다."""
        assert validate_path("/nonexistent/path/xyz") is False

    def test_validate_path_returns_false_when_empty(self):
        """경로가 빈 문자열이면 False를 반환한다."""
        assert validate_path("") is False


# ──────────────────────────────────────────────
# 언어 검증 (CF12, CF13, CF14)
# ──────────────────────────────────────────────

class TestLanguageValidation:
    """언어 검증."""

    def test_validate_lang_accepts_java(self):
        """CF12: java는 지원 언어이다."""
        assert validate_lang("java") is True

    def test_validate_lang_accepts_python(self):
        """CF12: python은 지원 언어이다."""
        assert validate_lang("python") is True

    def test_validate_lang_rejects_unsupported(self):
        """CF13: fortran은 미지원 언어이다."""
        assert validate_lang("fortran") is False

    def test_validate_lang_rejects_empty(self):
        """빈 문자열은 미지원이다."""
        assert validate_lang("") is False


# ──────────────────────────────────────────────
# agent 커맨드 매핑 (CF15, CF16)
# ──────────────────────────────────────────────

class TestAgentMapping:
    """agent 이름 → 실행 명령어 매핑."""

    def test_known_agent_returns_command(self):
        """CF15: 알려진 agent 이름에 대해 매핑된 커맨드를 반환한다."""
        cmd = get_agent_command("claude")
        assert cmd is not None
        assert len(cmd) > 0

    def test_known_agents_include_expected(self):
        """CF15: 최소한 claude, copilot, cursor, gemini, opencode가 포함된다."""
        for name in ("claude", "copilot", "cursor", "gemini", "opencode"):
            assert name in AGENT_COMMANDS, f"{name} not in AGENT_COMMANDS"

    def test_unknown_agent_returns_none(self):
        """CF16: 알 수 없는 agent 이름에 대해 None을 반환한다."""
        assert get_agent_command("unknown_agent_xyz") is None

    def test_agent_install_has_same_keys_as_commands(self):
        """AGENT_INSTALL과 AGENT_COMMANDS는 동일한 키를 가진다."""
        assert set(AGENT_INSTALL.keys()) == set(AGENT_COMMANDS.keys())

    def test_agent_install_values_are_nonempty(self):
        """AGENT_INSTALL의 모든 값은 비어있지 않다."""
        for name, cmd in AGENT_INSTALL.items():
            assert cmd, f"AGENT_INSTALL[{name!r}] is empty"


# ──────────────────────────────────────────────
# git config 연동 (CF17, CF18, CF19)
# ──────────────────────────────────────────────

class TestGitConfig:
    """git config 읽기/쓰기."""

    def test_get_git_config_returns_value_when_set(self):
        """CF17: git config 값이 설정되어 있으면 반환한다."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="TestUser\n", returncode=0
            )
            assert get_git_config("user.name") == "TestUser"

    def test_get_git_config_returns_empty_when_unset(self):
        """CF18: git config 값이 미설정이면 빈 문자열을 반환한다."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="\n", returncode=1
            )
            assert get_git_config("user.name") == ""

    def test_get_git_config_raises_when_git_missing(self):
        """CF19: git이 미설치면 Error 메시지와 함께 예외를 발생시킨다 (중단)."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(RuntimeError) as exc_info:
                get_git_config("user.name")
            assert "git을 찾을 수 없습니다" in str(exc_info.value)
            assert exc_info.value.args[0] == GIT_NOT_FOUND_MSG

    def test_set_git_config_calls_subprocess(self):
        """set_git_config가 git config --global을 호출한다."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            set_git_config("user.name", "TestUser")
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "git" in args
            assert "user.name" in args
            assert "TestUser" in args


# ──────────────────────────────────────────────
# check_config 출력 (CF20)
# ──────────────────────────────────────────────

class TestCheckConfig:
    """설정 상태 조회 출력."""

    def test_check_config_shows_all_keys(self, config_env, capsys):
        """CF20: 모든 설정 키의 상태를 출력한다."""
        config_set("prog_lang", "java")
        config_set("editor", "code")

        check_config()

        captured = capsys.readouterr()
        assert "prog_lang" in captured.out
        assert "editor" in captured.out
        assert "solution_root" in captured.out

    def test_check_config_shows_missing_indicator(self, config_env, capsys):
        """CF20: 미설정 키에 대해 missing 표시를 한다."""
        check_config()

        captured = capsys.readouterr()
        # 아무것도 설정되지 않은 상태에서 missing/미설정 표시 확인
        assert "missing" in captured.out.lower() or "미설정" in captured.out

    def test_check_config_shows_ok_when_root_paths_exist(self, config_env, tmp_path, capsys):
        """CF10/CF11, S7: solution_root/agent_root가 존재하면 ✓ 로 표시한다 (경로검증 존재)."""
        existing_dir = str(tmp_path)
        config_set("solution_root", existing_dir)
        config_set("boj_agent_root", existing_dir)

        check_config()

        captured = capsys.readouterr()
        assert existing_dir in captured.out
        for line in captured.out.splitlines():
            if "solution_root" in line or "agent_root" in line:
                assert "✓" in line, f"root 라인에 ✓ 없음: {line}"
                assert "미설정" not in line and "깨져 있습니다" not in line, f"root 라인에 ok 표시 필요: {line}"

    def test_check_config_shows_invalid_path_as_broken(self, config_env, capsys):
        """S7, CF10/CF11: 설정된 경로가 존재하지 않으면 '깨져 있습니다'로 구분한다."""
        config_set("solution_root", "/nonexistent/solution/path")
        config_set("boj_agent_root", "/nonexistent/agent/path")

        check_config()

        captured = capsys.readouterr()
        assert "깨져 있습니다" in captured.out
        assert "/nonexistent/solution/path" in captured.out
        assert "/nonexistent/agent/path" in captured.out
        # invalid인 경우 '미설정'이 아님을 확인 (같은 줄에 미설정 없어야 함)
        lines = captured.out.splitlines()
        for line in lines:
            if "깨져 있습니다" in line:
                assert "미설정" not in line, "invalid 경로에는 '미설정'이 아닌 '깨져 있습니다' 표시"

    def test_check_config_handles_git_missing_without_crash(self, config_env, capsys):
        """git 미설치 시 check_config는 크래시하지 않고 git 상태만 '찾을 수 없습니다'로 표시한다."""
        with patch("src.core.config.get_git_config", side_effect=RuntimeError(GIT_NOT_FOUND_MSG)):
            check_config()

        captured = capsys.readouterr()
        assert "git을 찾을 수 없습니다" in captured.out
        assert "setup:" in captured.out or "setup_done" in captured.out
        assert "Traceback" not in captured.out
        assert "RuntimeError" not in captured.out


# ──────────────────────────────────────────────
# BOJ_CONFIG_DIR 오버라이드 (CF21)
# ──────────────────────────────────────────────

class TestConfigDirOverride:
    """BOJ_CONFIG_DIR 환경변수로 디렉터리 오버라이드."""

    def test_uses_custom_config_dir(self, tmp_path, monkeypatch):
        """CF21: BOJ_CONFIG_DIR로 설정 디렉터리를 변경할 수 있다."""
        custom_dir = tmp_path / "custom_config"
        custom_dir.mkdir()
        monkeypatch.setenv("BOJ_CONFIG_DIR", str(custom_dir))

        config_set("prog_lang", "python")

        assert (custom_dir / "prog_lang").exists()
        assert config_get("prog_lang", "java") == "python"


# ──────────────────────────────────────────────
# DEFAULTS 상수
# ──────────────────────────────────────────────

class TestDefaults:
    """기본값 상수 검증."""

    def test_defaults_has_required_keys(self):
        """DEFAULTS에 모든 config key가 정의되어 있다."""
        required = {"prog_lang", "editor", "agent", "username",
                     "solution_root", "boj_agent_root"}
        assert required.issubset(set(DEFAULTS.keys()))

    def test_default_lang_is_java(self):
        """기본 언어는 java이다."""
        assert DEFAULTS["prog_lang"] == "java"
