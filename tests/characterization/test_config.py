import os
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from helpers import REPO_ROOT, run_boj  # noqa: E402


def run_config_get(env, key, default=""):
    """config.sh의 boj_config_get을 bash로 호출한다."""
    tmp_path = Path(env["BOJ_ROOT"])
    script = f'''
        source "{tmp_path}/src/lib/config.sh"
        boj_config_get "{key}" "{default}"
    '''
    result = subprocess.run(
        ["bash", "-c", script],
        env=env, capture_output=True, text=True, timeout=5,
    )
    return result.stdout


class TestEnvVarPriority:
    """환경변수가 파일 설정보다 우선한다."""

    def test_env_overrides_file_for_lang(self, boj_env):
        """BOJ_LANG 환경변수가 파일 설정보다 우선한다."""
        tmp_path, env = boj_env
        config_dir = Path(env["BOJ_CONFIG_DIR"])
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "lang").write_text("python")
        env["BOJ_LANG"] = "cpp"

        result = run_config_get(env, "lang", "java")
        assert result == "cpp"

    def test_env_overrides_file_for_editor(self, boj_env):
        """BOJ_EDITOR 환경변수가 파일 설정보다 우선한다."""
        tmp_path, env = boj_env
        config_dir = Path(env["BOJ_CONFIG_DIR"])
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "editor").write_text("vim")
        env["BOJ_EDITOR"] = "cursor"

        result = run_config_get(env, "editor", "code")
        assert result == "cursor"

    def test_env_overrides_default_for_agent(self, boj_env):
        """BOJ_AGENT_CMD 환경변수가 기본값보다 우선한다."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"

        result = run_config_get(env, "agent_cmd", "")
        assert result == "echo MOCK"


class TestFileConfig:
    """파일 설정이 기본값보다 우선한다."""

    def test_file_overrides_default_for_lang(self, boj_env):
        """파일에 lang이 있으면 기본값 java 대신 사용한다."""
        tmp_path, env = boj_env
        # Remove env var if exists
        env.pop("BOJ_LANG", None)
        config_dir = Path(env["BOJ_CONFIG_DIR"])
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "lang").write_text("python")

        result = run_config_get(env, "lang", "java")
        assert result == "python"

    def test_file_missing_returns_default(self, boj_env):
        """파일이 없으면 기본값을 반환한다."""
        tmp_path, env = boj_env
        env.pop("BOJ_LANG", None)

        result = run_config_get(env, "lang", "java")
        assert result == "java"


class TestDefaultValues:
    """config 파일과 환경변수 모두 없을 때 기본값."""

    def test_default_lang_is_java(self, boj_env):
        tmp_path, env = boj_env
        env.pop("BOJ_LANG", None)
        result = run_config_get(env, "lang", "java")
        assert result == "java"

    def test_default_editor_is_code(self, boj_env):
        tmp_path, env = boj_env
        # boj_env already sets BOJ_EDITOR=true, so remove it to test default
        env.pop("BOJ_EDITOR", None)
        result = run_config_get(env, "editor", "code")
        assert result == "code"

    def test_default_agent_is_empty(self, boj_env):
        tmp_path, env = boj_env
        env.pop("BOJ_AGENT_CMD", None)
        result = run_config_get(env, "agent_cmd", "")
        assert result == ""


class TestConfigDirOverride:
    """BOJ_CONFIG_DIR로 커스텀 config 디렉터리를 사용할 수 있다."""

    def test_custom_config_dir(self, boj_env):
        tmp_path, env = boj_env
        custom_dir = tmp_path / "custom_config"
        custom_dir.mkdir()
        (custom_dir / "lang").write_text("kotlin")
        env["BOJ_CONFIG_DIR"] = str(custom_dir)
        env.pop("BOJ_LANG", None)

        result = run_config_get(env, "lang", "java")
        assert result == "kotlin"


class TestSetupCheck:
    """boj setup --check 명령이 현재 설정을 표시한다."""

    def test_setup_check_shows_defaults(self, boj_env):
        """설정 없이 --check 실행 시 기본 상태를 보여준다."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        result = run_boj(env, "setup", "--check")
        assert result.returncode == 0
        assert "lang:" in result.stdout
        assert "editor:" in result.stdout


class TestSetupNonInteractive:
    """boj setup --lang/--root 비대화형 설정."""

    def test_setup_lang_saves(self, boj_env):
        """--lang python으로 설정 시 lang 파일이 생성된다."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        result = run_boj(env, "setup", "--lang", "python")
        assert result.returncode == 0
        config_dir = Path(env["BOJ_CONFIG_DIR"])
        assert (config_dir / "lang").read_text().strip() == "python"

    def test_setup_invalid_lang_fails(self, boj_env):
        """잘못된 언어로 설정 시 에러가 발생한다."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        result = run_boj(env, "setup", "--lang", "brainfuck")
        assert result.returncode != 0
        assert "Error:" in result.stderr or "지원하지 않는" in result.stderr

    def test_setup_root_invalid_path_fails(self, boj_env):
        """존재하지 않는 경로로 root 설정 시 에러가 발생한다."""
        tmp_path, env = boj_env
        env["BOJ_AGENT_CMD"] = "echo MOCK"
        result = run_boj(env, "setup", "--root", "/nonexistent/path")
        assert result.returncode != 0
