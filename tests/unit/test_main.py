"""src/cli/main.py 통합 디스패처 단위 테스트."""

import os
import subprocess
import sys
import tempfile

import pytest


@pytest.fixture()
def setup_done_env():
    """setup_done 파일이 있는 격리된 config 환경."""
    with tempfile.TemporaryDirectory() as config_dir:
        open(os.path.join(config_dir, "setup_done"), "w").close()
        env = {**os.environ, "BOJ_CONFIG_DIR": config_dir}
        yield env


class TestMainHelp:
    """--help / help / 인수 없음 → 사용법 출력."""

    @pytest.mark.parametrize("args", [[], ["--help"], ["-h"], ["help"]])
    def test_should_print_usage_when_help_or_no_args(self, args):
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", *args],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "사용법: boj" in result.stdout


class TestMainUnknownCommand:
    """알 수 없는 서브커맨드 → exit 1 + 에러 메시지."""

    def test_should_exit_1_when_unknown_subcommand(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "nonexistent"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Unknown subcommand: nonexistent" in result.stderr


class TestMainRouting:
    """서브커맨드가 올바른 모듈로 라우팅되는지 확인."""

    @pytest.mark.parametrize(
        "command",
        ["make", "run", "open", "commit", "review", "submit", "setup"],
    )
    def test_should_route_to_subcommand_help(self, command, setup_done_env):
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", command, "--help"],
            capture_output=True,
            text=True,
            env=setup_done_env,
        )
        # 각 서브커맨드의 --help는 argparse가 0으로 종료
        assert result.returncode == 0
        assert command in result.stdout.lower() or "usage" in result.stdout.lower()


class TestMainSetupGuard:
    """setup_done 없으면 setup 외 명령어 차단."""

    def test_should_block_when_setup_not_done(self):
        with tempfile.TemporaryDirectory() as config_dir:
            env = {**os.environ, "BOJ_CONFIG_DIR": config_dir}
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.main", "run", "--help"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 1
            assert "설정이 완료되지 않았습니다" in result.stdout

    def test_should_allow_setup_when_not_done(self):
        with tempfile.TemporaryDirectory() as config_dir:
            env = {**os.environ, "BOJ_CONFIG_DIR": config_dir}
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.main", "setup", "--help"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0
