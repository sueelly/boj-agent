# submit 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드
3. 옵션 파싱 (--lang, --open, --force)
4. 언어별 파일 확장자 결정
5. Solution 파일 존재 확인
6. submit/ 폴더 생성
7. 기존 Submit 파일 존재 확인 (--force 아니면 BojError)
8. 언어별 Submit 생성
   - Java: imports 추출 + Main 클래스 + Solution/Parse 병합
   - Python: 헤더 + Solution 내용 + main 블록
   - C++: bits/stdc++.h + Solution 내용 + main
   - C: stdio.h + Solution 내용 + main
9. Java: javac 컴파일 검증
10. --open: 제출 페이지 브라우저 열기

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| SB1 | Java Submit.java 생성 | happy |
| SB2 | 생성된 Submit.java javac 통과 | happy |
| SB3 | Parse.java 있으면 병합 | branches |
| SB4 | Parse.java 없어도 Submit 생성 (TODO 스텁) | branches |
| SB5 | --force → 기존 Submit.java 덮어씀 | branches |
| SB6 | --lang python → submit/Submit.py 생성 | branches |
| SB7 | --lang cpp → submit/Submit.cpp 생성 | branches |
| SB8 | Solution.java 없음 → exit 1 | errors |
| SB9 | 미지원 언어 → exit 1 | errors |
| SB10 | Submit 이미 있고 --force 없음 → exit 1 | errors |

## 분기 → 테스트 매핑 테이블

### 단위 테스트 (`tests/unit/test_submit.py`)
| 분기 | 클래스 | 테스트 메서드 |
|------|--------|-------------|
| SB1 | TestGenerateJavaSubmit | test_with_parse |
| SB1 | TestGenerateJavaSubmit | test_with_fixture |
| SB1 | TestGenerateSubmit | test_java_submit_end_to_end |
| SB2 | TestCompileCheck | test_compile_success |
| SB2 | TestCompileCheck | test_compile_failure |
| SB3 | TestGenerateJavaSubmit | test_with_parse |
| SB4 | TestGenerateJavaSubmit | test_without_parse |
| SB5 | TestGenerateSubmit | test_existing_submit_no_force_raises_error |
| SB5 | TestGenerateSubmit | test_existing_submit_with_force_overwrites |
| SB6 | TestGeneratePythonSubmit | test_basic_generation |
| SB6 | TestGenerateSubmit | test_python_submit_end_to_end |
| SB7 | TestGenerateCppSubmit | test_removes_existing_includes |
| SB7 | TestGenerateSubmit | test_cpp_submit_end_to_end |
| SB8 | TestGenerateSubmit | test_missing_solution_raises_error |
| SB9 | TestGenerateSubmit | test_unsupported_language_raises_error |
| SB10 | TestGenerateSubmit | test_existing_submit_no_force_raises_error |
| — | TestGenerateJavaSubmit | test_inner_classes_preserved |
| — | TestGenerateJavaSubmit | test_duplicate_imports_deduplicated |
| — | TestGenerateCSubmit | test_basic_generation |
| — | TestGenerateSubmit | test_creates_submit_directory |

### 통합 테스트 (`tests/integration/test_submit_py.py`)
| 분기 | 클래스 | 테스트 메서드 |
|------|--------|-------------|
| SB1 | TestSubmitPyIntegration | test_java_submit_generates_file |
| SB3 | TestSubmitCoreIntegration | test_java_with_parse_fixture |
| SB4 | TestSubmitCoreIntegration | test_java_without_parse |
| SB5 | TestSubmitPyIntegration | test_force_flag_overwrites |
| SB6 | TestSubmitPyIntegration | test_python_submit_generates_file |
| SB6 | TestSubmitCoreIntegration | test_python_with_fixture |
| SB8 | TestSubmitPyIntegration | test_missing_solution_returns_error |
| SB8 | TestSubmitPyIntegration | test_missing_problem_dir_returns_error |
| SB10 | TestSubmitPyIntegration | test_force_flag_overwrites (두 번째 생성 시) |
| — | TestSubmitPyIntegration | test_open_flag_accepted |
