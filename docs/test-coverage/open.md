# open 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드
3. 옵션 파싱 (--editor)
4. 문제 폴더 탐색
5. 폴더 없으면 boj make 자동 실행 후 에디터 열기 시도
6. 에디터 명령 실행 (boj_open_editor)
   - BOJ_EDITOR 환경변수 > 설정 파일 > 기본값(code)
   - fallback: cursor → vim → nano 순서

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| OP1 | 기존 문제 폴더 → 에디터 호출 | happy |
| OP2 | BOJ_EDITOR 환경변수 사용 | branches |
| OP3 | --editor 플래그 override | branches |
| OP4 | 문제 폴더 없음 → exit 1 | errors |
| OP5 | 에디터 없음 → exit 1 | errors |

## 분기 → 테스트 매핑 테이블
| 분기 | 파일 | 테스트명 |
|------|------|---------|
| OP1 | tests/unit/commands/open_happy.sh | opens_existing_problem_dir |
| OP2 | tests/unit/commands/open_branches.sh | editor_env_var_used |
| OP3 | tests/unit/commands/open_branches.sh | editor_flag_overrides |
| OP4 | tests/unit/commands/open_errors.sh | missing_problem_dir |
| OP5 | tests/unit/commands/open_errors.sh | no_editor_available |
