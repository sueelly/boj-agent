# ProblemSpec Contract for Parse.java Generation

이 문서는 `problem.spec.json` 을 `test/Parse.java` 로 내릴 때,
각 필드를 어떻게 해석해야 하는지 정의한다.

이 문서는 schema 자체가 아니라 **generator 계약(contract)** 이다.

---

## 1. 목적

`problem.spec.json` 은 문제 설명 전체를 다시 담는 파일이 아니다.
`Parse.java` 생성에 필요한 최소한의 논리 정보를 제공하는 중간 표현이다.

`Parse.java` 생성 시에는 아래 네 축이 중요하다.

1. `input` — raw input string 을 어떤 논리 값으로 읽을지
2. `output` — `solve(...)` 결과를 어떻게 문자열로 바꿀지
3. `userApi` — `Solution.solve(...)` 를 어떤 시그니처로 호출할지
4. `notes` — 모호성이나 보조 힌트

---

## 2. top-level structure

최소 기대 구조는 다음과 같다.

```json
{
  "schemaVersion": "1.0",
  "source": { ... },
  "input": { ... },
  "output": { ... },
  "userApi": { ... },
  "notes": [ ... ]
}
```

`notes` 는 선택이다.

---

## 3. input section

### `input.locals`
파싱에는 필요하지만 `solve(...)` 인자로 직접 가지 않을 수 있는 값들이다.

예:
- `n`
- `m`
- `t`
- 반복 횟수
- 길이 정보

`Parse.java` 는 이 값을 실제로 읽어야 할 수 있다.
하지만 `userApi` 에 보이지 않으면 `solve(...)` 인자로 넘기지 않는다.

---

### `input.model`
`Solution.solve(...)` 에 전달될 **논리 입력 모델**이다.

예:
- scalar
- array
- matrix
- record
- enum
- tagged_union

`Parse.java` 는 raw string 을 읽어서 이 logical model 과 일치하는 Java 값을 만들어야 한다.

---

### `input.stream`
입력 전체의 반복 구조를 설명한다.

주요 필드:
- `topLevelMode`: `single` / `testcases` / `eof` / `sentinel`
- `tokenMode`: `token` / `line` / `mixed`

`Parse.java` 는 이 정보를 이용해 입력 전체를 한 번의 실행 단위로 읽는다.

---

### `input.normalization`
보조 메타정보다.

예:
- `hiddenLocals`
- `indexBase`
- notes

`Parse.java` 에서 직접 코드 생성에 쓰일 수도 있고, 단지 설명 힌트일 수도 있다.

---

## 4. output section

### `output.model`
`solve(...)` 의 논리 반환값이다.

예:
- scalar
- array
- matrix
- record

### `output.presentation`
이 논리 반환값을 **실제 stdout 문자열**로 바꾸는 규칙이다.

이 두 개는 항상 분리해서 해석해야 한다.

예:
- `boolean` + `YES/NO`
- `int[]` + 공백 구분 한 줄
- `Output(distance, path)` + multi-section

---

## 5. userApi section

이 섹션은 `Solution.solve(...)` 호출 방식을 결정한다.

### `methodName`
현재는 항상 `solve` 를 기대한다.

### `inputStyle`
- `flatten`
- `input_record`

#### `flatten`
`userApi.flattenedParameters` 순서대로 `solve(...)` 에 전달한다.

예:
```java
sol.solve(n, edges)
sol.solve(nums)
```

#### `input_record`
논리 입력 모델 전체를 하나의 `Input` 객체로 전달한다.

예:
```java
sol.solve(inputObj)
```

---

### `flattenedParameters`
`inputStyle = flatten` 일 때만 의미가 있다.

이 배열의 순서가 곧 `solve(...)` 파라미터 순서다.

에이전트는 이 순서를 바꾸면 안 된다.

---

### `returnStyle`
- `direct_model`
- `output_record`

#### `direct_model`
`solve(...)` 가 직접 스칼라/배열/문자열 등을 반환한다.

#### `output_record`
`solve(...)` 가 `Output` record 를 반환한다.

`Parse.java` 는 이 값을 `output.presentation` 에 맞게 문자열로 변환해야 한다.

---

## 6. TypeSpec contract

`Parse.java` generator 는 아래 타입들을 지원해야 한다.

### scalar
지원 primitive:
- `int`
- `long`
- `double`
- `string`
- `boolean`
- `char`
- `bigint`
- `bigdecimal`

### array
길이 정보는 다음 중 하나로 온다.
- `length`
- `lengthFrom`

### matrix
주요 필드:
- `cellType`
- `rows` / `rowsFrom`
- `cols` / `colsFrom`
- `rowEncoding`

### record
Java record 와 대응한다고 가정한다.

### enum
Java enum 과 대응한다고 가정한다.

### tagged_union
Java 11 에서는 sealed interface 가 없으므로,
`Parse.java` 입장에서는 **이미 존재하는 타입 이름**을 그대로 사용하거나,
문제별 타입 정의가 `Solution.java` 또는 별도 파일에 있다고 가정한다.

즉 `Parse.java` 는 union variant 객체를 생성하는 코드만 가지면 된다.

---

## 7. Parse.java generator가 반드시 기대하는 것

아래는 spec 쪽 invariant 다.

### invariant 1
`userApi.inputStyle = input_record` 이면 top-level input model 은 Java 쪽에 존재하는 `Input` 타입과 일치해야 한다.

### invariant 2
`userApi.returnStyle = output_record` 이면 top-level output model 은 Java 쪽 `Output` 타입과 일치해야 한다.

### invariant 3
`userApi.inputStyle = flatten` 이면 `flattenedParameters` 가 반드시 있어야 한다.

### invariant 4
`output.presentation` 만으로 formatter 생성이 가능해야 한다.

이 invariant 들이 깨지면 `Parse.java` 를 억지로 생성하지 말고 실패해야 한다.

---

## 8. Parse.java 관점에서 spec이 충분한 경우

다음 조건을 만족하면 `Parse.java` 를 deterministic 하게 만들 수 있다.

1. top-level input 구조가 single/testcases/eof/sentinel 중 하나로 명확하다.
2. 배열/행렬 길이 참조가 해석 가능하다.
3. query/tagged_union 의 variant shape 가 명확하다.
4. `userApi` 가 `solve(...)` 인자 구조를 결정해준다.
5. `output.presentation` 이 문자열 포맷 방식을 결정해준다.

---

## 9. spec이 불충분한 경우

다음과 같으면 추측해서 생성하지 말아야 한다.

- 어떤 local 이 언제 읽히는지 전혀 복원 불가
- `flattenedParameters` 와 logical model 연결이 불분명
- `multi_section` 출력인데 field 정보가 없음
- query variant shape 가 일부 누락됨
- line mode 가 필요한데 spec 에 token/line 구분이 없음

이 경우는 실패 메시지를 반환해야 한다.
