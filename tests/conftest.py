"""pytest 전역 conftest — 커스텀 마커, 옵션, 공통 픽스처 등록.

마커:
    live: 실제 BOJ HTTP 연결이 필요한 테스트. 기본 실행, --skip-live로 스킵.
    agent: 실제 에이전트(Claude 등)가 필요한 테스트. --run-agent로 활성화.

공통 픽스처:
    boj_env: 격리된 BOJ CLI 환경 (tmp_path + env dict).
    fixture_path: 테스트 픽스처 경로 헬퍼.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


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


# ---------------------------------------------------------------------------
# 공통 픽스처 (integration / e2e 공유)
# ---------------------------------------------------------------------------

@pytest.fixture
def boj_env(tmp_path):
    """격리된 BOJ 환경을 생성한다."""
    for d in ("src", "templates", "prompts"):
        src = REPO_ROOT / d
        if src.exists():
            shutil.copytree(src, tmp_path / d)

    # 실행 권한
    for sh in (tmp_path / "src").rglob("*.sh"):
        sh.chmod(0o755)
    (tmp_path / "src" / "boj").chmod(0o755)

    # git init
    subprocess.run(
        ["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=tmp_path, check=True, capture_output=True,
    )

    env = os.environ.copy()
    env.update({
        "BOJ_ROOT": str(tmp_path),
        "HOME": str(tmp_path),
        "BOJ_CONFIG_DIR": str(tmp_path / ".config" / "boj"),
        "BOJ_EDITOR": "true",
    })

    return tmp_path, env


@pytest.fixture
def fixture_path():
    """픽스처 경로 헬퍼."""
    def _get(problem_num: int | str) -> Path:
        p = FIXTURES_DIR / str(problem_num)
        assert p.exists(), f"Fixture not found: {p}"
        return p
    return _get


def run_boj(env, *args, input_text: str | None = None) -> subprocess.CompletedProcess:
    """격리 환경에서 boj CLI를 실행한다."""
    tmp_path = Path(env["BOJ_ROOT"])
    return subprocess.run(
        [str(tmp_path / "src" / "boj"), *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        input=input_text,
        timeout=60,
    )


def setup_problem_dir(tmp_path, fix, lang="java"):
    """픽스처에서 문제 폴더를 구성한다."""
    prob_dir = tmp_path / "99999-두수의합"
    prob_dir.mkdir(exist_ok=True)

    # README 복사
    if (fix / "readme.md").exists():
        shutil.copy(fix / "readme.md", prob_dir / "README.md")

    # 솔루션 복사
    if lang == "java" and (fix / "Solution.java").exists():
        shutil.copy(fix / "Solution.java", prob_dir)
    elif lang == "python" and (fix / "solution.py").exists():
        shutil.copy(fix / "solution.py", prob_dir)

    # 테스트 파일 복사
    if (fix / "test").exists():
        shutil.copytree(fix / "test", prob_dir / "test", dirs_exist_ok=True)

    return prob_dir
