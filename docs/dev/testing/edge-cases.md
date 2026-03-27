# Edge Case Matrix — boj CLI 명령어별 엣지 케이스

> 이 문서는 구현 및 테스트의 기준입니다. 새 명령어 추가 시 이 문서도 함께 업데이트하세요.
>
> **형식**: Command | 카테고리 | 케이스 | 기대 동작 (에러 메시지 / 자동복구 / 중단 여부)

---

## 공통 (모든 명령어)

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| C1 | config | `setup_done` 플래그 없음 | "설정이 완료되지 않았습니다. `boj setup`을 진행합니다." → setup 실행 | 아니오 | 예 |
| C2 | config | `solution_root` 경로가 존재하지 않음 | "solutions_root가 비어(또는 깨져) 있습니다. `boj setup`을 실행하거나 설정을 확인하세요." | 아니오 | 예 |
| C3 | config | `boj_agent_root` 경로가 존재하지 않음 | "agent_root가 비어(또는 깨져) 있습니다. `boj setup`을 실행하거나 설정을 확인하세요." | 아니오 | 예 |
| C4 | git | git repo 아닌 디렉터리에서 실행 | git 관련 명령(commit) 시 `Error: git 저장소가 아닙니다.` | 아니오 | 예 (commit만) |
| C5 | 파일시스템 | `solution_root` 에 읽기 권한 없음 | `Error: 레포에 접근할 수 없습니다 (권한 부족).` | 아니오 | 예 |

---

## `boj setup`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| S1 | config | 최초 실행 (설정 없음) | 대화형 프롬프트로 root, 언어, agent, git, username, 에디터 순서로 안내 | N/A | 아니오 |
| S2 | config | 부분 설정 (일부 파일만 있음) | 누락된 항목만 물어봄, 기존 값 유지 | 예 | 아니오 |
| S3 | config | `~/.config/boj/` 쓰기 권한 없음 | `Error: 설정 디렉터리에 쓸 수 없습니다: ~/.config/boj/` | 아니오 | 예 |
| S4 | git | git 미설치 환경 | `Warning: git을 찾을 수 없습니다. git 설치 후 다시 실행하세요.` | 아니오 | 부분 (git 단계만) |
| S5 | git | git repo URL clone 실패 | `Error: 저장소 clone에 실패했습니다. URL을 확인하세요.` | 아니오 | 부분 (git 단계만) |
| S6 | git | `gh` CLI 미설치 (새 repo 생성 선택 시) | gh 설치 안내 + 다른 옵션으로 fallback | 아니오 | 부분 (git 단계만) |
| S7 | config | `boj setup --check` 실행 | 현재 설정 상태 표시 (ok/missing/invalid 구분) | N/A | 아니오 |
| S8 | config | 이미 설정 완료 후 재실행 | 현재 값 보여주고 "수정하시겠습니까? (y/N)" 확인 | N/A | 아니오 |
| S9 | agent | agent 미설정 | "agent가 없으면 사용이 불가합니다. 무료 gemini를 추천합니다." 안내 | N/A | 아니오 |
| S10 | config | 설정 완료 | `~/.config/boj/setup_done` 파일 생성 + 사용법/설정법 출력 | N/A | 아니오 |
| S11 | input | Ctrl+C (KeyboardInterrupt) | 정상 종료 (exit code 130), "설정이 중단되었습니다." 메시지 | N/A | 예 |
| S12 | agent | 알려진 agent 선택 (claude 등) | AGENT_COMMANDS 자동 매핑 + AGENT_INSTALL 설치 안내 | N/A | 아니오 |
| S13 | agent | 기타 agent 선택 | 직접 명령어 입력 → 그대로 저장 | N/A | 아니오 |
| S14 | editor | 에디터 미입력 | "boj open 명령어를 사용할 수 없습니다" 안내 후 계속 | N/A | 아니오 |
| S15 | lang | 미지원 언어 입력 | "미지원" 경고 + 재입력 요청 | N/A | 아니오 |

---

## `boj make`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| M1 | 문제데이터 | 문제 번호가 존재하지 않음 (BOJ 404) | `Error: 문제 번호 99999를 찾을 수 없습니다. (HTTP 404)` | 아니오 | 예 |
| M2 | 네트워크 | 네트워크 없음 (BOJ 접근 불가) | `Error: BOJ에 연결할 수 없습니다. 네트워크를 확인하세요.` | 아니오 | 예 |
| M3 | 파일시스템 | 문제 폴더 이미 존재 (`-f` 없음) | `Error: '4949-괄호의-값' 폴더가 이미 존재합니다. 덮어쓰려면 -f 옵션을 사용하세요.` | 아니오 | 예 |
| M3a | 파일시스템 | 문제 폴더 이미 존재 (`-f` 있음) | 기존 폴더 덮어쓰기 후 정상 진행 | 예 | 아니오 |
| M4 | 파일시스템 | `solution_root` 쓰기 권한 없음 | `Error: 문제 폴더를 생성할 수 없습니다 (권한 없음).` | 아니오 | 예 |
| M5 | 문제데이터 | 문제 본문에 이미지 있음 (`--image-mode reference`) | 이미지를 원본 URL 참조로 README에 포함 | N/A | 아니오 |
| M6 | 문제데이터 | 이미지 다운로드 실패 (`--image-mode download`) | `Warning: 이미지 다운로드 실패 (URL). reference 모드로 대체.` | reference로 대체 | 아니오 |
| M7 | 문제데이터 | 이미지 URL이 외부 도메인 | reference 모드: 원본 URL 사용. download 모드: 시도 후 실패 시 경고 | 경고 후 계속 | 아니오 |
| M8 | 템플릿 | 요청 언어 템플릿 없음 (`--lang rust`) | `Error: 'rust' 템플릿이 없습니다. 지원 언어: java python` | 아니오 | 예 |
| M9 | config | `setup_done` 플래그 없음 | C1 공통 가드에서 처리 (디스패처 레벨). make 고유 동작 없음. | 예 | 아니오 |
| M10 | subprocess | 에이전트 exit nonzero + stderr 있음 | `Error: spec 생성 실패` + exit code + stderr 포함 | 아니오 | 예 |
| M10a | subprocess | 에이전트 exit 0 + spec 미생성 + stdout 있음 | `Error: spec 생성 실패` + stdout 포함 | 아니오 | 예 |
| M10b | subprocess | 에이전트 exit nonzero + stderr 비어있음 | `Error: spec 생성 실패` + exit code 포함 | 아니오 | 예 |
| M10c | subprocess | 에이전트 exit 0 + spec 미생성 + 출력 없음 | `Error: spec 생성 실패` (기본 메시지만) | 아니오 | 예 |
| M11 | 문제데이터 | 생성 후 자체검증: README ↔ 문제 불일치 | `Warning: README 내용이 문제와 다를 수 있습니다. 확인하세요.` | 아니오 | 아니오 |
| M12 | spec | `problem.spec.json` 생성 실패 (파일 없음 / JSON 파싱 에러) | `Error: spec 생성에 실패했습니다. boj make <N> -f 로 재시도하세요.` | 아니오 | 예 |
| M13 | 파일시스템 | `--keep-artifacts` 사용 | 모든 파일 유지 (화이트리스트 정리 스킵) | N/A | 아니오 |
| M13a | 파일시스템 | 화이트리스트 정리 (기본) | README.md, Solution.*, test/, artifacts/(이미지만) 유지. 나머지(.omc, problem.json 등) 삭제 | N/A | 아니오 |
| M14 | skeleton | 에이전트 stdout에 유효한 JSON manifest | `{"files": {...}}` 파싱 → 파일 생성 (Solution, Parse, test_cases.json 등) | N/A | 아니오 |
| M14a | skeleton | 에이전트 stdout이 빈 문자열 / JSON 아님 | Solution 미생성 Warning + test_cases.json fallback 생성 | fallback | 아니오 |
| M14b | skeleton | 에이전트 실패 (exit nonzero) | Solution 미생성 Warning + test_cases.json fallback 생성 (samples 기반) | fallback | 아니오 |
| M15 | skeleton | test_cases.json fallback 생성 | problem.json의 samples에서 결정론적으로 `{"testCases": [...]}` 생성 | 예 | 아니오 |
| M15a | skeleton | problem.json에 samples 없음 | fallback 생성 스킵 (test_cases.json 미생성) | 아니오 | 아니오 |
| M16 | skeleton | template_vars 치환 | `{{LANG}}`, `{{EXT}}`, `{{SUPPORTS_PARSE}}` 등 프롬프트 내 플레이스홀더를 Python에서 치환 후 에이전트에 전달 | N/A | 아니오 |
| M17 | UX | 에디터 선오픈 (README 직후) | README 생성 직후 `open_editor` 호출 — spec/skeleton 대기 중 문제 확인 가능 | N/A | 아니오 |
| M18 | UX | `--no-open` + 선오픈 | `--no-open` 이면 선오픈도 하지 않는다 (open_editor 미호출) | N/A | 아니오 |
| M19 | UX | 에디터 미설정 + 선오픈 | 에디터 미설정이면 선오픈도 하지 않는다 (open_editor 미호출) | N/A | 아니오 |
| M20 | config | `make_auto_open=false` + `--no-open` 미지정 | `make_auto_open` 설정이 "false"이면 에디터 자동 열기 하지 않는다 (open_editor 미호출) | N/A | 아니오 |
| M21 | config | `make_auto_open=true` (기본값) 또는 미설정 | `make_auto_open`이 "true"(또는 미설정)이면 기존 동작 유지 (에디터 열기) | N/A | 아니오 |

---

## `boj run`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| R1 | 파일시스템 | 문제 폴더 없음 | `Error: '4949'로 시작하는 폴더를 찾을 수 없습니다. 존재하는 문제: ...` | 아니오 | 예 |
| R2 | 파일시스템 | `test/test_cases.json` 없음 | `Error: test/test_cases.json이 없습니다. make를 먼저 실행하세요.` | 아니오 | 예 |
| R3 | 파일시스템 | `Solution.java` 없음 | `Error: Solution.java를 찾을 수 없습니다.` | 아니오 | 예 |
| R4 | 파일시스템 | `test/Parse.java` 없음 | `Error: test/Parse.java를 찾을 수 없습니다.` | 아니오 | 예 |
| R5 | 템플릿 | `templates/java/Test.java` 없음 | `Error: 테스트 러너 템플릿이 없습니다 (prog_lang=java).` | 아니오 | 예 |
| R6 | 문제데이터 | `test_cases.json` 형식 오류 (JSON 파싱 불가) | `Error: test_cases.json 파싱 실패. JSON 형식을 확인하세요.` | 아니오 | 예 |
| R7 | 문제데이터 | `test_cases.json` 에 testCases 배열 없음 | `Warning: 테스트 케이스가 없습니다. (테스트 케이스 0개)` | 아니오 | 아니오 (0개로 실행) |
| R8 | 문제데이터 | 테스트 케이스에 `id` 없음 | id 자동 부여 (1, 2, ...) 후 정상 실행 | 예 | 아니오 |
| R9 | 문제데이터 | 테스트 케이스에 `description` 없음 | `"예제 N"` 기본값으로 대체 후 정상 실행 | 예 | 아니오 |
| R10 | 파일시스템 | Solution.java 컴파일 오류 | javac 에러 메시지 그대로 출력 | 아니오 | 예 |
| R11 | 파일시스템 | Solution.java 런타임 예외 | 해당 테스트 케이스 `❌ 에러: NullPointerException` 출력 후 계속 | 아니오 | 아니오 (계속) |
| R12 | config | `prog_lang` 이 지원하지 않는 값 | `Error: 지원하지 않는 언어: fortran. 지원: java python` | 아니오 | 예 |
| R13 | 리소스 | README.md에서 시간 제한 파싱 (예: "2 초") | 파싱된 값(초 단위)을 subprocess timeout으로 적용 | N/A | 아니오 |
| R14 | 리소스 | README.md에서 메모리 제한 파싱 (예: "256 MB") | 파싱된 값(MB 단위)을 resource.setrlimit으로 적용 | N/A | 아니오 |
| R15 | 리소스 | README.md 없음 (시간/메모리 제한 파싱 불가) | 기본값 사용 (시간 5초, 메모리 256MB) + `Warning: README.md를 찾을 수 없습니다. 기본 제한을 사용합니다.` | 예 | 아니오 |
| R16 | 리소스 | 테스트 실행 시간 초과 | `Error: 시간 초과 (제한: N초)` 출력 후 전체 실행 중단 (exit 1). 전체 프로세스 단위 timeout 적용. | 아니오 | 예 |
| R17 | 리소스 | 테스트 메모리 초과 | `Error: 메모리 초과 (제한: N MB)` 출력 후 전체 실행 중단 (exit 1). 전체 프로세스 단위 제한 적용. | 아니오 | 예 |

---

## `boj commit`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| CT1 | 파일시스템 | 문제 폴더 없음 | `Error: '4949'로 시작하는 폴더가 없습니다.` | 아니오 | 예 |
| CT2 | git | git repo 아님 | `Error: git 저장소가 아닙니다.` | 아니오 | 예 |
| CT3 | git | 변경사항 없음 (nothing to commit) | `Warning: 커밋할 변경사항이 없습니다.` | 아니오 | 예 (정상 종료) |
| CT4 | 인증 | BOJ username 미설정 | 통계 조회 스킵, `[BOJ 통계: username 없음]` 메시지에 포함 후 커밋 | 예 | 아니오 |
| CT5 | 인증 | BOJ username이 존재하지 않거나 일치하지 않음 | `[BOJ 통계: 조회 실패 — username 확인 필요]` 포함 후 커밋 | 예 | 아니오 |
| CT6 | 네트워크 | BOJ 통계 조회 timeout | 3초 후 timeout, `[BOJ 통계: 조회 실패]` 포함 후 커밋 | 예 | 아니오 |
| CT7 | 문제데이터 | 해당 문제 Accepted 제출 없음 | `[BOJ 통계: Accepted 제출 없음]` 포함 후 커밋 | 예 | 아니오 |
| CT8 | git | git user.email 미설정 | `Error: git user.email이 설정되지 않았습니다. boj setup 또는 git config 실행.` | 아니오 | 예 |
| CT9 | git | staged 변경사항 이미 있음 | 기존 staged 파일 + 문제 폴더 파일 합산 후 확인 메시지 | 사용자 확인 | 사용자 선택 |

---

## `boj open`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| O1 | 파일시스템 | 문제 폴더 없음 | make 먼저 실행 안내 + `boj make 4949` 명령 제안 | 아니오 | 예 |
| O2 | config | 에디터 CLI 없음 (cursor/code 모두 없음) | `Error: 에디터를 찾을 수 없습니다. --editor 또는 ~/.config/boj/editor 설정.` | 아니오 | 예 |
| O3 | config | `--editor vim` 사용 | `vim /path/to/problem` 실행 | N/A | 아니오 |
| O4 | config | 설정 에디터가 PATH에 없음 | `Error: 설정된 에디터 'mycustom'을 찾을 수 없습니다.` | 아니오 | 예 |

---

## `boj review`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| RV1 | 파일시스템 | 문제 폴더 없음 | `Error: '4949'로 시작하는 문제 폴더가 없습니다.` | 아니오 | 예 |
| RV2 | 파일시스템 | `Solution.java` 없음 | `Warning: Solution 파일이 없습니다. 리뷰할 코드가 없을 수 있습니다.` | 아니오 | 아니오 (계속) |
| RV3 | config | 에이전트 설정 없음 | 에디터 열기 + "리뷰해줘" 클립보드 복사 fallback | 예 | 아니오 |
| RV4 | config | 에이전트 오류 | `Error: 에이전트 실행 실패.` + 수동 리뷰 안내 | 아니오 | 예 |

---

## `boj submit`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| SB1 | 파일시스템 | 문제 폴더 없음 | `Error: '4949'로 시작하는 폴더가 없습니다.` | 아니오 | 예 |
| SB2 | 파일시스템 | `Solution.java` 없음 | `Error: Solution.java가 없습니다. 먼저 풀이를 작성하세요.` | 아니오 | 예 |
| SB3 | 파일시스템 | `test/Parse.java` 없음 | `Warning: Parse.java가 없습니다. stdin 직접 입력 방식으로 생성합니다.` | stdin 방식으로 대체 | 아니오 |
| SB4 | 파일시스템 | `submit/` 폴더 없음 | 자동 생성 | 예 | 아니오 |
| SB5 | 파일시스템 | `Submit.java` 이미 존재 | `Warning: Submit.java가 이미 있습니다. 덮어쓰시겠습니까? (y/N)` | 사용자 확인 | 사용자 선택 |
| SB6 | 문제데이터 | Solution에 inner class 있음 | inner class 포함하여 Submit.java 생성 | 예 | 아니오 |
| SB7 | 문제데이터 | Solution에 외부 라이브러리 import | `Warning: 외부 라이브러리는 BOJ에서 지원하지 않습니다: import com.example.*` | 아니오 | 아니오 (경고만) |
| SB8 | config | 언어 미설정 | java 기본값 사용, `Warning: 언어 미설정. java 사용.` | 예 | 아니오 |
| SB9 | 파일시스템 | 생성된 Submit.java 컴파일 검증 실패 | `Warning: Submit.java 컴파일 확인 실패. 수동으로 확인하세요.` | 아니오 | 아니오 (경고만) |
| SB10 | config | `--open` 이지만 브라우저 없음 | `Warning: 브라우저를 열 수 없습니다. URL: https://www.acmicpc.net/submit/4949` | URL 출력 | 아니오 |
| SB11 | config | `submit_open` 설정 없음 (기본값) | 기본값 `true` → 제출 후 브라우저 자동 열기 | N/A | 아니오 |
| SB12 | config | `submit_open=false` 설정 | 브라우저 자동 열기 안 함 | N/A | 아니오 |
| SB13 | config | `submit_open=false` + `--open` 플래그 | `--open` 우선 → 브라우저 열기 | N/A | 아니오 |
| SB14 | config | `submit_open=true` + `--no-open` 플래그 | `--no-open` 우선 → 브라우저 안 열기 | N/A | 아니오 |

---

## `boj reset`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| RS1 | UX | 확인 프롬프트 (--force 없음) | "Solution 파일을 초기 상태로 되돌리겠습니까? (y/N)" 표시, N이면 중단 | 아니오 | 사용자 선택 |
| RS2 | UX | --force 플래그 사용 | 확인 프롬프트 생략하고 즉시 실행 | N/A | 아니오 |
| RS3 | 파일시스템 | --no-backup 없음 (기본) | reset 전 Solution 파일을 `Solution.java.bak` 으로 복사 | 예 | 아니오 |
| RS4 | git | submit/ 디렉터리 존재 시 | submit/ 디렉터리 전체 삭제 (cleanup_submit) | 예 | 아니오 |
| RS5 | 파일시스템 | Solution 파일 없음 | `Error: Solution 파일을 찾을 수 없습니다.` | 아니오 | 예 |
| RS6 | git | git repo 아님 | `Error: git 저장소가 아닙니다.` | 아니오 | 예 |

---

## `config` (Python 모듈 — `src/core/config.py`)

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| CF1 | 우선순위 | 환경변수 설정됨 + 파일도 존재 | 환경변수 값 반환 (파일 무시) | N/A | 아니오 |
| CF2 | 우선순위 | 환경변수 없음 + 파일 존재 | 파일 값 반환 | N/A | 아니오 |
| CF3 | 우선순위 | 환경변수 없음 + 파일 없음 | 기본값 반환 | N/A | 아니오 |
| CF4 | 파일시스템 | `~/.config/boj/` 디렉터리 없음 (write 시) | 자동 생성 후 저장 | 예 | 아니오 |
| CF5 | 파일시스템 | `~/.config/boj/` 쓰기 권한 없음 | `Error: 설정 디렉터리에 쓸 수 없습니다: ~/.config/boj/` | 아니오 | 예 |
| CF6 | 파일시스템 | config 파일 내용이 빈 문자열 | 기본값 반환 (빈 문자열은 미설정으로 취급) | N/A | 아니오 |
| CF7 | 파일시스템 | config 파일에 trailing whitespace/newline | strip 후 반환 | 예 | 아니오 |
| CF8 | setup_done | `~/.config/boj/setup_done` 파일 존재 | 설정 완료로 판단 | N/A | 아니오 |
| CF9 | setup_done | `~/.config/boj/setup_done` 파일 없음 | "설정이 완료되지 않았습니다. `boj setup`을 진행합니다." 안내 | 아니오 | 예 |
| CF10 | 경로검증 | `boj_agent_root` 경로 존재하지 않음 | "agent_root가 비어(또는 깨져) 있습니다. `boj setup`을 실행하거나 설정을 확인하세요." | 아니오 | 예 |
| CF11 | 경로검증 | `solution_root` 경로 존재하지 않음 | "solutions_root가 비어(또는 깨져) 있습니다. `boj setup`을 실행하거나 설정을 확인하세요." | 아니오 | 예 |
| CF12 | 언어검증 | 지원 언어 (`java`, `python`) | 검증 통과 | N/A | 아니오 |
| CF13 | 언어검증 | 미지원 언어 (`fortran`) | `Error: 지원하지 않는 언어: fortran. 지원: java python` | 아니오 | 예 |
| CF14 | 언어검증 | `languages.json` 파일 없음/파싱 실패 | `Error: languages.json을 읽을 수 없습니다.` | 아니오 | 예 |
| CF15 | agent | 알려진 agent 이름 (`claude`, `cursor` 등) | 매핑된 실행 명령어 반환 | N/A | 아니오 |
| CF16 | agent | 알 수 없는 agent 이름 | 사용자 입력 명령어 그대로 저장 (기타 취급) | N/A | 아니오 |
| CF17 | git | `git config --global user.name/email` 설정됨 | 값 반환 | N/A | 아니오 |
| CF18 | git | `git config --global user.name/email` 미설정 | 빈 문자열 반환 (호출자가 처리) | N/A | 아니오 |
| CF19 | git | git 미설치 | `Error: git을 찾을 수 없습니다.` | 아니오 | 예 |
| CF20 | check | `boj_check_config()` 호출 | 전체 설정 상태 포맷팅 출력 (key: value, ok/missing/invalid 구분, S7과 동일) | N/A | 아니오 |
| CF21 | config | `BOJ_CONFIG_DIR` 환경변수로 디렉터리 오버라이드 | 해당 경로를 설정 디렉터리로 사용 | N/A | 아니오 |

---

## `install` (설치 스크립트 — `scripts/install.py`)

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| IN1 | 파일시스템 | `~/bin` 없음 | 자동 생성 | 예 | 아니오 |
| IN2 | 파일시스템 | `~/.config/boj/` 없음 | 자동 생성 | 예 | 아니오 |
| IN3 | 파일시스템 | `~/.local/share/boj-agent/` 이미 존재 | `--force` 없으면 확인 요청 | 사용자 선택 | 사용자 선택 |
| IN4 | 파일시스템 | self-move (src == dest) | 복사 스킵, 현재 위치 사용 | 예 | 아니오 |
| IN5 | 파일시스템 | 쓰기 권한 없음 | `Error: 권한이 없습니다.` | 아니오 | 예 |
| IN6 | PATH | `~/bin` 이 PATH에 없음 | 셸 rc 수정 안내 메시지 (계속 진행) | 아니오 | 아니오 |
| IN7 | subprocess | `boj setup` 실패 | `Warning: setup 실패. 수동 실행하세요.` | 아니오 | 아니오 |
| IN8 | 파일시스템 | `src/boj` 없음 (깨진 clone) | `Error: boj-agent 저장소가 아닙니다.` | 아니오 | 예 |

## client (CL1-CL5)

| # | 카테고리 | 케이스 | 기대 동작 | 복구 가능 | 비정상 종료 |
|---|----------|--------|-----------|-----------|------------|
| CL1 | HTTP | 정상 HTML 파싱 | problem dict 반환 | 예 | 아니오 |
| CL2 | HTTP | 404 응답 | `Error: 문제를 찾을 수 없습니다` + exit(1) | 아니오 | 예 |
| CL3 | HTTP | 403 응답 | `Error: BOJ 접근 거부` + exit(1) | 아니오 | 예 |
| CL4 | HTTP | 네트워크 타임아웃 | `Error: BOJ 페이지 가져오기 실패` + exit(1) | 아니오 | 예 |
| CL5 | 테스트 | BOJ_CLIENT_TEST_HTML 설정 | 로컬 파일에서 읽기, HTTP 미사용 | 예 | 아니오 |

## normalizer (NR1-NR5)

| # | 카테고리 | 케이스 | 기대 동작 | 복구 가능 | 비정상 종료 |
|---|----------|--------|-----------|-----------|------------|
| NR1 | 입력 | 정상 problem dict | HTML README 문자열 반환 | 예 | 아니오 |
| NR2 | 입력 | samples 빈 배열 | 예제 섹션 없는 README | 예 | 아니오 |
| NR3 | 입력 | input_html/output_html 없음 | 빈 섹션으로 생성 | 예 | 아니오 |
| NR4 | 입력 | 이미지 포함 HTML | img 태그 그대로 유지 | 예 | 아니오 |
| NR5 | 입력 | 특수문자 제목 | HTML 엔티티 보존 | 예 | 아니오 |

---

## 요약: 에러 메시지 규칙

| 수준 | 접두사 | 종료 코드 | 용도 |
|------|--------|-----------|------|
| Error | `Error:` | 1 (비정상) | 계속 진행 불가, 사용자 조치 필요 |
| Warning | `Warning:` | 0 (계속) | 진행 가능하나 주의 필요 |
| Info | (없음) | 0 | 정상 진행 상황 안내 |

## 자동복구 정책

- **setup_done 없음**: 디스패처에서 `boj setup` 자동 실행 (모든 명령어 공통, C1)
- **BOJ 통계 실패**: commit은 진행, 메시지에 실패 이유 포함
- **이미지 다운로드 실패**: reference 모드로 대체
- **id/description 없음**: 자동 보완 후 실행
- **submit/ 폴더 없음**: 자동 생성
- **폴더 이미 존재**: `-f` 옵션으로 덮어쓰기 (미지정 시 에러)

*최종 업데이트: 2026-03-27*

