# Architecture — BOJ-Agent

> 현재 구조와 Python 전환 목표 구조를 기술합니다.

---

## 현재 구조

```
boj-agent/
  src/
    boj                       # CLI 진입점 (Bash 디스패처 → Python 라우팅)
    setup-boj-cli.sh          # [deprecated] → scripts/install.py
    core/                     # Python 핵심 로직 (순수 함수, CLI 없음)
      config.py               # 설정 로더 (env > 파일 > 기본값)
      client.py               # BOJ HTML fetch + 파싱 (requests+BS4)
      normalizer.py           # problem.json → README.md
      make.py                 # boj make 핵심 로직
      run.py                  # boj run 핵심 로직
      commit.py               # boj commit 핵심 로직
      submit.py               # boj submit 핵심 로직
      open.py                 # boj open 핵심 로직
      review.py               # boj review 핵심 로직
      exceptions.py           # 공통 예외 클래스
    cli/                      # CLI 래퍼 (core 위 얇은 레이어)
      main.py                 # argparse 디스패처
      boj_setup.py, boj_make.py, boj_run.py, boj_commit.py
      boj_submit.py, boj_open.py, boj_review.py
    commands/                 # [legacy fallback] Bash 서브커맨드
      make.sh, run.sh, commit.sh, submit.sh, setup.sh, open.sh, review.sh
    lib/                      # [legacy] 공통 라이브러리
      config.sh               # Bash 설정 로더
      boj_client.py           # → core/client.py로 이동 완료
      boj_normalizer.py       # → core/normalizer.py로 이동 완료
  templates/
    _common/
      test_cases.json         # 스키마 예시
    java/
      Test.java               # 테스트 러너 (런타임 인프라)
      ParseAndCallSolve.java  # 인터페이스 계약
      Solution.java           # 풀이 스텁 (참고용)
      Parse.java              # 파싱 스텁 (참고용)
      submit/Submit.java      # 제출 형식 스텁 (참고용)
    python/
      test_runner.py          # 테스트 러너 (런타임 인프라)
      solution.py             # 풀이 스텁 (참고용)
    cpp/, c/, kotlin/         # 스텁만 존재 (런타임 미지원) → 삭제 예정
    languages.json            # 언어 메타데이터
  prompts/
    make-spec.md              # make Step 2: spec 생성 (make.py generate_spec)
    make-skeleton.md          # make Step 3: 스켈레톤 생성 (make.py generate_skeleton)
    make-parse-and-tests.md   # [deprecated] make 파이프라인 미사용, make-skeleton으로 통합
    review.md                 # review용 에이전트 프롬프트
  reference/
    spec/                     # boj-spec-kit 레퍼런스 (problem.spec.json 생성용)
      problem-spec-format.md, boj-spec-rules.md, spec-levels.md
      boj-input-pattern-catalog.md, boj-output-pattern-catalog.md, boj-spec-fewshots.md
      problem-spec-contract.md, spec-to-parse-rules.md, parse-pattern-catalog.md
      output-format-catalog.md, spec-to-parse-fewshots.md
  tests/
    run_tests.py              # 통합 테스트 러너 (pytest + bash 자동 발견)
    run_tests.sh              # 레거시 Bash 러너 (전환 기간 유지)
    fixtures/                 # 테스트 픽스처 (99999, 1000, 6588, 9495)
    unit/                     # Python pytest 단위 테스트 + Bash 단위 테스트
    integration/              # Python/Bash 통합 테스트
    e2e/                      # E2E 테스트
  scripts/
    install.py                # [deprecated] → pip install boj-agent
  pyproject.toml              # 패키지 정의 (pip install boj-agent)
  docs/                       # 문서
    ARCHITECTURE.md           # 프로젝트 구조 (현재 + 목표)
    COMMAND-SPEC.md           # 명령어별 로직 정의서
    user-guide.md             # 사용자 가이드
    dev/                      # 개발 프로세스 가이드
      WORKFLOW.md             # 이슈 → PR → 머지 워크플로우
      VERIFICATION.md         # 7단계 검증 파이프라인
      testing/                # 테스트 문서 (통합)
        strategy.md           # pytest 특성화 테스트 전략
        edge-cases.md         # 엣지케이스 매트릭스
        coverage/             # 명령어별 테스트 커버리지
    records/                  # 기록
      DEVLOG.md               # 변경 기록 (구조화 + Legacy 여정)
```

### 핵심 설계 결정

**설정 우선순위**: 환경변수 `BOJ_<KEY>` > `$BOJ_CONFIG_DIR/<key>` 파일 > 기본값

**ROOT 탐지**: `templates/java/Test.java` 존재 여부로 프로젝트 루트 판별 (cwd 위로 탐색 → BOJ_ROOT fallback)

**에이전트 중립**: `BOJ_AGENT_CMD` 환경변수로 어떤 에이전트든 교체 가능. 미설정 시 에디터+클립보드 fallback.

**templates/ 이중 역할**:
- 런타임 인프라: Test.java, ParseAndCallSolve.java, test_runner.py (`boj run`에서 classpath/import 참조)
- 참고 예시: Solution.java, Parse.java 등 (에이전트/사용자 참고용)

### 현재 구조의 한계

1. **Shell + Python 혼합**: config.sh(Bash)와 boj_client.py(Python)에 설정 로직 이중화
2. **Bash 테스트 한계**: PTY 없이 대화형 테스트 불가, 느슨한 문자열 매칭
3. **run.sh trap 중복**: Java/Python 거의 동일한 정규화+복원 코드
4. **submit.sh sed/grep 접합**: inner class에서 깨질 수 있음
5. **templates/ 정체성 혼란**: 런타임 인프라 + 참고 예시 + ROOT 마커 혼재

---

## 목표 구조 (Option C — 확정)

```
boj-agent/
  src/
    core/                 # Python 패키지 — 순수 로직, CLI 없음
      __init__.py
      config.py               # 설정 로더 (env > 파일 > 기본값), config.sh 대체
      client.py               # BOJ HTML fetcher (src/lib/boj_client.py에서 이동)
      normalizer.py           # problem.json → README.md (src/lib/boj_normalizer.py에서 이동)
      make.py                 # boj make 핵심 로직 (5단계 파이프라인)
      runners/                # 언어별 테스트 실행 로직
        __init__.py
        java/
          java.py               # Java 컴파일/실행 로직
          java_runtime/         # Java 전용 런타임 파일 (templates/java/에서 이동)
            Test.java
            ParseAndCallSolve.java
        python/
          python.py             # Python 실행 로직
          python_runtime/       # Python 전용 런타임 파일 (templates/python/에서 이동)
            test_runner.py
      submitter.py            # 제출 파일 생성 (Java 우선)
      workspace.py            # 문제 디렉터리 레이아웃, 경로 해석
    cli/                  # CLI 진입점 — core 위 얇은 래퍼
      __init__.py
      main.py                 # argparse 디스패처 (또는 Click)
      boj_make.py
      boj_run.py
      boj_commit.py
      boj_submit.py
      boj_open.py
      boj_setup.py
      boj_review.py
    boj                       # 쉘 스텁: exec python3 -m boj_cli "$@" (PATH 호환용 유지)
    lib/                      # legacy. 전환 기간 동안 유지
      boj_client.py           # core/client.py로 옮길 때까지 유지
      boj_normalizer.py       # core/normalizer.py로 옮길 때까지 유지
      config.sh               # 모든 쉘 명령 이전 완료까지 유지
  reference/                  # 에이전트/사용자 참고용 예시
    stubs/                    # 언어별 스켈레톤 예시
      java/Solution.java, Parse.java
      python/solution.py, parse.py
    schemas/                  # JSON 스키마 예시
      test_cases.json
    spec/                     # boj-spec-kit 레퍼런스 (problem.spec.json 생성용)
      problem-spec-format.md      # JSON 스키마 규격
      boj-spec-rules.md           # spec 생성 상위 규칙
      boj-input-pattern-catalog.md
      boj-output-pattern-catalog.md
      boj-spec-fewshots.md        # few-shot 예시
      spec-levels.md              # Level 1/2/3 복잡도 분류
    usecases/                 # 실제 사용 시 결과 예시
      java/
        README.md
        Solution.java
        artifacts/                # make 중간 산출물
          problem.json
          problem.spec.json
          images/                 # 문제 이미지 파일
        test/
          test_cases.json
          Parse.java
        submit/
          Submit.java
          REVIEW.md
  tests/
    run_tests.py              # 통합 테스트 러너 (pytest + bash 자동 발견)
    unit/                     # core 단위 테스트 (pytest + bash)
    integration/              # subprocess boj CLI 호출 테스트 (pytest + bash)
    e2e/                      # E2E 테스트 (bash)
    fixtures/                 # 기존 픽스처 유지
  prompts/                    # 에이전트 지시문 (reference/와 같은 레벨)
  docs/                       # 문서
    ARCHITECTURE.md, COMMAND-SPEC.md, user-guide.md
    dev/                      # 개발 프로세스 가이드
    records/                  # 기록 (DEVLOG.md)
  languages.json              # 언어 메타데이터 (프로젝트 루트)
  pyproject.toml              # 패키지 정의
```

### 경계

- **core**: CLI 없음, 컬러 없음, 대화형 프롬프트 없음. 순수 함수와 subprocess 호출. 100% 테스트 가능.
- **cli**: 얇은 래퍼. 출력 포맷, 대화형 프롬프트 처리. core 호출.
- 향후 MCP: 필요 시 core 함수를 MCP 도구로 노출 가능. 코어 수정 불필요.

### Option C 선택 이유

1. 런타임 파일(Test.java, test_runner.py)이 `core/runners/` 안에 있어 패키지와 일체화
2. `reference/`는 에이전트 프롬프트와 함께 참조되는 자료이므로 `prompts/`와 같은 레벨
3. ROOT 탐지를 `pyproject.toml` 또는 `.boj-root` 마커 파일로 교체
4. 실체 없는 언어 스텁 제거 — `languages.json`에 메타데이터만 유지

### 마이그레이션 순서

1. ~~`boj setup`~~ — ✅ 완료 (#46)
2. ~~`scripts/install.py`~~ — ✅ 완료 (#47)
3. ~~`boj make`~~ — ✅ 완료 (#54)
4. ~~`boj run`~~ — ✅ 완료 (#60)
5. ~~`boj open`~~ — ✅ 완료 (#66)
6. ~~`boj review`~~ — ✅ 완료 (#67)
7. ~~`boj commit`~~ — ✅ 완료 (#68)
8. ~~`boj submit`~~ — ✅ 완료 (#69)
9. ~~PyPI 패키지화~~ — ✅ 완료 (#70): `pyproject.toml`, `src/cli/main.py` 디스패처, `pip install boj-agent`

명령어마다 별도 PR. 한 번에 전부 재구성하지 않음.

### templates/ 정리 계획 (#54)

- **삭제**: `c/`, `cpp/`, `kotlin/` (런타임 미지원, 스텁만 존재)
- **이동**: `java/{Test,ParseAndCallSolve}.java` → `core/runners/java/java_runtime/`
- **이동**: `python/test_runner.py` → `core/runners/python/python_runtime/`
- **이동**: `_common/test_cases.json` → `reference/schemas/`
- **이동**: `java/{Solution,Parse}.java` → `reference/stubs/java/`
- **이동**: `python/solution.py` → `reference/stubs/python/`
- **이동**: `languages.json` → 프로젝트 루트

---

---

## Claude Code 플러그인 (`#71`)

```
.claude-plugin/
├── plugin.json                    # 플러그인 매니페스트
├── README.md                      # 설치/사용 가이드
└── skills/
    ├── boj-make/SKILL.md          # boj make 래퍼
    ├── boj-run/SKILL.md           # boj run 래퍼
    ├── boj-commit/SKILL.md        # boj commit 래퍼
    ├── boj-review/SKILL.md        # boj review 래퍼
    ├── boj-submit/SKILL.md        # boj submit 래퍼
    ├── boj-open/SKILL.md          # boj open 래퍼
    ├── boj-setup/SKILL.md         # boj setup 래퍼
    └── boj-solve/SKILL.md         # 복합: make → 풀이 → run → commit → submit
```

### 설계 원칙

- **스킬은 래퍼**: 로직은 `boj` CLI에 위임, 스킬은 Bash로 호출만 담당
- **자연어 트리거**: 각 SKILL.md의 `description`에 한국어 트리거 문구 포함 (예: "백준 N번 만들어줘")
- **CLI 의존**: `boj` CLI가 PATH에 있어야 동작. 없으면 설치 안내 후 중단
- **메인 컨텍스트 실행**: 파일 생성/git 변경이 필요하므로 fork context 사용 안 함

### 사용 방법

```bash
# 로컬 테스트
claude --plugin-dir .claude-plugin

# 슬래시 커맨드
/boj-make 1000
/boj-solve 1000

# 자연어 (description 기반 자동 매칭)
"백준 1000번 풀어줘"  → boj-solve 트리거
"1000번 돌려줘"       → boj-run 트리거
```

*최종 업데이트: 2026-03-15*
