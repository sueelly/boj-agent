"""boj make 핵심 로직 — 5단계 spec 기반 파이프라인.

Issue #54 — TDD Red 단계 스텁.
구현은 Green 단계에서 채운다.
"""

from pathlib import Path


def run_setup() -> None:
    """boj setup을 실행한다. ensure_setup에서 호출."""
    raise NotImplementedError


def run_agent(problem_dir: Path, agent_cmd: str, prompt_name: str) -> int:
    """에이전트를 실행한다. generate_spec/generate_skeleton에서 호출."""
    raise NotImplementedError


def ensure_setup() -> None:
    """사전 조건: setup_done 확인, 없으면 boj setup 실행."""
    raise NotImplementedError


def check_existing(problem_dir: Path, force: bool) -> None:
    """사전 조건: 기존 폴더 존재 시 -f 검증."""
    raise NotImplementedError


def fetch_problem(problem_id: str, image_mode: str = "download") -> Path:
    """Step 0: BOJ fetch → problem.json."""
    raise NotImplementedError


def generate_readme(problem_json_path: Path) -> Path:
    """Step 1: README.md 생성."""
    raise NotImplementedError


def generate_spec(problem_dir: Path, agent_cmd: str) -> dict:
    """Step 2: problem.spec.json 생성."""
    raise NotImplementedError


def generate_skeleton(problem_dir: Path, lang: str, agent_cmd: str) -> None:
    """Step 3: Solution + Parse 생성."""
    raise NotImplementedError


def cleanup_artifacts(problem_dir: Path, keep: bool) -> None:
    """Step 5: artifacts 정리."""
    raise NotImplementedError


def run_make(problem_id: str, **kwargs) -> None:
    """전체 파이프라인 오케스트레이션."""
    raise NotImplementedError
