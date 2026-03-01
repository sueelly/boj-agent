# GitHub Issues 템플릿 (복붙 생성용)

> `gh` CLI 설치 후: `gh issue create --title "..." --body "..."` 로 생성
> 아래 각 이슈를 순서대로 생성하면 됩니다.

---

## Issue #1: Claude/Agent 설정 BOJ 프로젝트 맞춤 개선

**Labels**: `chore`, `config`
**Title**: `chore(config): BOJ 프로젝트 맞춤으로 CLAUDE.md, settings.json 업데이트`

### 목표
현재 CLAUDE.md와 .claude/settings.json이 일반 Spring/Java 백엔드 보일러플레이트 기준으로 설정되어 있음.
BOJ CLI 프로젝트(Bash 스크립트/템플릿/테스트/브라우저/Git)에 맞는 규칙과 권한으로 수정.

### 범위
- `CLAUDE.md`: BOJ 프로젝트 빌드·테스트·아키텍처 규칙 명시
- `.claude/settings.json`: BOJ 관련 Bash 권한 추가 (javac, java, python3, curl, boj 등)
- `.claude/rules/` 중 Spring/Java 전용 룰 제거 또는 비활성화

### Acceptance Criteria
- [ ] CLAUDE.md에 `boj run`, `./tests/run_tests.sh` 등 실제 테스트 명령 명시
- [ ] settings.json에 `javac`, `java`, `boj`, `curl`, `open` 허용 추가
- [ ] Spring 룰 파일이 BOJ 프로젝트에 오개입하지 않도록 격리
- [ ] 변경 이유를 짧게 주석/커밋 메시지로 기록

### 테스트 항목
- Claude Code가 `boj run` 명령을 자동 승인 없이 실행 가능한지 확인

### 엣지 케이스
- 기존 `.claude/hooks/` 동작이 BOJ 워크플로우와 충돌하는 경우

---

## Issue #2: 명령어별 Edge Case Matrix 정의

**Labels**: `docs`, `design`
**Title**: `docs(edge-cases): 명령어별 엣지 케이스 매트릭스 문서 작성`

### 목표
make/open/run/commit/review/submit/setup 각 명령에 대해 발생 가능한 엣지 케이스와 기대 동작을 문서화.
구현 및 테스트의 기준이 될 단일 진실 문서.

### 범위
- `docs/edge-cases.md` 신규 생성
- 카테고리: config/인증/네트워크/파일시스템/Git/템플릿/문제데이터
- 형식: Command × Case × Expected Behavior 표

### Acceptance Criteria
- [ ] 7개 명령 모두 포함
- [ ] 각 명령에 최소 5개 엣지 케이스
- [ ] 기대 동작이 "에러 메시지 내용", "자동 복구 여부", "중단 여부" 포함
- [ ] 테스트 구현과 1:1 대응 가능한 형태

### 엣지 케이스 (이 문서 자체의)
- 명령 신규 추가 시 문서 업데이트 누락 방지 → 커밋 훅 또는 PR 체크리스트에 포함

---

## Issue #3: setup 명령어 추가

**Labels**: `feat`, `auth`
**Title**: `feat(setup): 초기 설정/인증 setup 명령어 추가`

### 목표
최초 1회 실행으로 (a) Git 연결/사용자 정보, (b) BOJ 연결 정보(세션 쿠키), (c) 에이전트 설정을 저장.
연결 없이 다른 명령 실행 시 setup을 안내하고, 성공 후 원래 명령 이어서 실행.

### 범위
- `src/commands/setup.sh` 신규
- `src/boj` 에 `setup` 서브커맨드 추가
- `~/.config/boj/` 설정 파일 작성
- Git 정보, BOJ 세션 쿠키(수동 입력/Playwright 중 택일), 에이전트 명령 저장

### Acceptance Criteria
- [ ] `boj setup` 실행 시 git user.name/email, BOJ 세션, 에이전트 명령 입력 안내
- [ ] 설정 완료 후 `~/.config/boj/` 에 파일 저장
- [ ] 설정 없이 `boj make 4949` 실행 시 setup 안내 메시지 출력
- [ ] 이미 설정된 경우 현재 값 보여주고 수정 여부 확인
- [ ] `boj setup --check` 로 현재 설정 상태 확인 가능

### 테스트 항목
- [ ] 설정 파일 없을 때 setup 안내
- [ ] 부분 설정 시 누락 항목만 요청
- [ ] 잘못된 BOJ 세션으로 연결 시도 시 에러 안내

### 엣지 케이스
- ~/.config/boj/ 디렉터리 권한 없음
- BOJ 세션 만료 상태
- Git 미설치 환경

---

## Issue #4: make 품질 개선 (이미지/자체검증/옵션)

**Labels**: `feat`, `quality`
**Title**: `feat(make): 이미지 처리, 자체 검증, 옵션 확장`

### 목표
생성된 README가 실제 BOJ 문제 내용과 불일치하지 않도록 자체 검증 수행.
문제 본문 이미지를 다운로드하거나 안정적으로 참조.
`--lang`, `--output`, `--image-mode` 등 옵션으로 config 기본값 override 가능.

### 범위
- `src/commands/make.sh` 수정
- 이미지 처리: `--image-mode=download|reference|skip` (기본: reference)
- 언어 오버라이드: `--lang java|python|cpp|c|...`
- 출력 경로: `--output /path/to/dir`
- 자체 검증: 생성 후 README ↔ 문제 URL 내용 비교 (에이전트 활용)

### Acceptance Criteria
- [ ] `boj make 4949 --lang python` 으로 Python 환경 생성
- [ ] `boj make 4949 --image-mode download` 시 이미지 로컬 다운로드
- [ ] `boj make 4949 --image-mode skip` 시 이미지 태그 제거
- [ ] 생성 후 자체 검증 실행 (최소 1회)
- [ ] 불일치 발견 시 재생성 또는 경고 출력

### 테스트 항목
- [ ] 이미지 있는 문제 (예: 그래프 문제) 처리
- [ ] 네트워크 없을 때 이미지 다운로드 실패 처리
- [ ] 에이전트 없을 때 fallback 동작

### 엣지 케이스
- 문제 번호 존재하지 않음 (404)
- 이미지 URL이 BOJ 도메인 외부
- 생성 중 에이전트 timeout
- 이미 존재하는 문제 폴더 (overwrite 여부)

---

## Issue #5: submit 명령어 추가

**Labels**: `feat`
**Title**: `feat(submit): Submit.java 생성 submit 명령어 추가`

### 목표
현재 문제의 `Solution.java` + `test/Parse.java`를 합쳐 BOJ 제출용 단일 파일 `submit/Submit.java` 생성.
BOJ 제출 환경에서 바로 컴파일/실행 가능한 형태(Main 클래스, stdin 직접 읽기).
선택적으로 제출 페이지 브라우저 오픈.

### 범위
- `src/commands/submit.sh` 신규
- 언어별 Submit 생성 로직 (Java 우선, 이후 Python/C++)
- `src/boj` 에 `submit` 서브커맨드 추가
- `--open` 플래그로 제출 페이지 브라우저 오픈

### Acceptance Criteria
- [ ] `boj submit 4949` 실행 시 `submit/Submit.java` 생성
- [ ] Submit.java는 Main 클래스 포함, stdin으로 직접 입력 받음
- [ ] `javac submit/Submit.java && java -cp submit Main` 으로 실행 가능
- [ ] `boj submit 4949 --open` 시 제출 페이지(`https://www.acmicpc.net/submit/4949`) 오픈
- [ ] 이미 존재하는 Submit.java 있으면 overwrite 전 확인

### 테스트 항목
- [ ] 생성된 Submit.java가 컴파일 성공
- [ ] 생성된 Submit.java로 예제 입출력 일치 확인
- [ ] Solution.java 없을 때 에러 안내
- [ ] Python 언어 시 Submit.py 생성

### 엣지 케이스
- Solution.java와 Parse.java의 클래스명 충돌
- Solution에 inner class 있을 때
- 언어가 설정 안 된 상태

---

## Issue #6: commit 개선 (자동 add + BOJ 제출 통계)

**Labels**: `feat`, `ux`
**Title**: `feat(commit): 자동 git add, BOJ Accepted 통계 commit message 포함`

### 목표
commit 전 문제 번호에 맞는 파일들을 자동 git add.
BOJ에서 해당 문제의 내 Accepted 제출 중 최신 memory/time을 조회해 commit 메시지에 포함.
조회 실패 시에도 commit은 가능하되 실패 사유를 메시지에 포함.

### 범위
- `src/commands/commit.sh` 수정
- BOJ 제출 통계 조회: curl + 세션 쿠키로 `/status?problem_id=N&user_id=U&result=4` 파싱
- 조회 실패 시 graceful fallback

### Acceptance Criteria
- [ ] `boj commit 4949` 시 문제 폴더 내 파일 자동 git add
- [ ] BOJ 세션 있으면 memory/time 조회해 메시지에 포함: `[✓ 메모리: 12288KB, 시간: 80ms]`
- [ ] 세션 없거나 조회 실패 시: `[BOJ 통계 조회 실패: 세션 없음]` 포함 후 commit 진행
- [ ] 네트워크 오류 시 3초 timeout 후 fallback
- [ ] 커밋 메시지 형식: `feat(boj): 4949-괄호의-값 풀이 완료 [#N] [✓ 80ms 12288KB]`

### 테스트 항목
- [ ] BOJ 세션 있을 때 통계 파싱 정확성
- [ ] 네트워크 타임아웃 시 fallback
- [ ] 문제 폴더 없을 때 에러
- [ ] git repo 아닌 경로에서 실행 시 에러

### 엣지 케이스
- BOJ 세션 만료
- 해당 문제에 Accepted 제출 없음
- BOJ 응답 HTML 구조 변경
- 이미 커밋된 파일만 있어 변경사항 없음

---

## Issue #7: test case UX 개선

**Labels**: `feat`, `ux`
**Title**: `feat(ux): test_cases.json id/description 자동 보완`

### 목표
test_cases.json에 `id`나 `description` 없이 입력/기대값만 있어도 CLI가 자동 보완.
사용성/호환성 기준으로 `id`는 1부터 자동 부여, `description`은 `"예제 N"` 기본값.

### 범위
- `src/lib/normalize_test_cases.sh` (또는 Python 스크립트) 신규
- `boj run` 전처리 단계에 통합
- 문서 명확화 (`docs/user-guide.md` 업데이트)

### Acceptance Criteria
- [ ] `{"input": "1 2", "expected": "3"}` 형태도 `boj run` 시 정상 동작
- [ ] id 없으면 배열 순서대로 1, 2, 3... 자동 부여
- [ ] description 없으면 `"예제 N"` 기본값
- [ ] 기존 id 있는 케이스와 혼재 시에도 동작
- [ ] 원본 파일은 수정하지 않음 (런타임 정규화만)

### 테스트 항목
- [ ] id만 없는 케이스
- [ ] description만 없는 케이스
- [ ] 둘 다 없는 케이스
- [ ] 혼재 케이스 (일부만 id 있음)

---

## Issue #8: 명령어 옵션 확장 (config override)

**Labels**: `feat`
**Title**: `feat(cli): 명령어별 config override 옵션 확장 (최소 3개)`

### 목표
config 기본값을 명령 옵션으로 override 가능하도록.
기존 호환성 유지하면서 옵션 추가.

### 구현 옵션 (최소 구현)
| 명령 | 옵션 | 설명 |
|------|------|------|
| `make` | `--lang java\|python\|cpp\|c` | 언어 override |
| `make` | `--image-mode download\|reference\|skip` | 이미지 처리 |
| `make` | `--output /path` | 출력 경로 |
| `run` | `--lang java\|python` | 언어 override |
| `commit` | `--no-stats` | BOJ 통계 조회 스킵 |
| `commit` | `--message "..."` | 커밋 메시지 직접 지정 |
| `submit` | `--open` | 제출 페이지 브라우저 오픈 |
| `submit` | `--lang java\|python` | 언어 override |
| `open` | `--editor code\|cursor\|vim` | 에디터 override |

### Acceptance Criteria
- [ ] 모든 옵션이 config 기본값보다 우선
- [ ] 알 수 없는 옵션 시 usage 안내
- [ ] `-h/--help` 로 옵션 목록 확인 가능
- [ ] 기존 위치 인자 방식과 호환 유지

---

## Issue #9: 포괄적 테스트 작성

**Labels**: `test`
**Title**: `test(all): 모든 명령어 정상+엣지케이스 테스트 추가`

### 목표
모든 명령에 대해 정상 + 실패/엣지 케이스 테스트.
외부 의존(BOJ/브라우저/git)은 mock/fixture로 안정화.

### 최소 커버 항목
- config 없음/깨짐
- 인증 만료
- 네트워크 장애
- 이미지 다운로드 실패
- 문제 번호 충돌 (폴더 이미 존재)
- 템플릿 누락
- git repo 아님
- Solution.java 없음

### 범위
- `tests/integration/` 에 명령별 테스트 파일
- `tests/fixtures/` 에 필요 픽스처 추가
- `tests/unit/` 신규: 개별 함수/로직 단위 테스트
- `tests/run_tests.sh` 업데이트 (unit + integration)

### Acceptance Criteria
- [ ] `./tests/run_tests.sh` 로 전체 실행 가능
- [ ] 각 명령어별 최소 1개 정상 + 2개 엣지 테스트
- [ ] CI 환경(GitHub Actions)에서도 실행 가능
- [ ] 테스트 실행 방법과 커버 범위 README에 명시

---

## Issue #10: baekjoon/ 레거시 제거

**Labels**: `chore`, `cleanup`
**Title**: `chore(cleanup): baekjoon/ 레거시 폴더 제거 및 의존성 정리`

### 목표
Cursor 시절 레거시인 `baekjoon/` 폴더 제거.
현재 `src/boj` 의 `find_boj_root()`가 `baekjoon/template/Test.java`도 인식하는 로직 제거.

### 범위
- `baekjoon/` 폴더 삭제
- `src/boj` 의 legacy 참조 코드 제거
- README 등 `baekjoon/` 참조 문서 업데이트

### Acceptance Criteria
- [ ] `baekjoon/` 삭제 후 `boj run/make/commit` 정상 동작
- [ ] `find_boj_root()` 에서 legacy 경로 제거
- [ ] git log에서 baekjoon/ 이력은 보존 (--rm 만)

---

## Issue #11: templates 언어 확장 (BOJ 지원 전 언어)

**Labels**: `feat`, `templates`
**Title**: `feat(templates): BOJ 지원 언어 메타데이터 기반 템플릿 확장`

### 목표
BOJ에서 제출 가능한 전체 언어 목록을 기준으로 templates 확장.
수작업 나열이 아닌 언어 메타데이터 파일(확장자/컴파일/실행/스켈레톤) 기반 관리.

### 범위
- `templates/languages.json`: 언어 메타데이터 정의
- 주요 언어 템플릿 추가: C, C++, Java, Python, Kotlin, Go, Rust, JavaScript, TypeScript, Ruby, Swift, Scala
- `boj make --lang <lang>` 에서 선택 가능
- 각 템플릿: 입력/출력/solve 자리 포함

### Acceptance Criteria
- [ ] `templates/languages.json` 에 최소 10개 언어 정의
- [ ] 각 언어 템플릿이 `boj run` 에서 실행 가능한 구조
- [ ] `boj make 4949 --lang kotlin` 실행 시 Kotlin 환경 생성
- [ ] 미지원 언어 요청 시 지원 목록 안내

### 엣지 케이스
- 컴파일러 미설치 언어 실행 시도
- 언어별 stdin 처리 방식 차이

---

*생성일: 2026-03-01*
*전체 작업 기반: 요구사항 문서 v1.0*
