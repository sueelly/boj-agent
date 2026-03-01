# 백준 문제 풀이 환경 생성 지시

이 지시문을 따르면 백준 알고리즘 문제 풀이용 폴더와 파일을 일관된 형식으로 생성할 수 있습니다.  
**반드시 웹 검색을 통해 해당 백준 문제 페이지의 실제 내용을 확인한 후 작성할 것. 기억에 의존하지 말 것.**

## 설정·템플릿 참조

- **언어**: `~/.config/boj/lang` 또는 환경변수 `BOJ_LANG` (없으면 기본값 `java`). 이 언어에 맞는 확장자와 규칙으로 생성.
- **계약(인터페이스)**: 생성하는 Parse(또는 동일 역할 파일)는 **테스트 러너와 호환**되어야 한다. 각 언어별 계약은 프로젝트의 `templates/<lang>/` 에 있음. 예: Java는 `ParseAndCallSolve` 인터페이스, Python은 `parse_and_solve(sol, input: str) -> str` 등. 해당 디렉터리의 인터페이스·주석을 참고해 동일한 시그니처로 생성할 것.

---

## 1. 폴더 생성

- **폴더명**: `[문제번호]-[문제제목]` (예: `10808-알파벳-개수`)
- 띄어쓰기는 `-`로 대체, 제목은 소문자·영문/한글 혼용 가능

---

## 2. 생성할 파일

### 2.1 README.md

백준 문제 페이지에서 가져온 내용을 아래 형식으로 작성 (기억에 의존하는 게 아니라 반드시 web으로 검색):

```html
<h2><a href="https://www.acmicpc.net/problem/문제번호">문제번호번: 문제제목</a></h2>
<p><strong>시간 제한:</strong> X초 | <strong>메모리 제한:</strong> XMB</p>
<hr>

<h3>문제</h3>
<p>문제 설명...</p>

<h3>입력</h3>
<p>입력 설명...</p>

<h3>출력</h3>
<p>출력 설명...</p>

<h3>예제 입력 1</h3>
<pre>예제 입력</pre>

<h3>예제 출력 1</h3>
<pre>예제 출력</pre>
```

(예제가 여러 개면 예제 2, 3... 동일 형식으로 추가)

---

### 2.2 Solution.* (언어별 확장자)

- **역할**: 순수 알고리즘만 담당. **파싱된 값을 파라미터로 받고**, 파싱 로직은 넣지 않음.
- **메서드**: `solve(...)` — 문제에 맞는 파라미터와 반환 타입으로 정의.
- **내부**: 구현은 비워두거나 `TODO`만 둠 (사용자가 직접 구현).

**Java 예시**:

```java
public class Solution {
    /**
     * [문제 한 줄 요약]
     *
     * @param n  (설명)
     * @param arr (설명)
     * @param x  (설명)
     * @return (설명)
     */
    public int solve(int n, int[] arr, int x) {
        // TODO: 여기에 알고리즘 구현
        return 0;
    }
}
```

- 파라미터는 문제마다 다름 (예: `int a, int b` / `String s` / `int n, int[][] edges`).
- **String input 하나로 받지 말 것.** Parse에서 파싱한 값을 개별 인자로 받음.

---

### 2.3 test/ 폴더

**test/Parse.\***  
- 테스트 시 JSON input 문자열을 파싱해 `Solution.solve(...)`에 넘기고, 반환값을 문자열로 돌려주는 구현.
- Java의 경우 `ParseAndCallSolve` 인터페이스의 `parseAndCallSolve(Solution sol, String input)` 구현.
- 입력 형식은 문제 설명에 맞게 한 문제마다 다르게 작성.

**test/test_cases.json**  
- README.md에 적힌 예제 입출력을 JSON으로 정의. `input`은 전체 입력 문자열(줄 구분은 `\n`), `expected`는 기대 출력 문자열.

```json
{
  "testCases": [
    {
      "id": 1,
      "description": "예제 1",
      "input": "9\n5 12 7 10 9 1 2 3 11\n13",
      "expected": "3"
    }
  ]
}
```

---

### 2.4 생성하지 않는 파일

- Main.java, Test.java, run.sh, test.sh 등은 생성하지 않음. 테스트는 루트에서 `boj run [문제번호]` 등으로 실행한다고 가정.

---

## 3. 중요 규칙

1. **Solution**: 파싱 로직 없이, Parse에서 넘겨준 값만으로 `solve(...)` 구현 가능하도록 시그니처 설계.
2. **test/Parse**: `parseAndCallSolve`(또는 동일 역할)에서 입력 문자열 → Solution 호출 → 결과 문자열 반환.
3. **test/test_cases.json**: 문제 예제를 그대로 옮기고, 필요 시 엣지 케이스 추가 가능.

---

## 4. 환경 생성 완료 후 (선택 안내)

파일 생성이 끝나면 사용자가 해당 문제 폴더만 에디터 루트로 열어 풀 수 있도록 안내할 수 있음. 예:

- "해당 문제 폴더에서 `code .`(또는 사용 중인 에디터)를 실행하면, 그 폴더만 루트로 열립니다."

---

**사용자 요청 예**: "백준 4949번 문제 풀이 환경 만들어줘" / "https://www.acmicpc.net/problem/3273 이 문제 환경 만들어줘"

이때 위 규칙에 따라 `[번호]-[제목]/` 폴더와 README.md, Solution.*, test/Parse.*, test/test_cases.json 을 생성하면 됨.
