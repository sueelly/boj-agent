# tests/characterization/conftest.py

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure this package directory is importable
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from helpers import REPO_ROOT, FIXTURES_DIR  # noqa: F401, E402

BOJ_CMD = REPO_ROOT / "src" / "boj"


@pytest.fixture
def boj_env(tmp_path):
    """격리된 BOJ 환경을 생성한다."""
    for d in ("src", "templates", "prompts"):
        src = REPO_ROOT / d
        if src.exists():
            shutil.copytree(src, tmp_path / d)

    for sh in (tmp_path / "src").rglob("*.sh"):
        sh.chmod(0o755)
    (tmp_path / "src" / "boj").chmod(0o755)

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
