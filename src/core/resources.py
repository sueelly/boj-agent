"""패키지 리소스 접근 모듈.

Issue #91 — PyPI 설치 시 prompts/templates 리소스 누락 수정.

importlib.resources (Python 3.10+) 기반으로 리소스 경로를 해석한다.
개발 환경(editable install, 소스 실행)에서는 프로젝트 루트 fallback을 사용한다.
"""

from importlib import resources as _importlib_resources
from pathlib import Path


def _get_importlib_root() -> Path | None:
    """importlib.resources로 src.resources 패키지 경로를 반환한다.

    패키지가 설치되지 않았거나 리소스가 없으면 None.
    """
    try:
        resource_root = _importlib_resources.files("src.resources")
        p = Path(str(resource_root))
        if p.is_dir():
            return p
    except (TypeError, ModuleNotFoundError):
        pass
    return None


def _get_dev_root() -> Path | None:
    """개발 환경에서 프로젝트 루트의 src/resources/ 경로를 반환한다.

    src/core/resources.py → parent(core) → parent(src) → src/resources/
    """
    candidate = Path(__file__).resolve().parent.parent / "resources"
    if candidate.is_dir() and (candidate / "prompts").is_dir():
        return candidate
    return None


def _get_resource_root() -> Path:
    """리소스 루트 디렉터리를 반환한다.

    우선순위: importlib.resources → 개발 환경 fallback.
    """
    root = _get_importlib_root()
    if root is not None:
        return root

    root = _get_dev_root()
    if root is not None:
        return root

    raise FileNotFoundError(
        "리소스 디렉터리를 찾을 수 없습니다. "
        "패키지가 올바르게 설치되었는지 확인하세요."
    )


def get_prompt_file(name: str) -> Path:
    """프롬프트 파일 경로를 반환한다.

    Args:
        name: 프롬프트 이름 (확장자 없이). 예: "make-spec"

    Returns:
        프롬프트 .md 파일의 Path.

    Raises:
        FileNotFoundError: 프롬프트 파일이 존재하지 않을 때.
    """
    root = _get_resource_root()
    prompt_file = root / "prompts" / f"{name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"프롬프트 파일을 찾을 수 없습니다: {name}.md"
        )
    return prompt_file


def get_languages_json() -> Path:
    """templates/languages.json 파일 경로를 반환한다.

    Raises:
        FileNotFoundError: languages.json이 존재하지 않을 때.
    """
    root = _get_resource_root()
    lang_file = root / "templates" / "languages.json"
    if not lang_file.exists():
        raise FileNotFoundError(
            "languages.json을 찾을 수 없습니다."
        )
    return lang_file


def get_template_lang_dir(lang: str) -> Path:
    """언어별 템플릿 디렉터리 경로를 반환한다.

    Args:
        lang: 언어 이름. 예: "java", "python"

    Returns:
        템플릿 디렉터리의 Path.

    Raises:
        FileNotFoundError: 해당 언어 디렉터리가 존재하지 않을 때.
    """
    root = _get_resource_root()
    lang_dir = root / "templates" / lang
    if not lang_dir.is_dir():
        raise FileNotFoundError(
            f"'{lang}' 템플릿 디렉터리를 찾을 수 없습니다."
        )
    return lang_dir
