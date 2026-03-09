# Edge Case Matrix — boj CLI 명령어별 엣지 케이스

> 이 문서는 구현 및 테스트의 기준입니다. 새 명령어 추가 시 이 문서도 함께 업데이트하세요.
>
> **형식**: Command | 카테고리 | 케이스 | 기대 동작 (에러 메시지 / 자동복구 / 중단 여부)

---

## 공통 (모든 명령어)

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| C1 | config | `~/.config/boj/root` 없음 | `Error: boj 레포 루트를 찾을 수 없습니다. setup을 먼저 실행하세요.` | 아니오 | 예 |
| C2 | config | `BOJ_ROOT` 경로가 존재하지 않음 | `Error: BOJ_ROOT 경로가 유효하지 않습니다: /invalid/path` | 아니오 | 예 |
| C3 | config | `templates/java/Test.java` 누락 | `Error: 템플릿 파일이 없습니다. boj-agent 레포가 올바른지 확인하세요.` | 아니오 | 예 |
| C4 | git | git repo 아닌 디렉터리에서 실행 | git 관련 명령(commit) 시 `Error: git 저장소가 아닙니다.` | 아니오 | 예 (commit만) |
| C5 | 파일시스템 | `BOJ_ROOT` 에 읽기 권한 없음 | `Error: 레포에 접근할 수 없습니다 (권한 부족).` | 아니오 | 예 |

---

## `boj setup`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| S1 | config | 최초 실행 (설정 없음) | 대화형 프롬프트로 git, BOJ 세션, 에이전트 순서로 안내 | N/A | 아니오 |
| S2 | config | 부분 설정 (일부 파일만 있음) | 누락된 항목만 물어봄, 기존 값 유지 | 예 | 아니오 |
| S3 | config | `~/.config/boj/` 쓰기 권한 없음 | `Error: 설정 디렉터리에 쓸 수 없습니다: ~/.config/boj/` | 아니오 | 예 |
| S4 | 인증 | BOJ 세션 쿠키 형식 오류 | `Warning: 세션 형식이 올바르지 않습니다. 다시 입력하세요.` | 재입력 요청 | 아니오 |
| S5 | 인증 | BOJ 세션으로 연결 테스트 실패 | `Warning: BOJ 연결 확인 실패. 저장은 하되 나중에 확인하세요.` | 저장 후 경고 | 아니오 |
| S6 | git | git 미설치 환경 | `Warning: git을 찾을 수 없습니다. git 설치 후 다시 실행하세요.` | 아니오 | 부분 (git 단계만) |
| S7 | config | `boj setup --check` 실행 | 현재 설정 상태 표시 (ok/missing/invalid 구분) | N/A | 아니오 |
| S8 | config | 이미 설정 완료 후 재실행 | 현재 값 보여주고 "수정하시겠습니까? (y/N)" 확인 | N/A | 아니오 |

---

## `boj make`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| M1 | 문제데이터 | 문제 번호가 존재하지 않음 (BOJ 404) | `Error: 문제 번호 99999를 찾을 수 없습니다. (HTTP 404)` | 아니오 | 예 |
| M2 | 네트워크 | 네트워크 없음 (BOJ 접근 불가) | `Error: BOJ에 연결할 수 없습니다. 네트워크를 확인하세요.` | 아니오 | 예 |
| M3 | 파일시스템 | 문제 폴더 이미 존재 | `Warning: '4949-괄호의-값' 폴더가 이미 있습니다. 덮어쓰시겠습니까? (y/N)` | 사용자 확인 | 사용자 선택 |
| M4 | 파일시스템 | BOJ_ROOT 쓰기 권한 없음 | `Error: 문제 폴더를 생성할 수 없습니다 (권한 없음).` | 아니오 | 예 |
| M5 | 문제데이터 | 문제 본문에 이미지 있음 (`--image-mode reference`) | 이미지를 원본 URL 참조로 README에 포함 | N/A | 아니오 |
| M6 | 문제데이터 | 이미지 다운로드 실패 (`--image-mode download`) | `Warning: 이미지 다운로드 실패 (URL). reference 모드로 대체.` | reference로 대체 | 아니오 |
| M7 | 문제데이터 | 이미지 URL이 외부 도메인 | reference 모드: 원본 URL 사용. download 모드: 시도 후 실패 시 경고 | 경고 후 계속 | 아니오 |
| M8 | 템플릿 | 요청 언어 템플릿 없음 (`--lang rust`) | `Error: 'rust' 템플릿이 없습니다. 지원 언어: java python cpp c` | 아니오 | 예 |
| M9 | config | 에이전트 설정 없음 (BOJ_AGENT_CMD 없음) | 에디터 열기 + 클립보드 복사 fallback | 예 | 아니오 |
| M10 | 문제데이터 | 에이전트 timeout/오류 | `Error: 에이전트 실행 실패. 수동으로 진행하세요.` + URL 출력 | 아니오 | 예 |
| M11 | 문제데이터 | 생성 후 자체검증: README ↔ 문제 불일치 | `Warning: README 내용이 문제와 다를 수 있습니다. 확인하세요.` | 아니오 | 아니오 |
| M12 | 파일시스템 | `--output` 경로가 존재하지 않음 | `Error: 출력 경로가 존재하지 않습니다: /invalid/path` | 아니오 | 예 |

---

## `boj run`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| R1 | 파일시스템 | 문제 폴더 없음 | `Error: '4949'로 시작하는 폴더를 찾을 수 없습니다. 존재하는 문제: ...` | 아니오 | 예 |
| R2 | 파일시스템 | `test/test_cases.json` 없음 | `Error: test/test_cases.json이 없습니다. make를 먼저 실행하세요.` | 아니오 | 예 |
| R3 | 파일시스템 | `Solution.java` 없음 | `Error: Solution.java를 찾을 수 없습니다.` | 아니오 | 예 |
| R4 | 파일시스템 | `test/Parse.java` 없음 | `Error: test/Parse.java를 찾을 수 없습니다.` | 아니오 | 예 |
| R5 | 템플릿 | `templates/java/Test.java` 없음 | `Error: 테스트 러너 템플릿이 없습니다 (BOJ_LANG=java).` | 아니오 | 예 |
| R6 | 문제데이터 | `test_cases.json` 형식 오류 (JSON 파싱 불가) | `Error: test_cases.json 파싱 실패. JSON 형식을 확인하세요.` | 아니오 | 예 |
| R7 | 문제데이터 | `test_cases.json` 에 testCases 배열 없음 | `Warning: 테스트 케이스가 없습니다. (테스트 케이스 0개)` | 아니오 | 아니오 (0개로 실행) |
| R8 | 문제데이터 | 테스트 케이스에 `id` 없음 | id 자동 부여 (1, 2, ...) 후 정상 실행 | 예 | 아니오 |
| R9 | 문제데이터 | 테스트 케이스에 `description` 없음 | `"예제 N"` 기본값으로 대체 후 정상 실행 | 예 | 아니오 |
| R10 | 파일시스템 | Solution.java 컴파일 오류 | javac 에러 메시지 그대로 출력 | 아니오 | 예 |
| R11 | 파일시스템 | Solution.java 런타임 예외 | 해당 테스트 케이스 `❌ 에러: NullPointerException` 출력 후 계속 | 아니오 | 아니오 (계속) |
| R12 | config | `BOJ_LANG` 이 지원하지 않는 값 | `Error: 지원하지 않는 언어: fortran. 지원: java python cpp c` | 아니오 | 예 |

---

## `boj commit`

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| CT1 | 파일시스템 | 문제 폴더 없음 | `Error: '4949'로 시작하는 폴더가 없습니다.` | 아니오 | 예 |
| CT2 | git | git repo 아님 | `Error: git 저장소가 아닙니다.` | 아니오 | 예 |
| CT3 | git | 변경사항 없음 (nothing to commit) | `Warning: 커밋할 변경사항이 없습니다.` | 아니오 | 예 (정상 종료) |
| CT4 | 인증 | BOJ 세션 없음 | 통계 조회 스킵, `[BOJ 통계: 세션 없음]` 메시지에 포함 후 커밋 | 예 | 아니오 |
| CT5 | 인증 | BOJ 세션 만료 | `[BOJ 통계: 세션 만료]` 포함 후 커밋 | 예 | 아니오 |
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

---

## 요약: 에러 메시지 규칙

| 수준 | 접두사 | 종료 코드 | 용도 |
|------|--------|-----------|------|
| Error | `Error:` | 1 (비정상) | 계속 진행 불가, 사용자 조치 필요 |
| Warning | `Warning:` | 0 (계속) | 진행 가능하나 주의 필요 |
| Info | (없음) | 0 | 정상 진행 상황 안내 |

## 자동복구 정책

- **에이전트 없음**: 에디터 + 클립보드 fallback
- **BOJ 통계 실패**: commit은 진행, 메시지에 실패 이유 포함
- **이미지 다운로드 실패**: reference 모드로 대체
- **id/description 없음**: 자동 보완 후 실행
- **submit/ 폴더 없음**: 자동 생성

*최종 업데이트: 2026-03-01*
