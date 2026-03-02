#!/usr/bin/env python3
"""BOJ Problem Fetcher: BOJ HTML → problem.json

Usage:
    python3 boj_client.py --problem N --out DIR [--image-mode download|reference|skip]

Output:
    DIR/problem.json

Test isolation:
    BOJ_CLIENT_TEST_HTML=/path/to/file.html  → skip HTTP, parse local file
"""

import argparse
import json
import os
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib import request

BOJ_BASE_URL = "https://www.acmicpc.net/problem"
USER_AGENT = "Mozilla/5.0 (compatible; boj-agent/1.0)"

# HTML5 void elements — never have a closing tag
_VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})


class _BaseParser(HTMLParser):
    """Base parser that locates an element by id and fires hooks for its content."""

    def __init__(self, target_id: str, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.target_id = target_id
        self._in_target = False
        self._target_tag = ""
        self._depth = 0
        self.done = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if self.done:
            return
        attrs_dict = dict(attrs)
        if not self._in_target and attrs_dict.get("id") == self.target_id:
            self._in_target = True
            self._target_tag = tag
            self._depth = 0
            self._on_enter(tag, attrs)
            return
        if self._in_target:
            self._on_nested_start(tag, attrs)
            if tag not in _VOID_ELEMENTS:
                self._depth += 1

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        # XHTML self-closing (<br/>) — treat as void, no depth change
        if self._in_target:
            self._on_nested_start(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if not self._in_target or self.done:
            return
        if self._depth == 0 and tag == self._target_tag:
            self._in_target = False
            self.done = True
            return
        if tag in _VOID_ELEMENTS:
            # Malformed HTML: void closing tag (e.g. </br>). Never incremented depth → don't decrement.
            self._on_nested_end(tag)
            return
        self._depth -= 1
        self._on_nested_end(tag)

    def handle_data(self, data: str) -> None:
        if self._in_target:
            self._on_data(data)

    # ── override hooks ──────────────────────────────────────────────────────
    def _on_enter(self, tag: str, attrs: list) -> None:
        pass

    def _on_nested_start(self, tag: str, attrs: list) -> None:
        pass

    def _on_nested_end(self, tag: str) -> None:
        pass

    def _on_data(self, data: str) -> None:
        pass


class _TextParser(_BaseParser):
    """Extracts text content (decoded) from the first element with target_id."""

    def __init__(self, target_id: str) -> None:
        super().__init__(target_id, convert_charrefs=True)
        self._chunks: list[str] = []

    def _on_data(self, data: str) -> None:
        self._chunks.append(data)

    def text(self) -> str:
        return "".join(self._chunks).strip()


class _InnerHTMLParser(_BaseParser):
    """Extracts inner HTML (entity-preserving) from the first element with target_id."""

    def __init__(self, target_id: str) -> None:
        super().__init__(target_id, convert_charrefs=False)
        self._chunks: list[str] = []

    def _on_data(self, data: str) -> None:
        self._chunks.append(data)

    def _on_nested_start(self, tag: str, attrs: list) -> None:
        attr_str = ""
        for name, value in attrs:
            if value is None:
                attr_str += f" {name}"
            else:
                attr_str += f' {name}="{value}"'
        if tag in _VOID_ELEMENTS:
            self._chunks.append(f"<{tag}{attr_str}/>")
        else:
            self._chunks.append(f"<{tag}{attr_str}>")

    def _on_nested_end(self, tag: str) -> None:
        self._chunks.append(f"</{tag}>")

    def handle_entityref(self, name: str) -> None:  # type: ignore[override]
        if self._in_target:
            self._chunks.append(f"&{name};")

    def handle_charref(self, name: str) -> None:  # type: ignore[override]
        if self._in_target:
            self._chunks.append(f"&#{name};")

    def inner_html(self) -> str:
        return "".join(self._chunks).strip()


# ── extraction helpers ──────────────────────────────────────────────────────

def _extract_text(html: str, element_id: str) -> "str | None":
    """Returns text if element found, None if not found."""
    p = _TextParser(element_id)
    p.feed(html)
    return p.text() if p.done else None


def _extract_inner_html(html: str, element_id: str) -> str:
    """Returns inner HTML if element found, empty string if not found."""
    p = _InnerHTMLParser(element_id)
    p.feed(html)
    return p.inner_html() if p.done else ""


def _extract_samples(html: str) -> list:
    samples = []
    n = 1
    while True:
        inp = _extract_text(html, f"sample-input-{n}")
        if inp is None:
            break
        out = _extract_text(html, f"sample-output-{n}") or ""
        samples.append({"id": n, "input": inp, "output": out})
        n += 1
    return samples


# ── fetch ───────────────────────────────────────────────────────────────────

def _fetch_html(problem_num: str) -> str:
    test_html = os.environ.get("BOJ_CLIENT_TEST_HTML", "")
    if test_html:
        return Path(test_html).read_text(encoding="utf-8")
    url = f"{BOJ_BASE_URL}/{problem_num}"
    req = request.Request(url, headers={"User-Agent": USER_AGENT})
    with request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8")


# ── public API ───────────────────────────────────────────────────────────────

def parse_problem(html: str, problem_num: str) -> dict:
    """Parse BOJ HTML and return problem data dict."""
    return {
        "problem_num": problem_num,
        "title": _extract_text(html, "problem_title") or "",
        "time_limit": _extract_text(html, "problem_time_limit") or "",
        "memory_limit": _extract_text(html, "problem_memory_limit") or "",
        "description_html": _extract_inner_html(html, "problem_description"),
        "input_html": _extract_inner_html(html, "problem_input"),
        "output_html": _extract_inner_html(html, "problem_output"),
        "samples": _extract_samples(html),
        "images": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="BOJ Problem Fetcher")
    parser.add_argument("--problem", required=True, help="Problem number")
    parser.add_argument("--out", required=True, help="Output directory for problem.json")
    parser.add_argument(
        "--image-mode",
        choices=["download", "reference", "skip"],
        default="reference",
        help="Image handling mode (default: reference)",
    )
    args = parser.parse_args()

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
