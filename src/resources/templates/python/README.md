# Python 템플릿 (Python 3.10+)

- **test_runner.py**: 공통 러너. `test/test_cases.json`을 읽고 `test.parse.parse_and_solve(sol, input)` 호출.
- **계약**: `test/parse.py`에 `def parse_and_solve(sol, input: str) -> str` 구현. `solution.py`에는 `Solution` 클래스와 `solve(...)` 메서드.

문제 폴더: `solution.py`, `test/parse.py`, `test/test_cases.json`. 실행은 문제 폴더를 cwd로 `python templates/python/test_runner.py` (또는 boj run이 이 경로로 실행).
