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
    fetch_problem,
    generate_readme,
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


# ──────────────────────────────────────────────
# Fixtures — fetch/readme 테스트용
# ──────────────────────────────────────────────

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

SAMPLE_PROBLEM = {
    "problem_num": "99999",
    "title": "두 수의 합",
    "time_limit": "1 초",
    "memory_limit": "256 MB",
    "description_html": "<p>두 정수 A와 B를 입력받은 다음, A+B를 출력하는 프로그램을 작성하시오.</p>",
    "input_html": "<p>첫째 줄에 A와 B가 주어진다.</p>",
    "output_html": "<p>첫째 줄에 A+B를 출력한다.</p>",
    "samples": [
        {"id": 1, "input": "1 2", "output": "3"},
        {"id": 2, "input": "3 4", "output": "7"},
    ],
    "images": [],
}


# ──────────────────────────────────────────────
# TestFetchProblem — Step 0
# ──────────────────────────────────────────────

class TestFetchProblem:
    """Step 0: BOJ fetch → problem.json."""

    def test_creates_problem_json_in_artifacts(self, tmp_path):
        """정상 동작: problem.json이 artifacts/에 생성된다."""
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>") as mock_fetch,
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM) as mock_parse,
        ):
            result = fetch_problem("99999", problem_dir=tmp_path / "99999-두-수의-합")

        assert result.exists()
        problem_json = result / "artifacts" / "problem.json"
        assert problem_json.exists()
        data = json.loads(problem_json.read_text())
        assert data["problem_num"] == "99999"
        assert data["title"] == "두 수의 합"

    def test_raises_when_html_fetch_fails(self, tmp_path):
        """네트워크 실패 시 SystemExit."""
        with patch("src.core.make.fetch_html", side_effect=SystemExit(1)):
            with pytest.raises(SystemExit) as exc_info:
                fetch_problem("99999", problem_dir=tmp_path / "99999-test")
            assert exc_info.value.code == 1

    def test_passes_image_mode_to_processing(self, tmp_path):
        """image_mode 파라미터가 이미지 처리에 전달된다."""
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM),
        ):
            result = fetch_problem(
                "99999",
                image_mode="skip",
                problem_dir=tmp_path / "99999-test",
            )
            # skip 모드: images 처리가 skip됨 (에러 없이 완료)
            assert result.exists()

    def test_raises_when_dir_exists_without_force_before_creating_artifacts(self, tmp_path):
        """기존 폴더 존재 시 artifacts 생성 전에 SystemExit."""
        # SAMPLE_PROBLEM의 제목을 기반으로 생성될 디렉터리 이름과 동일하게 미리 생성
        existing_dir = tmp_path / "99999-두-수의-합"
        existing_dir.mkdir()

        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM),
        ):
            with pytest.raises(SystemExit) as exc_info:
                fetch_problem("99999", base_dir=tmp_path)

        assert exc_info.value.code == 1
        # artifacts/ 디렉터리가 새로 생성되지 않았는지 확인
        assert not (existing_dir / "artifacts").exists()


# ──────────────────────────────────────────────
# TestGenerateReadme — Step 1
# ──────────────────────────────────────────────

class TestGenerateReadme:
    """Step 1: problem.json → README.md 생성."""

    def test_creates_readme_from_problem_json(self, tmp_path):
        """정상 동작: problem.json에서 README.md를 생성한다."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir()
        problem_json = artifacts / "problem.json"
        problem_json.write_text(json.dumps(SAMPLE_PROBLEM, ensure_ascii=False))

        readme_path = generate_readme(problem_json)

        assert readme_path.exists()
        content = readme_path.read_text()
        assert "99999번: 두 수의 합" in content

    def test_raises_when_problem_json_missing(self, tmp_path):
        """problem.json이 없으면 에러를 발생시킨다."""
        missing = tmp_path / "nonexistent" / "artifacts" / "problem.json"
        with pytest.raises((SystemExit, FileNotFoundError)):
            generate_readme(missing)

    def test_readme_contains_problem_title(self, tmp_path):
        """README에 문제 제목이 포함된다."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir()
        problem_json = artifacts / "problem.json"
        problem_json.write_text(json.dumps(SAMPLE_PROBLEM, ensure_ascii=False))

        readme_path = generate_readme(problem_json)
        content = readme_path.read_text()

        assert "두 수의 합" in content
        assert "예제 입력 1" in content
        assert "예제 출력 1" in content

    def test_readme_matches_fixture_snapshot(self):
        """fixture 99999의 problem.json → readme.md 스냅샷과 일치한다."""
        fixture_dir = FIXTURES_DIR / "99999"
        problem_json = fixture_dir / "problem.json"
        expected = (fixture_dir / "readme.md").read_text(encoding="utf-8")

        readme_path = generate_readme(problem_json)
        result = readme_path.read_text()

        assert result == expected
