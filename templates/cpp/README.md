# C++ 템플릿 (C++17)

- **test_runner.cpp**: 공통 러너. `test/test_cases.json`을 읽고, 문제가 제공하는 `parse_and_solve(input)` 호출 후 비교.
- **계약**: 문제 폴더의 `test/parse_and_solve.cpp` (및 필요 시 solution.cpp)가 `std::string parse_and_solve(const std::string& input)` 를 구현. 이 함수 내부에서 입력을 파싱하고 solution 로직을 호출해 결과 문자열을 반환.

빌드: `test_runner.cpp` + 문제의 `solution.cpp` + `test/parse_and_solve.cpp` 를 함께 컴파일. 실행 시 cwd는 문제 폴더, `test/test_cases.json` 경로 사용.
