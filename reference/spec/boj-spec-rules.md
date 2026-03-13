# BOJ Spec Rules

이 문서는 BOJ 문제 설명을 `problem.spec.json`으로 바꾸는 데 필요한 **상위 규칙**을 정의합니다.

catalog와 few-shot 예시보다 우선합니다.

---

## 1. 목표

문제 설명을 아래 다섯 요소로 분해합니다.

- parse-only locals
- logical input model
- logical output model
- stdout presentation
- user-facing solve API

즉, 이 문서는 stdin/stdout 문장을 그대로 옮기는 것이 아니라 **정규화된 문제 표현**을 만들기 위한 규칙입니다.

---

## 2. 기본 원칙

### Rule 2.1
파싱 관점과 알고리즘 관점을 분리합니다.

### Rule 2.2
출력 값과 출력 포맷을 분리합니다.

### Rule 2.3
spec은 문제 원문 재진술이 아니라, 나중에 코드 생성 가능한 **중간 표현**이어야 합니다.

---

## 3. 입력 규칙

### Rule 3.1. stream mode를 반드시 명시한다
입력 스트림은 정확히 하나로 분류합니다.

- `single`
- `testcases`
- `eof`
- `sentinel`

---

### Rule 3.2. token mode를 반드시 명시한다
입력 파싱 방식은 정확히 하나로 분류합니다.

- `token`
- `line`
- `mixed`

---

### Rule 3.3. count-only local은 숨긴다
배열 길이, 반복 횟수, testcase 수처럼 **오직 읽기 개수만 알려주는 값**은 `input.locals`에 두고, 보통 `input.model`에서는 숨깁니다.

예:
- 첫 줄 `N`
- 둘째 줄 `N`개의 정수

이 경우 보통 `n`은 locals에 두고, logical model은 `int[] nums`가 됩니다.

---

### Rule 3.4. 의미 있는 값은 숨기지 않는다
아래처럼 알고리즘 의미가 있는 값은 logical model에 남깁니다.

예:
- graph node count
- start node
- destination
- target value
- budget
- limit
- window size
- threshold

즉 기준은 이렇습니다.

- 단지 몇 개 읽을지 알려주는 값이면 숨긴다
- 문제 로직 의미가 있으면 남긴다

---

### Rule 3.5. 반복되는 고정 폭 튜플은 named record 배열을 우선한다
반복되는 줄이 고정된 의미를 가진다면 `int[][]`보다 named record 배열을 우선합니다.

좋은 예:
- `Point[]`
- `Edge[]`
- `Interval[]`
- `Job[]`

나쁜 예:
- `int[][] tuples`

---

### Rule 3.6. BOJ-native 표현을 우선한다
LeetCode식 helper-heavy 모델로 성급하게 바꾸지 않습니다.

기본 우선순위:
- graph → `n`, `Edge[]`
- tree → `n`, `Edge[]` 또는 `parent[]`
- linked-list-like sequence → array

---

### Rule 3.7. 문자 보드는 기본적으로 char matrix
입력이 `N`줄의 compact board라면, 알고리즘이 셀 단위라면 `char[][]`를 기본으로 사용합니다.

`String[]`는 줄 전체 문자열 처리가 더 본질적일 때만 사용합니다.

---

### Rule 3.8. query/command는 1급 타입으로 다룬다
명령/질의 줄의 형태가 여러 가지면 raw line text보다 구조화된 모델을 우선합니다.

기본적으로 `tagged_union`을 사용합니다.

---

### Rule 3.9. EOF와 sentinel은 parser concern이다
EOF나 sentinel 종료는 `input.stream`이 표현해야 하며, solve API에 직접 노출하지 않습니다.

---

## 4. 출력 규칙

### Rule 4.1
`output.model`과 `output.presentation`을 항상 분리합니다.

### Rule 4.2
YES/NO 스타일 답은 가능하면 `boolean` logical model + mapping presentation으로 표현합니다.

### Rule 4.3
출력이 동질적이면 굳이 record를 만들지 않습니다.

예:
- 배열 한 줄 출력
- 쿼리 결과 여러 줄 출력
- testcase 결과 여러 줄 출력

---

### Rule 4.4
출력 필드의 의미가 다르면 record를 사용합니다.

예:
- distance + path
- count + list
- min + max

---

### Rule 4.5
raw block string은 escape hatch로만 사용합니다.

즉 구조화가 가능한데도 `String solve(...)` 형태로 몰아넣지 않습니다.

---

## 5. user API 규칙

### Rule 5.1
사용자 API에는 `Object`를 절대 사용하지 않습니다.

### Rule 5.2
입력이 단순하면 `flatten`을 우선합니다.

### Rule 5.3
입력이 너무 넓거나 heterogeneous하면 `input_record`를 사용합니다.

### Rule 5.4
출력이 단순하면 `direct_model`을 우선합니다.

### Rule 5.5
출력이 multi-section이거나 의미가 서로 다른 필드 조합이면 `output_record`를 사용합니다.

---

## 6. 타입 폭 규칙

### Rule 6.1
기본값을 무조건 `int`로 두지 않습니다.

### Rule 6.2
대략 아래 기준을 따릅니다.

- 32-bit 안전 범위 → `int`
- 64-bit 규모 → `long`
- `long` 초과 가능 → `bigint`
- 정확한 decimal precision 필요 → `bigdecimal`

---

## 7. 메타데이터 규칙

### Rule 7.1
1-index / 0-index는 보통 metadata나 normalization 정보로 둡니다.

solve 시그니처에 별도 플래그로 노출하지 않습니다.

### Rule 7.2
graph의 directed/weighted 같은 정보는 보통 logical model 그 자체보다 메모/정규화 정보 쪽이 더 자연스럽습니다.

---

## 8. 안티패턴

### Anti-pattern 8.1
`Input(int n, int[] nums)` where `n` only describes array length.

### Anti-pattern 8.2
`Input(Graph graph)` as default graph representation.

### Anti-pattern 8.3
`Input(TreeNode root)` as default BOJ tree representation.

### Anti-pattern 8.4
`Input(ListNode head)` as default BOJ linked-list representation.

### Anti-pattern 8.5
query stream을 `String[] lines`로만 표현하는 것.

### Anti-pattern 8.6
구조화 가능한 출력을 raw block `String`으로 몰아넣는 것.

### Anti-pattern 8.7
너무 많은 heterogeneous top-level field를 무리하게 flatten하는 것.

---

## 9. 애매할 때의 우선순위

여러 표현이 가능하면 아래 순서로 결정합니다.

1. BOJ-native한가
2. logical model이 더 단순한가
3. user-facing API가 더 읽기 좋은가
4. parser가 deterministic하게 만들기 쉬운가
5. 추후 코드 생성이 쉬운가

그래도 애매하면 conservative한 표현을 택하고 `notes`에 짧게 남깁니다.

---

## 10. 최종 판단 체크리스트

### field를 남길 조건
- 알고리즘 의미가 있다
- 숨기면 문제 의미가 손실된다

### field를 숨길 조건
- 길이/반복 수 설명용이다
- 숨기는 것이 logical model을 더 깔끔하게 만든다

### record를 쓸 조건
- 반복 tuple의 필드 의미가 안정적이다
- top-level bundle이 heterogeneous하다
- output field 이름이 의미를 갖는다

### direct output을 쓸 조건
- scalar / array / matrix 같은 단순 모델이면 충분하다
