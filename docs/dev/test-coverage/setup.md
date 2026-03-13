# setup 테스트 커버리지

> 구현: `src/cli/boj_setup.py` + `src/core/config.py` (Issue #46)
> 디스패처: `src/boj`가 `PYTHONPATH=$ROOT python3 src/cli/boj_setup.py` 호출 (Issue #57)

## 로직 흐름 (단계별)

1. `src/boj`가 `setup` 서브커맨드 감지 → `boj_setup.py` 호출
2. argparse로 옵션 파싱 (`--check`, `--root`, `--lang`, `--username`, `--editor`, `--agent`)
3. `--check`: `check_config()` 출력 → exit 0
4. 비대화형 set 모드: 지정된 옵션 키만 저장 → exit
5. 대화형 모드 (옵션 없음):
   - [1/6] BOJ_SOLUTION_ROOT 경로 입력/저장
   - [2/6] 기본 언어 입력/검증/저장
   - [3/6] 에이전트 선택/저장
   - [4/6] Git 사용자 정보 확인/설정
   - [5/6] BOJ 사용자 ID 입력/저장
   - [6/6] 에디터 명령어 입력/저장
6. `setup_done` 플래그 생성 + 사용법 출력

## 분기 목록 (edge-cases.md S1-S15 매핑)

| ID | 분기 | edge-cases 참조 | 경로 |
|----|------|----------------|------|
| S1 | 최초 실행 (config 없음) → 대화형 6단계 | S1 | happy |
| S2 | 부분 설정 → 기존 값 표시 + "변경하시겠습니까?" | S2 | branches |
| S3 | `~/.config/boj/` 쓰기 권한 없음 → Error: | S3 | errors |
| S4 | git 미설치 → Warning + git 단계 건너뜀 | S4 | branches |
| S5 | clone 실패 → Error 메시지 | S5 | errors |
| S6 | gh CLI 미설치 (repo 생성 선택 시) → 설치 안내 + 재선택 | S6 | branches |
| S7 | `--check` → 현재 설정 표시 | S7 | happy |
| S8 | 설정 완료 후 재실행 → 현재 값 보여주고 변경 확인 | S8 | branches |
| S9 | agent 미설정 → gemini 추천 안내 | S9 | branches |
| S10 | 설정 완료 → `setup_done` 생성 + 사용법 출력 | S10 | happy |
| S11 | Ctrl+C → exit 130 + "설정이 중단되었습니다." | S11 | errors |
| S12 | 알려진 agent 선택 → AGENT_COMMANDS 자동 매핑 | S12 | branches |
| S13 | 기타 agent → 직접 입력 저장 | S13 | branches |
| S14 | 에디터 미입력 → 경고 후 계속 | S14 | branches |
| S15 | 미지원 언어 → 경고 + 재입력 | S15 | branches |

## 분기 → 테스트 매핑 테이블

### Python 단위 테스트 (`tests/unit/test_setup.py`) — 주 테스트

| 분기 | 테스트 클래스 | 설명 |
|------|-------------|------|
| S1, S10 | `TestMainIntegration`, `TestFinishSetup` | 최초 실행, setup_done 생성 |
| S2, S8 | `TestEdgeCases` | 부분 설정, 재실행 |
| S3 | `TestEdgeCases` | 쓰기 권한 없음 |
| S4 | `TestInteractiveGit.test_git_not_installed` | git 미설치 |
| S5 | `TestEdgeCases` | clone 실패 |
| S6 | `TestInteractiveGit.test_gh_create_repo_without_gh` | gh 미설치 |
| S7 | `TestCheckMode`, `TestEdgeCases` | --check 모드 |
| S9 | `TestInteractiveAgent.test_no_agent_recommends_gemini` | agent 미설정 |
| S11 | `TestMainIntegration.test_keyboard_interrupt_exits_gracefully` | Ctrl+C |
| S12 | `TestInteractiveAgent.test_select_known_agent` | 알려진 agent |
| S13 | `TestInteractiveAgent.test_select_custom_agent` | 기타 agent |
| S14 | `TestInteractiveEditor.test_empty_editor_warns` | 에디터 미입력 |
| S15 | `TestInteractiveLang.test_unsupported_lang_shows_warning` | 미지원 언어 |

### Bash 단위 테스트 (`tests/unit/commands/`) — 레거시 회귀 테스트

| 분기 | 파일 | 테스트명 | 비고 |
|------|------|---------|------|
| S7 | `setup_happy.sh` | `check_shows_current_config` | --check 출력 형식 |
| S2 | `setup_branches.sh` | `root_saved_to_config` | root 저장 (직접 파일 작성) |
| S2 | `setup_branches.sh` | `lang_saved_to_config` | lang 저장 (`prog_lang` 키) |
| — | `setup_branches.sh` | `session_saved_to_config` | session 저장 (레거시) |
| S15 | `setup_errors.sh` | `invalid_lang_exits_one` | 미지원 언어 → exit 1 |
| S3 | `setup_errors.sh` | `nonexistent_root_exits_one` | 존재하지 않는 root → exit 1 |

### Python 통합 테스트 (`tests/integration/test_boj_setup_py.py`)

subprocess로 `boj setup` CLI를 호출하여 전체 흐름을 검증한다.
