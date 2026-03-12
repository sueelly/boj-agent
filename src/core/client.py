"""BOJ HTML fetcher + parser.

boj_client.py에서 순수 로직을 복사한 독립 모듈.
CLI main()은 포함하지 않는다 (core는 순수 로직만).

이미지 처리 (COMMAND-SPEC Step 0, edge-cases M5/M6):
  download: description_html에서 <img> 추출 → artifacts/에 다운로드 → src를 로컬 경로로 치환
  reference: 원본 BOJ URL 유지
  skip: <img> 태그 제거
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BOJ_BASE_URL = "https://www.acmicpc.net/problem"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
_DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}
BOJ_LOGIN_URL = "https://www.acmicpc.net/signin"


# ── login ───────────────────────────────────────────────────────────────────


def boj_login(username: str, password: str) -> str:
    """Log in to BOJ and return the OnlineJudge session cookie value.

    Raises:
        ValueError: if login fails (wrong credentials or unexpected response).
    """
    login_url = os.environ.get("BOJ_LOGIN_URL_OVERRIDE", BOJ_LOGIN_URL)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    try:
        session.get(login_url, timeout=10)
    except requests.exceptions.RequestException:
        pass  # 로그인 페이지 GET 실패는 무시

    try:
        session.post(
            login_url,
            data={"login_user_id": username, "login_password": password, "auto_login": "on"},
            timeout=10,
            allow_redirects=True,
        )
    except requests.exceptions.RequestException as e:
        raise ValueError(f"로그인 요청 실패: {e}")

    cookie = session.cookies.get("OnlineJudge")
    if not cookie:
        raise ValueError("로그인 실패: 아이디/비밀번호를 확인하세요")
    return cookie


# ── fetch ───────────────────────────────────────────────────────────────────


def fetch_html(problem_num: str) -> str:
    """BOJ HTML을 가져온다.

    테스트 격리:
        BOJ_CLIENT_TEST_HTML 환경변수로 로컬 파일 경로를 지정하면 HTTP 요청 대신 파일을 읽는다.
        BOJ_BASE_URL_OVERRIDE로 커스텀 base URL을 지정할 수 있다.
    """
    test_html = os.environ.get("BOJ_CLIENT_TEST_HTML", "")
    if test_html:
        return Path(test_html).read_text(encoding="utf-8")

    base_url = os.environ.get("BOJ_BASE_URL_OVERRIDE", BOJ_BASE_URL)
    url = f"{base_url}/{problem_num}"

    try:
        resp = requests.get(url, headers=_DEFAULT_HEADERS, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Error: BOJ 페이지 가져오기 실패: {e}", file=sys.stderr)
        sys.exit(1)

    if resp.status_code == 403:
        print(f"Error: BOJ 접근 거부 (403): {url}", file=sys.stderr)
        sys.exit(1)
    if resp.status_code == 404:
        print(f"Error: 문제를 찾을 수 없습니다: {problem_num}", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    return resp.text


# ── parse ───────────────────────────────────────────────────────────────────


def parse_problem(html: str, problem_num: str) -> dict:
    """Parse BOJ HTML and return problem data dict."""
    soup = BeautifulSoup(html, "html.parser")

    def _text(element_id: str) -> "str | None":
        el = soup.find(id=element_id)
        return el.get_text(strip=True) if el else None

    def _inner_html(element_id: str) -> str:
        el = soup.find(id=element_id)
        return el.decode_contents().strip() if el else ""

    samples = []
    n = 1
    while True:
        inp = soup.find(id=f"sample-input-{n}")
        if inp is None:
            break
        out = soup.find(id=f"sample-output-{n}")
        samples.append({
            "id": n,
            "input": inp.get_text(separator="\n").strip(),
            "output": out.get_text(separator="\n").strip() if out else "",
        })
        n += 1

    description_html = _inner_html("problem_description")

    # 이미지 추출
    images = extract_images(description_html, problem_num)

    return {
        "problem_num": problem_num,
        "title": _text("problem_title") or "",
        "time_limit": _text("problem_time_limit") or "",
        "memory_limit": _text("problem_memory_limit") or "",
        "description_html": description_html,
        "input_html": _inner_html("problem_input"),
        "output_html": _inner_html("problem_output"),
        "samples": samples,
        "images": images,
    }


# ── image handling ──────────────────────────────────────────────────────────


def extract_images(html: str, problem_num: str) -> list[dict]:
    """HTML에서 <img> 태그의 src와 alt를 추출한다.

    Args:
        html: description_html 문자열.
        problem_num: 문제 번호 (상대 URL 해석용).

    Returns:
        [{"url": "https://...", "alt": "..."}, ...] 형태의 리스트.
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    images = []
    base_url = f"https://www.acmicpc.net/problem/{problem_num}"

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src:
            continue
        # 상대 URL → 절대 URL
        abs_url = urljoin(base_url, src)
        images.append({
            "url": abs_url,
            "alt": img.get("alt", ""),
        })

    return images


def download_images(
    images: list[dict],
    artifacts_dir: Path,
) -> list[dict]:
    """이미지를 다운로드하여 artifacts_dir에 저장한다.

    Args:
        images: extract_images()에서 반환된 이미지 목록.
        artifacts_dir: 이미지 저장 디렉터리.

    Returns:
        [{"url": "https://...", "local_path": "img_1.png", "alt": "..."}, ...]
        다운로드 실패 시 해당 항목의 local_path는 빈 문자열.
    """
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for i, img in enumerate(images, start=1):
        url = img["url"]
        # 확장자 추출 (기본 .png)
        ext = _guess_extension(url)
        local_name = f"img_{i}{ext}"
        local_path = artifacts_dir / local_name

        try:
            resp = requests.get(url, headers=_DEFAULT_HEADERS, timeout=15)
            resp.raise_for_status()
            local_path.write_bytes(resp.content)
            results.append({
                "url": url,
                "local_path": local_name,
                "alt": img.get("alt", ""),
            })
        except (requests.exceptions.RequestException, OSError) as e:
            print(
                f"Warning: 이미지 다운로드 실패 ({url}). reference 모드로 대체.",
                file=sys.stderr,
            )
            results.append({
                "url": url,
                "local_path": "",
                "alt": img.get("alt", ""),
            })

    return results


def rewrite_image_urls(html: str, image_results: list[dict], artifacts_rel: str = "artifacts") -> str:
    """description_html의 <img src>를 로컬 경로로 치환한다.

    다운로드 성공한 이미지만 치환하고, 실패한 이미지는 원본 URL을 유지한다.

    Args:
        html: description_html 문자열.
        image_results: download_images()에서 반환된 결과.
        artifacts_rel: artifacts 상대 경로 (README.md 기준).

    Returns:
        치환된 HTML 문자열.
    """
    result = html
    for img_info in image_results:
        if not img_info["local_path"]:
            continue  # 다운로드 실패 → 원본 유지
        old_url = img_info["url"]
        new_path = f"{artifacts_rel}/{img_info['local_path']}"
        result = result.replace(old_url, new_path)
    return result


def strip_images(html: str) -> str:
    """HTML에서 <img> 태그를 모두 제거한다 (image_mode=skip)."""
    if not html:
        return html
    return re.sub(r"<img\s[^>]*>", "", html)


def _guess_extension(url: str) -> str:
    """URL에서 이미지 확장자를 추측한다."""
    lower = url.lower().split("?")[0]
    for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"):
        if lower.endswith(ext):
            return ext
    return ".png"  # 기본값
