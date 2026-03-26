"""패키지 리소스 접근 단위 테스트 (src/core/resources.py).

Issue #91 — PyPI 설치 시 prompts/templates 리소스 누락 수정.
edge-cases.md M20 커버리지.

TestResourceAccess: 기본 리소스 접근 (개발 환경 + 패키지 환경 공통).
TestResourceAccessIsolated: 프로젝트 루트 없이 importlib.resources만으로 접근 시뮬레이션.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.core.resources import (
    get_prompt_file,
    get_languages_json,
    get_template_lang_dir,
)


# ──────────────────────────────────────────────
# TestResourceAccess — M20 기본 리소스 접근
# ──────────────────────────────────────────────

class TestResourceAccess:
    """M20: 패키지 리소스 접근 — 개발/설치 환경 공통."""

    def test_get_prompt_file_returns_existing_path(self):
        """make-spec 프롬프트 파일이 존재하는 Path를 반환한다."""
        result = get_prompt_file("make-spec")
        assert isinstance(result, Path)
        assert result.exists()
        assert result.name == "make-spec.md"

    def test_get_prompt_file_returns_existing_for_all_prompts(self):
        """모든 프롬프트 파일이 존재하는 Path를 반환한다."""
        for name in ("make-spec", "make-skeleton", "make-parse-and-tests", "review"):
            result = get_prompt_file(name)
            assert result.exists(), f"prompt '{name}' not found at {result}"

    def test_get_prompt_file_raises_for_unknown(self):
        """존재하지 않는 프롬프트 이름은 FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="nonexistent"):
            get_prompt_file("nonexistent-prompt")

    def test_get_languages_json_returns_existing_path(self):
        """languages.json이 존재하는 Path를 반환한다."""
        result = get_languages_json()
        assert isinstance(result, Path)
        assert result.exists()
        assert result.name == "languages.json"

    def test_get_languages_json_is_valid_json(self):
        """languages.json은 유효한 JSON이다."""
        import json
        result = get_languages_json()
        data = json.loads(result.read_text(encoding="utf-8"))
        assert "java" in data["languages"]

    def test_get_template_lang_dir_returns_existing_path(self):
        """java 템플릿 디렉터리가 존재하는 Path를 반환한다."""
        result = get_template_lang_dir("java")
        assert isinstance(result, Path)
        assert result.exists()
        assert result.is_dir()

    def test_get_template_lang_dir_java_contains_test_java(self):
        """java 템플릿 디렉터리에 Test.java가 존재한다."""
        result = get_template_lang_dir("java")
        assert (result / "Test.java").exists()

    def test_get_template_lang_dir_raises_for_unknown(self):
        """존재하지 않는 언어 디렉터리는 FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="brainfuck"):
            get_template_lang_dir("brainfuck")


# ──────────────────────────────────────────────
# TestResourceAccessIsolated — M20 격리 테스트
# ──────────────────────────────────────────────

class TestResourceAccessIsolated:
    """M20: site-packages 설치 시뮬레이션 — importlib.resources만으로 접근."""

    def test_falls_back_to_importlib_when_dev_path_missing(self, tmp_path):
        """개발 경로가 없을 때 importlib.resources로 fallback한다."""
        # importlib.resources.files()가 tmp_path를 반환하도록 mock
        mock_prompts = tmp_path / "prompts"
        mock_prompts.mkdir()
        (mock_prompts / "make-spec.md").write_text("mock prompt")

        mock_resource_root = MagicMock()
        mock_resource_root.__truediv__ = lambda self, key: tmp_path / key

        with patch("src.core.resources._get_dev_root", return_value=None):
            with patch("src.core.resources._get_importlib_root", return_value=tmp_path):
                result = get_prompt_file("make-spec")

        assert result.exists()
        assert result.name == "make-spec.md"

    def test_raises_when_both_paths_missing(self):
        """개발 경로와 importlib 경로 모두 없으면 FileNotFoundError."""
        with patch("src.core.resources._get_dev_root", return_value=None):
            with patch("src.core.resources._get_importlib_root", return_value=None):
                with pytest.raises(FileNotFoundError):
                    get_prompt_file("make-spec")
