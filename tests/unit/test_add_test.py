"""src/core/add_test.py 단위 테스트.

Issue #88 — boj add-test 명령어.
"""

import json
from pathlib import Path

import pytest

from src.core.exceptions import BojError
from src.core.add_test import (
    load_existing_test_cases,
    next_test_id,
    is_duplicate,
    merge_test_cases,
    save_test_cases,
    parse_agent_response,
    build_add_test_prompt,
)


class TestLoadExistingTestCases:
    """기존 test_cases.json 로드."""

    def test_loads_existing(self, tmp_path):
        tc_dir = tmp_path / "test"
        tc_dir.mkdir()
        (tc_dir / "test_cases.json").write_text(json.dumps({
            "testCases": [{"id": 1, "input": "1 2", "expected": "3"}]
        }))
        result = load_existing_test_cases(tmp_path)
        assert len(result) == 1
        assert result[0]["input"] == "1 2"

    def test_returns_empty_when_missing(self, tmp_path):
        assert load_existing_test_cases(tmp_path) == []


class TestNextTestId:
    """다음 테스트 ID 계산."""

    def test_returns_1_for_empty(self):
        assert next_test_id([]) == 1

    def test_returns_next_id(self):
        existing = [{"id": 1}, {"id": 3}, {"id": 2}]
        assert next_test_id(existing) == 4

    def test_handles_missing_id(self):
        existing = [{"input": "1"}, {"id": 5}]
        assert next_test_id(existing) == 6


class TestIsDuplicate:
    """중복 감지."""

    def test_detects_exact_duplicate(self):
        existing = [{"input": "1 2", "expected": "3"}]
        assert is_duplicate({"input": "1 2"}, existing) is True

    def test_detects_whitespace_duplicate(self):
        existing = [{"input": "1 2 ", "expected": "3"}]
        assert is_duplicate({"input": " 1 2"}, existing) is True

    def test_no_duplicate(self):
        existing = [{"input": "1 2", "expected": "3"}]
        assert is_duplicate({"input": "3 4"}, existing) is False

    def test_empty_existing(self):
        assert is_duplicate({"input": "1 2"}, []) is False


class TestMergeTestCases:
    """테스트 케이스 병합."""

    def test_merges_new_cases(self):
        existing = [{"id": 1, "input": "1 2", "expected": "3"}]
        new = [{"input": "3 4", "expected": "7"}]
        merged, added = merge_test_cases(existing, new)
        assert added == 1
        assert len(merged) == 2
        assert merged[1]["id"] == 2
        assert merged[1]["input"] == "3 4"

    def test_skips_duplicates(self):
        existing = [{"id": 1, "input": "1 2", "expected": "3"}]
        new = [{"input": "1 2", "expected": "3"}]
        merged, added = merge_test_cases(existing, new)
        assert added == 0
        assert len(merged) == 1

    def test_adds_description_with_mode(self):
        merged, _ = merge_test_cases([], [{"input": "1", "expected": "1"}], mode="edge")
        assert "edge" in merged[0]["description"]

    def test_preserves_custom_description(self):
        new = [{"input": "1", "expected": "1", "description": "커스텀"}]
        merged, _ = merge_test_cases([], new)
        assert merged[0]["description"] == "커스텀"


class TestSaveTestCases:
    """test_cases.json 저장."""

    def test_creates_file(self, tmp_path):
        cases = [{"id": 1, "input": "1 2", "expected": "3"}]
        path = save_test_cases(tmp_path, cases)
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data["testCases"]) == 1

    def test_creates_test_dir(self, tmp_path):
        save_test_cases(tmp_path, [])
        assert (tmp_path / "test").is_dir()


class TestParseAgentResponse:
    """에이전트 응답 파싱."""

    def test_parses_pure_json(self):
        stdout = json.dumps({
            "newTestCases": [{"input": "1", "expected": "1"}],
            "reasoning": "test",
        })
        result = parse_agent_response(stdout)
        assert len(result) == 1

    def test_parses_json_in_code_fence(self):
        stdout = 'Here:\n```json\n{"newTestCases": [{"input": "1", "expected": "1"}]}\n```'
        result = parse_agent_response(stdout)
        assert len(result) == 1

    def test_raises_on_empty(self):
        with pytest.raises(BojError, match="비어있습니다"):
            parse_agent_response("")

    def test_raises_on_no_json(self):
        with pytest.raises(BojError, match="JSON을 찾을 수 없습니다"):
            parse_agent_response("no json here")

    def test_raises_on_invalid_json(self):
        with pytest.raises(BojError, match="파싱 실패"):
            parse_agent_response("{invalid json}")

    def test_raises_on_empty_test_cases(self):
        with pytest.raises(BojError, match="생성하지 않았습니다"):
            parse_agent_response('{"newTestCases": []}')


class TestBuildAddTestPrompt:
    """프롬프트 구성."""

    def test_includes_mode(self, tmp_path):
        prompt = build_add_test_prompt(tmp_path, "edge", 3, [])
        assert "edge" in prompt

    def test_includes_count(self, tmp_path):
        prompt = build_add_test_prompt(tmp_path, "basic", 5, [])
        assert "5" in prompt

    def test_includes_existing_cases(self, tmp_path):
        existing = [{"id": 1, "input": "1 2", "expected": "3"}]
        prompt = build_add_test_prompt(tmp_path, "basic", 3, existing)
        assert "1 2" in prompt

    def test_includes_problem_json(self, tmp_path):
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        (artifacts / "problem.json").write_text('{"title": "테스트 문제"}')
        prompt = build_add_test_prompt(tmp_path, "basic", 3, [])
        assert "테스트 문제" in prompt

    def test_includes_solution(self, tmp_path):
        (tmp_path / "Solution.java").write_text("public class Solution {}")
        prompt = build_add_test_prompt(tmp_path, "basic", 3, [])
        assert "public class Solution" in prompt
