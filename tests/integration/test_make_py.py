"""boj make 통합 테스트 — 모킹 기반 (네트워크 불필요).

fixture 99999를 사용하여 전체 파이프라인을 검증한다.
BOJ_CLIENT_TEST_HTML 환경변수로 네트워크를 격리한다.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.exceptions import ProblemExistsError
from src.core.make import (
    check_existing,
    fetch_problem,
    generate_readme,
    cleanup_artifacts,
)


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def config_env(tmp_path, monkeypatch):
    """격리된 config 환경."""
    config_dir = tmp_path / ".config" / "boj"
    config_dir.mkdir(parents=True)
    monkeypatch.setenv("BOJ_CONFIG_DIR", str(config_dir))
    for key in (
        "BOJ_PROG_LANG", "BOJ_EDITOR", "BOJ_AGENT",
        "BOJ_USERNAME", "BOJ_SOLUTION_ROOT", "BOJ_AGENT_ROOT",
    ):
        monkeypatch.delenv(key, raising=False)
    return config_dir


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
        {"id": 2, "input": "10 20", "output": "30"},
    ],
    "images": [],
}


class TestMakePyIntegration:
    """모킹 기반 통합 테스트 — happy path."""

    def test_make_creates_readme_and_problem_json(self, tmp_path):
        """happy path: fetch → problem.json + README.md 생성."""
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM),
        ):
            problem_dir = fetch_problem(
                "99999", problem_dir=tmp_path / "99999-두-수의-합",
            )

        # problem.json 확인
        problem_json = problem_dir / "artifacts" / "problem.json"
        assert problem_json.exists()
        data = json.loads(problem_json.read_text())
        assert data["problem_num"] == "99999"

        # README.md 생성
        readme_path = generate_readme(problem_json)
        assert readme_path.exists()
        content = readme_path.read_text()
        assert "99999번: 두 수의 합" in content
        assert "예제 입력 1" in content

    def test_make_exits_when_dir_exists_without_force(self, tmp_path):
        """M3: 폴더 존재 + -f 없음 → ProblemExistsError."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        with pytest.raises(ProblemExistsError):
            check_existing(problem_dir, force=False)

    def test_make_allows_force_overwrite(self, tmp_path):
        """M3a: 폴더 존재 + -f → 정상 진행."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        check_existing(problem_dir, force=True)  # 예외 없음

    def test_cleanup_removes_artifacts_after_pipeline(self, tmp_path):
        """파이프라인 후 cleanup이 JSON만 삭제한다."""
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM),
        ):
            problem_dir = fetch_problem(
                "99999", problem_dir=tmp_path / "99999-test",
            )

        # spec 파일도 생성 (cleanup 대상)
        spec_path = problem_dir / "artifacts" / "problem.spec.json"
        spec_path.write_text("{}")

        cleanup_artifacts(problem_dir, keep=False)

        assert not (problem_dir / "artifacts" / "problem.json").exists()
        assert not spec_path.exists()

    def test_keep_artifacts_preserves_all(self, tmp_path):
        """--keep-artifacts 시 모든 파일 유지."""
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM),
        ):
            problem_dir = fetch_problem(
                "99999", problem_dir=tmp_path / "99999-test",
            )

        cleanup_artifacts(problem_dir, keep=True)

        assert (problem_dir / "artifacts" / "problem.json").exists()
