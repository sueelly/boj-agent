"""pytest 전역 conftest — 커스텀 마커 및 옵션 등록.

마커:
    live: 실제 BOJ HTTP 연결이 필요한 테스트. 기본 실행, --skip-live로 스킵.
    agent: 실제 에이전트(Claude 등)가 필요한 테스트. --run-agent로 활성화.
"""

import pytest


def pytest_addoption(parser):
    """커스텀 CLI 옵션 등록."""
    parser.addoption(
        "--skip-live",
        action="store_true",
        default=False,
        help="실제 BOJ 서버에 연결하는 라이브 테스트 스킵",
    )
    parser.addoption(
        "--run-agent",
        action="store_true",
        default=False,
        help="실제 에이전트(Claude 등)를 사용하는 테스트 실행",
    )
    parser.addoption(
        "--agent",
        default="claude",
        help="에이전트 테스트에 사용할 에이전트 (기본: claude)",
    )


def pytest_configure(config):
    """커스텀 마커 등록."""
    config.addinivalue_line("markers", "live: 실제 BOJ HTTP 연결 필요 (--skip-live로 스킵)")
    config.addinivalue_line("markers", "agent: 실제 에이전트 필요 (--run-agent)")


def pytest_collection_modifyitems(config, items):
    """마커 기반 자동 스킵."""
    if config.getoption("--skip-live"):
        skip_live = pytest.mark.skip(reason="--skip-live 옵션으로 스킵됨")
        for item in items:
            if "live" in item.keywords:
                item.add_marker(skip_live)

    if not config.getoption("--run-agent"):
        skip_agent = pytest.mark.skip(reason="--run-agent 옵션이 필요합니다")
        for item in items:
            if "agent" in item.keywords:
                item.add_marker(skip_agent)
