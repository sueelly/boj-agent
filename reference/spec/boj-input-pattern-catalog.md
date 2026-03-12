# BOJ Input Pattern Catalog

이 문서는 BOJ 문제 설명을 `input.model`로 정규화할 때 자주 나오는 **대표 입력 패턴**을 정리한 카탈로그입니다.

상위 규칙은 `boj-spec-rules.md`가 우선합니다.

---

## Pattern 1. 단일 스칼라

### 정의
입력이 값 하나인 경우입니다.

### 대표 형태
- 정수 1개
- 문자열 1개
- long 1개
- decimal 1개

### 권장 logical model
- scalar

### 권장 user API
```java
int solve(int n)
String solve(String s)
long solve(long x)
```

### 예시 문제군
- 팩토리얼
- 자리수 계산
- 문자열 뒤집기

### 비고
값 하나를 굳이 `Input` record로 감싸지 않는 것이 보통 더 읽기 좋습니다.

---

## Pattern 2. 고정 개수 스칼라 튜플

### 정의
소수의 scalar가 각자 의미를 가진 채 함께 주어지는 경우입니다.

### 대표 형태
- `N K`
- `A B C`
- `R C`

### 권장 logical model
- 작은 record 또는 flatten

### 권장 user API
```java
int solve(int n, int k)
long solve(int a, int b, int c)
```

### 예시 문제군
- 범위 설정
- 격자 크기
- 파라미터 조합

### 주의
의미가 다른 값들을 `int[] params`처럼 뭉개지 않습니다.

---

## Pattern 3. 1차원 배열

### 정의
길이 정보 뒤에 같은 종류 값이 연속으로 나오는 경우입니다.

### 대표 형태
- `N` 다음 `N`개 정수
- `N` 다음 `N`개 문자열

### 권장 logical model
- array

### 권장 user API
```java
long solve(int[] nums)
String solve(String[] words)
```

### 기본 규칙
`N`이 배열 길이만 설명하면 `locals`에 두고 logical model에서는 숨깁니다.

### `N`을 남기는 경우
- `N` 자체가 로직 의미를 가짐
- 숨기면 문제 의미가 흐려짐

### 예시 문제군
- 정렬
- prefix sum
- LIS
- 좌표 압축

---

## Pattern 4. 헤더 + 배열

### 정의
배열과 함께 의미 있는 scalar header가 같이 주어지는 경우입니다.

### 대표 형태
- `N K` + 배열
- `target` + 배열
- `budget` + 값 목록

### 권장 logical model
- 의미 있는 scalar + array
- flatten이 읽기 좋으면 flatten

### 권장 user API
```java
int solve(int k, int[] nums)
long solve(int target, int[] arr)
long solve(int n, int target, int[] arr)
```

### 핵심 기준
- 길이만 알려주면 숨긴다
- 의미가 있으면 남긴다

---

## Pattern 5. 2차원 수치 행렬

### 정의
`N M` 뒤에 `N`줄의 숫자 row가 오는 형태입니다.

### 권장 logical model
- matrix

### 권장 user API
```java
int solve(int[][] matrix)
long solve(int n, int m, int[][] matrix)
```

### 예시 문제군
- DP table
- 비용 행렬
- 인접 행렬
- 지도 숫자판

### 주의
행/열 크기가 단순 파싱 정보면 숨길 수 있습니다.

---

## Pattern 6. 문자 그리드 / compact board

### 정의
공백 없이 이어진 문자 줄들이 보드를 구성하는 경우입니다.

### 대표 형태
- `10101`
- `.#..#`
- `RGB`

### 권장 logical model
- `char[][]`

### 대안
- `String[]` if whole-line semantics matter more than cell-level behavior

### 권장 user API
```java
int solve(char[][] board)
```

### 선택 기준
- 셀 단위 탐색 / BFS / DFS / 시뮬레이션 → `char[][]`
- 줄 단위 문자열 처리 → `String[]`

### 예시 문제군
- 미로
- 섬 개수
- 색종이/체스판 계열

---

## Pattern 7. 반복되는 고정 구조

### 정의
같은 의미의 고정 폭 튜플이 여러 줄 반복되는 경우입니다.

### 권장 logical model
- named record array

### 대표 record 예시
```java
record Point(int x, int y) {}
record Interval(int start, int end) {}
record Job(int deadline, int reward) {}
```

### 권장 user API
```java
long solve(Point[] points)
int solve(Interval[] intervals)
long solve(Job[] jobs)
```

### 예시 문제군
- 좌표들
- 구간들
- 작업 목록
- 사람 정보
- 아이템 목록

### 핵심 이유
`int[][]`보다 field 의미가 선명합니다.

---

## Pattern 8. 그래프: 간선 리스트

### 정의
BOJ에서 가장 흔한 그래프 입력 형태입니다.

### 대표 형태
- `N M`
- 다음 `M`줄에 `u v`
- 또는 `u v w`

### 권장 logical model
- `n` + `Edge[]`
- weighted면 `WeightedEdge[]`

### 권장 user API
```java
int solve(int n, Edge[] edges)
long solve(int n, WeightedEdge[] edges)
```

### 예시 record
```java
record Edge(int from, int to) {}
record WeightedEdge(int from, int to, int weight) {}
```

### 왜 raw edge가 기본인가
그래프 객체를 바로 만들면 아래가 숨겨지기 쉽습니다.
- index base
- 방향성
- self-loop
- multi-edge
- weightedness

### 권장 방향
logical model은 raw input에 가깝게 두고, helper 변환은 나중 단계로 미룹니다.

---

## Pattern 9. 트리

### 정의
BOJ 트리는 보통 LeetCode식 root serialization이 아니라 간선/부모 배열 형태로 옵니다.

### 권장 logical model
- `int n, Edge[] edges`
- 또는 `int[] parent`

### 권장 user API
```java
int solve(int n, Edge[] edges)
long solve(int[] parent)
```

### 왜 `TreeNode root`를 기본으로 두지 않는가
BOJ 원문과 멀어지고, deterministic한 생성이 어려워질 수 있기 때문입니다.

### 예외
문제 표현이 정말로 root object를 자연스럽게 유도할 때만 사용합니다.

---

## Pattern 10. 연결 리스트 유사 입력

### 정의
실제로는 sequence 문제인데 linked-list helper로 바꾸고 싶어지는 경우입니다.

### BOJ 기본 권장
- array

### 권장 user API
```java
int solve(int[] nums)
```

### 이유
BOJ는 대개 linked structure serialization을 직접 주지 않습니다.

### 예외
문제가 명시적으로 linked node 관계를 deterministic하게 구성하게 할 때만 `ListNode`를 고려합니다.

---

## Pattern 11. 여러 테스트케이스

### 정의
첫 줄 `T` 이후 같은 구조가 반복되는 경우입니다.

### 권장 logical model
- `TestCase[]`
- 또는 testcase logical unit array

### 권장 user API
```java
long[] solve(TestCase[] cases)
List<String> solve(TestCase[] cases)
```

### 예시 record
```java
record TestCase(int[] nums) {}
```

### 이유
테스트케이스 반복은 stream concern이지 solve API concern이 아닙니다.

---

## Pattern 12. Query / Command Stream

### 정의
명령 줄의 형태가 여러 종류인 경우입니다.

### 대표 형태
- `push X`
- `pop`
- `top`
- `1 x`
- `2 l r`

### 권장 logical model
- `Query[]`
- element는 가능하면 `tagged_union`

### 권장 user API
```java
List<Integer> solve(Query[] queries)
int[] solve(Query[] queries)
```

### 대표 예시
```java
enum Op { PUSH, POP, TOP, SIZE, EMPTY }
record Query(Op op, Integer x) {}
```

또는 일반화된 형태:

```java
record Query(String op, int[] args, String[] sArgs) {}
```

### 이유
에이전트가 가장 자주 실수하는 유형입니다.
raw text보다 구조화된 표현이 훨씬 안정적입니다.

---

## Pattern 13. EOF까지 읽기

### 정의
입력이 EOF까지 반복되는 경우입니다.

### 권장 logical model
- 반복 logical case 배열

### 권장 user API
```java
long[] solve(Pair[] pairs)
List<String> solve(TestCase[] cases)
```

### 대표 record
```java
record Pair(int a, int b) {}
```

### 이유
EOF는 parser concern이므로 solve에 노출하지 않습니다.

---

## Pattern 14. Sentinel 종료형

### 정의
특정 sentinel이 나오면 입력이 끝나는 경우입니다.

### 대표 형태
- `0 0`
- `#`
- `END`

### 권장 logical model
- 반복 logical case 배열

### 권장 user API
```java
long[] solve(Pair[] pairs)
```

### 이유
sentinel 체크는 parser의 책임입니다.

---

## Pattern 15. 줄 보존이 중요한 자유 텍스트

### 정의
공백, 전체 줄, 빈 줄 자체가 의미를 가지는 경우입니다.

### 권장 logical model
- `String`
- `String[]`

### 권장 user API
```java
String solve(String text)
List<String> solve(String[] lines)
```

### 예시 문제군
- 문장 분석
- 여러 줄 텍스트 가공
- line-sensitive parsing

### 주의
이 경우 `tokenMode`를 `line` 또는 `mixed`로 정확히 잡아야 합니다.

---

## Pattern 16. 혼합형 블록 입력

### 정의
서로 다른 블록이 순차적으로 등장하는 경우입니다.

### 예시
- 초기 배열 + 쿼리
- 그래프 + 추가 조건 + 질의
- 사전 블록 + 탐색 블록

### 권장 logical model
- top-level record

### 권장 user API
```java
List<Integer> solve(Input input)
Output solve(Input input)
```

### 대표 예시
```java
record Input(int[] arr, Query[] queries) {}
record Input(int n, int[] weights, Edge[] edges, Query[] queries) {}
```

### 이유
heterogeneous input은 무리하게 flatten하면 가독성이 급격히 나빠집니다.

---

## Pattern 17. 큰 수 / 정밀도형

### 정의
`long`을 넘을 수 있거나 exact decimal precision이 필요한 경우입니다.

### 권장 logical model
- `bigint`
- `bigdecimal`

### 권장 user API
```java
String solve(BigInteger n)
BigDecimal solve(BigDecimal value)
```

### 타입 폭 가이드
- 32-bit safe → `int`
- 64-bit scale → `long`
- beyond `long` → `bigint`
- exact decimal precision → `bigdecimal`

---

# Supplemental Patterns

## Supplemental 1. 병렬 배열

### 정의
서로 연관된 정보가 여러 배열로 나뉘어 들어옵니다.

### 권장
정말 병렬 구조가 본질이면 유지합니다.
하지만 index 기준 pairing이 semantic tuple이면 record array 승격을 고려합니다.

예:
```java
record Interval(int start, int end) {}
```

---

## Supplemental 2. 1-index / 0-index 정보

### 권장
solve 시그니처에 노출하기보다 normalization metadata나 note로 처리합니다.

---

## Supplemental 3. Graph metadata

### 권장
방향성 / 가중치 같은 정보는 raw input을 유지한 채 note나 normalization에 남기는 편이 안전합니다.

---

## Supplemental 4. 문자열 + 숫자 혼합 명령

### 예시
- `add apple 3`
- `find banana`

### 권장 logical model
- query tagged union
- 또는 `Query(String op, String key, Integer value)` 같은 구조

---

## Supplemental 5. 여러 블록이 순차적으로 등장

### 권장
top-level record로 각 block을 명시적으로 분리합니다.

---

# Quick Defaults

애매하면 아래 기본값을 우선합니다.

- single value → scalar
- repeated semantic tuple → record array
- graph → `n`, `Edge[]`
- tree → `n`, `Edge[]` 또는 `parent[]`
- board → `char[][]`
- command stream → `Query[]`
- repeated cases → `TestCase[]`
- EOF/sentinel → parser concern only
- large numbers → conservative widening
