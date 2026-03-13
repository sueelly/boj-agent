# ProblemSpec Format

이 문서는 `problem.spec.json`의 **필드 구조와 의미**를 정의하는 계약 문서입니다.

이 단계에서는 JSON Schema 대신 사람이 읽기 쉬운 규격 문서로 사용합니다.

---

## Top-level structure

최상위 JSON 객체는 아래 필드를 가집니다.

```json
{
  "schemaVersion": "1.0",
  "specLevel": 1,
  "source": { ... },
  "input": { ... },
  "output": { ... },
  "userApi": { ... },
  "notes": [ ... ]
}
```

### Required fields
- `schemaVersion`
- `source`
- `input`
- `output`
- `userApi`

### Optional fields
- `specLevel`: `1` | `2` | `3`. Spec 복잡도 단계. 있으면 Parse 생성 시 참고하며, 해당 level에서 요구하는 필드만 채우면 됨. 자세한 건 `reference/spec/spec-levels.md`.
- `notes`

---

## 1. `schemaVersion`

```json
"schemaVersion": "1.0"
```

고정값으로 `1.0`을 사용합니다.

---

## 2. `source`

문제 출처 메타데이터입니다.

```json
"source": {
  "platform": "boj",
  "problemId": "1000",
  "title": "A+B"
}
```

### Required fields
- `platform`: 항상 `boj`
- `problemId`: 문자열
- `title`: 문자열

---

## 3. `input`

입력 구조를 정의합니다.

```json
"input": {
  "locals": [ ... ],
  "model": { ... },
  "stream": { ... },
  "normalization": { ... }
}
```

### Required fields
- `model`
- `stream`

### Optional fields
- `locals`
- `normalization`

---

## 3-1. `input.locals`

파싱에는 필요하지만, logical input model에는 반드시 드러나지 않아도 되는 값입니다.

예:
- `n`
- `m`
- `t`
- 배열 길이
- testcase 개수

형태:

```json
"locals": [
  { "name": "n", "type": "int" },
  { "name": "m", "type": "int" }
]
```

각 local은 다음 필드를 가집니다.

- `name`: 식별자
- `type`: primitive type

허용 primitive type:
- `int`
- `long`
- `double`
- `string`
- `boolean`
- `char`
- `bigint`
- `bigdecimal`

---

## 3-2. `input.model`

사용자가 `solve(...)`에서 다루게 될 **logical input model**입니다.

허용 type shape:
- `scalar`
- `array`
- `matrix`
- `record`
- `enum`
- `tagged_union`

---

## 3-2-1. Scalar

```json
{ "kind": "scalar", "type": "int" }
```

---

## 3-2-2. Array

```json
{
  "kind": "array",
  "element": { "kind": "scalar", "type": "int" },
  "lengthFrom": "n",
  "readAs": "tokens"
}
```

### Fields
- `kind`: `array`
- `element`: element type spec
- `lengthFrom`: optional, local name or visible field name
- `length`: optional fixed integer length
- `readAs`: optional, one of:
  - `tokens`
  - `lines`

`length`와 `lengthFrom` 둘 중 하나가 있는 것이 일반적입니다.

---

## 3-2-3. Matrix

```json
{
  "kind": "matrix",
  "cellType": "char",
  "rowsFrom": "n",
  "colsFrom": "m",
  "rowEncoding": "char_line"
}
```

### Fields
- `kind`: `matrix`
- `cellType`: primitive type
- `rowsFrom` or `rows`
- `colsFrom` or `cols`
- `rowEncoding`: one of
  - `token_row`
  - `char_line`
  - `string_line`

---

## 3-2-4. Record

```json
{
  "kind": "record",
  "name": "Edge",
  "fields": [
    { "name": "from", "type": { "kind": "scalar", "type": "int" } },
    { "name": "to", "type": { "kind": "scalar", "type": "int" } }
  ]
}
```

### Fields
- `kind`: `record`
- `name`: type name
- `fields`: array of field specs

각 field spec:

```json
{
  "name": "from",
  "type": { "kind": "scalar", "type": "int" }
}
```

---

## 3-2-5. Enum

```json
{
  "kind": "enum",
  "name": "Op",
  "valueType": "string",
  "values": [
    { "name": "PUSH", "wireValue": "push" },
    { "name": "POP", "wireValue": "pop" }
  ]
}
```

### Fields
- `kind`: `enum`
- `name`: enum 이름
- `valueType`: `string` or `int`
- `values`: enum value list

---

## 3-2-6. Tagged union

명령/질의처럼 줄 형태가 여러 개인 경우에 사용합니다.

```json
{
  "kind": "tagged_union",
  "name": "Query",
  "tagField": "op",
  "tagType": "string",
  "variants": [
    {
      "tagValue": "push",
      "name": "Push",
      "fields": [
        { "name": "x", "type": { "kind": "scalar", "type": "int" } }
      ]
    },
    {
      "tagValue": "pop",
      "name": "Pop",
      "fields": []
    }
  ]
}
```

### Fields
- `kind`: `tagged_union`
- `name`: union 이름
- `tagField`: tag 의미 이름
- `tagType`: `string` or `int`
- `variants`: variant 배열

---

## 3-3. `input.stream`

입력 스트림 구조를 설명합니다.

```json
"stream": {
  "topLevelMode": "single",
  "tokenMode": "token"
}
```

### Required fields
- `topLevelMode`
- `tokenMode`

### `topLevelMode`
- `single`
- `testcases`
- `eof`
- `sentinel`

### `tokenMode`
- `token`
- `line`
- `mixed`

### Optional fields
- `testcaseCountLocal`
- `sentinel`

예시:

```json
"stream": {
  "topLevelMode": "testcases",
  "tokenMode": "token",
  "testcaseCountLocal": "t"
}
```

sentinel 예시:

```json
"stream": {
  "topLevelMode": "sentinel",
  "tokenMode": "token",
  "sentinel": {
    "mode": "tuple_equals",
    "value": [0, 0]
  }
}
```

`sentinel.mode` 허용값:
- `scalar_equals`
- `line_equals`
- `tuple_equals`

---

## 3-4. `input.normalization`

정규화 과정에서 숨긴 값이나 메타 정보를 적습니다.

```json
"normalization": {
  "hiddenLocals": ["n", "m"],
  "indexBase": 1,
  "notes": [
    "Used char matrix because the board is manipulated cell-by-cell."
  ]
}
```

### Optional fields
- `hiddenLocals`: 숨긴 local 이름 목록
- `indexBase`: `0` or `1`
- `notes`: 짧은 메모

---

## 4. `output`

출력 구조를 정의합니다.

```json
"output": {
  "model": { ... },
  "presentation": { ... }
}
```

### Required fields
- `model`
- `presentation`

`model`은 input과 동일한 type shape 시스템을 사용합니다.

---

## 4-1. `output.presentation`

stdout에 어떻게 출력해야 하는지를 설명합니다.

```json
"presentation": {
  "style": "single_line_scalar"
}
```

### `style` 허용값
- `single_line_scalar`
- `space_separated_single_line`
- `one_per_line`
- `matrix_rows`
- `boolean_mapping`
- `fixed_precision_scalar`
- `raw_block`
- `single_line_record`
- `multi_section`

---

## 4-1-1. boolean mapping

```json
"presentation": {
  "style": "boolean_mapping",
  "trueValue": "YES",
  "falseValue": "NO"
}
```

---

## 4-1-2. fixed precision

```json
"presentation": {
  "style": "fixed_precision_scalar",
  "precision": 6
}
```

---

## 4-1-3. single-line separated output

```json
"presentation": {
  "style": "space_separated_single_line",
  "separator": " "
}
```

`separator`를 생략하면 기본 공백으로 간주합니다.

---

## 4-1-4. matrix rows

```json
"presentation": {
  "style": "matrix_rows",
  "rowSeparator": "\n",
  "colSeparator": " "
}
```

---

## 4-1-5. multi-section

출력 record의 각 field를 서로 다른 방식으로 출력할 때 사용합니다.

```json
"presentation": {
  "style": "multi_section",
  "sections": [
    {
      "field": "distance",
      "style": "single_line_scalar"
    },
    {
      "field": "path",
      "style": "space_separated_single_line",
      "separator": " "
    }
  ]
}
```

각 section은 다음 필드를 가질 수 있습니다.
- `field`
- `style`
- `separator`
- `rowSeparator`
- `colSeparator`
- `precision`
- `trueValue`
- `falseValue`

---

## 5. `userApi`

사용자가 구현할 `solve(...)`의 시그니처 형태를 정의합니다.

```json
"userApi": {
  "methodName": "solve",
  "inputStyle": "flatten",
  "flattenedParameters": [ ... ],
  "returnStyle": "direct_model"
}
```

### Required fields
- `methodName`: 항상 `solve`
- `inputStyle`
- `returnStyle`

### `inputStyle`
- `flatten`
- `input_record`

### `returnStyle`
- `direct_model`
- `output_record`

### `flattenedParameters`
`inputStyle = flatten`일 때만 사용합니다.

예:

```json
"flattenedParameters": [
  { "name": "n", "type": { "kind": "scalar", "type": "int" } },
  { "name": "edges", "type": { "kind": "array", "element": { "kind": "record", "name": "Edge", "fields": [ ... ] } } }
]
```

---

## 6. `notes`

짧은 보충 메모입니다.

```json
"notes": [
  "Kept n visible because graph algorithms usually require vertex count explicitly."
]
```

길게 쓰지 않습니다.

---

## 7. 강한 권장 규칙

### 1.
`input.model`은 raw stdin이 아니라 **logical input**이어야 합니다.

### 2.
`output.model`과 `output.presentation`은 반드시 분리합니다.

### 3.
`Object`는 user-facing API에 등장하면 안 됩니다.

### 4.
길이만 알려주는 `n`은 보통 `locals`로 숨깁니다.

### 5.
그래프는 기본적으로 `n + Edge[]` 형태를 우선합니다.

### 6.
BOJ 트리는 기본적으로 `TreeNode root`로 가지 않습니다.

### 7.
질의 스트림은 가능한 한 `tagged_union`으로 표현합니다.
