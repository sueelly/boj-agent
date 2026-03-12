"""BOJ Statement Normalizer: problem dict → README.md content.

boj_normalizer.py에서 순수 로직을 복사한 독립 모듈.
CLI main()은 포함하지 않는다 (core는 순수 로직만).

Pure function: same problem dict always produces the same README.md content.
Format: HTML-based README with problem statement, examples, and metadata.
"""


def normalize(problem: dict) -> str:
    """Convert problem dict to README.md content string (deterministic).

    Args:
        problem: parse_problem()에서 반환된 문제 딕셔너리.
            필수 키: problem_num, title, time_limit, memory_limit
            선택 키: description_html, input_html, output_html, samples

    Returns:
        HTML 포맷의 README.md 내용 문자열.
    """
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
