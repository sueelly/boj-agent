"""E2E: scripts/install.py → PATH의 `boj` → make/run.

격리 HOME에서 install 후 셸 이름 `boj`로 make/run까지 검증한다.
tests/e2e/ — run_tests.py 가 수집하는 경로 (legacy bash 폴더 아님).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# tests/e2e/ → repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_99999 = REPO_ROOT / "tests" / "fixtures" / "99999"
REQUIREMENTS = REPO_ROOT / "requirements.txt"


def _env_for_e2e(home: Path, base: dict | None = None) -> dict[str, str]:
    env = dict(base or os.environ)
    env["HOME"] = str(home)
    env.pop("BOJ_ROOT", None)
    env["BOJ_CONFIG_DIR"] = str(home / ".config" / "boj")
    env["BOJ_AGENT_CMD"] = "echo MOCK_AGENT"
    env["BOJ_EDITOR"] = "true"
    return env


@pytest.mark.slow
def test_install_then_boj_on_path_make_and_run(tmp_path: Path) -> None:
    """install.py --skip-setup → ~/bin/boj → boj make 99999 → boj run → 2/2."""
    home = tmp_path
    workspace = home / "workspace"
    workspace.mkdir(parents=True)
    env = _env_for_e2e(home)

    # [1] 설치
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "install.py"), "--force", "--skip-setup"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"install.py failed:\n{r.stderr}\n{r.stdout}"

    bin_dir = home / "bin"
    assert (bin_dir / "boj").is_file(), "~/bin/boj not installed"

    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    boj_exe = shutil.which("boj", path=env["PATH"])
    assert boj_exe and Path(boj_exe).resolve() == (bin_dir / "boj").resolve(), (
        f"command boj not on PATH: PATH head={env['PATH'][:120]}"
    )

    # [2] Python deps for make (bs4 등)
    py_target = home / "py"
    pip = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "-r",
            str(REQUIREMENTS),
            "--target",
            str(py_target),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if pip.returncode != 0:
        pytest.skip(f"pip install --target failed (network?): {pip.stderr[:500]}")

    py_sep = os.pathsep
    env["PYTHONPATH"] = py_sep.join(
        [str(py_target), env["PYTHONPATH"]] if env.get("PYTHONPATH") else [str(py_target)]
    )

    agent_root = home / ".local" / "share" / "boj-agent"
    cfg = home / ".config" / "boj"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "setup_done").write_text("")
    (cfg / "prog_lang").write_text("java\n")
    (cfg / "solution_root").write_text(f"{workspace}\n")
    (cfg / "agent_cmd").write_text(f"{env['BOJ_AGENT_CMD']}\n")
    (cfg / "editor").write_text("true\n")
    (cfg / "username").write_text("e2e\n")

    env["BOJ_ROOT"] = str(agent_root)
    env["BOJ_CLIENT_TEST_HTML"] = str(FIXTURES_99999 / "raw.html")

    # [3] boj make
    make = subprocess.run(
        f'echo y | "{boj_exe}" make 99999 --no-open',
        shell=True,
        cwd=str(workspace),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    out_make = (make.stdout or "") + (make.stderr or "")

    prob_dir = None
    for base in (workspace, agent_root):
        if not base.is_dir():
            continue
        for p in base.iterdir():
            if p.is_dir() and p.name.startswith("99999"):
                prob_dir = p
                break
        if prob_dir:
            break

    assert prob_dir is not None, f"boj make did not create 99999* dir.\n{out_make[:4000]}"

    shutil.copy(FIXTURES_99999 / "Solution.java", prob_dir / "Solution.java")
    test_dst = prob_dir / "test"
    if test_dst.exists():
        shutil.rmtree(test_dst)
    shutil.copytree(FIXTURES_99999 / "test", test_dst)

    del env["BOJ_CLIENT_TEST_HTML"]

    # [4] boj run
    run = subprocess.run(
        [boj_exe, "run", "99999"],
        cwd=str(workspace),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    out_run = (run.stdout or "") + (run.stderr or "")
    assert "2/2" in out_run, f"expected 2/2 in run output:\n{out_run[:4000]}"
