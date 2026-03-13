# Parse Pattern Catalog

이 문서는 `problem.spec.json` 의 입력 모델을 `Parse.java` 코드로 내릴 때 자주 쓰는 패턴을 정리한 카탈로그다.

상위 규칙은 `spec-to-parse-rules.md` 를 따른다.

---

## Pattern 1. Single scalar

### Spec shape
- `input.model.kind = scalar`
- `topLevelMode = single`

### Typical Parse.java shape
```java
int n = in.nextInt();
return String.valueOf(sol.solve(n));
```

### Notes
- string/char/bigint/bigdecimal 도 동일한 구조
- 가장 단순한 패턴

---

## Pattern 2. Fixed scalar tuple

### Spec shape
- top-level logical input is a small record
- `userApi.inputStyle = flatten`

### Typical Parse.java shape
```java
int n = in.nextInt();
int k = in.nextInt();
int result = sol.solve(n, k);
return String.valueOf(result);
```

### Notes
- 파라미터 순서는 `userApi.flattenedParameters` 를 따른다
- 임의 reorder 금지

---

## Pattern 3. One-dimensional array with count local

### Spec shape
- `locals` contains `n`
- `input.model.kind = array`
- `lengthFrom = n`

### Typical Parse.java shape
```java
int n = in.nextInt();
int[] nums = new int[n];
for (int i = 0; i < n; i++) nums[i] = in.nextInt();
long result = sol.solve(nums);
return String.valueOf(result);
```

### Notes
- count-only local 은 solve 에 넘기지 않을 수 있다
- spec 의 `flattenedParameters` 가 `nums` 하나면 그대로 call

---

## Pattern 4. Header plus array

### Spec shape
- locals: `n`
- model: record or flatten parameters including `k`, `target`, etc.

### Typical Parse.java shape
```java
int n = in.nextInt();
int target = in.nextInt();
int[] arr = new int[n];
for (int i = 0; i < n; i++) arr[i] = in.nextInt();
int result = sol.solve(target, arr);
return String.valueOf(result);
```

### Notes
- count-only `n` 은 hidden 가능
- semantic scalar (`target`) 은 유지

---

## Pattern 5. Numeric matrix

### Spec shape
- `kind = matrix`
- `rowsFrom = n`, `colsFrom = m`
- `rowEncoding = token_row`

### Typical Parse.java shape
```java
int n = in.nextInt();
int m = in.nextInt();
int[][] matrix = new int[n][m];
for (int i = 0; i < n; i++) {
    for (int j = 0; j < m; j++) {
        matrix[i][j] = in.nextInt();
    }
}
return String.valueOf(sol.solve(matrix));
```

### Notes
- dimensions 이 solve 에 보이면 함께 넘긴다
- 보이지 않으면 내부 파싱용 local 로만 사용

---

## Pattern 6. Character grid / board

### Spec shape
- `kind = matrix`
- `cellType = char`
- `rowEncoding = char_line`

### Typical Parse.java shape
```java
int n = in.nextInt();
int m = in.nextInt();
char[][] board = new char[n][];
for (int i = 0; i < n; i++) {
    board[i] = in.next().toCharArray();
}
return String.valueOf(sol.solve(board));
```

### Notes
- 공백 없는 줄이면 `next()`
- 공백 포함 자유 텍스트면 `nextLine()` 기반으로 바꿔야 함

---

## Pattern 7. Repeated semantic tuples

### Spec shape
- top-level array of record
- example: `Point[]`, `Edge[]`, `Interval[]`

### Typical Parse.java shape
```java
int n = in.nextInt();
Point[] points = new Point[n];
for (int i = 0; i < n; i++) {
    int x = in.nextInt();
    int y = in.nextInt();
    points[i] = new Point(x, y);
}
long result = sol.solve(points);
return String.valueOf(result);
```

### Notes
- record field 순서대로 local 을 읽고 생성

---

## Pattern 8. Graph edge list

### Spec shape
- locals: `n`, `m`
- model contains `n` and `Edge[]` or `WeightedEdge[]`

### Typical Parse.java shape
```java
int n = in.nextInt();
int m = in.nextInt();
WeightedEdge[] edges = new WeightedEdge[m];
for (int i = 0; i < m; i++) {
    edges[i] = new WeightedEdge(in.nextInt(), in.nextInt(), in.nextInt());
}
long result = sol.solve(n, edges);
return String.valueOf(result);
```

### Notes
- 그래프는 raw edge 유지
- `Graph` 로 바로 만들지 않음

---

## Pattern 9. Parent array / tree-like sequence

### Spec shape
- top-level array or record containing `parent[]`

### Typical Parse.java shape
```java
int n = in.nextInt();
int[] parent = new int[n + 1];
for (int i = 2; i <= n; i++) parent[i] = in.nextInt();
return String.valueOf(sol.solve(parent));
```

### Notes
- exact index convention 은 spec.notes 또는 normalization 을 따른다
- 파싱 규칙이 불충분하면 추측 금지

---

## Pattern 10. Multiple testcases

### Spec shape
- `topLevelMode = testcases`
- testcase count local exists
- logical model usually array of `TestCase`

### Typical Parse.java shape
```java
int t = in.nextInt();
TestCase[] cases = new TestCase[t];
for (int i = 0; i < t; i++) {
    int n = in.nextInt();
    int[] arr = new int[n];
    for (int j = 0; j < n; j++) arr[j] = in.nextInt();
    cases[i] = new TestCase(arr);
}
long[] result = sol.solve(cases);
return formatOnePerLine(result);
```

### Notes
- testcase 내부 local 은 각 반복에서 새로 읽는다
- 출력도 보통 one-per-line

---

## Pattern 11. Query / command stream

### Spec shape
- `kind = array`
- element = `tagged_union`
- `readAs = lines` or mixed token/line

### String-tag variant example
```java
int q = in.nextInt();
in.nextLine();
Query[] queries = new Query[q];
for (int i = 0; i < q; i++) {
    String line = in.nextLine();
    StringTokenizer st = new StringTokenizer(line);
    String op = st.nextToken();
    switch (op) {
        case "push":
            queries[i] = new Push(Integer.parseInt(st.nextToken()));
            break;
        case "pop":
            queries[i] = new Pop();
            break;
        default:
            throw new IllegalArgumentException("Unknown op: " + op);
    }
}
int[] result = sol.solve(queries);
return formatOnePerLine(result);
```

### Int-tag variant example
```java
int q = in.nextInt();
Query[] queries = new Query[q];
for (int i = 0; i < q; i++) {
    int type = in.nextInt();
    switch (type) {
        case 1:
            queries[i] = new Update(in.nextInt(), in.nextInt());
            break;
        case 2:
            queries[i] = new RangeQuery(in.nextInt(), in.nextInt());
            break;
        default:
            throw new IllegalArgumentException("Unknown type: " + type);
    }
}
```

### Notes
- line mode 가 필요하면 `nextLine()` 전환을 신경써야 함
- command variant 는 구조적으로 표현해야 함

---

## Pattern 12. Read until EOF

### Spec shape
- `topLevelMode = eof`

### Typical Parse.java shape
```java
List<Pair> list = new ArrayList<>();
while (in.hasNext()) {
    int a = in.nextInt();
    int b = in.nextInt();
    list.add(new Pair(a, b));
}
Pair[] pairs = list.toArray(new Pair[0]);
String[] result = sol.solve(pairs);
return formatOnePerLine(result);
```

### Notes
- EOF 는 파서 concern
- solve 는 이미 수집된 배열/리스트를 받는다

---

## Pattern 13. Sentinel termination

### Spec shape
- `topLevelMode = sentinel`
- sentinel value explicitly given

### Typical Parse.java shape
```java
List<Pair> list = new ArrayList<>();
while (true) {
    int a = in.nextInt();
    int b = in.nextInt();
    if (a == 0 && b == 0) break;
    list.add(new Pair(a, b));
}
Pair[] pairs = list.toArray(new Pair[0]);
String[] result = sol.solve(pairs);
return formatOnePerLine(result);
```

### Notes
- sentinel 비교 규칙은 spec 을 그대로 따른다
- tuple sentinel / scalar sentinel / line sentinel 을 구분해야 한다

---

## Pattern 14. Free-form text / line-preserved input

### Spec shape
- tokenMode = `line` or `mixed`
- model often `String` or `String[]`

### Typical Parse.java shape
```java
String text = input;
return sol.solve(text);
```

or

```java
List<String> lines = new ArrayList<>();
while (in.hasNext()) {
    lines.add(in.nextLine());
}
String[] arr = lines.toArray(new String[0]);
return formatOnePerLine(sol.solve(arr));
```

### Notes
- whitespace preservation matters
- token splitting 금지

---

## Pattern 15. Mixed block input

### Spec shape
- 여러 section 이 순차적으로 등장
- top-level model is usually record

### Typical Parse.java shape
```java
int n = in.nextInt();
int[] arr = new int[n];
for (int i = 0; i < n; i++) arr[i] = in.nextInt();

int q = in.nextInt();
Query[] queries = new Query[q];
for (int i = 0; i < q; i++) {
    int type = in.nextInt();
    queries[i] = new Query(type, in.nextInt(), in.nextInt());
}

Input data = new Input(arr, queries);
Output out = sol.solve(data);
return formatOutput(out);
```

### Notes
- mixed block 는 wrapper record 가 더 자연스러운 경우가 많다
- parse 순서를 절대 바꾸면 안 된다

---

## Pattern 16. Big integer / precision-sensitive input

### Spec shape
- scalar/array/matrix with `bigint` or `bigdecimal`

### Typical Parse.java shape
```java
BigInteger n = new BigInteger(in.next());
return sol.solve(n).toString();
```

or

```java
BigDecimal value = new BigDecimal(in.next());
BigDecimal result = sol.solve(value);
return result.toPlainString();
```

### Notes
- exact decimal semantics 가 필요하면 `toPlainString()` 우선 고려

---

## Pattern 17. input_record call bridge

### Spec shape
- logical model top-level is `Input`
- `userApi.inputStyle = input_record`

### Typical Parse.java shape
```java
int n = in.nextInt();
int[] arr = new int[n];
for (int i = 0; i < n; i++) arr[i] = in.nextInt();
Input data = new Input(arr);
long result = sol.solve(data);
return String.valueOf(result);
```

### Notes
- flatten 과 달리 record 생성이 필요

---

# Quick defaults

문제가 애매할 때 기본값:

- one scalar -> scalar read + direct solve
- `N + N values` -> read local count + array
- board -> char[][]
- graph -> `n` + `Edge[]`
- queries -> tagged union array
- multiple cases -> array of logical cases
- EOF/sentinel -> parser concern only
