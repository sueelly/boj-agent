# Architecture — BOJ-Agent

> 현재 구조와 Python 전환 목표 구조를 기술합니다.

---

## 현재 구조

```
boj-agent/
  src/
    boj                       # CLI 진입점 (Bash 디스패처)
    setup-boj-cli.sh          # ~/bin/boj 설치 스크립트
    commands/                 # 서브커맨드 (각각 독립 Bash 스크립트)
      make.sh     (254줄)    # [A]Fetch → [B]Normalize → [C]Agent skeleton
      run.sh      (168줄)    # test_cases.json 기반 테스트 실행
      commit.sh   (179줄)    # git add/commit + BOJ 통계
      submit.sh   (301줄)    # Submit 파일 생성 (Java sed/grep 접합)
      setup.sh    (284줄)    # 대화형/비대화형 설정
      open.sh     (50줄)     # 에디터 열기
      review.sh   (51줄)     # 에이전트 리뷰 호출
    lib/
      config.sh   (195줄)    # 공통 설정 로더 + 유틸리티 함수
      boj_client.py           # BOJ HTML fetch + 파싱 (Python, requests+BS4)
      boj_normalizer.py       # problem.json → README.md (Python)
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
    cpp/, c/, kotlin/         # 스텁만 존재 (런타임 미지원)
    languages.json            # 언어 메타데이터
  prompts/
    make-skeleton.md          # make용 스켈레톤 생성 프롬프트 (make.sh:181에서 사용)
    review.md                 # review용 에이전트 프롬프트 (review.sh:29에서 사용)
  tests/
    run_tests.py              # 통합 테스트 러너 (pytest + bash 자동 발견)
    run_tests.sh              # 레거시 Bash 러너 (전환 기간 유지)
    fixtures/                 # 테스트 픽스처 (99999, 1000, 6588, 9495)
    unit/                     # Bash 단위 테스트 + Python pytest
    integration/              # Bash/Python 통합 테스트
    e2e/                      # E2E 테스트
  docs/                       # 문서
    ARCHITECTURE.md           # 프로젝트 구조 (현재 + 목표)
    COMMAND-SPEC.md           # 명령어별 로직 정의서
    edge-cases.md             # 엣지케이스 매트릭스
    user-guide.md             # 사용자 가이드
    dev/                      # 개발 프로세스 가이드
      WORKFLOW.md             # 이슈 → PR → 머지 워크플로우
      VERIFICATION.md         # 7단계 검증 파이프라인
      test-strategy.md        # pytest 특성화 테스트 전략
      test-coverage/          # 테스트 커버리지 데이터
      rewrite-plan.md         # Python 전환 계획
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
    usecases/                 # 실제 사용 시 결과 예시
      java/                   # README, Solution, submit/, test/
  tests/
    run_tests.py              # 통합 테스트 러너 (pytest + bash 자동 발견)
    unit/                     # core 단위 테스트 (pytest + bash)
    integration/              # subprocess boj CLI 호출 테스트 (pytest + bash)
    e2e/                      # E2E 테스트 (bash)
    fixtures/                 # 기존 픽스처 유지
  prompts/                    # 에이전트 지시문 (reference/와 같은 레벨)
  docs/                       # 문서
    ARCHITECTURE.md, COMMAND-SPEC.md, edge-cases.md, user-guide.md
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

1. `boj run` (Java only) — 첫 수직 슬라이스
2. `boj make` — client + normalizer 이미 Python
3. `boj submit` — sed/grep 접합을 Python 문자열 처리로 개선
4. `boj commit`, `boj open`, `boj setup`, `boj review` — 순차

명령어마다 별도 PR. 한 번에 전부 재구성하지 않음.

---

*최종 업데이트: 2026-03-09*
