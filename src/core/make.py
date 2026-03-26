"""boj make 핵심 로직 — 5단계 spec 기반 파이프라인.

Issue #54 — TDD Green 단계.
"""

import json
import re
import shlex
import shutil
import subprocess
from pathlib import Path

from src.core.client import fetch_html, parse_problem
from src.core.exceptions import ProblemExistsError, SpecError
from src.core.normalizer import normalize

# 정리 시 artifacts/ 내 유지할 이미지 확장자
_IMAGE_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp",
})

# 정리 시 problem_dir 루트에서 항상 유지할 항목
_KEEP_NAMES_BASE = frozenset({"README.md", "test", "artifacts"})

# title_slug 생성 제약
_MAX_SLUG_LENGTH = 30
_SLUG_PATTERN = re.compile(r"[^a-zA-Z0-9가-힣\-]")


def _validate_problem_id(problem_id: str) -> None:
    """problem_id가 양의 정수인지 검증한다.

    Raises:
        ValueError: 유효하지 않은 problem_id일 때.
    """
    if not problem_id or not problem_id.isdigit() or int(problem_id) <= 0:
        raise ValueError(f"유효하지 않은 문제 번호입니다: {problem_id!r}")


def _sanitize_title_slug(title: str) -> str:
    """제목을 안전한 디렉터리 이름으로 변환한다.

    - 공백 → 하이픈
    - 허용 문자: 영문, 숫자, 한글, 하이픈
    - 최대 30자
    """
    slug = title.replace(" ", "-")
    slug = _SLUG_PATTERN.sub("", slug)
    return slug[:_MAX_SLUG_LENGTH]


def _get_lang_meta(lang: str) -> dict[str, str]:
    """languages.json에서 언어 메타데이터를 가져온다.

    Returns:
        ext, supports_parse, solution_file 키를 가진 딕셔너리.
    """
    from src.core.resources import get_languages_json
    lang_file = get_languages_json()
    data = json.loads(lang_file.read_text(encoding="utf-8"))
    lang_info = data["languages"].get(lang, {})

    ext = lang_info.get("extension", lang)
    skeleton = lang_info.get("skeleton", {})
    solution_file = skeleton.get("solution", f"Solution.{ext}")
    supports_parse = skeleton.get("parse") is not None

    return {
        "ext": ext,
        "supports_parse": "true" if supports_parse else "false",
        "solution_file": solution_file,
    }


def run_agent(
    problem_dir: Path,
    agent_cmd: str,
    prompt_name: str,
    context_files: dict[str, Path] | None = None,
    template_vars: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """에이전트를 subprocess로 실행한다.

    프롬프트 파일의 내용을 읽어 problem_dir 컨텍스트와 함께
    stdin으로 에이전트에 전달한다. context_files로 지정된 파일들은
    자동으로 읽어 프롬프트에 포함된다.

    Args:
        problem_dir: 문제 폴더 경로.
        agent_cmd: 에이전트 실행 명령어 (예: "claude -p --").
        prompt_name: 프롬프트 이름 (예: "make-spec", "make-skeleton").
        context_files: 프롬프트에 포함할 파일 딕셔너리.
            키는 표시 이름, 값은 파일 경로.
            예: {"problem.json": problem_dir / "artifacts" / "problem.json"}
        template_vars: 프롬프트 내 ``{{KEY}}`` 플레이스홀더를 치환할 딕셔너리.
            예: {"LANG": "java", "EXT": "java"}

    Returns:
        CompletedProcess 결과 (returncode, stdout, stderr 포함).
    """
    from src.core.resources import get_prompt_file
    prompt_file = get_prompt_file(prompt_name)
    prompt_content = prompt_file.read_text(encoding="utf-8")

    # 템플릿 변수 치환
    if template_vars:
        for key, value in template_vars.items():
            prompt_content = prompt_content.replace(f"{{{{{key}}}}}", value)

    full_prompt = (
        f"{prompt_content}\n\n"
        f"---\n\n"
        f"## 작업 대상\n\n"
        f"문제 디렉터리: {problem_dir}\n"
    )

    # context_files 내용을 프롬프트에 포함
    if context_files:
        for name, path in context_files.items():
            if path.exists():
                data = path.read_text(encoding="utf-8")
                full_prompt += (
                    f"\n### {name}\n\n"
                    f"```json\n{data}\n```\n"
                )

    cmd = shlex.split(agent_cmd)
    return subprocess.run(
        cmd, input=full_prompt, cwd=str(problem_dir),
        capture_output=True, text=True,
    )


def check_existing(problem_dir: Path, force: bool) -> None:
    """사전 조건: 기존 폴더 존재 시 -f 검증.

    Args:
        problem_dir: 문제 폴더 경로.
        force: True면 기존 폴더 덮어쓰기 허용.

    Raises:
        ProblemExistsError: 폴더가 존재하고 force=False일 때.
    """
    if problem_dir.exists() and not force:
        raise ProblemExistsError(
            f"{problem_dir.name} 폴더가 이미 존재합니다. "
            f"덮어쓰려면 -f 옵션을 사용하세요."
        )


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
        ValueError: 유효하지 않은 problem_id.
        FetchError: HTML fetch 실패 시.
        ProblemExistsError: 폴더 존재 + force=False일 때.
    """
    _validate_problem_id(problem_id)

    html = fetch_html(problem_id)
    problem = parse_problem(html, problem_id)

    # problem_dir 결정 (미지정 시 제목 기반 자동 생성)
    if problem_dir is None:
        title_slug = _sanitize_title_slug(problem["title"])
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


def generate_readme(problem_json_path: Path, problem_dir: Path | None = None) -> Path:
    """Step 1: problem.json → README.md 생성.

    Args:
        problem_json_path: problem.json 파일 경로.
        problem_dir: README.md를 생성할 디렉터리. None이면 problem_json_path의
                     상위 디렉터리(artifacts/)의 부모를 사용한다.

    Returns:
        생성된 README.md 경로.

    Raises:
        FileNotFoundError: problem.json 파일이 없을 때.
    """
    if not problem_json_path.exists():
        raise FileNotFoundError(f"problem.json을 찾을 수 없습니다: {problem_json_path}")

    problem = json.loads(problem_json_path.read_text(encoding="utf-8"))
    content = normalize(problem)

    # README.md는 problem_dir 루트에 생성
    if problem_dir is None:
        problem_dir = problem_json_path.parent.parent
    readme_path = problem_dir / "README.md"
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
        SpecError: spec 파일 미생성 또는 유효하지 않은 JSON일 때.
    """
    result = run_agent(problem_dir, agent_cmd, "make-spec", context_files={
        "problem.json": problem_dir / "artifacts" / "problem.json",
    })

    spec_path = problem_dir / "artifacts" / "problem.spec.json"

    # 에이전트가 파일을 직접 생성하지 않은 경우,
    # stdout에 JSON이 출력되었을 수 있다 (claude -p 모드).
    # 마크다운 분석 텍스트 + JSON 혼합 출력도 처리한다.
    if not spec_path.exists() and result.stdout and result.stdout.strip():
        extracted = _extract_json_manifest(result.stdout.strip())
        if extracted is not None:
            spec_path.parent.mkdir(parents=True, exist_ok=True)
            spec_path.write_text(
                json.dumps(extracted, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    if not spec_path.exists():
        lines = []
        if result.returncode != 0:
            lines.append(f"에이전트 exit code: {result.returncode}")
        if result.stderr and result.stderr.strip():
            lines.append(f"stderr: {result.stderr.strip()}")
        if result.stdout and result.stdout.strip():
            lines.append(f"stdout: {result.stdout.strip()}")
        detail = "\n" + "\n".join(lines) if lines else ""
        raise SpecError(
            "problem.spec.json이 생성되지 않았습니다. "
            f"boj make <문제번호> -f 로 재시도하세요.{detail}"
        )

    try:
        spec = json.loads(spec_path.read_text())
    except (json.JSONDecodeError, ValueError) as e:
        raise SpecError(
            "problem.spec.json이 유효하지 않은 JSON입니다. "
            "boj make <문제번호> -f 로 재시도하세요."
        ) from e

    return spec


def generate_skeleton(problem_dir: Path, lang: str, agent_cmd: str) -> None:
    """Step 3: Solution + Parse 생성.

    에이전트에 make-skeleton 프롬프트를 전달해 Solution/Parse 및 test_cases.json 생성.
    에이전트는 stdout으로 JSON manifest를 출력하고, Python이 파일을 생성한다.
    """
    import sys

    lang_meta = _get_lang_meta(lang)

    # problem.json 내용을 템플릿 변수로 직접 삽입
    problem_json_path = problem_dir / "artifacts" / "problem.json"
    problem_json_content = ""
    if problem_json_path.exists():
        problem_json_content = problem_json_path.read_text(encoding="utf-8")

    template_vars = {
        "LANG": lang,
        "EXT": lang_meta["ext"],
        "SUPPORTS_PARSE": lang_meta["supports_parse"],
        "PROBLEM_DIR": str(problem_dir),
        "PROBLEM_JSON": problem_json_content,
    }

    result = run_agent(
        problem_dir, agent_cmd, "make-skeleton",
        context_files={
            "problem.spec.json": problem_dir / "artifacts" / "problem.spec.json",
        },
        template_vars=template_vars,
    )

    # stdout에서 JSON manifest 추출 → 파일 생성
    files_written = _write_skeleton_files(problem_dir, result)

    # fallback: test_cases.json을 problem.json samples에서 결정론적으로 생성
    test_cases_path = problem_dir / "test" / "test_cases.json"
    if not test_cases_path.exists():
        _generate_test_cases_fallback(problem_dir)

    # 필수 파일 검증
    solution_file = lang_meta["solution_file"]
    if not (problem_dir / solution_file).exists():
        detail = ""
        if result.returncode != 0:
            detail = f" (exit {result.returncode})"
        elif result.stderr and result.stderr.strip():
            detail = f" ({result.stderr.strip()[:200]})"
        elif not files_written and result.stdout and result.stdout.strip():
            detail = f" (stdout: {result.stdout.strip()[:200]})"
        print(
            f"Warning: {solution_file}이 생성되지 않았습니다.{detail}",
            file=sys.stderr,
        )


def _extract_json_manifest(stdout: str) -> dict | None:
    """stdout에서 JSON manifest(``{"files": {...}}``)를 추출한다."""
    # 1차: 전체 stdout이 유효한 JSON
    try:
        data = json.loads(stdout)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, ValueError):
        pass

    # 2차: 마크다운 코드 펜스 안의 JSON
    fence_match = re.search(r"```(?:json)?\s*\n({.*?})\s*\n```", stdout, re.DOTALL)
    if fence_match:
        try:
            data = json.loads(fence_match.group(1))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, ValueError):
            pass

    # 3차: 첫 번째 { ~ 마지막 } 범위
    start = stdout.find("{")
    end = stdout.rfind("}")
    if start != -1 and end > start:
        try:
            data = json.loads(stdout[start : end + 1])
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, ValueError):
            pass

    return None


def _write_skeleton_files(
    problem_dir: Path,
    result: subprocess.CompletedProcess,
) -> bool:
    """에이전트 stdout JSON manifest를 파싱하여 파일들을 생성한다.

    Returns:
        True면 하나 이상의 파일이 생성됨.
    """
    if not (result.stdout and result.stdout.strip()):
        return False

    manifest = _extract_json_manifest(result.stdout.strip())
    if not manifest or "files" not in manifest:
        return False

    written = False
    for rel_path, content in manifest["files"].items():
        file_path = problem_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(str(content), encoding="utf-8")
        written = True

    return written


def _generate_test_cases_fallback(problem_dir: Path) -> None:
    """problem.json의 samples에서 test_cases.json을 결정론적으로 생성한다."""
    problem_json_path = problem_dir / "artifacts" / "problem.json"
    if not problem_json_path.exists():
        return

    problem = json.loads(problem_json_path.read_text(encoding="utf-8"))
    samples = problem.get("samples", [])
    if not samples:
        return

    test_cases = {
        "testCases": [
            {"input": s["input"], "expected": s["output"]}
            for s in samples
        ],
    }

    test_dir = problem_dir / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "test_cases.json").write_text(
        json.dumps(test_cases, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def open_editor(problem_dir: Path, editor_cmd: str | None) -> None:
    """Step 2: 설정된 에디터로 문제 폴더를 연다 (non-blocking).

    Popen으로 실행하여 spec/skeleton 생성이 에디터와 병렬로 진행된다.
    terminal editor(vim/nano)는 터미널을 공유하므로 파이프라인 출력과 겹칠 수 있다.
    editor_cmd가 비어 있으면 스킵.
    """
    if not (editor_cmd or "").strip():
        return
    cmd = [*shlex.split(editor_cmd.strip()), str(problem_dir)]
    subprocess.Popen(cmd, cwd=str(problem_dir))


def cleanup_artifacts(problem_dir: Path, keep: bool, lang: str = "java") -> None:
    """Step 5: 화이트리스트 기반 정리.

    keep=True면 모든 파일 유지.
    keep=False면 화이트리스트(README.md, Solution, test/, artifacts 이미지)만
    남기고 나머지를 삭제한다.

    Args:
        problem_dir: 문제 폴더 경로.
        keep: True면 모든 파일 유지 (--keep-artifacts).
        lang: 프로그래밍 언어 (Solution 파일명 결정에 사용).
    """
    if keep:
        return

    if not problem_dir.is_dir():
        return

    # 언어별 Solution 파일명 결정
    lang_meta = _get_lang_meta(lang)
    solution_file = lang_meta["solution_file"]

    keep_names = _KEEP_NAMES_BASE | {solution_file}

    # 화이트리스트에 없는 항목 삭제
    for item in problem_dir.iterdir():
        if item.name in keep_names:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # artifacts/ 내부: 이미지만 유지, 나머지 삭제
    artifacts = problem_dir / "artifacts"
    if not artifacts.is_dir():
        return

    for item in artifacts.iterdir():
        if item.is_file() and item.suffix.lower() in _IMAGE_EXTENSIONS:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # 빈 artifacts/ 삭제
    if artifacts.is_dir() and not any(artifacts.iterdir()):
        artifacts.rmdir()


def run_make(problem_id: str, **kwargs) -> None:
    """전체 파이프라인 오케스트레이션."""
    raise NotImplementedError
