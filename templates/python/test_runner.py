#!/usr/bin/env python3
"""
공통 테스트 러너 (Python 3.10+).
문제 폴더에서 실행: cwd가 문제 폴더일 때 test/test_cases.json을 읽고,
test.parse.parse_and_solve(sol, input) 호출 후 기대값과 비교.

계약: test/parse.py에 parse_and_solve(sol, input: str) -> str 함수가 있어야 함.
solution 모듈에는 solve(...) 메서드를 가진 객체가 있어야 함.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path


def unescape(s: str) -> str:
    return s.replace("\\n", "\n").replace("\\t", "\t").replace("\\\"", '"').replace("\\\\", "\\")


def load_test_cases(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    # minimal extraction: find "testCases": [ ... ]
    m = re.search(r'"testCases"\s*:\s*\[([\s\S]*?)\]\s*}', text)
    if not m:
        return []
    arr_content = m.group(1)
    cases = []
    for obj in re.finditer(r'\{([^{}]*)\}', arr_content):
        content = obj.group(1)
        id_m = re.search(r'"id"\s*:\s*(\d+)', content)
        desc_m = re.search(r'"description"\s*:\s*"([^"]*)"', content)
        input_m = re.search(r'"input"\s*:\s*"([^"]*)"', content)
        exp_m = re.search(r'"expected"\s*:\s*"([^"]*)"', content)
        if input_m and exp_m:
            cases.append({
                "id": int(id_m.group(1)) if id_m else 0,
                "description": desc_m.group(1) if desc_m else "",
                "input": unescape(input_m.group(1)),
                "expected": unescape(exp_m.group(1)),
            })
    return cases


def normalize(s: str) -> str:
    return " ".join(s.strip().split())


def main() -> None:
    # Insert problem dir (cwd) at front so user's solution.py takes priority
    # over any same-named file in the script's own templates directory.
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    test_file = Path("test/test_cases.json")
    if not test_file.exists():
        print("❌ Error: test/test_cases.json 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    import solution

    parse_path = Path("test/parse.py")
    if not parse_path.exists():
        print("❌ Error: test/parse.py 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)
    _spec = importlib.util.spec_from_file_location("_parse", parse_path)
    parse = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(parse)

    sol = solution.Solution()
    cases = load_test_cases(test_file)
    passed = failed = 0

    print("🧪 테스트 시작")
    print("==========================================")

    for tc in cases:
        try:
            result = parse.parse_and_solve(sol, tc["input"])
            norm_result = normalize(result)
            norm_expected = normalize(tc["expected"])
            if norm_result == norm_expected:
                passed += 1
                desc = f" ({tc['description']})" if tc.get("description") else ""
                print(f"✅ 테스트 {tc['id']}: 통과{desc}")
            else:
                failed += 1
                print(f"❌ 테스트 {tc['id']}: 실패")
                print(f"   입력: {tc['input'].replace(chr(10), '\\\\n')}")
                print(f"   기대값: {tc['expected']}")
                print(f"   결과값: {result}")
        except Exception as e:
            failed += 1
            print(f"❌ 테스트 {tc['id']}: 에러 - {e}")

    print("==========================================")
    total = passed + failed
    if failed == 0 and total > 0:
        print(f"📊 결과: {passed}/{total} 통과 🎉 All Passed!")
    elif total == 0:
        print("📊 결과: 테스트 케이스 없음")
    else:
        print(f"📊 결과: {passed}/{total} 통과 ({failed}개 실패)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
