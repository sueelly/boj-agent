"""Python make 명령어 단위 테스트 (src/core/make.py).

Issue #54 — TDD Red 단계.
edge-cases.md M1~M13 커버리지.

엣지케이스 커버리지 매핑:
- M3  (폴더 존재, -f 없음)   → TestCheckExisting.test_raises_when_dir_exists_without_force
- M3a (폴더 존재, -f 있음)   → TestCheckExisting.test_allows_overwrite_when_force
- M9  (setup_done 없음)      → TestEnsureSetup.test_runs_setup_when_no_flag
- M12 (spec 생성 실패)       → TestGenerateSpec.test_raises_when_spec_file_missing
- M13 (--keep-artifacts)      → TestCleanupArtifacts.test_keeps_all_when_flag
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.core.make import (
    ensure_setup,
    check_existing,
    generate_spec,
    cleanup_artifacts,
)
from src.core.config import (
    config_get,
    config_set,
    is_setup_done,
    mark_setup_done,
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


@pytest.fixture
def problem_dir(tmp_path):
    """테스트용 문제 디렉터리 (artifacts/ 포함)."""
    prob = tmp_path / "99999-test-problem"
    prob.mkdir()
    artifacts = prob / "artifacts"
    artifacts.mkdir()
    return prob


# ──────────────────────────────────────────────
# TestEnsureSetup — M9
# ──────────────────────────────────────────────

class TestEnsureSetup:
    """사전 조건: setup_done 플래그 확인."""

    def test_runs_setup_when_no_flag(self, config_env):
        """M9: setup_done 없으면 boj setup을 자동 실행한다."""
        assert not is_setup_done()
        with patch("src.core.make.run_setup") as mock_setup:
            ensure_setup()
            mock_setup.assert_called_once()

    def test_skips_setup_when_flag_exists(self, config_env):
        """setup_done 있으면 setup을 실행하지 않는다."""
        mark_setup_done()
        with patch("src.core.make.run_setup") as mock_setup:
            ensure_setup()
            mock_setup.assert_not_called()


# ──────────────────────────────────────────────
# TestCheckExisting — M3, M3a
# ──────────────────────────────────────────────

class TestCheckExisting:
    """사전 조건: 기존 폴더 존재 시 -f 검증."""

    def test_raises_when_dir_exists_without_force(self, tmp_path):
        """M3: 폴더 존재 + -f 없으면 SystemExit."""
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        with pytest.raises(SystemExit) as exc_info:
            check_existing(prob_dir, force=False)
        assert exc_info.value.code == 1

    def test_allows_overwrite_when_force(self, tmp_path):
        """M3a: 폴더 존재 + -f 있으면 정상 진행 (예외 없음)."""
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        check_existing(prob_dir, force=True)  # 예외 없음

    def test_passes_when_dir_not_exists(self, tmp_path):
        """폴더 미존재 시 정상 진행."""
        prob_dir = tmp_path / "99999-test"
        check_existing(prob_dir, force=False)  # 예외 없음

    def test_error_message_contains_folder_name(self, tmp_path, capsys):
        """에러 메시지에 폴더 이름과 -f 안내가 포함된다."""
        prob_dir = tmp_path / "4949-괄호의-값"
        prob_dir.mkdir()
        with pytest.raises(SystemExit):
            check_existing(prob_dir, force=False)
        captured = capsys.readouterr()
        assert "4949" in captured.err or "4949" in captured.out
        assert "-f" in captured.err or "-f" in captured.out


# ──────────────────────────────────────────────
# TestGenerateSpec — M12
# ──────────────────────────────────────────────

class TestGenerateSpec:
    """Step 2: problem.spec.json 생성."""

    def test_raises_when_spec_file_missing(self, problem_dir):
        """M12: 에이전트 실행 후 spec 파일 없으면 SystemExit."""
        with patch("src.core.make.run_agent", return_value=0):
            with pytest.raises(SystemExit) as exc_info:
                generate_spec(problem_dir, "echo MOCK")
            assert exc_info.value.code == 1

    def test_raises_when_spec_invalid_json(self, problem_dir):
        """M12: spec 파일이 유효하지 않은 JSON이면 SystemExit."""
        spec_path = problem_dir / "artifacts" / "problem.spec.json"
        spec_path.write_text("NOT VALID JSON {{{")
        with patch("src.core.make.run_agent", return_value=0):
            with pytest.raises(SystemExit) as exc_info:
                generate_spec(problem_dir, "echo MOCK")
            assert exc_info.value.code == 1

    def test_succeeds_when_spec_valid(self, problem_dir):
        """유효한 spec 생성 시 정상 반환."""
        spec_path = problem_dir / "artifacts" / "problem.spec.json"
        spec_path.write_text(json.dumps({
            "schemaVersion": "1.0",
            "source": {"problemId": "99999"},
            "input": {},
            "output": {},
        }))
        with patch("src.core.make.run_agent", return_value=0):
            result = generate_spec(problem_dir, "echo MOCK")
        assert result is not None

    def test_error_message_suggests_retry(self, problem_dir, capsys):
        """에러 메시지에 '-f 로 재시도' 안내가 포함된다."""
        with patch("src.core.make.run_agent", return_value=0):
            with pytest.raises(SystemExit):
                generate_spec(problem_dir, "echo MOCK")
        captured = capsys.readouterr()
        assert "-f" in captured.err or "-f" in captured.out


# ──────────────────────────────────────────────
# TestCleanupArtifacts — M13
# ──────────────────────────────────────────────

class TestCleanupArtifacts:
    """Step 5: artifacts 정리."""

    def test_removes_json_keeps_images(self, problem_dir):
        """cleanup은 JSON만 삭제하고 이미지는 유지한다."""
        artifacts = problem_dir / "artifacts"
        (artifacts / "problem.json").write_text("{}")
        (artifacts / "problem.spec.json").write_text("{}")
        (artifacts / "image.png").write_bytes(b"PNG")

        cleanup_artifacts(problem_dir, keep=False)

        assert not (artifacts / "problem.json").exists()
        assert not (artifacts / "problem.spec.json").exists()
        assert (artifacts / "image.png").exists()

    def test_keeps_all_when_flag(self, problem_dir):
        """M13: --keep-artifacts 시 모든 파일 유지."""
        artifacts = problem_dir / "artifacts"
        (artifacts / "problem.json").write_text("{}")
        (artifacts / "problem.spec.json").write_text("{}")

        cleanup_artifacts(problem_dir, keep=True)

        assert (artifacts / "problem.json").exists()
        assert (artifacts / "problem.spec.json").exists()

    def test_no_error_when_artifacts_dir_missing(self, tmp_path):
        """artifacts/ 폴더 없어도 에러 없이 진행."""
        prob_dir = tmp_path / "99999-no-artifacts"
        prob_dir.mkdir()
        cleanup_artifacts(prob_dir, keep=False)  # 예외 없음

    def test_removes_only_spec_json_files(self, problem_dir):
        """problem.json, problem.spec.json만 삭제. 다른 JSON은 유지."""
        artifacts = problem_dir / "artifacts"
        (artifacts / "problem.json").write_text("{}")
        (artifacts / "problem.spec.json").write_text("{}")
        (artifacts / "other_data.json").write_text("{}")

        cleanup_artifacts(problem_dir, keep=False)

        assert not (artifacts / "problem.json").exists()
        assert not (artifacts / "problem.spec.json").exists()
        assert (artifacts / "other_data.json").exists()
