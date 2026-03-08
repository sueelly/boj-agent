# run 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드 (boj_lang 등)
3. `--lang` 옵션 파싱
4. 언어 유효성 검사 (`boj_validate_lang`)
5. 문제 폴더 탐색 (`boj_require_problem_dir`)
6. test/test_cases.json 존재 확인
7. test_cases.json 정규화 (id 없는 케이스 자동 부여)
8. 언어별 실행 분기 (java / python / cpp / c / 기타)
   - Java: Parse.java + Template 존재 확인 → javac → java Test
   - Python: solution.py 존재 확인 → test_runner.py
   - cpp/c: 미구현 → exit 1
   - 기타: 미지원 → exit 1

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| R1 | java 정상 실행 (2/2 passed) | happy |
| R2 | python 정상 실행 (2/2 passed) | happy |
| R3 | test_cases.json id 없음 → 자동 부여 | branches |
| R4 | `--lang` 플래그로 언어 override | branches |
| R5 | 일부 테스트만 통과 (1/2 passed) | branches |
| R6 | 문제 폴더 없음 → exit 1 + Error: | errors |
| R7 | Solution.java 없음 → exit 1 + Error: | errors |
| R8 | test/test_cases.json 없음 → exit 1 | errors |
| R9 | 미지원 언어 (cpp) → exit 1 + Error: | errors |
| R10 | 컴파일 에러 있는 Solution.java → exit 1 | errors |

## 분기 → 테스트 매핑 테이블
| 분기 | 파일 | 테스트명 |
|------|------|---------|
| R1 | tests/unit/commands/run_happy.sh | java_two_of_two_pass |
| R2 | tests/unit/commands/run_happy.sh | python_two_of_two_pass |
| R3 | tests/unit/commands/run_branches.sh | test_cases_no_id_auto_assigned |
| R4 | tests/unit/commands/run_branches.sh | lang_override_flag |
| R5 | tests/unit/commands/run_branches.sh | partial_pass_shows_count |
| R6 | tests/unit/commands/run_errors.sh | missing_problem_dir |
| R7 | tests/unit/commands/run_errors.sh | missing_solution_file |
| R8 | tests/unit/commands/run_errors.sh | missing_test_cases_json |
| R9 | tests/unit/commands/run_errors.sh | unsupported_lang_cpp |
| R10 | tests/unit/commands/run_errors.sh | compile_error_reported |
