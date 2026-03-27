"""업데이트 체크 단위 테스트 (src/core/update_checker.py).

Issue #93 — CLI 실행 시 새 버전 업데이트 안내.
"""

import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.core.update_checker import (
    check_for_update,
    _parse_version,
    _fetch_latest_version,
)


class TestParseVersion:
    """버전 문자열 파싱."""

    def test_standard_version(self):
        assert _parse_version("1.0.1") == (1, 0, 1)

    def test_two_part_version(self):
        assert _parse_version("2.0") == (2, 0)

    def test_invalid_version_returns_zeros(self):
        assert _parse_version("abc") == (0, 0, 0)

    def test_none_returns_zeros(self):
        assert _parse_version(None) == (0, 0, 0)


class TestCheckForUpdate:
    """check_for_update 통합 로직."""

    def test_returns_message_when_new_version(self, tmp_path, monkeypatch):
        """새 버전이 있으면 업데이트 안내 메시지를 반환한다."""
        monkeypatch.setenv("BOJ_CONFIG_DIR", str(tmp_path))

        with (
            patch("src.core.update_checker._get_current_version", return_value="1.0.0"),
            patch("src.core.update_checker._fetch_latest_version", return_value="2.0.0"),
        ):
            result = check_for_update()

        assert result is not None
        assert "1.0.0" in result
        assert "2.0.0" in result
        assert "pip install --upgrade" in result

    def test_returns_none_when_up_to_date(self, tmp_path, monkeypatch):
        """최신 버전이면 None을 반환한다."""
        monkeypatch.setenv("BOJ_CONFIG_DIR", str(tmp_path))

        with (
            patch("src.core.update_checker._get_current_version", return_value="1.0.1"),
            patch("src.core.update_checker._fetch_latest_version", return_value="1.0.1"),
        ):
            result = check_for_update()

        assert result is None

    def test_returns_none_when_network_fails(self, tmp_path, monkeypatch):
        """네트워크 실패 시 None을 반환한다."""
        monkeypatch.setenv("BOJ_CONFIG_DIR", str(tmp_path))

        with patch("src.core.update_checker._fetch_latest_version", return_value=None):
            result = check_for_update()

        assert result is None

    def test_uses_cache_within_interval(self, tmp_path, monkeypatch):
        """캐시가 유효하면 네트워크 호출 없이 캐시된 결과를 사용한다."""
        monkeypatch.setenv("BOJ_CONFIG_DIR", str(tmp_path))

        cache = {"last_check": time.time(), "latest_version": "9.9.9"}
        (tmp_path / "update_check.json").write_text(json.dumps(cache))

        with (
            patch("src.core.update_checker._get_current_version", return_value="1.0.0"),
            patch("src.core.update_checker._fetch_latest_version") as mock_fetch,
        ):
            result = check_for_update()

        mock_fetch.assert_not_called()
        assert result is not None
        assert "9.9.9" in result

    def test_fetches_when_cache_expired(self, tmp_path, monkeypatch):
        """캐시가 만료되면 PyPI에서 새로 조회한다."""
        monkeypatch.setenv("BOJ_CONFIG_DIR", str(tmp_path))

        cache = {"last_check": time.time() - 100000, "latest_version": "1.0.0"}
        (tmp_path / "update_check.json").write_text(json.dumps(cache))

        with (
            patch("src.core.update_checker._get_current_version", return_value="1.0.0"),
            patch("src.core.update_checker._fetch_latest_version", return_value="1.0.1"),
        ):
            result = check_for_update()

        assert result is not None
        assert "1.0.1" in result

    def test_never_raises(self, tmp_path, monkeypatch):
        """어떤 예외가 발생해도 None을 반환한다."""
        monkeypatch.setenv("BOJ_CONFIG_DIR", str(tmp_path))

        with patch("src.core.update_checker._fetch_latest_version", side_effect=RuntimeError("boom")):
            result = check_for_update()

        assert result is None
