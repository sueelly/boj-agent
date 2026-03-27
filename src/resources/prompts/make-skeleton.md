# 백준 문제 풀이 스켈레톤 생성 지시

이 지시문에 따라 아래 제공된 `problem.json`을 기반으로 풀이 스켈레톤을 생성하세요.
**별도 웹 검색 불필요 — 아래 JSON에 모든 정보가 포함됩니다.**

---

## 설정 정보

- **언어**: `{{LANG}}` (확장자: `{{EXT}}`)
- **SUPPORTS_PARSE**: `{{SUPPORTS_PARSE}}` (Java/Python은 true, 나머지는 false)
- **문제 디렉터리**: `{{PROBLEM_DIR}}`

---

## 입력 데이터

```json
{{PROBLEM_JSON}}
```

> **problem.json 필드**: `problem_num`, `title`, `time_limit`, `memory_limit`, `description_html`, `input_html`, `output_html`, `samples[{id, input, output}]`, `images`

---

## 생성할 파일

### 1. Solution 파일

- **파일명**: Java → `Solution.java`, Python → `solution.py` (소문자), 기타 → `Solution.{{EXT}}`
- **역할**: 순수 알고리즘 담당. 파싱된 값을 파라미터로 받아 결과 반환.
- **메서드**: `solve(...)` — 문제에 맞는 파라미터와 반환 타입.
- **구현**: 비워두거나 `TODO`만 둠 (사용자가 직접 구현).

**주석 규칙 (필수)**:
- **모든 주석은 한글로 작성**한다. 영어 주석 금지.
- **파일 상단에 문제 설명 요약 주석**을 반드시 포함한다:
  - 문제 번호, 제목
  - 문제 핵심 요약 (1-2줄)
  - 입출력 형식 간략 설명

Java 예시:
```java
/**
 * BOJ 1000 - A+B
 *
 * 두 정수 A와 B를 입력받아 A+B를 출력한다.
 *
 * 입력: 두 정수 A, B (0 < A, B < 10)
 * 출력: A+B
 */
public class Solution {
    public int solve(int a, int b) {
        return 0; // TODO: 구현
    }
}
```

Python 예시:
```python
"""
BOJ 1000 - A+B

두 정수 A와 B를 입력받아 A+B를 출력한다.

입력: 두 정수 A, B (0 < A, B < 10)
출력: A+B
"""

class Solution:
    def solve(self, a: int, b: int) -> int:
        return 0  # TODO: 구현
```

**서명 금지 규칙 (절대 위반 금지)**:
- **단일 String/str 파라미터 전부 금지** — 파라미터 이름과 무관하게, `solve`가 String 하나만 받는 형태는 금지 (raw stdin blob).
- 예: `solve(String input)`, `solve(String s)`, `solve(String data)`, `solve(s: str)` 등 모두 금지.
- 반드시 입력을 파싱한 후의 값들을 **개별 파라미터**로 받을 것.

Java 예시:
```java
// O: 파싱된 값을 개별 파라미터로
public int solve(int a, int b) { ... }
public String solve(int n, int[] arr) { ... }

// X: raw stdin blob
public int solve(String input) { ... }  // 절대 금지
```

### 2. `test/Parse.{{EXT}}` (SUPPORTS_PARSE=true일 때만)

입력 문자열을 파싱해 `Solution.solve(...)`에 넘기고, 반환값을 문자열로 돌려주는 어댑터.

**Java** — `public class Parse implements ParseAndCallSolve`:
```java
import java.util.StringTokenizer;

public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        StringTokenizer st = new StringTokenizer(input);
        int n = Integer.parseInt(st.nextToken());
        // ... 문제에 맞게 파싱
        return String.valueOf(sol.solve(n));
    }
}
```
- `public class` 필수 (submit.sh가 제출 파일 생성 시 `public` 제거)
- `implements ParseAndCallSolve` 필수 (테스트 러너 계약)

**Python** — 모듈 레벨 함수 `parse_and_solve`:
```python
def parse_and_solve(sol, input: str) -> str:
    lines = input.strip().split('\n')
    n = int(lines[0])
    # ... 문제에 맞게 파싱
    return str(sol.solve(n))
```
- 클래스가 아닌 **모듈 레벨 함수**로 작성
- 파일 경로: `test/parse.py` (소문자)

### 3. `test/test_cases.json`

problem.json의 `samples`를 변환:
```json
{
  "testCases": [
    {"input": "...", "expected": "..."},
    ...
  ]
}
```
- `id`와 `description`은 **생략 가능** — `boj run`이 자동으로 채움 (순번 1,2,3... / "예제 N")
- `input`은 전체 입력(줄 구분 `\n`), `expected`는 기대 출력

### 4. `artifacts/signature_review.md` — 서명 리뷰

solve() 서명을 3역할 관점에서 평가. 아래 기준으로 채점 (각 0-2점, 총 24점 만점):

**응시자 관점** (4기준):
| 기준 | 설명 |
|------|------|
| 파라미터 이름이 직관적인가 | 변수명만 보고 의미 파악 가능 |
| 반환 타입이 명확한가 | 기대 출력과 일치 |
| 구현 방향이 명확한가 | 서명만 보고 어떻게 풀지 감 잡힘 |
| 불필요한 파싱 로직이 없는가 | Solution이 파싱을 하지 않음 |

**출제자 관점** (4기준):
| 기준 | 설명 |
|------|------|
| 문제 입력 형식과 일치하는가 | 입력 스펙과 파라미터 대응 |
| 경계값/엣지케이스 처리 가능한가 | 자료형이 범위를 커버 |
| 반환값이 출력 형식과 일치하는가 | 출력 스펙과 반환 타입 대응 |
| 알고리즘 핵심 로직과 일치하는가 | 풀이 의도가 서명에 드러남 |

**코드 리뷰어 관점** (4기준):
| 기준 | 설명 |
|------|------|
| raw stdin blob 패턴 없음 | 단일 String/str 금지 위반 없음 |
| 타입 안전성 | 적절한 자료형 사용 |
| 언어 관용구 준수 | 언어별 네이밍/타입 컨벤션 |
| Parse 계약과의 호환성 | Parse가 이 서명으로 호출 가능 |

**판정 기준**:
- **PASS**: 총점 18+ AND raw stdin blob 없음
- **WARN**: 총점 12-17 또는 경미한 문제
- **FAIL**: 총점 11 이하 또는 raw stdin blob 감지

---

## 서명 리뷰 루프 (필수)

스켈레톤 생성 후 반드시 다음 루프를 실행:

1. Solution의 `solve()` 서명으로 `artifacts/signature_review.md` 작성
2. 판정이 **PASS**이면 → 완료
3. 판정이 **WARN** 또는 **FAIL**이면 → 개선 제안에 따라 서명 수정 → 다시 1로
4. **최대 5회** 반복. 5회 내 PASS 불가 시 최선의 결과로 마무리

> **참고**: 생성 완료 후 make.sh가 자동으로 Gate Check를 수행합니다.
> `solve(String x)` / `solve(x: str)` 패턴이 감지되면 경고가 출력됩니다.
> 이어서 `boj run`이 자동 실행되어 컴파일/테스트를 검증합니다.

---

## 출력 형식 (필수)

**파일을 직접 생성하지 마세요.** 아래 JSON 형식으로 **stdout에만 출력**하세요.
설명 텍스트 없이 JSON만 출력하세요.

```json
{
  "files": {
    "Solution.java": "파일 내용 전체...",
    "test/Parse.java": "파일 내용 전체...",
    "test/test_cases.json": "{\"testCases\": [...]}",
    "artifacts/signature_review.md": "리뷰 내용..."
  }
}
```

- 파일 경로는 문제 디렉터리 기준 **상대 경로**.
- 파일 내용은 **문자열** (JSON 파일도 문자열로 감싸서 출력).
- SUPPORTS_PARSE=false이면 `test/Parse.*` 키를 생략.

---

## 중요 규칙

1. **Solution**: 파싱 로직 없이 `solve(...)` 시그니처만. Parse가 파싱을 담당.
2. **SUPPORTS_PARSE=false**: test/Parse.* 생성 안 함. Solution에서 stdin 직접 읽는 BOJ 표준 방식.
3. **test_cases.json**: `testCases` 키 사용. `input`은 전체 입력(줄 구분 `\n`), `expected`는 기대 출력.
4. **서명 검증**: 반드시 리뷰 루프를 통해 solve() 서명이 PASS인지 확인.
5. **Main 클래스 금지**: Main.java, Test.java, run.sh 생성 금지 (별도 템플릿 존재).
6. **출력 형식 준수**: 반드시 위 JSON 형식으로만 출력. 파일 직접 생성 금지.
