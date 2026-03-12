# Spec Level 설계

spec 생성 시 **level**을 두어, 문제 복잡도에 따라 채울 필드와 Parse 생성 방식을 구분한다.

---

## 전제

- **제거 대상**: `prompts/make-parse-and-tests.md` (make 파이프라인 미사용, make-skeleton으로 통합), `reference/spec/` 내 parse 관련 (spec-to-parse-rules, output-format-catalog, parse-pattern-catalog, spec-to-parse-fewshots 등).
- **Parse 생성**: spec과 Solution의 `solve(...)` 시그니처만 보고 생성. 공통 InputReader 없이, **해당 문제에 필요한 최소한의 파싱만** 작성한다. (예: 1000번 → `split("\\s+")` + `parseInt` 두 번.)
- **테스트**: `Test.java`가 `Parse.parseAndCallSolve(sol, input)` 호출. Parse는 `ParseAndCallSolve` 구현 유지.

---

## Level 1 — 최소

**언제**: 한 줄·몇 토큰 입력, 스칼라 하나 출력. (A+B, A-B, 단일 정수/문자열 등.)

| 구분 | 내용 |
|------|------|
| **spec 필수** | `schemaVersion`, `source`, `input.model`, `input.stream`, `output.model`, `output.presentation`, `userApi` |
| **input.stream** | `topLevelMode: "single"`, `tokenMode: "token"` 또는 `"line"` |
| **input.model** | solve 인자에 대응하는 스칼라 또는 짧은 record |
| **output.presentation** | `single_line_scalar` 등 단일 스타일 하나 |
| **userApi** | `inputStyle: "flatten"`, `flattenedParameters`(순서만), `returnStyle: "direct_model"` |
| **생략 가능** | `input.locals`, `input.normalization` |

**Parse**: 시그니처만 보면 됨. 예: `solve(int a, int b)` → `input.trim().split("\\s+")` 후 `parseInt` 두 번, `String.valueOf(sol.solve(a, b))` 반환.

---

## Level 2 — 중간

**언제**: 여러 줄·배열·행렬, 테스트 케이스 반복(sentinel/eof/testcases), 출력 형식은 하나.

| 구분 | 내용 |
|------|------|
| **spec 필수** | Level 1 전부 + stream/model/presentation을 이 문제에 맞게 구체화 |
| **input.stream** | `single` \| `testcases` \| `eof` \| `sentinel` 중 하나, `tokenMode` 명시 |
| **input** | 필요 시 `locals`(예: `n`, `m`), `model`에 array/matrix 및 `lengthFrom`/`rowsFrom`/`colsFrom` 등 |
| **output.presentation** | `one_per_line`, `space_separated_single_line` 등 |
| **userApi** | flatten 또는 input_record, direct_model 또는 output_record |
| **생략 가능** | `input.normalization`, tagged_union·multi_section 등 고급 패턴 |

**Parse**: spec의 stream·model·presentation만 보고 생성. 루프·배열·행렬 등 필요한 만큼만 추가. 공용 InputReader 없음.

---

## Level 3 — 전체

**언제**: 쿼리/명령 스트림, 그래프·트리, multi_section·boolean_mapping·fixed_precision 등 복합 출력.

| 구분 | 내용 |
|------|------|
| **spec 필수** | `reference/spec/problem-spec-format.md` 및 기존 spec 규칙 전부 |
| **input** | stream, locals, model, 필요 시 normalization |
| **output** | model, presentation(boolean_mapping, fixed_precision_scalar, multi_section 등) |
| **userApi** | input_record, tagged_union 등 포함 |

**Parse**: spec 전체를 보고 생성. 복잡할 때만 작은 헬퍼(예: 소규모 reader) 도입.

---

## Level 선택

| 징후 | level |
|------|--------|
| 한 줄, 스칼라 2~3개, 출력 하나 | 1 |
| 여러 줄, N·M·배열·행렬, 한 출력 형식 | 2 |
| 쿼리/명령 분기, 그래프·트리, 복합 출력 | 3 |

---

## spec에 level 반영

- `problem.spec.json` 최상위에 **`"specLevel": 1`** (또는 2, 3) 포함.
- Generator는 먼저 level을 정한 뒤, 해당 level의 필수 항목만 채우고 나머지는 생략 가능.

---

## Parse 생성 시 (에이전트 지시용)

레퍼런스 없이 Parse만 만들 때 한 줄 지침 예:

> `problem.spec.json`과 `Solution.solve(...)` 시그니처만 보고 `Parse.java`를 작성한다. `ParseAndCallSolve`를 구현하고, `parseAndCallSolve(Solution sol, String input)`에서 `input`만 파싱해 `sol.solve(...)`를 호출한 뒤, spec의 `output.presentation`에 맞는 문자열을 **반환**한다. 공용 InputReader는 쓰지 않고, 이 문제에 필요한 최소 파싱만 한다.
