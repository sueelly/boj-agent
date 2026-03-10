#!/usr/bin/env python3
"""BOJ Statement Normalizer: problem.json → README.md

Usage:
    python3 boj_normalizer.py --input problem.json --out README.md

Pure function: same problem.json always produces the same README.md.
Format follows prompts/make-environment.md spec.
"""

import argparse
import json
import sys
from pathlib import Path


def normalize(problem: dict) -> str:
    """Convert problem dict to README.md content string (deterministic)."""
    num = problem["problem_num"]
    title = problem["title"]
    time_limit = problem["time_limit"]
    memory_limit = problem["memory_limit"]
    description_html = problem.get("description_html", "")
    input_html = problem.get("input_html", "")
    output_html = problem.get("output_html", "")
    samples = problem.get("samples", [])

    parts: list[str] = []
    parts.append(f'<h2><a href="https://www.acmicpc.net/problem/{num}">{num}번: {title}</a></h2>')
    parts.append(f'<p><strong>시간 제한:</strong> {time_limit} | <strong>메모리 제한:</strong> {memory_limit}</p>')
    parts.append("<hr>")
    parts.append("")
    parts.append("<h3>문제</h3>")
    parts.append(description_html)
    parts.append("")
    parts.append("<h3>입력</h3>")
    parts.append(input_html)
    parts.append("")
    parts.append("<h3>출력</h3>")
    parts.append(output_html)
    parts.append("")
    for sample in samples:
        parts.append(f'<h3>예제 입력 {sample["id"]}</h3>')
        parts.append(f'<pre>{sample["input"]}</pre>')
        parts.append("")
        parts.append(f'<h3>예제 출력 {sample["id"]}</h3>')
        parts.append(f'<pre>{sample["output"]}</pre>')
        parts.append("")

    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="BOJ Statement Normalizer")
    parser.add_argument("--input", required=True, help="Path to problem.json")
    parser.add_argument("--out", required=True, help="Path for output README.md")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: 파일을 찾을 수 없습니다: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        problem = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: problem.json 파싱 실패: {e}", file=sys.stderr)
        sys.exit(1)

    content = normalize(problem)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"README.md → {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
