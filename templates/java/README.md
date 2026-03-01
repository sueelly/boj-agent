# Java 템플릿 (Java 11+)

- **ParseAndCallSolve.java**: 문제별 `test/Parse.java`가 구현할 인터페이스.
- **Test.java**: 공통 테스트 러너. `test/test_cases.json`을 읽고 Parse로 파싱 후 Solution에 전달.
- **Solution.java**, **submit/Submit.java**: 스텁/참고용.

문제 폴더에는 `Solution.java`, `test/Parse.java`, `test/test_cases.json`을 생성하고, `boj run` 시 이 디렉터리의 ParseAndCallSolve, Test와 함께 컴파일·실행된다.
