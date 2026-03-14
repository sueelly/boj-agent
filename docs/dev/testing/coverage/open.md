# open 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드
3. 옵션 파싱 (--editor)
4. 문제 폴더 탐색 (config에서 solution_root 읽기)
5. 에디터 결정 (--editor flag > config > 기본값)
6. 에디터 PATH 존재 확인 (shutil.which)
7. subprocess.Popen으로 에디터 실행

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| OP1 | 기존 문제 폴더 → 에디터 호출 | happy |
| OP2 | config에서 에디터 읽기 | branches |
| OP3 | --editor 플래그 override | branches |
| OP4 | 문제 폴더 없음 → exit 1 | errors |
| OP5 | 에디터 없음 (빈 문자열/None/PATH 없음) → exit 1 | errors |

## 분기 → 테스트 매핑 테이블

### 단위 테스트 (`tests/unit/test_open.py`)
| 분기 | 클래스 | 테스트 메서드 |
|------|--------|-------------|
| OP1 | TestFindOrCreateProblemDir | test_returns_path_when_dir_exists |
| OP1 | TestOpenInEditor | test_calls_popen_with_editor_and_dir |
| OP1 | TestOpenProblem | test_opens_existing_dir_with_editor |
| OP2 | TestOpenProblem | test_uses_config_editor_when_no_override |
| OP2 | TestFindOrCreateProblemDir | test_uses_config_when_base_dir_none |
| OP3 | TestOpenProblem | test_editor_override_takes_precedence |
| OP3 | TestOpenInEditor | test_handles_editor_with_args |
| OP4 | TestFindOrCreateProblemDir | test_raises_when_dir_missing |
| OP4 | TestFindOrCreateProblemDir | test_raises_message_suggests_make |
| OP4 | TestOpenProblem | test_raises_when_dir_missing |
| OP5 | TestOpenInEditor | test_raises_when_editor_empty |
| OP5 | TestOpenInEditor | test_raises_when_editor_none |
| OP5 | TestOpenInEditor | test_raises_when_editor_whitespace_only |
| OP5 | TestOpenInEditor | test_raises_when_editor_not_in_path |
| OP5 | TestOpenProblem | test_raises_when_editor_not_found |

### 통합 테스트 (`tests/integration/test_open_py.py`)
| 분기 | 클래스 | 테스트 메서드 |
|------|--------|-------------|
| OP1 | TestOpenHappy | test_open_existing_problem_dir |
| OP3 | TestOpenHappy | test_open_with_editor_flag |
| OP4 | TestOpenErrors | test_exits_one_when_problem_dir_missing |
| OP5 | TestOpenErrors | test_exits_one_when_editor_not_in_path |
| OP5 | TestOpenErrors | test_exits_one_when_editor_empty |
