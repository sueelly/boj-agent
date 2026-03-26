# C 템플릿 (C11)

- **test_runner.c**: 공통 러너. `test/test_cases.json`을 읽고, 문제가 제공하는 `parse_and_solve(input, output, size)` 호출 후 비교.
- **계약**: 문제 폴더의 `test/parse_and_solve.c`가 다음을 구현:
  - `void parse_and_solve(const char* input, char* output, size_t out_size);`
  - input: test 케이스 입력 문자열, output: 결과를 넣을 버퍼 (null 종료), out_size: 버퍼 크기.

빌드: test_runner.c + 문제의 solution.c + test/parse_and_solve.c. 실행 시 cwd는 문제 폴더.
