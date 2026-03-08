"""Shared helpers for characterization tests."""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
BOJ_CMD = REPO_ROOT / "src" / "boj"


def run_boj(env, *args, input_text: str | None = None) -> subprocess.CompletedProcess:
    tmp_path = Path(env["BOJ_ROOT"])
    return subprocess.run(
        [str(tmp_path / "src" / "boj"), *args],
        cwd=tmp_path, env=env, capture_output=True, text=True,
        input=input_text, timeout=30,
    )
