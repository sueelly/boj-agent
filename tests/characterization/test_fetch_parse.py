import json
import os
import subprocess
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "lib"))
from boj_client import parse_problem

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"

FIXTURE_PROBLEMS = sorted(
    p.name for p in FIXTURES_DIR.iterdir()
    if p.is_dir() and (p / "raw.html").exists()
)


class TestParseHappy:
    """Happy path: fixture HTML → problem.json 필드 일치"""

    @pytest.mark.parametrize("problem_num", FIXTURE_PROBLEMS)
    def test_parse_matches_fixture_json(self, problem_num):
        """모든 픽스처에 대해 parse_problem 결과가 problem.json과 일치한다."""
        fix_dir = FIXTURES_DIR / problem_num
        html = (fix_dir / "raw.html").read_text(encoding="utf-8")
        expected = json.loads((fix_dir / "problem.json").read_text(encoding="utf-8"))

        result = parse_problem(html, problem_num)

        assert result["problem_num"] == expected["problem_num"]
        assert result["title"] == expected["title"]
        assert len(result["samples"]) == len(expected["samples"])
        for r_sample, e_sample in zip(result["samples"], expected["samples"]):
            assert r_sample["input"] == e_sample["input"]
            assert r_sample["output"] == e_sample["output"]

    @pytest.mark.parametrize("problem_num", FIXTURE_PROBLEMS)
    def test_parse_has_required_fields(self, problem_num):
        """모든 픽스처에 대해 필수 필드가 존재한다."""
        fix_dir = FIXTURES_DIR / problem_num
        html = (fix_dir / "raw.html").read_text(encoding="utf-8")

        result = parse_problem(html, problem_num)

        for field in ("problem_num", "title", "time_limit", "memory_limit",
                       "description_html", "input_html", "output_html", "samples", "images"):
            assert field in result, f"Missing field: {field}"


class TestParseMalformed:
    """Malformed HTML 처리"""

    def test_empty_title_when_no_problem_title(self):
        """제목 없는 HTML → title이 빈 문자열."""
        html = "<html><body><div id='problem_description'>test</div></body></html>"
        result = parse_problem(html, "99999")
        assert result["title"] == ""

    def test_empty_samples_when_no_sample_input(self):
        """sample-input-* 없는 HTML → samples가 빈 리스트."""
        html = "<html><body><span id='problem_title'>Test</span></body></html>"
        result = parse_problem(html, "99999")
        assert result["samples"] == []


class TestCLIIntegration:
    """boj_client.py CLI 통합 테스트"""

    def test_cli_generates_problem_json(self, tmp_path):
        """CLI로 실행 시 problem.json이 생성된다."""
        fix_html = FIXTURES_DIR / "99999" / "raw.html"
        env = {**dict(os.environ), "BOJ_CLIENT_TEST_HTML": str(fix_html)}

        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "src" / "lib" / "boj_client.py"),
             "--problem", "99999", "--out", str(tmp_path)],
            env=env, capture_output=True, text=True, timeout=10,
        )

        assert result.returncode == 0
        out_file = tmp_path / "problem.json"
        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert data["problem_num"] == "99999"

    def test_cli_exits_one_when_title_missing(self, tmp_path):
        """제목이 없는 HTML로 CLI 실행 시 exit 1."""
        bad_html = tmp_path / "bad.html"
        bad_html.write_text("<html><body></body></html>")
        env = {**dict(os.environ), "BOJ_CLIENT_TEST_HTML": str(bad_html)}

        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "src" / "lib" / "boj_client.py"),
             "--problem", "99999", "--out", str(tmp_path / "out")],
            env=env, capture_output=True, text=True, timeout=10,
        )

        assert result.returncode == 1
        assert "Error:" in result.stderr
