"""boj make 핵심 로직 — 5단계 spec 기반 파이프라인.

Issue #54 — TDD Green 단계.
"""

import json
import subprocess
import sys
from pathlib import Path

from src.core.client import fetch_html, parse_problem
from src.core.config import is_setup_done
from src.core.normalizer import normalize

# 삭제 대상 아티팩트 파일 이름
_CLEANUP_TARGETS = ("problem.json", "problem.spec.json")


def run_setup() -> None:
    """boj setup을 실행한다. ensure_setup에서 호출.

    src.cli.boj_setup.main()을 직접 호출한다.
    """
    from src.cli.boj_setup import main as setup_main
    setup_main([])


def run_agent(problem_dir: Path, agent_cmd: str, prompt_name: str) -> int:
    """에이전트를 subprocess로 실행한다.

    Args:
        problem_dir: 문제 폴더 경로.
        agent_cmd: 에이전트 실행 명령어 (예: "claude", "gemini").
        prompt_name: 프롬프트 이름 (예: "make-spec", "make-skeleton").

    Returns:
        프로세스 종료 코드.
    """
    prompts_dir = Path(__file__).resolve().parent.parent.parent / "prompts"
    prompt_file = prompts_dir / f"{prompt_name}.md"

    cmd = f"{agent_cmd} {prompt_file} {problem_dir}"
    result = subprocess.run(
        cmd, shell=True, cwd=str(problem_dir),
        capture_output=True, text=True,
    )
    return result.returncode


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


def fetch_problem(
    problem_id: str,
    image_mode: str = "download",
    problem_dir: Path | None = None,
    base_dir: Path | None = None,
    force: bool = False,
) -> Path:
    """Step 0: BOJ fetch → problem.json.

    BOJ HTML을 가져와 파싱하고 problem.json을 artifacts/에 저장한다.

    Args:
        problem_id: BOJ 문제 번호 (예: "99999").
        image_mode: 이미지 처리 모드 ("download", "reference", "skip").
        problem_dir: 문제 폴더 경로. None이면 자동 생성.

    Returns:
        생성된 문제 폴더 경로.

    Raises:
        SystemExit: HTML fetch 또는 파싱 실패 시.
    """
    html = fetch_html(problem_id)
    problem = parse_problem(html, problem_id)

    # problem_dir 결정 (미지정 시 제목 기반 자동 생성)
    if problem_dir is None:
        title_slug = problem["title"].replace(" ", "-")
        root_dir = base_dir or Path.cwd()
        problem_dir = root_dir / f"{problem_id}-{title_slug}"

    # 기존 폴더 존재 여부를 먼저 검사하여 부분 수정 방지
    check_existing(problem_dir, force=force)

    # 디렉터리 생성
    artifacts_dir = problem_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # image_mode 처리
    if image_mode == "skip":
        from src.core.client import strip_images
        problem["description_html"] = strip_images(problem.get("description_html", ""))
    elif image_mode == "download" and problem.get("images"):
        from src.core.client import download_images, rewrite_image_urls
        image_results = download_images(problem["images"], artifacts_dir)
        problem["description_html"] = rewrite_image_urls(
            problem.get("description_html", ""), image_results,
        )

    # problem.json 저장
    problem_json_path = artifacts_dir / "problem.json"
    problem_json_path.write_text(
        json.dumps(problem, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return problem_dir


def generate_readme(problem_json_path: Path) -> Path:
    """Step 1: problem.json → README.md 생성.

    Args:
        problem_json_path: problem.json 파일 경로.

    Returns:
        생성된 README.md 경로.

    Raises:
        SystemExit: problem.json 파일이 없거나 파싱 실패 시.
        FileNotFoundError: problem.json 파일이 없을 때.
    """
    if not problem_json_path.exists():
        raise FileNotFoundError(f"problem.json을 찾을 수 없습니다: {problem_json_path}")

    problem = json.loads(problem_json_path.read_text(encoding="utf-8"))
    content = normalize(problem)

    # README.md는 problem_dir 루트에 생성 (artifacts/ 상위)
    readme_path = problem_json_path.parent.parent / "README.md"
    readme_path.write_text(content, encoding="utf-8")

    return readme_path


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
