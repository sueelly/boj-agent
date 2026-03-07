#!/usr/bin/env python3
"""BOJ Problem Fetcher: BOJ HTML → problem.json

Usage:
    python3 boj_client.py --problem N --out DIR [--image-mode download|reference|skip]

Output:
    DIR/problem.json

Test isolation:
    BOJ_CLIENT_TEST_HTML=/path/to/file.html  → skip HTTP, parse local file
    BOJ_BASE_URL_OVERRIDE=http://localhost:PORT → use custom base URL (for local HTTP server tests)
    BOJ_LOGIN_URL_OVERRIDE=http://localhost:PORT/signin → use custom login URL (for local HTTP server tests)
    BOJ_CONFIG_DIR=/path/to/dir              → use custom config dir (overrides ~/.config/boj)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BOJ_BASE_URL = "https://www.acmicpc.net/problem"
BOJ_LOGIN_URL = "https://www.acmicpc.net/signin"
USER_AGENT = "Mozilla/5.0 (compatible; boj-agent/1.0)"


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

def _load_session() -> str:
    """Load BOJ session cookie value from config file."""
    config_dir = os.environ.get("BOJ_CONFIG_DIR", str(Path.home() / ".config" / "boj"))
    session_file = Path(config_dir) / "session"
    if session_file.exists():
        return session_file.read_text(encoding="utf-8").strip()
    return ""


def _fetch_html(problem_num: str) -> str:
    test_html = os.environ.get("BOJ_CLIENT_TEST_HTML", "")
    if test_html:
        return Path(test_html).read_text(encoding="utf-8")

    session_cookie = _load_session()
    base_url = os.environ.get("BOJ_BASE_URL_OVERRIDE", BOJ_BASE_URL)
    url = f"{base_url}/{problem_num}"
    cookies = {"OnlineJudge": session_cookie} if session_cookie else {}

    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, cookies=cookies, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Error: BOJ 페이지 가져오기 실패: {e}", file=sys.stderr)
        sys.exit(1)

    if resp.status_code == 403:
        print(
            "Error: BOJ 인증 실패 (403). 세션 쿠키를 설정하세요:\n"
            "  boj setup --session <OnlineJudge 쿠키 값>",
            file=sys.stderr,
        )
        sys.exit(1)
    if resp.status_code == 404:
        print(f"Error: 문제를 찾을 수 없습니다: {problem_num}", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    return resp.text


# ── public API ───────────────────────────────────────────────────────────────

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
            "input": inp.get_text(strip=True),
            "output": out.get_text(strip=True) if out else "",
        })
        n += 1

    return {
        "problem_num": problem_num,
        "title": _text("problem_title") or "",
        "time_limit": _text("problem_time_limit") or "",
        "memory_limit": _text("problem_memory_limit") or "",
        "description_html": _inner_html("problem_description"),
        "input_html": _inner_html("problem_input"),
        "output_html": _inner_html("problem_output"),
        "samples": samples,
        "images": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="BOJ Problem Fetcher")
    parser.add_argument("--problem", help="Problem number")
    parser.add_argument("--out", help="Output directory for problem.json")
    parser.add_argument(
        "--image-mode",
        choices=["download", "reference", "skip"],
        default="reference",
        help="Image handling mode (default: reference)",
    )
    # login mode
    parser.add_argument("--login", action="store_true", help="Log in to BOJ and obtain session cookie")
    parser.add_argument("--username", help="BOJ username (used with --login)")
    parser.add_argument("--password", help="BOJ password (used with --login)")
    parser.add_argument("--save", action="store_true", help="Save session cookie to config dir (used with --login)")
    args = parser.parse_args()

    if args.login:
        if not args.username or not args.password:
            print("Error: --login requires --username and --password", file=sys.stderr)
            sys.exit(1)
        try:
            session = boj_login(args.username, args.password)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: BOJ 로그인 실패: {e}", file=sys.stderr)
            sys.exit(1)
        if args.save:
            config_dir = os.environ.get("BOJ_CONFIG_DIR", str(Path.home() / ".config" / "boj"))
            Path(config_dir).mkdir(parents=True, exist_ok=True)
            Path(config_dir, "session").write_text(session, encoding="utf-8")
            print(f"✓ session 저장됨 ({config_dir}/session)", file=sys.stderr)
        else:
            print(session)
        return

    if not args.problem or not args.out:
        parser.error("--problem and --out are required (or use --login mode)")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        html = _fetch_html(args.problem)
    except Exception as e:
        print(f"Error: BOJ 페이지 가져오기 실패: {e}", file=sys.stderr)
        sys.exit(1)

    problem = parse_problem(html, args.problem)

    if not problem["title"]:
        print(f"Error: 문제 제목을 찾을 수 없습니다. 문제번호를 확인하세요: {args.problem}", file=sys.stderr)
        sys.exit(1)

    out_file = out_dir / "problem.json"
    out_file.write_text(json.dumps(problem, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"problem.json → {out_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
