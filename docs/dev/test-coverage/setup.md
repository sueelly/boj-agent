# setup 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT 인수 수신
2. 옵션 파싱 (--check)
3. --check: boj_check_config 출력 → exit 0
4. 대화형 설정:
   - [1] BOJ_ROOT 경로 입력/저장
   - [2] 기본 언어 입력/검증/저장
   - [3] git 사용자 정보 확인
   - [4] BOJ 세션 쿠키 입력/저장
   - [5] 에이전트 명령 입력/저장

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| ST1 | --check → 현재 설정 출력 | happy |
| ST2 | --root /tmp → config 파일에 저장 | branches |
| ST3 | --lang python → config에 저장 | branches |
| ST4 | --session abc → config에 저장 | branches |
| ST5 | 유효하지 않은 언어 → exit 1 + Error: | errors |
| ST6 | 존재하지 않는 --root → exit 1 | errors |

## 분기 → 테스트 매핑 테이블
| 분기 | 파일 | 테스트명 |
|------|------|---------|
| ST1 | tests/unit/commands/setup_happy.sh | check_shows_current_config |
| ST2 | tests/unit/commands/setup_branches.sh | root_saved_to_config |
| ST3 | tests/unit/commands/setup_branches.sh | lang_saved_to_config |
| ST4 | tests/unit/commands/setup_branches.sh | session_saved_to_config |
| ST5 | tests/unit/commands/setup_errors.sh | invalid_lang_exits_one |
| ST6 | tests/unit/commands/setup_errors.sh | nonexistent_root_exits_one |
