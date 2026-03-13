# Spec to Parse.java Rules

이 문서는 `problem.spec.json` 을 읽어 `test/Parse.java` 를 생성할 때 따라야 하는 상위 규칙이다.

catalog 와 fewshot 보다 우선한다.

---

## 1. 목표

`Parse.java` 는 다음 책임만 가진다.

1. raw input string 파싱
2. `Solution.solve(...)` 호출
3. solve 결과를 stdout 형식 문자열로 변환
4. 그 문자열을 반환

그 외 역할은 가지지 않는다.

---

## 2. 하네스 고정 규칙

### Rule 2.1
`Parse.java` 는 반드시 `ParseAndCallSolve` 를 구현한다.

### Rule 2.2
`parseAndCallSolve(Solution sol, String input)` 시그니처는 바꾸지 않는다.

### Rule 2.3
`parseAndCallSolve(...)` 안에서 `System.in` 을 읽지 않는다.

### Rule 2.4
`parseAndCallSolve(...)` 안에서 `System.out` 으로 출력하지 않는다.

### Rule 2.5
반드시 최종 stdout 문자열을 `return` 한다.

---

## 3. Solution 호출 규칙

### Rule 3.1
`problem.spec.json.userApi` 를 유일한 호출 기준으로 사용한다.

### Rule 3.2
`userApi.inputStyle = flatten` 이면 `flattenedParameters` 순서대로 `sol.solve(...)` 를 호출한다.

### Rule 3.3
`userApi.inputStyle = input_record` 이면 단일 `Input` 객체를 만들어 `sol.solve(input)` 로 호출한다.

### Rule 3.4
기존 `Solution.java` 가 존재하면 실제 메서드 시그니처와 spec 이 일치하는지 확인해야 한다.

### Rule 3.5
일치하지 않으면 추측하지 말고 실패한다.

---

## 4. 입력 파싱 규칙

### Rule 4.1
`input.stream.topLevelMode` 는 입력 전체 반복 구조를 결정한다.

- `single` -> 한 번만 읽는다
- `testcases` -> `t` 읽고 케이스 반복
- `eof` -> `hasNext()` 기반 반복
- `sentinel` -> sentinel 만족 전까지 반복

### Rule 4.2
`input.stream.tokenMode` 는 reader 사용 방식을 결정한다.

- `token` -> `next()` 계열 중심
- `line` -> `nextLine()` 중심
- `mixed` -> 두 방식을 함께 사용

### Rule 4.3
`input.locals` 는 실제로 읽을 수 있다.
하지만 solve 인자로 넘길지는 `userApi` 와 logical model 이 결정한다.

### Rule 4.4
count-only local 은 파싱에는 쓰되, 불필요하면 solve 에 넘기지 않는다.

### Rule 4.5
배열/행렬 길이 참조(`lengthFrom`, `rowsFrom`, `colsFrom`)는 실제 읽힌 local 과 연결 가능해야 한다.
불가능하면 실패한다.

---

## 5. 타입 파싱 규칙

### Rule 5.1 scalar
기본 매핑:
- int -> `nextInt()`
- long -> `nextLong()`
- double -> `nextDouble()`
- string -> token mode:`next()` / line mode:`nextLine()`
- char -> token 하나를 받아 `charAt(0)`
- bigint -> `new BigInteger(next())`
- bigdecimal -> `new BigDecimal(next())`

### Rule 5.2 array
배열은 길이를 먼저 결정한 뒤 순서대로 읽는다.

### Rule 5.3 matrix
행렬은 row-major order 로 읽는다.

### Rule 5.4 char board
`rowEncoding = char_line` 이면 줄 하나를 읽고 `toCharArray()` 한다.

### Rule 5.5 record
record 는 field 순서대로 읽는다.

### Rule 5.6 tagged_union
query/command 는 tag 값으로 분기해서 variant 객체를 만든다.

---

## 6. 출력 포맷 규칙

### Rule 6.1
출력 문자열은 반드시 `output.presentation` 만으로 결정한다.

### Rule 6.2
반환 타입이 같더라도 presentation style 이 다르면 다른 formatter 를 생성해야 한다.

예:
- `int[]` + `space_separated_single_line`
- `int[]` + `one_per_line`

### Rule 6.3
`boolean_mapping` 은 `trueValue` 와 `falseValue` 를 그대로 사용한다.

### Rule 6.4
`fixed_precision_scalar` 는 spec 의 precision 을 사용한다.

### Rule 6.5
`multi_section` 은 section 순서대로 출력한다.

---

## 7. InputReader 규칙

### Rule 7.1
문자열 기반 `InputReader` 를 `Parse.java` 내부에 생성한다.

### Rule 7.2
최소한 아래 API 를 지원해야 한다.
- `String next()`
- `int nextInt()`
- `long nextLong()`
- `double nextDouble()`
- `String nextLine()`
- `boolean hasNext()`

### Rule 7.3
`next()` 와 `nextLine()` 혼용 시 줄 경계가 깨지지 않도록 구현한다.

---

## 8. test_cases.json 규칙

### Rule 8.1
실제 sample input/output 이 없는 경우 expected 값을 발명하지 않는다.

### Rule 8.2
`test/test_cases.json` 을 생성할 때는 하네스 형식을 정확히 따른다.

### Rule 8.3
newline 은 JSON 문자열 안에서 `\n` 으로 이스케이프한다.

---

## 9. 금지 패턴

### Forbidden 9.1
reflection 으로 `solve(...)` 를 찾기

### Forbidden 9.2
`Parse.java` 안에서 stdout 직접 출력

### Forbidden 9.3
presentation style 을 무시하고 `String.valueOf(result)` 만 쓰기

### Forbidden 9.4
spec 이 불충분한데 추측으로 파싱 순서를 작성하기

### Forbidden 9.5
공통 하네스 파일 수정하기

---

## 10. 실패해야 하는 경우

다음 경우는 조용히 넘어가지 말고 실패해야 한다.

1. `Solution.solve(...)` 시그니처 불일치
2. `lengthFrom` 참조 불가
3. unknown presentation style
4. tagged_union 분기 정보 불충분
5. input_record 인데 `Input` 타입이 존재하지 않음
6. output_record 인데 `Output` 타입이 존재하지 않음

---

## 11. 최종 판단 요약

`Parse.java` 는 statement 를 해석하는 코드가 아니다.
이미 해석된 spec 을 **문자열 파싱 + solve 호출 + 문자열 포맷** 으로 내리는 얇은 adapter 여야 한다.
