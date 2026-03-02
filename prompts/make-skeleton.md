# 백준 문제 풀이 스켈레톤 생성 지시

이 지시문에 따라 아래 제공된 `problem.json`을 기반으로 풀이 스켈레톤을 생성하세요.
**별도 웹 검색 불필요 — 아래 JSON에 모든 정보가 포함됩니다.**

---

## 설정 정보

- **언어**: `{{LANG}}` (확장자: `{{EXT}}`)
- **SUPPORTS_PARSE**: `{{SUPPORTS_PARSE}}` (Java/Python은 true, 나머지는 false)
- **출력 디렉터리**: `{{PROBLEM_DIR}}`

---

## 입력 데이터

```json
{{PROBLEM_JSON}}
```

---

## 생성할 파일

### 1. `Solution.{{EXT}}`

- **역할**: 순수 알고리즘 담당. 파싱된 값을 파라미터로 받아 결과 반환.
- **메서드**: `solve(...)` — 문제에 맞는 파라미터와 반환 타입.
- **구현**: 비워두거나 `TODO`만 둠 (사용자가 직접 구현).

**서명 금지 규칙 (절대 위반 금지)**:
- `solve(String input)` ← 금지 (raw stdin blob)
- `solve(String raw)` ← 금지
- `solve(String stdin)` ← 금지
- `solve(String s)` 단독 파라미터 ← 금지 (파싱 없이 전체 입력을 받는 형태)
- 반드시 입력을 파싱한 후의 값들을 개별 파라미터로 받을 것

Java 예시:
```java
// O: 파싱된 값을 개별 파라미터로
public int solve(int a, int b) { ... }
public String solve(int n, int[] arr) { ... }

// X: raw stdin blob
public int solve(String input) { ... }  // 절대 금지
```

### 2. `test/Parse.{{EXT}}` (SUPPORTS_PARSE=true일 때만)

- Java: `ParseAndCallSolve` 인터페이스 구현 (`parseAndCallSolve(Solution sol, String input)`)
- Python: `parse_and_solve(sol, input: str) -> str` 함수
- templates 디렉터리의 인터페이스 계약을 반드시 준수할 것

### 3. `test/test_cases.json`

problem.json의 `samples`를 변환:
```json
{
  "testCases": [
    {"id": 1, "description": "예제 1", "input": "...", "expected": "..."},
    ...
  ]
}
```

### 4. `artifacts/signature_review.md`

아래 `prompts/signature-review-template.md` 형식을 따라 생성:
- 3역할(응시자/출제자/리뷰어) 관점 평가
- 기준별 0-2점 채점
- 종합 판정 (PASS/FAIL/WARN)
- 판정 이유 및 개선 제안

---

## 중요 규칙

1. **Solution**: 파싱 로직 없이 `solve(...)` 시그니처만. Parse가 파싱을 담당.
2. **SUPPORTS_PARSE=false**: test/Parse.* 생성 안 함. Solution에서 stdin 직접 읽는 BOJ 표준 방식.
3. **test_cases.json**: `testCases` 키 사용. `input`은 전체 입력(줄 구분 `\n`), `expected`는 기대 출력.
4. **서명 검증**: 생성 전 solve() 파라미터가 금지 패턴에 해당하는지 반드시 확인.
5. **Main 클래스 금지**: Main.java, Test.java, run.sh 생성 금지 (별도 템플릿 존재).
