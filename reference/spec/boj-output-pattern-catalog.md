# BOJ Output Pattern Catalog

이 문서는 BOJ 문제의 출력 요구를 `output.model`과 `output.presentation`으로 정규화할 때 사용하는 카탈로그입니다.

핵심 원칙은 항상 같습니다.

- `model`: solve가 반환하는 논리 값
- `presentation`: stdout에 출력되는 형식

---

## Pattern 1. 단일 스칼라

### 정의
답이 값 하나인 경우입니다.

### 권장 logical model
- scalar

### 권장 user API
```java
int solve(...)
long solve(...)
String solve(...)
double solve(...)
```

### 권장 presentation
- `single_line_scalar`

### 예시 문제군
- 합
- 개수
- 최댓값
- 최소 이동 횟수

---

## Pattern 2. boolean answer with textual mapping

### 정의
답은 논리적으로 boolean인데, 출력은 특정 문자열/숫자 형식인 경우입니다.

### 대표 형태
- YES / NO
- Yes / No
- 1 / 0

### 권장 logical model
- boolean

### 권장 user API
```java
boolean solve(...)
```

### 권장 presentation
```json
{
  "style": "boolean_mapping",
  "trueValue": "YES",
  "falseValue": "NO"
}
```

### 핵심 이유
알고리즘은 boolean으로 두고, formatter가 요구 문자열로 매핑하는 것이 가장 깔끔합니다.

---

## Pattern 3. 고정 길이 의미 튜플

### 정의
출력 필드 수는 적지만 각 값의 의미가 다른 경우입니다.

### 예시
- min, max
- x, y
- numerator, denominator

### 권장 logical model
- record

### 권장 user API
```java
Output solve(...)
```

### 대표 예시
```java
record Output(int min, int max) {}
```

### 권장 presentation
- `single_line_record`
- 필요하면 `multi_section`

### 이유
`int[]`보다 의미가 훨씬 명확합니다.

---

## Pattern 4. 동질적 배열 한 줄 출력

### 정의
같은 종류의 값들을 한 줄에 구분자로 출력하는 경우입니다.

### 권장 logical model
- array

### 권장 user API
```java
int[] solve(...)
long[] solve(...)
List<String> solve(...)
```

### 권장 presentation
- `space_separated_single_line`

### 기본 구분자
- 보통 공백

---

## Pattern 5. 동질적 배열 여러 줄 출력

### 정의
같은 종류의 값들을 줄마다 하나씩 출력하는 경우입니다.

### 권장 logical model
- array

### 권장 user API
```java
int[] solve(...)
long[] solve(...)
List<String> solve(...)
```

### 권장 presentation
- `one_per_line`

### 예시 문제군
- query 결과들
- testcase 결과들
- 여러 개의 답

---

## Pattern 6. 2차원 행렬 출력

### 정의
행 단위로 여러 줄 출력하고, 각 행 내부에 여러 값이 있는 경우입니다.

### 권장 logical model
- matrix

### 권장 user API
```java
int[][] solve(...)
char[][] solve(...)
```

### 권장 presentation
- `matrix_rows`

### 기본값
- row separator: newline
- col separator: space

### 예외
`char[][]` 보드처럼 붙여서 출력하는 문제는 `colSeparator`를 빈 문자열로 둘 수 있습니다.

---

## Pattern 7. 문자열 줄 목록

### 정의
출력이 숫자 배열보다 line sequence에 가까운 경우입니다.

### 권장 logical model
- `String[]`
- `List<String>`

### 권장 user API
```java
List<String> solve(...)
```

### 권장 presentation
- `one_per_line`

### 예시 문제군
- symbolic outputs
- 여러 줄 텍스트 결과
- 각 testcase의 문자열 결과

---

## Pattern 8. testcase 결과 모음

### 정의
여러 테스트케이스 각각이 하나의 답을 내는 경우입니다.

### 권장 logical model
- homogeneous result array

### 권장 user API
```java
long[] solve(TestCase[] cases)
List<String> solve(TestCase[] cases)
```

### 권장 presentation
- `one_per_line`

### 이유
테스트케이스 반복 출력은 formatter concern입니다.

---

## Pattern 9. query response collection

### 정의
모든 query가 출력하는 것은 아니지만, 출력하는 것들의 타입은 같은 경우입니다.

### 권장 logical model
- printed result만 모은 homogeneous array/list

### 권장 user API
```java
int[] solve(Query[] queries)
List<Integer> solve(Query[] queries)
```

### 권장 presentation
- `one_per_line`

### 이유
출력 없는 query를 output model에 억지로 포함시키지 않습니다.

---

## Pattern 10. fixed precision scalar

### 정의
실수 값을 고정 소수점 자리수로 출력해야 하는 경우입니다.

### 권장 logical model
- `double`
- 필요하면 `bigdecimal`

### 권장 user API
```java
double solve(...)
BigDecimal solve(...)
```

### 권장 presentation
```json
{
  "style": "fixed_precision_scalar",
  "precision": 6
}
```

---

## Pattern 11. raw block output

### 정의
출력 전체를 한 개의 raw string block으로 다루는 편이 더 자연스러운 경우입니다.

### 권장 logical model
- string

### 권장 user API
```java
String solve(...)
```

### 권장 presentation
- `raw_block`

### 사용 조건
- 출력 형식이 매우 irregular함
- ASCII art-like output
- structured formatting 이점이 거의 없음

### 경고
이건 escape hatch입니다. 기본값이 아닙니다.

---

## Pattern 12. multi-section structured output

### 정의
서로 다른 의미의 output field들이 서로 다른 방식으로 출력되는 경우입니다.

### 예시
- 첫 줄 count, 둘째 줄 path
- 첫 줄 distance, 다음 줄 sequence
- scalar + list

### 권장 logical model
- record

### 권장 user API
```java
Output solve(...)
```

### 대표 예시
```java
record Output(int count, int[] path) {}
```

### 권장 presentation
- `multi_section`

### 이유
이걸 raw string으로 몰아넣지 말고 구조를 유지해야 formatter 생성이 쉬워집니다.

---

# Selection Rules

## scalar를 우선할 때
- 논리 값이 하나뿐이다

## array를 우선할 때
- 출력이 동질적이고 반복적이다

## matrix를 우선할 때
- 출력이 본질적으로 2차원이다

## record를 우선할 때
- 출력 필드 의미가 다르다
- field name이 가독성에 실질적으로 기여한다
- multi-section formatting이 필요하다

## raw block을 허용할 때
- supported presentation styles로 구조화하는 이점이 거의 없다

---

# 자주 하는 실수

1. YES/NO 문제를 `String` return으로 직접 만들어버리는 것
2. simple list 출력을 raw block string으로 처리하는 것
3. 의미가 다른 값들을 homogeneous array로 처리하는 것
4. plain array 결과인데 불필요하게 record output을 도입하는 것
5. fixed precision 문제에서 precision field를 누락하는 것
6. BOJ에서 출력 형식도 정답 판정 일부라는 점을 놓치는 것
