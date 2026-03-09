# BOJ-Agent 재작성 및 마이그레이션 계획

## 맥락

이 프로젝트는 BOJ(백준 온라인 저지) 문제 풀이 워크플로를 자동화하는 **Bash 기반 CLI**이다. 약 50커밋에 걸쳐 자연스럽게 성장했고, 이제 유지보수 어려움 징후가 보인다: 쉘 전용 우회 코드, 취약한 테스트 단언, 에이전트에 따라 달라지는 비결정적 동작 등. A→B(Fetch→Normalize) 파이프라인은 이미 이슈 #13에서 Python으로 이전되어 올바른 방향을 잡았다. 이 계획은 그 이전을 체계적으로 완료하며, **Python 코어 + CLI를 단일 소스로 하는 구조**로 Java 우선 지원을 목표로 한다.

---

## 1. 동작 인벤토리

**프로젝트가 지원하는 사용자 대면 워크플로:**

| 워크플로 | 명령 | 상태 |
|----------|------|------|
| 문제 셋업 | `boj make <N>` | 유지할 가치 있음 — 핵심 워크플로 |
| 테스트 실행 | `boj run <N>` | 유지할 가치 있음 — 핵심 워크플로 |
| 통계 포함 Git 커밋 | `boj commit <N>` | 유지할 가치 있음 — 편의 기능 |
| 제출용 파일 생성 | `boj submit <N>` | 유지할 가치 있음 (Java) |
| 에디터 열기 | `boj open <N>` | 유지할 가치 있음 |
| 코드 리뷰 | `boj review <N>` | 유지할 가치 있음 |
| 최초 설정 | `boj setup` | 유지할 가치 있음 |

7개 워크플로 모두 유지할 만하다. `boj make`와 `boj review`는 설계상 에이전트 의존(비결정적 C 단계)이고, 나머지는 완전히 결정적이어야 한다.

---

## 2. 실패/취약 인벤토리

**깨졌거나 취약한 동작:**

- `run.sh`: Java와 Python용 trap 로직이 중복(거의 동일 복사, ~98행과 ~130행). 한쪽만 수정하면 다른 쪽은 묵음으로 어긋남.
- `run.sh`: `normalize_test_cases()`가 mktemp에 쓰고 echo로 경로 반환 — `HOME` 오버라이드가 실패할 수 있는 서브셸에서 취약.
- `submit.sh` (`generate_java_submit`): `sed 's/^public class Solution/class Solution/'`, `grep -v "^import"`로 Java 파일 접합 — Solution에 어노테이션·내부 클래스·비표준 포맷이 있으면 깨짐.
- `commit.sh`: BOJ 통계 조회가 `curl`로 HTML 스크래핑. 취약: BOJ HTML 구조, 레이트 리밋, 세션 쿠키 유효성에 의존.
- `make.sh` Gate Check: 정규식 `solve\s*\(\s*(String\s+\w+|(self\s*,\s*)?\w+\s*:\s*str)\s*\)`가 String으로 시작하는 올바른 다중 인자 시그니처에서 오탐할 수 있음.
- `make.sh` Execution Verify: 에이전트 단계 후 `boj run` 호출 — 에이전트가 아직 파일을 만들지 않았으면 항상 실패하고 오해의 소지 있는 경고만 남김.
- `setup.sh`: 완전 대화형(`read -p`), PTY 모킹 없이는 테스트 불가.
- 테스트의 `grep -qi "passed"` / `grep -q "2/2"`: 느슨한 문자열 매칭 — 에러 메시지에 "passed"가 우연히 포함돼도 통과.
- 단위 테스트 `run_happy.sh`: `export HOME="$tmp"`를 전역 설정해 같은 프로세스 내 후속 테스트의 git config 해석에 영향.
- E2E `test_full_workflow.sh`: 픽스처를 쓰지 않으면 네트워크(BOJ fetch) 필요 가능 — 오프라인 안전 여부 미검증.
- 누락된 테스트: `review.sh`는 에이전트 출력에 대한 단언 없음; `submit.sh` Java 생성은 생성 파일 내용에 대한 단언으로 테스트되지 않음.

**검증 없이 나갈 가능성이 있는 부분:**

- `boj submit` Java 생성: 컴파일 검사는 있지만 생성된 Main 클래스 로직(parseAndCallSolve 연결)은 E2E 미테스트.
- `boj commit` BOJ 통계: 네트워크 의존, 모킹 없음, "실패 시 스킵" 처리 — 실패가 묵음.
- Gate Check: 오탐이 발생하는지, 올바른 시그니처가 걸리지 않는지 검증하는 테스트 없음.

---

## 3. 의존성 인벤토리

**BOJ 웹사이트 의존:**

- `boj_client.py`: `https://www.acmicpc.net/problem/{N}` HTTP fetch — `BOJ_CLIENT_TEST_HTML` env로 격리(양호)
- `commit.sh`: `curl https://www.acmicpc.net/status?...` — 격리 수단 없음, 항상 네트워크
- `submit.sh --open`: `open https://www.acmicpc.net/submit/{N}` — 사소함, 수용 가능
- `boj_client.py`의 `boj_login()`: POST `https://www.acmicpc.net/signin` — `BOJ_LOGIN_URL_OVERRIDE`로 격리

**쉘 전용 의존:**

- `echo -e`로 ANSI 컬러 코드 — 이식성 낮음, 쉘마다 다름
- 클립보드용 `pbcopy` (macOS 전용) — 하드코딩 폴백
- 대화형 프롬프트용 `read -p` — PTY 없이는 테스트 불가
- Bash 3.2 호환 우회(git 히스토리 커밋 `9962530`에 기록)
- `${!env_var}` 간접 확장 — bash 전용

**파일 레이아웃 관례(암묵적 계약):**

- `templates/java/Test.java`가 있어야 리포 루트 추적 가능
- 문제 폴더: `{ROOT}/{N}-{slug}/` 내 `test/test_cases.json`, `test/Parse.java`, `Solution.java`
- 설정: `~/.config/boj/{key}` 파일
- 에이전트 프롬프트: `prompts/make-skeleton.md`, `prompts/make-environment.md`
- 중간 A→B 산출물: `artifacts/problem.json`

**에이전트 관련 가정:**

- `BOJ_AGENT_CMD` env는 마지막 인자로 프롬프트 문자열을 받는 명령이어야 함
- `prompts/`는 Claude Code를 대상 에이전트로 가정(한국어, Claude 전용 관례)
- MCP 경계 없음 — 에이전트는 쉘 exec로 호출, 출력은 비구조화

---

## 4. 유지 / 폐기 / 재작성 분류

| 구성요소 | 결정 | 이유 |
|----------|------|------|
| `src/lib/boj_client.py` | **유지** | 이미 Python, 테스트 양호, env로 픽스처 격리 |
| `src/lib/boj_normalizer.py` | **유지** | 이미 Python, 순수 함수, 결정적, 스냅샷 테스트 가능 |
| `tests/unit/test_boj_client.py` | **유지** | Python pytest, 나머지 스위트의 좋은 모델 |
| `tests/fixtures/` | **유지** | 로컬 HTML/JSON 픽스처가 올바른 방식 |
| `templates/java/` | **유지** | Java 테스트 러너(`Test.java`, `ParseAndCallSolve.java`) 정상 동작 |
| `prompts/` | **유지** | 에이전트 프롬프트는 언어/플랫폼 중립 텍스트 |
| `tests/unit/lib/test_helper.sh` | **단기 유지** | 쉘 테스트가 있는 동안 필요; 이후 pytest 픽스처로 이전 |
| `tests/unit/commands/*.sh` | **Python으로 재작성** | 쉘 단위 테스트는 동작하지만 느리고 취약; pytest subprocess가 더 깔끔 |
| `src/lib/config.sh` | **Python으로 재작성** | 설정 로직이 기반; Python 버전으로 제대로 된 단위 테스트 가능 |
| `src/commands/run.sh` | **Python으로 재작성** | 핵심 워크플로; trap 중복; Java만 타깃으로 할 예정 |
| `src/commands/make.sh` | **Python으로 재작성** | 이미 Python A+B 래핑; 얇은 쉘 래퍼는 가치 없음 |
| `src/commands/commit.sh` | **Python으로 재작성** | BOJ 통계 스크래핑에 모킹 필요; 쉘 grep/sed 취약 |
| `src/commands/submit.sh` | **Python으로 재작성** | Java 접합 로직은 AST 인식 또는 최소한 Python 문자열 처리 필요 |
| `src/commands/setup.sh` | **Python으로 재작성** | 대화형 설정은 Python에서 프롬프트 모킹으로 테스트하기 쉬움 |
| `src/commands/open.sh` | **Python으로 재작성** | 사소함, 10줄 수준 |
| `src/commands/review.sh` | **Python으로 재작성** | 에이전트 래퍼, 사소한 이전 |
| `src/boj` (디스패처) | **Python으로 재작성** | CLI 진입점; Click 또는 argparse로 교체 |
| `tests/integration/*.sh` | **Python으로 재작성** | 픽스처 방식 유지; `subprocess.run` 사용 |
| `tests/e2e/test_full_workflow.sh` | **폐기** | 코어 안정화 후 Python 통합 테스트로 재구성 |
| `tests/harness/` | **폐기** | 다언어 매트릭스 하네스는 1단계 범위 외 |

---

## 5. 아키텍처 평가

**현재 구조가 유지보수하기 어려운 이유:**

1. Shell + Python 혼합: `config.sh`(쉘)와 `boj_client.py`(Python)에 로직이 나뉘어 설정 시스템이 두 개 동기화되어야 함.
2. 쉘 명령은 전체 프로세스 띄우고 임시 디렉터리 세팅 없이는 단위 테스트 불가.
3. `exec "$CMD_SCRIPT" "$ROOT" "$PROBLEM_NUM" "${@:3}"` 패턴으로 각 명령이 옵션 파싱·에러 처리를 따로 재구현함.
4. 컬러 코드·대화형 프롬프트가 로직과 뒤섞여 있어 env 트릭 없이는 테스트 시 억제 불가.
5. CLAUDE.md의 `set -e` 회피 언급은 팀이 이미 쉘 에러 처리가 불안정하다고 인지했음을 보여 줌.
6. `run.sh`의 trap 기반 정리(Java·Python에 중복)는 알려진 취약 패턴.

**잘 된 점:**

- A→B Python 파이프라인(이슈 #13)은 올바른 선택. `boj_client.py`와 `boj_normalizer.py`가 코드베이스에서 가장 건강한 부분.
- 테스트 헬퍼 추상화(`test_helper.sh`)는 픽스처 격리에 대한 좋은 사고를 보여 줌.
- 테스트 격리를 위한 `BOJ_CLIENT_TEST_HTML`, `BOJ_BASE_URL_OVERRIDE`가 올바른 패턴.

---

## 6. 확정 목표 아키텍처 (Option C)

```
boj-agent/
  src/
    boj_core/                 # Python 패키지 — 순수 로직, CLI 없음
      __init__.py
      config.py               # 설정 로더 (env > 파일 > 기본값), config.sh 대체
      client.py               # BOJ HTML fetcher (src/lib/boj_client.py에서 이동)
      normalizer.py           # problem.json -> README.md (src/lib/boj_normalizer.py에서 이동)
      runners/                # 언어별 테스트 실행 로직
        __init__.py
        java.py               # Java 컴파일/실행 로직
        python.py             # Python 실행 로직
        java_runtime/         # Java 전용 런타임 파일 (templates/java/에서 이동)
          Test.java
          ParseAndCallSolve.java
        python_runtime/       # Python 전용 런타임 파일 (templates/python/에서 이동)
          test_runner.py
      submitter.py            # 제출 파일 생성 (Java 우선)
      workspace.py            # 문제 디렉터리 레이아웃, 경로 해석
    boj_cli/                  # CLI 진입점 — boj_core 위 얇은 래퍼
      __init__.py
      main.py                 # argparse 디스패처 (또는 Click)
      cmd_make.py             # boj make
      cmd_run.py              # boj run
      cmd_commit.py           # boj commit
      cmd_submit.py           # boj submit
      cmd_open.py             # boj open
      cmd_setup.py            # boj setup
      cmd_review.py           # boj review
    boj                       # 쉘 스텁: exec python3 -m boj_cli "$@"  (PATH 호환용 유지)
    lib/                      # 전환 기간 동안 유지
      boj_client.py           # boj_core/client.py로 옮길 때까지 유지
      boj_normalizer.py       # boj_core/normalizer.py로 옮길 때까지 유지
      config.sh               # 모든 쉘 명령 이전 완료까지 유지
  reference/                  # 에이전트/사용자 참고용 예시 (프로젝트 루트)
    stubs/                    # 언어별 스켈레톤 예시
      java/Solution.java
      java/Parse.java
      python/solution.py
      python/parse.py
    schemas/                  # JSON 스키마 예시
      test_cases.json
  tests/
    unit/
      test_config.py
      test_client.py          # 이미 존재 — 유지
      test_normalizer.py      # 픽스처로 이미 존재 — 정식화
      test_runner.py          # Java 러너 단위 테스트 (픽스처로 컴파일·실행)
      test_submitter.py       # 제출 생성 단위 테스트
      test_workspace.py
    integration/
      test_run.py             # 픽스처로 subprocess boj run
      test_make.py            # BOJ_CLIENT_TEST_HTML로 subprocess boj make
    fixtures/                 # 기존 픽스처 전부 유지
  docs/
    rewrite-plan.md           # 본 문서
    ARCHITECTURE.md
    test-strategy.md
  prompts/                    # 에이전트 지시문 (reference/와 같은 레벨)
  pyproject.toml              # 패키지 정의
  languages.json              # 언어 메타데이터 (프로젝트 루트로 이동)
```

**Option C 선택 이유:**

1. 런타임 파일(Test.java, test_runner.py)이 `boj_core/runners/` 안에 있어 패키지와 일체화
2. `reference/`는 에이전트 프롬프트와 함께 참조되는 자료이므로 `prompts/`와 같은 레벨
3. ROOT 탐지를 `templates/java/Test.java` 대신 `pyproject.toml` 또는 `.boj-root` 마커 파일로 교체
4. 실체 없는 언어 스텁 제거 — `languages.json`에 메타데이터만 유지

**경계:**

- `boj_core`: CLI 없음, 컬러 없음, 대화형 프롬프트 없음. 순수 함수와 subprocess 호출. 100% 테스트 가능.
- `boj_cli`: 얇은 래퍼. 출력 포맷, 대화형 프롬프트 처리. `boj_core` 호출.
- 향후 MCP: 필요 시 `boj_core` 함수를 MCP 도구로 노출 가능. 코어 수정 불필요.

---

## 7. 마이그레이션 전략

**먼저 한 개의 수직 슬라이스 보존 — Java용 `boj run`:**

1. `boj_client.py` → `boj_core/client.py` 이동(이름만 변경, 로직 동일)
2. `boj_normalizer.py` → `boj_core/normalizer.py` 이동(이름만 변경, 로직 동일)
3. `boj_core/config.py` 작성 — `config.sh`의 `boj_config_get`/`boj_load_config` 이전
4. `boj_core/runner.py` 작성 — `run.sh` 76–113행의 Java 컴파일·실행 로직
5. `boj_cli/cmd_run.py` 작성 — 얇은 CLI 래퍼
6. `tests/unit/test_runner.py` 작성 — 픽스처 99999 사용
7. `tests/integration/test_run.py` 작성 — `test_boj_run.sh`를 대체하는 subprocess 테스트
8. 검증: Python 구현으로 `boj run 99999`가 E2E 동작
9. Python 버전이 모든 테스트를 통과할 때까지 `src/commands/run.sh` 그대로 유지

**이후 명령별로 하나씩 확장:**

- `boj make` (client + normalizer 필요 — 이미 Python, 연결만)
- `boj submit` (Java만 — 가장 취약한 쉘 로직, 재작성 가치 최대)
- `boj commit`, `boj open`, `boj setup`, `boj review` (순차적으로)

**한 번에 전부 재구성하지 말 것. 명령마다 별도 PR.**

---

## 8. 브랜치 전략 (확정)

PR #23, #24가 이미 main에 머지된 상태이므로 main이 가장 안정된 기준점이다.

**확정 전략:**

1. `main`에서 `refactor/docs-consolidation` 브랜치 생성 (현재 진행 중)
2. 문서 정리 PR을 먼저 머지
3. 이후 `main`에서 `refactor/python-rewrite` 브랜치를 별도로 생성
4. Python 재작성은 명령어별로 별도 PR (`boj run` → `boj make` → `boj submit` → 나머지)

**참고:** 이슈 #23이 추가하는 `tests/unit/test_boj_client.py`와 픽스처는 Python 재작성에 필수. 버리지 말 것.

---

## 9. 문서화 계획

재작성 코드를 시작하기 전에 다음 파일 작성:

| 파일 | 내용 |
|------|------|
| `docs/rewrite-plan.md` | 본 문서 |
| `docs/architecture.md` | 목표 아키텍처 다이어그램 + 경계 정의 + 데이터 흐름 |
| `docs/test-strategy.md` | 픽스처 관례, pytest 패턴, 새 픽스처 추가 방법, 격리 규칙 |
| `docs/migration-log.md` | 명령별 마이그레이션 로그(날짜, 변경 내용, 검증 근거) |
| `docs/portfolio-notes.md` | 포트폴리오용 프로젝트 서술 — 존재 이유, 배운 점 |

---

## 10. 구체 실행 계획

**Phase 1 — 기반(우선 수행):**

1. PR #23을 main에 머지(또는 안정 상태로 만들기)
2. 업데이트된 main에서 `rewrite/python-core` 브랜치 생성
3. `docs/architecture.md`, `docs/test-strategy.md` 작성
4. `pyproject.toml`에 boj-core 패키지 구조 설정
5. `boj_client.py` → `boj_core/client.py`, `boj_normalizer.py` → `boj_core/normalizer.py` 이동/이름 변경
6. `boj_core/config.py` 작성 (`config.sh`에서 이전)
7. `boj_core/runner.py` 작성 (Java run — `run.sh` 76–113행에서 이전)
8. 픽스처 99999로 `tests/unit/test_runner.py` 작성
9. subprocess로 `tests/integration/test_run.py` 작성
10. Python으로 `boj run 99999` E2E 검증

**당장 하지 말 것:**

- `boj run` Python이 안정·테스트될 때까지 `boj make` 이전하지 말 것
- Python 대체가 없는 쉘 명령은 재작성하지 말고 그대로 두고 실행 유지
- Phase 1에서 다언어 지원(Python run, C++ 등) 추가하지 말 것
- MCP 레이어는 아직 만들지 말 것
- Python 대응이 테스트 통과할 때까지 쉘 파일 삭제하지 말 것

**Phase 1에서 명시적으로 범위 외:**

- `boj run`의 Python 언어 지원 (Java만)
- C, C++, Kotlin, Go, Rust, Swift, Scala 지원
- Claude Code 외 다중 에이전트
- MCP 경계 / MCP 서버
- 전언어 템플릿 생성
- BOJ 자동 제출

**코딩 전에 해결할 불확실성:**

1. `pyproject.toml` 패키지 이름을 `boj`로 할지 `boj_core`로 할지? (기존 `src/boj` 쉘 스크립트와 PATH 충돌 영향)
2. CLI는 `click`을 쓸지 `argparse`를 쓸지? (Click이 깔끔하지만 의존성 추가)
3. `boj_core/runner.py`는 `javac`/`java`를 직접 호출할지, 출력 캡처한 subprocess로 할지?
