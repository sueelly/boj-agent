"""AI 기반 테스트 케이스 자동 생성 모듈.

Issue #88 — boj add-test 명령어.
problem.json과 Solution을 분석하여 추가 테스트 케이스를 생성한다.
"""

import json
from pathlib import Path

from src.core.exceptions import BojError


def load_existing_test_cases(problem_dir: Path) -> list[dict]:
    """기존 test_cases.json을 읽는다.

    Returns:
        테스트 케이스 리스트. 파일이 없으면 빈 리스트.
    """
    tc_path = problem_dir / "test" / "test_cases.json"
    if not tc_path.exists():
        return []
    data = json.loads(tc_path.read_text(encoding="utf-8"))
    return data.get("testCases", [])


def next_test_id(existing: list[dict]) -> int:
    """기존 테스트 케이스의 마지막 id + 1을 반환한다."""
    if not existing:
        return 1
    max_id = max(tc.get("id", 0) for tc in existing)
    return max_id + 1


def is_duplicate(new_case: dict, existing: list[dict]) -> bool:
    """새 테스트 케이스가 기존 케이스와 중복되는지 확인한다.

    input이 동일하면 중복으로 간주.
    """
    new_input = new_case.get("input", "").strip()
    for tc in existing:
        if tc.get("input", "").strip() == new_input:
            return True
    return False


def merge_test_cases(
    existing: list[dict],
    new_cases: list[dict],
    mode: str = "basic",
) -> tuple[list[dict], int]:
    """새 테스트 케이스를 기존 목록에 병합한다.

    Args:
        existing: 기존 테스트 케이스 리스트.
        new_cases: 새로 생성된 테스트 케이스 리스트.
        mode: 생성 모드 (basic/edge/extreme).

    Returns:
        (병합된 리스트, 추가된 개수) 튜플.
    """
    start_id = next_test_id(existing)
    added = 0
    merged = list(existing)

    for case in new_cases:
        if is_duplicate(case, merged):
            continue

        merged.append({
            "id": start_id + added,
            "input": case.get("input", ""),
            "expected": case.get("expected", ""),
            "description": case.get("description", f"{mode} 자동 생성"),
        })
        added += 1

    return merged, added


def save_test_cases(problem_dir: Path, test_cases: list[dict]) -> Path:
    """test_cases.json을 저장한다.

    Returns:
        저장된 파일 경로.
    """
    tc_dir = problem_dir / "test"
    tc_dir.mkdir(exist_ok=True)
    tc_path = tc_dir / "test_cases.json"
    data = {"testCases": test_cases}
    tc_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return tc_path


def parse_agent_response(stdout: str) -> list[dict]:
    """에이전트 stdout에서 새 테스트 케이스를 추출한다.

    에이전트는 {"newTestCases": [...]} 형태의 JSON을 출력한다.

    Returns:
        새 테스트 케이스 리스트.

    Raises:
        BojError: JSON 파싱 실패 시.
    """
    text = stdout.strip()
    if not text:
        raise BojError("에이전트 출력이 비어있습니다.")

    # JSON 블록 추출 (```json ... ``` 또는 순수 JSON)
    if "```json" in text:
        start = text.index("```json") + len("```json")
        end = text.index("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.index("```") + len("```")
        end = text.index("```", start)
        text = text[start:end].strip()

    # 첫 번째 { 부터 마지막 } 까지 추출
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace == -1 or last_brace == -1:
        raise BojError("에이전트 출력에서 JSON을 찾을 수 없습니다.")

    json_str = text[first_brace:last_brace + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise BojError(f"에이전트 출력 JSON 파싱 실패: {e}")

    cases = data.get("newTestCases", [])
    if not cases:
        raise BojError("에이전트가 테스트 케이스를 생성하지 않았습니다.")

    return cases


def build_add_test_prompt(
    problem_dir: Path,
    mode: str,
    count: int,
    existing: list[dict],
) -> str:
    """add-test 프롬프트를 구성한다.

    Args:
        problem_dir: 문제 폴더 경로.
        mode: 생성 모드 (basic/edge/extreme).
        count: 생성할 테스트 케이스 수.
        existing: 기존 테스트 케이스.

    Returns:
        완성된 프롬프트 문자열.
    """
    # problem.json 읽기
    problem_json = problem_dir / "artifacts" / "problem.json"
    if not problem_json.exists():
        # artifacts 없으면 상위에서 찾기
        problem_json = problem_dir / "problem.json"
    problem_data = ""
    if problem_json.exists():
        problem_data = problem_json.read_text(encoding="utf-8")

    # Solution 파일 읽기
    solution_content = ""
    for name in ("Solution.java", "solution.py", "Solution.cpp", "Solution.c"):
        sol = problem_dir / name
        if sol.exists():
            solution_content = sol.read_text(encoding="utf-8")
            break

    mode_desc = {
        "basic": "기본적인 테스트 케이스 (해피패스, 간단한 변형)",
        "edge": "경계값, 빈 입력, 최소/최대값, 특수 케이스",
        "extreme": "최악의 시나리오 — 최대 입력 크기, TLE/MLE 유발 가능한 극단적 케이스",
    }

    existing_json = json.dumps(existing, ensure_ascii=False, indent=2) if existing else "[]"

    prompt = f"""# 테스트 케이스 자동 생성

## 모드: {mode} — {mode_desc.get(mode, mode)}
## 생성 개수: {count}개

## 문제 정보
```json
{problem_data}
```

## 현재 Solution
```
{solution_content}
```

## 기존 테스트 케이스 (중복 금지)
```json
{existing_json}
```

## 추론 단계 (Chain-of-Thought)

1. **문제 분석**: 입력 형식, 제약 조건, 알고리즘 유형을 파악하세요.
2. **기존 테스트 분석**: 이미 커버된 시나리오를 확인하세요.
3. **누락 시나리오 도출**: {mode} 모드에 맞는 테스트 케이스 후보를 추론하세요.
4. **케이스 생성**: input/expected 쌍을 {count}개 생성하세요.
5. **검증**: 기존 케이스와 중복이 없는지 확인하세요.

## 출력 형식 (반드시 이 JSON 형식으로만 출력)

```json
{{
  "newTestCases": [
    {{"input": "...", "expected": "..."}},
    ...
  ],
  "reasoning": "생성 근거 설명..."
}}
```

중요: JSON 외의 텍스트를 출력하지 마세요.
"""
    return prompt
