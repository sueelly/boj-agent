"""버전 업데이트 체크 모듈.

Issue #93 — CLI 실행 시 새 버전이 있으면 안내.

하루 1회 PyPI JSON API를 확인하고, 새 버전 발견 시 stderr로 안내.
네트워크 실패/오프라인 시 조용히 무시.
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

from src.core.config import _config_dir as get_config_dir

_PYPI_URL = "https://pypi.org/pypi/boj-agent/json"
_CHECK_INTERVAL = 86400  # 24시간
_CACHE_FILE = "update_check.json"
_TIMEOUT = 3  # 초


def _get_current_version() -> str:
    """현재 설치된 패키지 버전을 반환한다."""
    try:
        from importlib.metadata import version
        return version("boj-agent")
    except Exception:
        return "0.0.0"


def _get_cache_path() -> Path:
    return Path(get_config_dir()) / _CACHE_FILE


def _read_cache() -> dict:
    cache_path = _get_cache_path()
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_cache(data: dict) -> None:
    try:
        cache_path = _get_cache_path()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass


def _parse_version(v: str) -> tuple[int, ...]:
    """버전 문자열을 비교 가능한 튜플로 변환한다."""
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def _fetch_latest_version() -> str | None:
    """PyPI에서 최신 버전을 조회한다. 실패 시 None."""
    try:
        req = urllib.request.Request(_PYPI_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("info", {}).get("version")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, KeyError):
        return None


def check_for_update() -> str | None:
    """새 버전이 있으면 안내 메시지를 반환한다. 없으면 None.

    하루 1회만 체크하며, 네트워크 실패 시 조용히 None 반환.
    """
    try:
        cache = _read_cache()
        last_check = cache.get("last_check", 0)

        if time.time() - last_check < _CHECK_INTERVAL:
            # 캐시된 결과 사용
            cached_latest = cache.get("latest_version")
            if cached_latest:
                current = _get_current_version()
                if _parse_version(cached_latest) > _parse_version(current):
                    return (
                        f"Update available: {current} → {cached_latest}. "
                        f"Run: pip install --upgrade boj-agent"
                    )
            return None

        latest = _fetch_latest_version()
        if latest is None:
            return None

        _write_cache({
            "last_check": time.time(),
            "latest_version": latest,
        })

        current = _get_current_version()
        if _parse_version(latest) > _parse_version(current):
            return (
                f"Update available: {current} → {latest}. "
                f"Run: pip install --upgrade boj-agent"
            )
    except Exception:
        pass

    return None
