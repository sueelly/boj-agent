"""src.core.normalizer 단위 테스트.

Issue #54 — normalize() 순수 함수 검증.
fixture 4개 (99999, 1000, 6588, 9495)의 problem.json → readme.md 변환 검증.
edge-cases.md NR1~NR5 기준.
"""

import json
from pathlib import Path

import pytest

from src.core.normalizer import normalize

# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

FIXTURE_IDS = ["99999", "1000", "6588", "9495"]


@pytest.fixture(params=FIXTURE_IDS)
def fixture_data(request):
    """fixture problem.json과 expected readme.md를 로드한다."""
    fixture_dir = FIXTURES_DIR / request.param
    problem = json.loads((fixture_dir / "problem.json").read_text(encoding="utf-8"))
    expected_readme = (fixture_dir / "readme.md").read_text(encoding="utf-8")
    return problem, expected_readme, request.param


# ──────────────────────────────────────────────
# NR1: 정상 problem dict → README 스냅샷 비교
# ──────────────────────────────────────────────

class TestNormalizeSnapshot:
    """normalize() 스냅샷 비교 검증."""

    def test_produces_expected_readme(self, fixture_data):
        """NR1: fixture의 problem.json으로 생성한 README가 expected와 일치한다."""
        problem, expected_readme, fixture_id = fixture_data
        result = normalize(problem)
        assert result == expected_readme, (
            f"fixture {fixture_id}: normalize() 출력이 expected readme.md와 불일치"
        )


# ──────────────────────────────────────────────
# NR1: 필수 필드 포함 검증
# ──────────────────────────────────────────────

class TestNormalizeContent:
    """normalize() 출력 내용 검증."""

    def test_contains_problem_title(self, fixture_data):
        """README에 문제 제목이 포함되어야 한다."""
        problem, _, fixture_id = fixture_data
        result = normalize(problem)
        assert problem["title"] in result, (
            f"fixture {fixture_id}: 제목 '{problem['title']}'이 README에 없음"
        )

    def test_contains_problem_number(self, fixture_data):
        """README에 문제 번호가 포함되어야 한다."""
        problem, _, fixture_id = fixture_data
        result = normalize(problem)
        assert problem["problem_num"] in result, (
            f"fixture {fixture_id}: 문제번호 '{problem['problem_num']}'이 README에 없음"
        )

    def test_contains_boj_link(self, fixture_data):
        """README에 BOJ 문제 링크가 포함되어야 한다."""
        problem, _, _ = fixture_data
        result = normalize(problem)
        expected_url = f"https://www.acmicpc.net/problem/{problem['problem_num']}"
        assert expected_url in result

    def test_contains_all_samples(self, fixture_data):
        """README에 모든 예제 입출력이 포함되어야 한다."""
        problem, _, fixture_id = fixture_data
        result = normalize(problem)
        for sample in problem.get("samples", []):
            assert sample["input"] in result, (
                f"fixture {fixture_id}: 예제 입력 {sample['id']}이 README에 없음"
            )
            assert sample["output"] in result, (
                f"fixture {fixture_id}: 예제 출력 {sample['id']}이 README에 없음"
            )

    def test_contains_time_and_memory_limit(self, fixture_data):
        """README에 시간/메모리 제한이 포함되어야 한다."""
        problem, _, _ = fixture_data
        result = normalize(problem)
        assert problem["time_limit"] in result
        assert problem["memory_limit"] in result


# ──────────────────────────────────────────────
# NR2: samples 빈 배열
# ──────────────────────────────────────────────

class TestNormalizeEdgeCases:
    """normalize() 엣지케이스 검증."""

    def test_empty_samples_produces_no_sample_section(self):
        """NR2: samples가 빈 배열이면 예제 섹션이 없어야 한다."""
        problem = {
            "problem_num": "12345",
            "title": "테스트 문제",
            "time_limit": "1 초",
            "memory_limit": "256 MB",
            "description_html": "<p>설명</p>",
            "input_html": "<p>입력</p>",
            "output_html": "<p>출력</p>",
            "samples": [],
        }
        result = normalize(problem)
        assert "예제 입력" not in result
        assert "예제 출력" not in result

    def test_missing_optional_fields(self):
        """NR3: description_html/input_html/output_html가 없어도 동작한다."""
        problem = {
            "problem_num": "12345",
            "title": "테스트 문제",
            "time_limit": "2 초",
            "memory_limit": "512 MB",
        }
        result = normalize(problem)
        assert "12345번: 테스트 문제" in result
        assert "2 초" in result
        assert "512 MB" in result

    def test_html_entities_preserved(self):
        """NR5: HTML 특수문자가 보존되어야 한다."""
        problem = {
            "problem_num": "99999",
            "title": "A &lt; B &amp; C",
            "time_limit": "1 초",
            "memory_limit": "256 MB",
            "description_html": "<p>1 &lt; N &le; 10<sup>5</sup></p>",
            "input_html": "",
            "output_html": "",
            "samples": [],
        }
        result = normalize(problem)
        assert "A &lt; B &amp; C" in result
        assert "&lt; N &le; 10<sup>5</sup>" in result

    def test_image_tags_preserved_in_description(self):
        """NR4: description_html 내 img 태그가 그대로 유지되어야 한다."""
        problem = {
            "problem_num": "10799",
            "title": "쇠막대기",
            "time_limit": "1 초",
            "memory_limit": "256 MB",
            "description_html": '<p>설명<img src="https://example.com/img.png" alt="그림"></p>',
            "input_html": "",
            "output_html": "",
            "samples": [],
        }
        result = normalize(problem)
        assert '<img src="https://example.com/img.png" alt="그림">' in result
