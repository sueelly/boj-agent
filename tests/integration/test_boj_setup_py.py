"""통합 테스트: src/cli/boj_setup.py (Python setup 명령어).

Issue #46 — subprocess로 실제 CLI를 호출해 end-to-end 동작 검증.
단위 테스트(test_setup.py)와 달리 실제 파일시스템과 프로세스를 사용한다.

커버 범위:
    IP1  --check → 설정 상태 출력
    IP2  --lang valid → 파일 저장 + exit 0
    IP3  --lang invalid → exit != 0 + 에러 메시지
    IP4  --root valid → 파일 저장 + exit 0
    IP5  --root invalid → exit != 0
    IP6  --username → 파일 저장
    IP7  --editor → 파일 저장
    IP8  --agent known → 명령어 자동 매핑 저장
    IP9  --agent custom → 그대로 저장
    IP10 복수 옵션 동시 적용
    IP11 --check가 저장된 값을 반영한다
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
PYTHON = sys.executable


def run_setup(args: list[str], config_dir: Path) -> subprocess.CompletedProcess:
    """src.cli.boj_setup을 subprocess로 실행한다."""
    return subprocess.run(
        [PYTHON, "-m", "src.cli.boj_setup"] + args,
        capture_output=True,
        text=True,
        env={
            **__import__("os").environ,
            "BOJ_CONFIG_DIR": str(config_dir),
            "PYTHONPATH": str(REPO_ROOT),
            "NO_COLOR": "1",  # ANSI 코드 제거 → 출력 검증 단순화
        },
        cwd=REPO_ROOT,
    )


@pytest.fixture
def config_dir(tmp_path):
    """격리된 config 디렉터리."""
    d = tmp_path / ".config" / "boj"
    d.mkdir(parents=True)
    return d


# ── IP1: --check ─────────────────────────────────────────────────────────────

class TestCheckMode:
    def test_ip1_check_shows_status_header(self, config_dir):
        """IP1: --check → 설정 상태 헤더 출력."""
        result = run_setup(["--check"], config_dir)
        assert result.returncode == 0
        assert "BOJ CLI 설정 상태" in result.stdout

    def test_ip1_check_shows_unset_indicator(self, config_dir):
        """IP1: --check → 미설정 항목 표시."""
        result = run_setup(["--check"], config_dir)
        assert "미설정" in result.stdout or "✗" in result.stdout


# ── IP2~IP3: --lang ───────────────────────────────────────────────────────────

class TestSetLang:
    def test_ip2_valid_lang_saves_file(self, config_dir):
        """IP2: --lang python → 파일 저장 + exit 0."""
        result = run_setup(["--lang", "python"], config_dir)
        assert result.returncode == 0
        assert (config_dir / "prog_lang").read_text().strip() == "python"

    def test_ip3_invalid_lang_exits_nonzero(self, config_dir):
        """IP3: --lang ruby → exit != 0."""
        result = run_setup(["--lang", "ruby"], config_dir)
        assert result.returncode != 0

    def test_ip3_invalid_lang_shows_error_message(self, config_dir):
        """IP3: --lang ruby → 에러 메시지에 언어명 포함."""
        result = run_setup(["--lang", "ruby"], config_dir)
        combined = result.stdout + result.stderr
        assert "ruby" in combined or "지원" in combined


# ── IP4~IP5: --root ───────────────────────────────────────────────────────────

class TestSetRoot:
    def test_ip4_valid_root_saves_file(self, config_dir, tmp_path):
        """IP4: --root <존재하는 경로> → 파일 저장 + exit 0."""
        valid_dir = tmp_path / "solutions"
        valid_dir.mkdir()
        result = run_setup(["--root", str(valid_dir)], config_dir)
        assert result.returncode == 0
        assert (config_dir / "boj_solution_root").read_text().strip() == str(valid_dir)

    def test_ip5_invalid_root_exits_nonzero(self, config_dir):
        """IP5: --root <존재하지 않는 경로> → exit != 0."""
        result = run_setup(["--root", "/nonexistent/path/xyz_boj_test"], config_dir)
        assert result.returncode != 0


# ── IP6: --username ───────────────────────────────────────────────────────────

class TestSetUsername:
    def test_ip6_username_saves_file(self, config_dir):
        """IP6: --username → 파일 저장."""
        result = run_setup(["--username", "testuser123"], config_dir)
        assert result.returncode == 0
        assert (config_dir / "username").read_text().strip() == "testuser123"


# ── IP7: --editor ─────────────────────────────────────────────────────────────

class TestSetEditor:
    def test_ip7_editor_saves_file(self, config_dir):
        """IP7: --editor → 파일 저장."""
        result = run_setup(["--editor", "vim"], config_dir)
        assert result.returncode == 0
        assert (config_dir / "editor").read_text().strip() == "vim"


# ── IP8~IP9: --agent ─────────────────────────────────────────────────────────

class TestSetAgent:
    def test_ip8_known_agent_maps_to_command(self, config_dir):
        """IP8: --agent claude → AGENT_COMMANDS 자동 매핑 저장."""
        result = run_setup(["--agent", "claude"], config_dir)
        assert result.returncode == 0
        saved = (config_dir / "agent").read_text().strip()
        assert "claude" in saved  # 매핑된 커맨드에 claude 포함

    def test_ip9_custom_agent_saved_as_is(self, config_dir):
        """IP9: --agent <unknown> → 직접 명령어로 저장."""
        result = run_setup(["--agent", "my-agent --flag"], config_dir)
        assert result.returncode == 0
        assert (config_dir / "agent").read_text().strip() == "my-agent --flag"


# ── IP10: 복수 옵션 ────────────────────────────────────────────────────────────

class TestMultipleOptions:
    def test_ip10_multiple_options_all_saved(self, config_dir):
        """IP10: 복수 옵션 동시 적용 → 모두 저장."""
        result = run_setup(
            ["--lang", "java", "--username", "multiuser", "--editor", "code"],
            config_dir,
        )
        assert result.returncode == 0
        assert (config_dir / "prog_lang").read_text().strip() == "java"
        assert (config_dir / "username").read_text().strip() == "multiuser"
        assert (config_dir / "editor").read_text().strip() == "code"


# ── IP11: --check가 저장된 값을 반영한다 ──────────────────────────────────────

class TestCheckReflectsSavedValues:
    def test_ip11_check_shows_previously_set_values(self, config_dir):
        """IP11: 설정 후 --check → 저장된 값이 출력에 반영된다."""
        run_setup(["--lang", "python", "--username", "checkuser"], config_dir)
        result = run_setup(["--check"], config_dir)
        assert "python" in result.stdout
        assert "checkuser" in result.stdout
