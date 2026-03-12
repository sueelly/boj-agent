"""boj make 핵심 로직 — 5단계 spec 기반 파이프라인.

Issue #54 — TDD Green 단계.
"""

import json
import sys
from pathlib import Path

from src.core.config import is_setup_done

# 삭제 대상 아티팩트 파일 이름
_CLEANUP_TARGETS = ("problem.json", "problem.spec.json")


def run_setup() -> None:
    """boj setup을 실행한다. ensure_setup에서 호출."""
    raise NotImplementedError


def run_agent(problem_dir: Path, agent_cmd: str, prompt_name: str) -> int:
    """에이전트를 실행한다. generate_spec/generate_skeleton에서 호출."""
    raise NotImplementedError


def ensure_setup() -> None:
    """사전 조건: setup_done 확인, 없으면 boj setup 실행."""
    if not is_setup_done():
        run_setup()


def check_existing(problem_dir: Path, force: bool) -> None:
    """사전 조건: 기존 폴더 존재 시 -f 검증.

    Args:
        problem_dir: 문제 폴더 경로.
        force: True면 기존 폴더 덮어쓰기 허용.

    Raises:
        SystemExit: 폴더가 존재하고 force=False일 때.
    """
    if problem_dir.exists() and not force:
        print(
            f"Error: {problem_dir.name} 폴더가 이미 존재합니다. "
            f"덮어쓰려면 -f 옵션을 사용하세요.",
            file=sys.stderr,
        )
        sys.exit(1)


def fetch_problem(problem_id: str, image_mode: str = "download") -> Path:
    """Step 0: BOJ fetch → problem.json."""
    raise NotImplementedError


def generate_readme(problem_json_path: Path) -> Path:
    """Step 1: README.md 생성."""
    raise NotImplementedError


def generate_spec(problem_dir: Path, agent_cmd: str) -> dict:
    """Step 2: problem.spec.json 생성.

    에이전트를 실행하여 spec 파일을 생성하고 JSON 파싱 후 반환한다.

    Args:
        problem_dir: 문제 폴더 경로 (artifacts/ 하위에 spec 생성).
        agent_cmd: 에이전트 실행 명령어.

    Returns:
        파싱된 spec 딕셔너리.

    Raises:
        SystemExit: spec 파일 미생성 또는 유효하지 않은 JSON일 때.
    """
    run_agent(problem_dir, agent_cmd, "make-spec")

    spec_path = problem_dir / "artifacts" / "problem.spec.json"

    if not spec_path.exists():
        print(
            "Error: problem.spec.json이 생성되지 않았습니다. "
            "boj make <문제번호> -f 로 재시도하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        spec = json.loads(spec_path.read_text())
    except (json.JSONDecodeError, ValueError):
        print(
            "Error: problem.spec.json이 유효하지 않은 JSON입니다. "
            "boj make <문제번호> -f 로 재시도하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    return spec


def generate_skeleton(problem_dir: Path, lang: str, agent_cmd: str) -> None:
    """Step 3: Solution + Parse 생성."""
    raise NotImplementedError


def cleanup_artifacts(problem_dir: Path, keep: bool) -> None:
    """Step 5: artifacts 정리.

    keep=False일 때 problem.json, problem.spec.json만 삭제한다.
    이미지 파일 및 기타 JSON은 유지한다.

    Args:
        problem_dir: 문제 폴더 경로.
        keep: True면 모든 파일 유지 (--keep-artifacts).
    """
    if keep:
        return

    artifacts = problem_dir / "artifacts"
    if not artifacts.is_dir():
        return

    for name in _CLEANUP_TARGETS:
        target = artifacts / name
        if target.exists():
            target.unlink()


def run_make(problem_id: str, **kwargs) -> None:
    """전체 파이프라인 오케스트레이션."""
    raise NotImplementedError
