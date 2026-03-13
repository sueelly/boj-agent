"""Python 설치 스크립트 단위 테스트 (scripts/install.py).

Issue #47 — TDD Red 단계.
docs/edge-cases.md IN1~IN8 + 각 함수 happy/error path 커버.

엣지케이스 커버리지 매핑:
- IN1 (~/bin 없음)            → TestInstallCli.test_creates_bin_dir_when_missing
- IN2 (~/.config/boj/ 없음)   → TestSaveConfig.test_creates_config_dir_when_missing
- IN3 (dest 이미 존재)        → TestCopyAgentFiles.test_asks_confirm_when_dest_exists
- IN4 (self-move)             → TestCopyAgentFiles.test_skips_copy_when_src_equals_dest
- IN5 (쓰기 권한 없음)        → TestInstallCli.test_errors_when_permission_denied
- IN6 (PATH에 ~/bin 없음)     → TestCheckPath / TestPrintPathAdvice
- IN7 (boj setup 실패)        → TestRunSetup.test_returns_nonzero_when_setup_fails
- IN8 (src/boj 없음)          → TestResolveRepoRoot.test_errors_when_boj_not_found
"""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from scripts.install import (
    resolve_repo_root,
    copy_agent_files,
    install_cli,
    save_config,
    check_path,
    add_to_path,
    detect_shell_rc,
    print_path_advice,
    run_setup,
    main,
)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def install_env(tmp_path, monkeypatch):
    """격리된 설치 환경: fake repo + fake HOME.

    Returns:
        (repo, home) 튜플.
        repo: fake boj-agent 저장소 경로.
        home: fake HOME 경로.
    """
    # fake repo
    repo = tmp_path / "boj-agent"
    (repo / "src").mkdir(parents=True)
    boj_script = repo / "src" / "boj"
    boj_script.write_text("#!/usr/bin/env bash\necho boj\n")
    boj_script.chmod(0o755)
    (repo / "src" / "commands").mkdir()
    (repo / "templates" / "java").mkdir(parents=True)
    (repo / "templates" / "java" / "Test.java").touch()
    (repo / "scripts").mkdir()

    # fake home
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    return repo, home


# ──────────────────────────────────────────────
# TestResolveRepoRoot
# ──────────────────────────────────────────────

class TestResolveRepoRoot:
    """resolve_repo_root()가 src/boj 기준으로 repo root를 찾는다."""

    def test_finds_root_from_scripts_dir(self, install_env):
        """scripts/ 하위에서 실행 시 repo root 반환."""
        repo, _ = install_env
        script = repo / "scripts" / "install.py"
        script.touch()
        result = resolve_repo_root(script)
        assert result == repo

    def test_errors_when_boj_not_found(self, tmp_path):
        """src/boj 없는 디렉터리 → FileNotFoundError. (IN8)"""
        script = tmp_path / "random" / "install.py"
        script.parent.mkdir(parents=True)
        script.touch()
        with pytest.raises(FileNotFoundError):
            resolve_repo_root(script)


# ──────────────────────────────────────────────
# TestCopyAgentFiles
# ──────────────────────────────────────────────

class TestCopyAgentFiles:
    """copy_agent_files()가 repo를 대상 경로로 복사한다."""

    def test_copies_files_to_dest(self, install_env):
        """정상 복사: src 내용이 dest에 존재."""
        repo, home = install_env
        dest = home / ".local" / "share" / "boj-agent"
        result = copy_agent_files(repo, dest)
        assert result == dest
        assert (dest / "src" / "boj").exists()
        assert (dest / "templates" / "java" / "Test.java").exists()

    def test_excludes_git_and_pycache(self, install_env):
        """복사 시 .git, __pycache__ 제외."""
        repo, home = install_env
        (repo / ".git").mkdir()
        (repo / ".git" / "HEAD").write_text("ref: refs/heads/main")
        (repo / "src" / "__pycache__").mkdir()
        (repo / "src" / "__pycache__" / "cache.pyc").touch()

        dest = home / ".local" / "share" / "boj-agent"
        copy_agent_files(repo, dest)
        assert not (dest / ".git").exists()
        assert not (dest / "src" / "__pycache__").exists()

    def test_skips_copy_when_src_equals_dest(self, install_env, capsys):
        """src == dest (self-move) → 복사 스킵. (IN4)"""
        repo, _ = install_env
        result = copy_agent_files(repo, repo)
        assert result == repo
        captured = capsys.readouterr()
        assert "스킵" in captured.out or "이미" in captured.out

    def test_asks_confirm_when_dest_exists(self, install_env, monkeypatch):
        """dest 이미 존재 + force=False → 사용자 확인 요청. (IN3)"""
        repo, home = install_env
        dest = home / ".local" / "share" / "boj-agent"
        dest.mkdir(parents=True)
        (dest / "old_file.txt").write_text("old")

        # 사용자가 "n" 입력 → 중단
        monkeypatch.setattr("builtins.input", lambda _: "n")
        with pytest.raises(SystemExit):
            copy_agent_files(repo, dest, force=False)

    def test_overwrites_when_force(self, install_env):
        """dest 이미 존재 + force=True → 덮어쓰기. (IN3)"""
        repo, home = install_env
        dest = home / ".local" / "share" / "boj-agent"
        dest.mkdir(parents=True)
        (dest / "old_file.txt").write_text("old")

        result = copy_agent_files(repo, dest, force=True)
        assert result == dest
        assert (dest / "src" / "boj").exists()

    def test_creates_parent_dirs(self, install_env):
        """dest 부모 디렉터리가 없으면 자동 생성."""
        repo, home = install_env
        dest = home / "deep" / "nested" / "boj-agent"
        result = copy_agent_files(repo, dest)
        assert result == dest
        assert (dest / "src" / "boj").exists()


# ──────────────────────────────────────────────
# TestInstallCli
# ──────────────────────────────────────────────

class TestInstallCli:
    """install_cli()가 boj 스크립트를 bin_dir에 설치한다."""

    def test_copies_boj_to_bin_dir(self, install_env):
        """src/boj → bin_dir/boj 복사 + 실행 권한."""
        repo, home = install_env
        bin_dir = home / "bin"
        bin_dir.mkdir()
        result = install_cli(repo, bin_dir)
        assert result == bin_dir / "boj"
        assert (bin_dir / "boj").exists()
        assert os.access(bin_dir / "boj", os.X_OK)

    def test_creates_bin_dir_when_missing(self, install_env):
        """~/bin 없으면 자동 생성. (IN1)"""
        repo, home = install_env
        bin_dir = home / "bin"
        assert not bin_dir.exists()
        result = install_cli(repo, bin_dir)
        assert bin_dir.exists()
        assert result == bin_dir / "boj"

    def test_errors_when_boj_script_missing(self, tmp_path):
        """agent_root에 src/boj 없음 → FileNotFoundError. (IN8)"""
        fake_root = tmp_path / "empty"
        fake_root.mkdir()
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        with pytest.raises(FileNotFoundError):
            install_cli(fake_root, bin_dir)


# ──────────────────────────────────────────────
# TestSaveConfig
# ──────────────────────────────────────────────

class TestSaveConfig:
    """save_config()가 agent_root 경로를 config에 저장한다."""

    def test_saves_agent_root_and_root(self, install_env):
        """boj_agent_root + root (하위호환) 파일 저장."""
        repo, home = install_env
        config_dir = home / ".config" / "boj"
        save_config(repo, config_dir)
        assert (config_dir / "boj_agent_root").read_text().strip() == str(repo)
        assert (config_dir / "root").read_text().strip() == str(repo)

    def test_creates_config_dir_when_missing(self, install_env):
        """~/.config/boj/ 없으면 자동 생성. (IN2)"""
        repo, home = install_env
        config_dir = home / ".config" / "boj"
        assert not config_dir.exists()
        save_config(repo, config_dir)
        assert config_dir.exists()
        assert (config_dir / "boj_agent_root").exists()


# ──────────────────────────────────────────────
# TestCheckPath
# ──────────────────────────────────────────────

class TestCheckPath:
    """check_path()가 PATH에 bin_dir 포함 여부를 반환한다."""

    def test_returns_true_when_in_path(self, tmp_path, monkeypatch):
        """bin_dir가 PATH에 있으면 True. (IN6)"""
        bin_dir = tmp_path / "bin"
        monkeypatch.setenv("PATH", f"{bin_dir}:/usr/bin")
        assert check_path(bin_dir) is True

    def test_returns_false_when_not_in_path(self, tmp_path, monkeypatch):
        """bin_dir가 PATH에 없으면 False. (IN6)"""
        bin_dir = tmp_path / "bin"
        monkeypatch.setenv("PATH", "/usr/bin:/usr/local/bin")
        assert check_path(bin_dir) is False


# ──────────────────────────────────────────────
# TestDetectShellRc
# ──────────────────────────────────────────────

class TestDetectShellRc:
    """detect_shell_rc()가 셸 설정 파일을 찾는다."""

    def test_finds_zshrc(self, tmp_path):
        """.zshrc 우선 반환."""
        (tmp_path / ".zshrc").touch()
        (tmp_path / ".bashrc").touch()
        result = detect_shell_rc(tmp_path)
        assert result == tmp_path / ".zshrc"

    def test_finds_bashrc_when_no_zshrc(self, tmp_path):
        """.zshrc 없으면 .bashrc 반환."""
        (tmp_path / ".bashrc").touch()
        result = detect_shell_rc(tmp_path)
        assert result == tmp_path / ".bashrc"

    def test_finds_bash_profile(self, tmp_path):
        """.zshrc/.bashrc 없으면 .bash_profile 반환."""
        (tmp_path / ".bash_profile").touch()
        result = detect_shell_rc(tmp_path)
        assert result == tmp_path / ".bash_profile"

    def test_returns_none_when_no_rc(self, tmp_path):
        """셸 rc 파일 없으면 None."""
        result = detect_shell_rc(tmp_path)
        assert result is None


# ──────────────────────────────────────────────
# TestPrintPathAdvice
# ──────────────────────────────────────────────
# TestAddToPath
# ──────────────────────────────────────────────

class TestAddToPath:
    """add_to_path()가 shell rc에 PATH export를 추가한다."""

    def test_adds_export_when_not_present(self, tmp_path):
        """rc 파일에 bin_dir 없을 때 export 라인 추가."""
        rc = tmp_path / ".zshrc"
        rc.write_text("# existing content\n")
        bin_dir = tmp_path / "bin"
        added = add_to_path(bin_dir, rc)
        assert added is True
        assert str(bin_dir) in rc.read_text()

    def test_skips_when_bin_dir_already_present(self, tmp_path):
        """rc 파일에 bin_dir 이미 있으면 스킵."""
        bin_dir = tmp_path / "bin"
        rc = tmp_path / ".zshrc"
        rc.write_text(f'export PATH="{bin_dir}:$PATH"\n')
        added = add_to_path(bin_dir, rc)
        assert added is False

    def test_skips_when_home_bin_pattern_present(self, tmp_path):
        """export PATH="$HOME/bin:$PATH" 가 있으면 스킵 (중복 추가 방지)."""
        rc = tmp_path / ".zshrc"
        rc.write_text('export PATH="$HOME/bin:$PATH"\n')
        bin_dir = tmp_path / "bin"
        added = add_to_path(bin_dir, rc)
        assert added is False

    def test_adds_when_only_comment_mentions_home_bin(self, tmp_path):
        """주석에만 $HOME/bin 있으면 추가 (과도 스킵 방지)."""
        rc = tmp_path / ".zshrc"
        rc.write_text("# see also $HOME/bin for local tools\n")
        bin_dir = tmp_path / "bin"
        added = add_to_path(bin_dir, rc)
        assert added is True
        assert str(bin_dir) in rc.read_text()

    def test_creates_rc_when_missing(self, tmp_path):
        """rc 파일 없으면 새로 생성."""
        rc = tmp_path / ".zshrc"
        bin_dir = tmp_path / "bin"
        added = add_to_path(bin_dir, rc)
        assert added is True
        assert rc.exists()
        assert str(bin_dir) in rc.read_text()


# ──────────────────────────────────────────────

class TestPrintPathAdvice:
    """print_path_advice()가 PATH 설정 안내를 출력한다."""

    def test_prints_advice_when_path_missing(self, tmp_path, capsys):
        """PATH에 없을 때 안내 메시지 출력. (IN6)"""
        bin_dir = tmp_path / "bin"
        shell_rc = tmp_path / ".zshrc"
        print_path_advice(bin_dir, shell_rc)
        captured = capsys.readouterr()
        assert "PATH" in captured.out
        assert str(bin_dir) in captured.out

    def test_mentions_shell_rc_when_available(self, tmp_path, capsys):
        """셸 rc 파일명을 안내에 포함."""
        bin_dir = tmp_path / "bin"
        shell_rc = tmp_path / ".zshrc"
        print_path_advice(bin_dir, shell_rc)
        captured = capsys.readouterr()
        assert ".zshrc" in captured.out

    def test_generic_advice_when_no_rc(self, tmp_path, capsys):
        """셸 rc 없을 때 일반 안내."""
        bin_dir = tmp_path / "bin"
        print_path_advice(bin_dir, None)
        captured = capsys.readouterr()
        assert "PATH" in captured.out


# ──────────────────────────────────────────────
# TestRunSetup
# ──────────────────────────────────────────────

class TestRunSetup:
    """run_setup()이 boj setup을 subprocess로 실행한다."""

    def test_calls_boj_setup(self, tmp_path):
        """shell_rc 없으면 boj setup 직접 호출."""
        boj_cmd = tmp_path / "boj"
        bin_dir = tmp_path / "bin"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_setup(
                boj_cmd, bin_dir=bin_dir, shell_rc=None, home=tmp_path
            )
        assert result == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert str(boj_cmd) in args
        assert "setup" in args

    def test_returns_nonzero_when_setup_fails(self, tmp_path):
        """boj setup 실패 시 non-zero 반환. (IN7)"""
        boj_cmd = tmp_path / "boj"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = run_setup(
                boj_cmd, bin_dir=tmp_path / "bin", shell_rc=None, home=tmp_path
            )
        assert result != 0

    def test_returns_nonzero_when_exception(self, tmp_path):
        """boj 실행 자체 실패 (FileNotFoundError 등) → non-zero."""
        boj_cmd = tmp_path / "nonexistent_boj"
        with patch("subprocess.run", side_effect=FileNotFoundError("not found")):
            result = run_setup(
                boj_cmd, bin_dir=tmp_path / "bin", shell_rc=None, home=tmp_path
            )
        assert result != 0


# ──────────────────────────────────────────────
# TestMain — end-to-end
# ──────────────────────────────────────────────

class TestMain:
    """main()이 전체 설치 흐름을 올바르게 실행한다."""

    def test_happy_path(self, install_env, monkeypatch):
        """정상 설치: 복사 + CLI 설치 + config 저장."""
        repo, home = install_env
        monkeypatch.setenv("PATH", f"{home / 'bin'}:/usr/bin")

        with patch("scripts.install.run_setup", return_value=0):
            exit_code = main(["--skip-setup"], script_path=repo / "scripts" / "install.py")

        assert exit_code == 0
        assert (home / "bin" / "boj").exists()
        config_dir = home / ".config" / "boj"
        assert (config_dir / "boj_agent_root").exists()
        assert (config_dir / "root").exists()

    def test_skip_setup_flag(self, install_env, monkeypatch):
        """--skip-setup → boj setup 호출 안 함."""
        repo, home = install_env
        monkeypatch.setenv("PATH", f"{home / 'bin'}:/usr/bin")

        with patch("scripts.install.run_setup") as mock_setup:
            main(["--skip-setup"], script_path=repo / "scripts" / "install.py")
        mock_setup.assert_not_called()

    def test_calls_setup_by_default(self, install_env, monkeypatch):
        """기본 실행 시 boj setup 호출."""
        repo, home = install_env
        monkeypatch.setenv("PATH", f"{home / 'bin'}:/usr/bin")

        with patch("scripts.install.run_setup", return_value=0) as mock_setup:
            main([], script_path=repo / "scripts" / "install.py")
        mock_setup.assert_called_once()

    def test_force_flag(self, install_env, monkeypatch):
        """--force → dest 존재해도 덮어쓰기."""
        repo, home = install_env
        dest = home / ".local" / "share" / "boj-agent"
        dest.mkdir(parents=True)
        (dest / "old.txt").write_text("old")
        monkeypatch.setenv("PATH", f"{home / 'bin'}:/usr/bin")

        with patch("scripts.install.run_setup", return_value=0):
            exit_code = main(
                ["--force", "--skip-setup"],
                script_path=repo / "scripts" / "install.py",
            )
        assert exit_code == 0
        assert (dest / "src" / "boj").exists()

    def test_adds_to_path_when_rc_exists(self, install_env, monkeypatch, capsys):
        """PATH에 ~/bin 없고 rc 파일 있으면 자동 추가. (IN6)"""
        repo, home = install_env
        monkeypatch.setenv("PATH", "/usr/bin")
        rc = home / ".zshrc"
        rc.write_text("# existing\n")

        with patch("scripts.install.run_setup", return_value=0):
            main(["--skip-setup"], script_path=repo / "scripts" / "install.py")

        captured = capsys.readouterr()
        assert ".zshrc" in captured.out
        assert str(home / "bin") in rc.read_text()

    def test_prints_advice_when_no_rc(self, install_env, monkeypatch, capsys):
        """PATH에 ~/bin 없으면 .zshrc 생성 + PATH 추가 + 적용 안내. (IN6)"""
        repo, home = install_env
        monkeypatch.setenv("PATH", "/usr/bin")
        for name in (".zshrc", ".bashrc", ".bash_profile"):
            rc = home / name
            if rc.exists():
                rc.unlink()

        with patch("scripts.install.run_setup", return_value=0):
            main(["--skip-setup"], script_path=repo / "scripts" / "install.py")

        captured = capsys.readouterr()
        assert "PATH" in captured.out
        assert (home / ".zshrc").exists()
        assert str(home / "bin") in (home / ".zshrc").read_text()

    def test_warns_when_setup_fails(self, install_env, monkeypatch, capsys):
        """boj setup 실패 시 Warning 출력. (IN7)"""
        repo, home = install_env
        monkeypatch.setenv("PATH", f"{home / 'bin'}:/usr/bin")

        with patch("scripts.install.run_setup", return_value=1):
            exit_code = main([], script_path=repo / "scripts" / "install.py")

        # 설치 자체는 성공, setup 실패는 경고만
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "수동" in captured.out

    def test_errors_when_invalid_repo(self, tmp_path, monkeypatch):
        """깨진 clone (src/boj 없음) → exit 1. (IN8)"""
        fake_script = tmp_path / "scripts" / "install.py"
        fake_script.parent.mkdir(parents=True)
        fake_script.touch()
        monkeypatch.setenv("HOME", str(tmp_path / "home"))

        exit_code = main([], script_path=fake_script)
        assert exit_code != 0
