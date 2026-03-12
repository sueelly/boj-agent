# Output Format Catalog

이 문서는 `problem.spec.json.output.presentation` 을 `Parse.java` 의 반환 문자열로 바꾸는 패턴을 정리한다.

핵심 원칙:
- `solve(...)` 반환값과
- 실제 stdout 문자열 포맷은
항상 분리해서 생각한다.

---

## Pattern 1. single_line_scalar

### Meaning
단일 값 하나를 한 줄에 출력한다.

### Typical Java shape
```java
return String.valueOf(result);
```

### Notes
- int, long, string, boolean raw, bigint 등에 사용 가능
- trailing newline 추가하지 않는 것을 기본값으로 둔다

---

## Pattern 2. boolean_mapping

### Meaning
논리값은 boolean 이지만 출력은 특정 문자열 매핑이다.

### Typical Java shape
```java
return result ? "YES" : "NO";
```

### Required spec fields
- `trueValue`
- `falseValue`

### Notes
- `YES/NO`, `Yes/No`, `1/0` 모두 가능
- solve 가 문자열을 직접 반환하게 만들지 않는다

---

## Pattern 3. space_separated_single_line

### Meaning
동질적인 값 목록을 한 줄에 separator 로 이어 붙인다.

### Typical Java shape
```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < result.length; i++) {
    if (i > 0) sb.append(' ');
    sb.append(result[i]);
}
return sb.toString();
```

### Notes
- default separator 는 space
- spec 에 `separator` 가 있으면 그것을 우선한다

---

## Pattern 4. one_per_line

### Meaning
목록을 줄마다 하나씩 출력한다.

### Typical Java shape
```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < result.length; i++) {
    if (i > 0) sb.append('\n');
    sb.append(result[i]);
}
return sb.toString();
```

### Notes
- query results
- testcase results
- 문자열 목록에도 자주 사용

---

## Pattern 5. matrix_rows

### Meaning
행렬을 행 단위로 출력한다.

### Typical Java shape
```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < result.length; i++) {
    if (i > 0) sb.append('\n');
    for (int j = 0; j < result[i].length; j++) {
        if (j > 0) sb.append(' ');
        sb.append(result[i][j]);
    }
}
return sb.toString();
```

### Notes
- default col separator 는 space
- char board compact row 는 separator 없이 이어붙일 수도 있다

---

## Pattern 6. fixed_precision_scalar

### Meaning
실수 하나를 고정 소수점 자릿수로 출력한다.

### Typical Java shape
```java
return String.format(Locale.US, "%.6f", result);
```

### Required spec fields
- `precision`

### Notes
- Locale.US 를 명시하는 편이 안전하다
- `BigDecimal` 이면 별도 formatting 전략 필요 가능

---

## Pattern 7. single_line_record

### Meaning
record field 들을 한 줄에 출력한다.

### Example
`Output(int min, int max)` -> `min max`

### Typical Java shape
```java
return result.min() + " " + result.max();
```

### Notes
- 필드 순서는 spec 의 fields 순서를 따른다
- separator 는 default space

---

## Pattern 8. multi_section

### Meaning
서로 의미가 다른 출력 파트를 다른 방식으로 출력한다.

### Example
- 첫 줄: distance
- 둘째 줄: path (space-separated)

### Typical Java shape
```java
StringBuilder sb = new StringBuilder();
sb.append(result.distance());
sb.append('\n');
for (int i = 0; i < result.path().length; i++) {
    if (i > 0) sb.append(' ');
    sb.append(result.path()[i]);
}
return sb.toString();
```

### Required spec fields
- `sections`
- 각 section 의 `field`
- 각 section 의 `style`

### Notes
- section 순서는 spec 을 그대로 따른다
- 각 section 은 자기 style 로 independently formatting 해야 한다

---

## Pattern 9. raw_block

### Meaning
결과 자체가 이미 stdout 최종 문자열이다.

### Typical Java shape
```java
return result;
```

### Notes
- 최후의 escape hatch
- 기본값으로 남용하면 안 된다

---

# Common helper methods recommended inside Parse.java

다음 helper 메서드를 넣으면 코드가 정리된다.

## `joinInts(int[] arr, String sep)`
```java
private String joinInts(int[] arr, String sep) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < arr.length; i++) {
        if (i > 0) sb.append(sep);
        sb.append(arr[i]);
    }
    return sb.toString();
}
```

## `joinLongs(long[] arr, String sep)`
## `joinStrings(String[] arr, String sep)`
## `appendMatrix(...)`

하지만 꼭 generic utility 를 만들 필요는 없고,
문제별 `Parse.java` 가 짧아지는 방향이면 inline 도 괜찮다.

---

# Formatting selection summary

- 단일 값 -> `single_line_scalar`
- boolean answer -> `boolean_mapping`
- 배열 한 줄 -> `space_separated_single_line`
- 배열 여러 줄 -> `one_per_line`
- 행렬 -> `matrix_rows`
- 실수 고정 자릿수 -> `fixed_precision_scalar`
- 이름 있는 튜플 -> `single_line_record`
- count + path 같은 복합 출력 -> `multi_section`
- 매우 특수한 자유 문자열 -> `raw_block`

---

# Mistakes to avoid

1. 배열을 `String.valueOf(arr)` 로 출력하기
2. `boolean_mapping` 을 무시하고 `true/false` 출력하기
3. multi_section 을 한 줄로 뭉개기
4. separator/precision 을 spec 대신 하드코딩하기
5. trailing spaces 또는 불필요한 trailing newline 남기기
