# run 테스트 커버리지

> Python 마이그레이션 (`src/core/run.py` + `src/cli/boj_run.py`) 기준.
> 기존 Bash `run.sh`의 R1-R10 분기를 모두 유지하고, 리소스 제한 기능을 추가한다.

## 로직 흐름 (단계별)

1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드 (`config_get("prog_lang")` 등)
3. `--lang` 옵션 파싱
4. 언어 유효성 검사 (`validate_lang`)
5. 문제 폴더 탐색 (`find_problem_dir`)
6. `README.md`에서 시간/메모리 제한 파싱 (`parse_resource_limits`)
7. `test/test_cases.json` 존재 확인
8. `test_cases.json` 정규화 (id/description 없는 케이스 자동 부여)
9. 언어별 실행 명령 조립 (`build_run_command`)
10. 리소스 제한 적용하여 테스트 실행 (`execute_tests`)
    - 시간 초과 → `TimeoutError`
    - 메모리 초과 → `MemoryLimitError`
11. 결과 출력 + exit code 반환

## 분기 목록

### 기존 분기 (R1-R12)

| ID | 분기 | 경로 | 테스트 레벨 |
|----|------|------|------------|
| R1 | java 정상 실행 (2/2 passed) | happy | unit + integration + e2e |
| R2 | python 정상 실행 (2/2 passed) | happy | unit + integration + e2e |
| R3 | test_cases.json id 없음 → 자동 부여 | branches | unit |
| R4 | `--lang` 플래그로 언어 override | branches | integration |
| R5 | 일부 테스트만 통과 (1/2 passed) | branches | integration |
| R6 | 문제 폴더 없음 → exit 1 + Error: | errors | unit + integration |
| R7 | Solution.java 없음 → exit 1 + Error: | errors | integration |
| R8 | test/test_cases.json 없음 → exit 1 | errors | unit + integration |
| R9 | 미지원 언어 (cpp) → exit 1 + Error: | errors | integration |
| R10 | 컴파일 에러 있는 Solution.java → exit 1 | errors | integration |
| R11 | Solution.java 런타임 예외 → 해당 테스트 실패, 계속 | errors | integration |
| R12 | `prog_lang` 미지원 값 → exit 1 | errors | integration |

### 새 분기 (R13-R17) — 리소스 제한

| ID | 분기 | 경로 | 테스트 레벨 |
|----|------|------|------------|
| R13 | README.md에서 시간 제한 파싱 (예: "2 초" → 2.0) | branches | unit |
| R14 | README.md에서 메모리 제한 파싱 (예: "256 MB" → 256) | branches | unit |
| R15 | README.md 없음 → 기본값 사용 (시간 5초, 메모리 256MB) | branches | unit |
| R16 | 테스트 실행 시간 초과 → Timeout 에러 출력 | errors | unit + integration |
| R17 | 테스트 메모리 초과 → Memory 에러 출력 | errors | unit + integration |

## 분기 → 테스트 매핑 테이블

### Unit 테스트 (`tests/unit/test_run.py`)

| 분기 | 테스트명 |
|------|---------|
| R1 | test_build_run_command_java_when_valid_setup |
| R2 | test_build_run_command_python_when_valid_setup |
| R3 | test_normalize_fills_missing_id_and_description |
| R6 | test_run_raises_when_problem_dir_missing |
| R8 | test_run_raises_when_test_cases_missing |
| R13 | test_parse_time_limit_from_readme |
| R14 | test_parse_memory_limit_from_readme |
| R15 | test_parse_limits_returns_defaults_when_readme_missing |
| R16 | test_execute_raises_timeout_when_exceeded |
| R17 | test_execute_raises_memory_error_when_exceeded |

### Integration 테스트 (`tests/integration/test_run_integration.py`)

| 분기 | 테스트명 |
|------|---------|
| R1 | test_run_java_passes_two_of_two |
| R2 | test_run_python_passes_two_of_two |
| R4 | test_run_lang_override_flag |
| R5 | test_run_partial_pass_shows_count |
| R6 | test_run_exits_one_when_problem_dir_missing |
| R7 | test_run_exits_one_when_solution_missing |
| R8 | test_run_exits_one_when_test_cases_missing |
| R9 | test_run_exits_one_when_unsupported_lang |
| R10 | test_run_exits_one_when_compile_error |
| R16 | test_run_reports_timeout_when_exceeded |
| R17 | test_run_reports_memory_error_when_exceeded |

### E2E 테스트 (`tests/e2e/test_run_e2e.py`)

| 분기 | 테스트명 |
|------|---------|
| R1 | test_boj_run_java_full_flow |
| R2 | test_boj_run_python_full_flow |
| — | test_boj_run_exit_code_zero_on_all_pass |
| — | test_boj_run_stdout_format_emoji_and_count |
