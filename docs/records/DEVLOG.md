# DEVLOG — BOJ-Agent 변경 기록

변경 사항을 날짜 / 변경 요약 / 의사결정 / 검증 방법 단위로 기록합니다.
새 항목은 상단에 추가합니다.

항목 형식:
```
## [YYYY-MM-DD] 변경 제목 [#N]
**변경 요약:** 한 줄 설명
**의사결정:** 선택한 방법과 이유 (검토한 대안 포함)
**검증 방법:** 어떤 테스트/명령으로 확인하는가
---
```

---

## [2026-03-13] feat(install,dispatcher): auto-add PATH and dispatch setup to Python [#57]
**변경 요약:** `src/boj`의 setup 디스패치를 `setup.sh` → `boj_setup.py`(PYTHONPATH 설정 포함)로 교체; `install.py`에 `add_to_path()` 추가하여 터미널 재시작 없이 `boj` 전역 사용 가능; `setup_branches.sh` 테스트의 lang 키 `lang` → `prog_lang` 수정.
**의사결정:** ARCHITECTURE.md Option C 전환 계획의 setup 단계 완료. `exec python3 "$SETUP_PY"` 방식으로 `setup.sh` 의존성 제거. PATH 자동 추가는 rc 파일이 있으면 직접 쓰고, 없으면 안내만 출력.
**검증 방법:** `python3 -m pytest tests/unit/test_install.py` 37개 통과; `bash tests/unit/commands/setup_*.sh` 전체 통과.
---

## [2026-03-13] docs(test): update test-strategy and setup coverage for Python implementation [#57]
**변경 요약:** `test-strategy.md` §1·§11·§12 실제 구현 구조 반영 (`tests/characterization/` → `tests/unit/test_*.py`); `test-coverage/setup.md` Bash ST1-ST6 → Python S1-S15 분기 매트릭스로 전면 재작성.
**의사결정:** 이전 세션에서 `tests/characterization/`를 계획했으나 실제 구현은 `tests/unit/test_*.py`에 직접 추가됨 — 문서가 구현과 일치하도록 정정.
**검증 방법:** 문서와 `tests/unit/test_setup.py` 테스트 클래스명 대조 확인.
---

## [2026-03-12] fix(make): require agent after ensure_setup, remove skip branches [#54]
**변경 요약:** COMMAND-SPEC(에이전트 필수, fallback 없음)에 맞춰 ensure_setup() 직후 에이전트 미설정 시 Error 후 exit 1. spec/skeleton 단계의 "에이전트 미설정 — 건너뜀" else 분기 제거하여 파이프라인이 항상 Step 2·3를 실행하도록 함.
**의사결정:** setup 완료 시점에 에이전트가 반드시 있다는 계약을 코드로 강제. agent_cmd는 진입 시 한 번만 조회하고, 비어 있으면 즉시 종료.
**검증 방법:** 에이전트 미설정 상태에서 `boj make 1000` → "에이전트가 설정되지 않았습니다" 메시지 및 exit 1.

---

## [2026-03-12] fix(make): add Step 3 (skeleton) and Step 4 (open) to pipeline [#54]
**변경 요약:** boj make가 Step 2(spec) 다음에 Step 5(cleanup)만 호출하던 문제 수정. Step 3 `generate_skeleton()`(run_agent make-skeleton), Step 4 `open_editor()` 호출 추가. 진행 메시지를 [1/6]~[6/6]으로 통일.
**의사결정:** `generate_skeleton`은 `run_agent(..., "make-skeleton")`으로 구현(에이전트가 Solution/Parse 생성). `open_editor(problem_dir, editor_cmd)`를 make.py에 추가해 설정된 editor로 폴더 오픈. --no-open이거나 editor 미설정 시 Step 4 스킵.
**검증 방법:** `python3 -m pytest tests/unit/test_make.py -v` 및 기존 통합 테스트. 수동: `boj make <N>` 후 Solution/Parse 생성 및 에디터 오픈 여부 확인.

---

## [2026-03-12] fix(make): respect solution_root in fetch_problem [#54]
**변경 요약:** `base_dir`을 계산만 하고 쓰지 않던 버그 수정. `fetch_problem()`에 `base_dir` 인자 추가하고 CLI에서 `solution_root` 설정값을 전달해 문제 폴더가 설정된 solution root 아래 생성되도록 함. config 키 `solution_root`/`prog_lang`으로 통일.
**의사결정:** core/make.py에 `base_dir` 파라미터 추가(기본 None → cwd). CLI는 `solution_root` 키를 사용하고, config 모듈에서 예전 `boj_solution_root` 파일명을 하위호환으로 처리.
**검증 방법:** 기존 단위/통합 테스트는 `problem_dir`를 명시해 호출하므로 회귀 없음. `solution_root` 설정 시 해당 경로 아래에 문제 폴더 생성되는지 수동 확인.

---

## [2026-03-12] feat(make): fetch_problem, generate_readme 구현 + 모듈 정규화 [#54]
**변경 요약:** `src/core/make.py`에 `fetch_problem`, `generate_readme`, `run_setup`, `run_agent` 구현. `src/core/client.py` (이미지 처리 포함), `src/core/normalizer.py` 독립 모듈 생성. `src/cli/boj_make.py` CLI 래퍼 생성. 라이브 테스트 4개 문제 (1516, 16957, 10799, 10951) + 이미지 다운로드 검증.
**의사결정:** `src/lib/` 레거시는 그대로 두고 `src/core/`에 로직을 직접 복사 (re-export 없음). BOJ 403 방지를 위해 브라우저 수준 User-Agent + Accept 헤더 추가. `--run-live` / `--run-agent` conftest 마커로 네트워크/에이전트 테스트 격리.
**검증 방법:** `python3 -m pytest tests/unit/ -v` → 181 passed, 1 skipped. `python3 -m pytest tests/integration/test_make_py.py -v` → 7 passed. `python3 -m pytest tests/integration/test_live_fetch.py -v --run-live` → 22 passed.

---

## [2026-03-12] feat(install): Python 설치 스크립트 구현 [#47]
**변경 요약:** `scripts/install.py` 신규 생성. clone → `python3 scripts/install.py`로 설치 완료. `src/setup-boj-cli.sh` deprecated 처리.
**의사결정:** standalone 스크립트로 구현 (내부 모듈 import 없음). 이유: 설치 시점에 모듈 경로 미확정. 순수 함수 + 명시적 path 파라미터로 테스트 용이성 확보. `~/.config/boj/root` 하위호환 유지.
**검증 방법:** `python3 -m pytest tests/unit/test_install.py -v` → 32개 통과

---

## [2026-03-12] feat(tests): Python 통합 테스트 러너 구현 [#50]
**변경 요약:** `tests/run_tests.py` 신규 생성. pytest(.py)와 bash(.sh) 테스트를 함께 자동 발견·실행. CI(`ci.yml`)를 `run_tests.sh` → `run_tests.py`로 교체.
**의사결정:** `run_tests.sh`는 `*.sh` 파일만 발견하므로 Python pytest 파일을 실행하지 못함. Python 러너는 두 종류를 모두 처리하며 --unit/--integration/--e2e 플래그를 동일하게 지원. 기존 `run_tests.sh`는 레거시로 유지.
**검증 방법:** `python3 tests/run_tests.py --unit` → 24개 통과 0개 실패
---

## [2026-03-12] feat(setup): Python setup 명령어 구현 [#46]
**변경 요약:** `src/commands/setup.sh` (284줄 Bash)를 대체하는 Python `src/cli/boj_setup.py` 구현. 6단계 대화형 마법사 + 비대화형 옵션(--check, --root, --lang, --username, --editor, --agent). 세션 쿠키 로직은 이슈 스코프 외로 제외.
**의사결정:** `prompter: Callable[[str], str]` 의존성 주입 패턴으로 대화형 로직 100% 단위 테스트 가능하게 설계. CLI 옵션은 이슈 기준(--root, --lang)으로 하되 내부적으로 config.py 키(boj_solution_root, prog_lang)를 사용. gh CLI 미설치 시 설치 안내 후 다른 옵션으로 fallback. agent 없음 선택 시 gemini 무료 추천 (config.py AGENT_COMMANDS 기준).
**검증 방법:** `PYTHONPATH=. python3 -m pytest tests/unit/test_setup.py -v`, `PYTHONPATH=. python3 -m src.cli.boj_setup --check`, `PYTHONPATH=. python3 -m src.cli.boj_setup --lang python`

---


## [2026-03-10] refactor(config): Python config 모듈 구현 [#45]
**변경 요약:** Bash `config.sh`를 대체하는 Python `src/core/config.py` 구현. config key 구조 변경(root 분리, session 제거, key 이름 변경), setup_done flag, agent 커맨드 매핑, git config 연동 추가.
**의사결정:** Option C 구조(src/core/)에 배치. 기존 config.sh는 Bash 명령어 전환 완료까지 병행 유지. 환경변수 매핑은 BOJ_PROG_LANG, BOJ_SOLUTION_ROOT 등 새 이름으로 통일하되 레거시(BOJ_ROOT, BOJ_LANG)는 Bash 측에서만 사용. 지원 언어는 런타임 지원 기준 java/python만.
**검증 방법:** `PYTHONPATH=. python3 -m pytest tests/unit/test_config.py -v` (31 passed), 전체 `tests/unit/` (38 passed, 1 skipped)

---

## [2026-03-09] refactor(docs): 문서 통합 및 코드 괴리 해소 [#42]
**변경 요약:** 문서 ↔ 코드 괴리 분석 후 정리. 실체 없는 언어 스텁 7개 디렉터리 삭제, 불필요 문서 3개 삭제, 레거시 픽스처 삭제, test_cases.json 형식 수정, Option C 아키텍처·브랜치 전략 확정, COMMAND-SPEC.md·ARCHITECTURE.md 신규 작성.
**의사결정:** 이전 분석이 "미구현"이라 판단한 플래그(--no-open, --image-mode, --output, --editor, --force, --no-stats, --message, BOJ_CONFIG_DIR)가 전부 구현되어 있음을 코드 리딩으로 발견. 잘못된 커밋을 revert하고 실제 괴리(test_cases.json flat→nested, 삭제된 스텁/픽스처 참조)만 수정. templates/ 구조는 Option C(boj_core/runners/ + reference/) 확정.
**검증 방법:** 각 명령어 코드(src/commands/*.sh)와 문서 1:1 대조, `git diff --stat`

---

## [2026-03-08] fix(client): remove session dep, fix whitespace, remove --password arg [#24]
**변경 요약:** `_load_session()` 제거 (BOJ 문제 페이지 공개 접근 가능), `get_text(strip=True)` → `get_text(separator="\n").strip()` whitespace 보존 수정, `--password` argparse 인자 및 `setup.sh` 옵션 파싱 완전 제거.
**의사결정:** Cursor bot 보안 리뷰 + BOJ 비인증 fetch 확인으로 세션 로직 불필요 판명. `get_text(strip=True)`는 각 텍스트 노드를 개별 strip 후 join해 내부 개행/공백을 손실시킴; `separator="\n"`으로 수정. `--password` 커맨드라인 인자는 `ps aux`에 노출되므로 `BOJ_LOGIN_PASSWORD` env var 전용으로 전환.
**검증 방법:** `python3 tests/unit/test_boj_client.py -v` (7 passed, 1 skipped)
---

## [2026-03-08] fix(ci): pip deps, git config, CWD side-effect, credential exposure [#23]
**변경 요약:** PR #24 CI 4종류 실패 수정 — pip install 누락, git global config 체크, make_branches.sh CWD 오염, setup.sh 비밀번호 커맨드라인 노출.
**의사결정:** (1) ci.yml에 `pip install -r requirements.txt` 추가. (2) `commit.sh` git email 체크를 `--global` 제거 → local 우선으로 변경. (3) `_run_make`를 `(...)` subshell로 래핑해 teardown 후 getcwd 오류 방지. (4) `--password` 인자 제거 후 `BOJ_LOGIN_PASSWORD` env var로 전달해 `ps aux` 노출 차단.
**검증 방법:** `./tests/run_tests.sh --unit` 전체 통과, `bash tests/unit/commands/make_branches.sh`, `bash tests/unit/commands/commit_branches.sh`
---

## [2026-03-08] refactor(client): urllib/HTMLParser → requests+BeautifulSoup 전환 [#13]
**변경 요약:** `boj_client.py`에서 stdlib(`urllib`, `http.cookiejar`, `html.parser`) 제거 후 `requests`+`beautifulsoup4`로 교체. 커스텀 HTMLParser 서브클래스 3개(`_BaseParser`, `_TextParser`, `_InnerHTMLParser`) 및 추출 헬퍼 함수 3개 삭제. `requirements.txt` 신규 생성.
**의사결정:** 기존 HTMLParser 기반 구현은 64줄짜리 `_BaseParser` + 2개 서브클래스로 유지보수 부담이 컸음. BeautifulSoup `find(id=...)` + `get_text()`/`decode_contents()`로 동일 기능을 훨씬 간결하게 표현 가능. `requests.Session`은 302 응답 Set-Cookie를 자동 처리하므로 로그인 로직도 단순화됨.
**검증 방법:** `python3 tests/unit/test_boj_client.py -v` (7개 로컬 테스트 모두 통과), `parse_problem` 픽스처 직접 검증(`title == '두 수의 합'`, `len(samples) == 2`), `./tests/integration/test_boj_run.sh` (PASS)

---

## [2026-03-08] docs(rewrite): Python 전환 계획 문서화 및 브랜칭 전략 결정 [#23]
**변경 요약:** 전체 코드베이스 분석 후 Shell→Python 전환 계획(`docs/rewrite-plan.md`)과 브랜칭 전략(`docs/branching-recommendation.md`) 작성
**의사결정:**
- **전환 방향**: Shell+Python 혼합 구조의 유지보수 한계(중복 trap 로직, config 이중화, PTY 없이 테스트 불가, `set -e` 회피 패턴)를 근거로 전체 CLI를 Python으로 이전하기로 결정. `boj_client.py`/`boj_normalizer.py`(issue #13)가 올바른 방향임을 확인.
- **이전 순서**: 한 번에 전부 바꾸지 않고 수직 슬라이스(vertical slice) 방식 채택. `boj run`(Java only) → `boj make` → `boj submit` → 나머지 순서로 명령어별 PR.
- **패키지 구조**: `boj_core/`(순수 로직, CLI/색상/대화 없음) + `boj_cli/`(얇은 래퍼) 이층 구조. `boj_core`는 100% 단위 테스트 가능, 미래 MCP 노출도 코어 변경 없이 가능.
- **브랜칭**: Option B 채택 — issue #23 테스트 인프라(fixtures, test_helper, test_boj_client.py)를 main에 머지 후 `rewrite/python-core` 브랜치 생성. issue #23 작업을 버리는 Option C는 배제.
- **검토한 대안**: Option A(test/issue-23 HEAD에서 바로 분기)는 이슈 경계가 불명확해서 PR 리뷰가 어렵다는 이유로 배제.
**검증 방법:** `cat docs/rewrite-plan.md`로 10개 섹션 존재 확인, `cat docs/branching-recommendation.md`로 옵션 3개 및 권장안 확인, `git diff --stat`로 docs/ 외 변경 없음 확인

---

## [2026-03-08] test(coverage): boj_client HTTP fetch/login 단위 테스트 및 픽스처 인프라 추가 [#23]
**변경 요약:** 로컬 HTTP 서버 기반 `test_boj_client.py` 작성, 4개 문제 픽스처(1000/6588/9495/99999) 추가, `test_helper.sh` 공통 헬퍼 도입, `setup` 명령에 비대화형 플래그(`--set-key`) 추가
**의사결정:** 네트워크 없이 재현 가능한 테스트를 위해 `BOJ_CLIENT_TEST_HTML`(HTML 픽스처 직접 주입) + `BOJ_BASE_URL_OVERRIDE`(로컬 서버 URL로 교체) 두 가지 격리 메커니즘을 병행 사용. 로컬 HTTP 서버 방식은 쿠키/헤더 동작까지 검증 가능해 단순 파일 주입보다 신뢰도가 높음. `boj_login()`은 `BOJ_LOGIN_URL_OVERRIDE`로 격리.
**검증 방법:** `python -m pytest tests/unit/test_boj_client.py -v` 전체 통과

---

## [2026-03-02] chore(docs): devlog.md → DEVLOG.md 리네임 및 구조화 [#14]
**변경 요약:** 서사형 devlog를 날짜/변경요약/의사결정/검증 단위의 구조화 변경 로그로 전환, /commit 스킬에 DEVLOG 업데이트 단계 추가
**의사결정:** 서사형(여정 블로그) 형식은 특정 변경이 언제·왜 이루어졌는지 추적이 어렵다. 구조화 형식으로 전환하고 /commit 흐름에 자동 기록 단계를 포함(옵션 B)하여 갱신 루틴을 강제한다. 옵션 A(post-commit hook)는 hook 실패 시 커밋이 차단될 위험이 있고, 옵션 C(check_devlog.sh)는 강제력이 약해 선택하지 않았다.
**검증 방법:** `git log --follow docs/records/DEVLOG.md`로 히스토리 보존 확인, /commit 스킬 실행 후 DEVLOG 항목 자동 추가 확인

---

## [2026-03-02] refactor(make): BOJ 문제 수집·정규화·시그니처 생성을 결정적 로컬 파이프라인으로 교체 [#13]
**변경 요약:** boj make의 에이전트 의존 로직(문제 수집/README 생성/Parse 시그니처 추론)을 결정적 로컬 파이프라인 4개 레이어로 교체
**의사결정:** 기존 boj make는 에이전트 프롬프트에 모든 판단을 위임해 같은 문제번호로도 결과가 달라졌다. 수집/정규화/시그니처생성/프롬프트최소화 레이어를 코드로 구현해 에이전트 의존도를 줄이고 결정성을 보장한다.
**검증 방법:** 동일 문제번호로 boj make 2회 실행 후 결과 동일성 확인, 통합 테스트 통과

---

## [2026-03-01] feat(templates): BOJ 지원 언어 메타데이터 기반 템플릿 확장 [#11]
**변경 요약:** templates/languages.json 도입, 12개 언어 템플릿(C/C++/Java/Python/Kotlin/Go/Rust/JS/TS/Ruby/Swift/Scala) 추가
**의사결정:** 언어별 확장자·컴파일·실행·스켈레톤을 수작업 나열 대신 메타데이터 파일(languages.json)로 관리. 새 언어 추가 시 JSON 한 항목 추가로 자동 지원 가능. boj make --lang <lang> 선택 가능.
**검증 방법:** `boj make <N> --lang python`, `boj make <N> --lang kotlin` 등 주요 언어 정상 동작 확인

---

## [2026-03-01] chore(cleanup): baekjoon/ 레거시 폴더 제거 및 의존성 정리 [#10]
**변경 요약:** Cursor 시절 레거시 baekjoon/ 폴더 삭제, find_boj_root()의 baekjoon/template/Test.java 인식 로직 제거
**의사결정:** src/boj가 BOJ_ROOT 환경변수·~/.config/boj/ 기반으로 동작하므로 baekjoon/ 디렉터리 탐색 코드가 불필요하다. 레거시 경로 인식을 남겨두면 구 저장소 clone이 있는 환경에서 오탐 가능성이 있어 제거한다.
**검증 방법:** baekjoon/ 삭제 후 `boj run/make/commit` 정상 동작, README baekjoon/ 참조 제거 확인

---

## [2026-03-01] test(all): 모든 명령어 정상+엣지케이스 테스트 추가 [#9]
**변경 요약:** make/run/commit/open/review/submit 전 명령어에 정상+실패/엣지케이스 통합·단위 테스트 추가
**의사결정:** 외부 의존성(BOJ API/git/브라우저)은 mock/fixture로 안정화해 CI에서 재현 가능하게 한다. tests/integration/(명령별), tests/unit/(개별 함수), tests/fixtures/(픽스처) 구조를 표준화.
**검증 방법:** `./tests/run_tests.sh --all` 전체 통과

---

## 프로젝트 여정 (Legacy)

> Cursor 시절부터 boj-agent CLI로 발전한 1~10단계 여정을 서사형으로 기록합니다.
> 아래 내용은 수정 없이 보존됩니다.

---

# 🤖 AI를 활용한 알고리즘 문제 풀이 자동화 여정

> 백준 알고리즘 문제 풀이 환경을 AI(Cursor)를 활용해 자동화한 과정을 기록합니다.

---

## 📌 배경: 왜 자동화가 필요했나?

백준(Baekjoon) 온라인 저지는 플랫폼 내에서 테스트 코드 실행이 불가능합니다. 
따라서 매번 문제를 풀 때마다:

1. 폴더 생성
2. 문제 내용 복사
3. 입력 파싱 코드 작성
4. 테스트 케이스 직접 실행
5. 제출용 코드 정리

이런 반복적인 작업이 필요했고, **알고리즘 구현에만 집중하고 싶다**는 생각에서 자동화를 시작했습니다.

---

## 🔄 진화 과정

### 1단계: 기본 템플릿 방식

**접근**: 템플릿 폴더를 만들고 수동으로 복사해서 사용

```
template/
├── Main.java       # 직접 수정 필요
├── Solution.java   # 직접 수정 필요
├── Test.java       # 직접 수정 필요
├── run.sh
└── test.sh
```

**문제점**:
- 매번 폴더명 직접 작성
- README.md 수동 작성
- Main.java, Test.java 매번 수정 필요
- 입력 형식 파악 후 직접 파싱 코드 작성

---

### 2단계: 스크립트 자동화 (new_problem.sh)

**개선**: 백준 문제 링크만 입력하면 폴더 자동 생성

```bash
./new_problem.sh https://www.acmicpc.net/problem/10808
```

**구현**:
- `scrape_problem.py`: 백준 페이지에서 문제 내용 스크래핑
- `new_problem.sh`: 폴더 생성 + 템플릿 복사 + README 작성

**문제점**:
- 여전히 Main.java, Test.java 수동 수정 필요
- 입력 형식에 맞는 파싱 로직 직접 작성
- 스크래핑 스크립트 유지보수 필요

---

### 3단계: Agentic Workflow 도입 🚀

**핵심 아이디어**: 
> "템플릿을 복사하는 게 아니라, AI가 문제를 분석해서 적합한 코드를 직접 생성하면 어떨까?"

**변화**:

| 기존 | Agentic 방식 |
|------|-------------|
| 템플릿 복사 후 수동 수정 | AI가 문제 분석 → 코드 자동 생성 |
| Main.java 직접 파싱 구현 | AI가 입력 형식 분석하여 생성 |
| Test.java 직접 수정 | JSON 파일에 케이스만 추가 |
| 반복적인 보일러플레이트 | 알고리즘 구현에만 집중 |

**구현**:

1. **`.cursorrules` 파일 생성**
   - AI가 참조하는 가이드라인
   - 폴더 구조, 파일 형식, 네이밍 규칙 정의
   - 문제 생성 / 코드 리뷰 워크플로우 정의

2. **JSON 기반 테스트 시스템**
   ```json
   {
     "testCases": [
       {"id": 1, "input": "baekjoon", "expected": "1 1 0 0 ..."}
     ]
   }
   ```
   - Test.java는 수정 불필요 (범용 테스트 러너)
   - 테스트 케이스는 JSON 파일에만 추가

3. **AI 도움 차단 (VSCode 이동)**
   - 문제 환경 생성 후 `code .` 실행
   - VSCode에서 AI 도움 없이 직접 풀이

---

### 4단계: 역할 분리 강화 🎯

**핵심 아이디어**:
> "Solution은 순수 알고리즘만 담당하고, 파싱은 Main과 Test가 담당해야 한다"

**문제점 (3단계)**:
```java
// Solution.java - 파싱 + 알고리즘이 섞여있음
public String solve(String input) {
    String[] lines = input.split("\n");
    int n = Integer.parseInt(lines[0]);
    // ... 파싱 로직
    // ... 알고리즘 로직
}
```

**개선 (4단계)**:
```java
// Main.java - 파싱 담당
int n = Integer.parseInt(br.readLine().trim());
int[] arr = parseArray(br.readLine());
int x = Integer.parseInt(br.readLine().trim());
int result = sol.solve(n, arr, x);  // 파싱된 값 전달

// Solution.java - 순수 알고리즘만
public int solve(int n, int[] arr, int x) {
    // 파싱 로직 없이 알고리즘만 구현
    return 0;
}

// Test.java - parseAndCallSolve()로 JSON 파싱
private static String parseAndCallSolve(Solution sol, String input) {
    String[] lines = input.split("\n");
    int n = Integer.parseInt(lines[0].trim());
    int[] arr = Arrays.stream(lines[1].split(" ")).mapToInt(Integer::parseInt).toArray();
    int x = Integer.parseInt(lines[2].trim());
    return String.valueOf(sol.solve(n, arr, x));
}
```

**장점**:

| 항목 | Before (String input) | After (개별 파라미터) |
|------|----------------------|---------------------|
| 역할 분리 | 파싱+알고리즘 혼재 | 명확한 분리 |
| 가독성 | solve(String) → 뭐가 들어오는지 모름 | solve(int n, int[] arr, int x) → 바로 파악 |
| 테스트 | 문자열로 조합해서 전달 | 값을 직접 전달 |
| 재사용성 | 파싱 로직이 Solution에 종속 | Solution은 어디서든 호출 가능 |

---

### 5단계: 정확한 문제 내용 가져오기 🔍

**문제점**:
- AI가 문제 내용을 기억에 의존해서 작성
- 부정확한 문제 설명이 README에 들어가는 경우 발생

**개선**:
- `.cursorrules`에 명시: **"반드시 웹 검색(web_search)을 통해 실제 백준 문제 내용을 확인한 후 작성"**
- 기억에 의존하지 않고 정확한 문제 설명 보장

```markdown
#### README.md
**중요: 반드시 웹 검색(web_search)을 통해 실제 백준 문제 내용을 확인한 후 작성할 것!**
**기억에 의존하지 말고 정확한 문제 설명을 가져와야 함.**
```

---

### 6단계: 제출 관련 파일 분리 📁

**핵심 아이디어**:
> "제출/리뷰 관련 파일을 별도 폴더로 분리하여 구조를 명확하게"

**변경 (6단계)**:
```
문제폴더/
├── README.md         # 문제 설명
├── Solution.java     # 내 풀이 (알고리즘)
├── Main.java         # 입력 파싱 (로컬용)
├── Test.java         # 테스트 러너 (로컬용)
├── test_cases.json   # 테스트 케이스
├── run.sh, test.sh   # 실행 스크립트
│
└── submit/           # 📁 제출 관련 파일 분리!
    ├── Submit.java   # 백준 제출용 코드
    └── REVIEW.md     # 코드 리뷰
```

**장점**:
- 풀이 파일과 제출 파일의 역할 명확화
- 폴더 구조만 봐도 어떤 파일이 어디에 있는지 직관적
- Git 커밋 시 submit 폴더만 따로 관리 가능

---

### 7단계: 스크립트 개선 🧹

**개선 내용**:
- `run.sh`, `test.sh` 실행 후 항상 `.class` 파일 삭제
- 컴파일 실패 시에도 삭제되어 폴더가 깔끔하게 유지

```bash
#!/bin/bash
javac Main.java Solution.java && java Main
rm -f *.class  # 항상 삭제
```

---

### 8단계: 템플릿 간소화 · run.sh 통합 · Parse 분리 🧩

**핵심 아이디어**:
> "Main/run/test는 제거하고, 테스트는 루트 하나의 run.sh로. 테스트 공통 로직은 template에 두고, 문제별로 Parse만 구현"

**변경 사항**:

| 구분 | Before | After |
|------|--------|--------|
| 문제 폴더 | Main.java, Test.java, run.sh, test.sh 포함 | **Parse.java** + Solution, README, test_cases.json 만 |
| 테스트 실행 | `cd [폴더]` 후 `./test.sh` | **루트에서** `./run.sh [문제번호]` |
| 테스트 로직 | 문제마다 Test.java 전체 복사, parseAndCallSolve만 수정 | **template/Test.java** 공통 사용, **Parse.java**가 ParseAndCallSolve 구현 |

**구조**:
- **template/**: `ParseAndCallSolve.java`(인터페이스), `Test.java`(공통 러너), Solution·test_cases 예시. Main·run·test 제거.
- **루트 run.sh**: `./run.sh 4949` → 해당 문제 폴더로 이동 후 template + Solution + Parse 컴파일·실행.
- **문제 폴더**: `Parse.java`에서 `parseAndCallSolve(Solution sol, String input)` 만 구현.

**장점**:
- 보일러플레이트 감소 (Main·Test·스크립트 복사 없음)
- 테스트 실행 방식 통일 (commit.sh와 같은 문제번호 인자)
- Parse 한 파일만 수정하면 되어 유지보수 용이

---

### 9단계: test/ 폴더 분리 · 테스트도 커밋 📂

**핵심 아이디어**:
> "중심은 Solution.java. 테스트(Parse, test_cases)는 test/로 모아 두고 둘 다 커밋해서, 필요하면 테스트까지 재현 가능하게. submit/을 둔 것처럼(백준에 그대로 붙여넣기용), test/는 '로컬 검증 재현용'."

**변경 사항**:
- 문제 폴더 루트의 `Parse.java`, `test_cases.json` → **test/Parse.java**, **test/test_cases.json** 으로 이동
- **test/** 폴더만 보면 "이 문제의 테스트 설정"이 한눈에 들어옴
- .gitignore·commit.sh에서 **test/** 도 추적·커밋 대상으로 포함 (예: `!*/test/`, `!*/test/Parse.java`, `!*/test/test_cases.json`, commit 시 test/ 추가)
- template/Test.java는 `test/test_cases.json` 경로로 읽도록 수정, run.sh는 `test/Parse.java` 기준으로 컴파일·실행

**정책 (저장소에서 무엇을 추적할지)**:
- **Solution.java** — 풀이의 중심, 반드시 커밋
- **submit/** — 백준에 그대로 붙여넣기용(Submit.java, REVIEW.md), 커밋
- **test/** — 필요 시 테스트까지 재현 가능하도록 Parse.java, test_cases.json 커밋
- **정책·설계 결정** — 별도 POLICY.md 없이, **DEVLOG에 단계별로 기록** (이렇게 하면 "왜 이렇게 바꿨는지"가 이력과 함께 남음)

---

### 10단계: boj CLI — 어디서든 실행 가능한 명령어 🖥️

**고민한 점**: `run.sh`·`commit.sh`를 쓰려면 매번 백준 폴더로 들어가야 해서 불편했다. "어디서든 `boj run 4949`처럼 쓰고 싶다" → 그러려면 **실행 시점에 baekjoon(또는 algorithm) 폴더를 어떻게 찾을지**가 문제였다.

**검토한 방안**:
- **A. 전체 디스크 탐색** (`find`로 run.sh 검색): 설정 없이 어디서든 가능하지만 느리고, clone이 여러 개면 어느 쓸지 불명확.
- **B. 현재 디렉터리에서 위로 올라가며 `baekjoon/run.sh` 포함 디렉터리 찾기**: 설정 없이, algorithm 아래 어디서든 동작·빠름. 다만 `~/Documents` 등 repo 밖에서는 실패.
- **C. algorithm(또는 baekjoon) 안에서만 허용**: 구현은 단순하지만 "어디서든"이 아니므로 요구와 맞지 않음.
- **D. 한 번만 경로 설정** (환경변수 `BOJ_ROOT` 등): 진짜 어디서든 사용 가능하고 빠르며 명확. 대신 최초 1회 설정 필요.

**선택**: **B + D 혼합**.  
우선 현재 디렉터리에서 위로 올라가며 `baekjoon/run.sh`가 있는 디렉터리를 찾고, 없으면 환경변수 `BOJ_ROOT`(algorithm 루트 또는 baekjoon 경로)를 사용. 전체 탐색은 하지 않음.

**구현**:
- **boj** 단일 스크립트: 위 방식으로 baekjoon 루트 확정 후, run/commit 로직을 **인라인**으로 수행. (run.sh, commit.sh 제거)
- **setup-boj-cli.sh**: 한 번 실행 시 `~/bin/boj` 설치, **레포 경로(BOJ_ROOT)** 및 PATH를 .zshrc에 저장 → 어디서든 `boj`만 사용.
- repo 탐지: `run.sh` 대신 `baekjoon/template/Test.java` 존재 여부로 판별.
- 서브커맨드: `boj run`, `boj commit`, `boj make`, `boj open`, `boj review`.

**run.sh / commit.sh 제거 및 boj 통합**  
- 처음에는 boj가 `run.sh`, `commit.sh`를 호출하는 래퍼였으나, 사용처가 boj 하나로 통일되므로 **run/commit 로직을 boj 안으로 인라인**하고 run.sh, commit.sh는 삭제함.
- 설치 시 **레포 주소(경로)** 만 저장해 두면 되므로, setup-boj-cli.sh에서 BOJ_ROOT를 한 번 설정하면 어디서든 `boj`만 쓰면 됨.

**boj make / boj review — Cursor Agent CLI 사용**  
- **make**: `agent`가 있으면 `agent chat -f -p "..."` 로 환경 생성. 없으면 baekjoon을 Cursor로 열고 클립보드 안내 → 사용자가 채팅에 붙여넣으면 AI가 폴더 생성 후 **해당 폴더에서 `code .`만 실행** (문제 풀 때 AI 없어야 하므로 VS Code만 사용).  
- **review**: `agent`가 있으면 해당 문제 폴더에서 agent chat. 없으면 **문제 폴더를 VS Code로** 열고 채팅 안내.  
- agent 호출 시 `-f -p`(force, print)로 자동 승인·비대화형 동작.

**문제 폴더는 무조건 code .**  
- 풀 때 AI 없이 풀어야 하므로, 생성된 문제 폴더를 여는 에디터는 **항상 `code .`(VS Code)**. Cursor가 아닌 VS Code로 열어서 AI 도움 없이 구현하도록 함.

**전역 사용 보장 (~/.config/boj/root)**  
- Cursor 터미널 등에서 .zshrc가 로드되지 않으면 BOJ_ROOT가 비어 있을 수 있음.  
- 설치 시 레포 경로를 `~/.config/boj/root`에 저장하고, boj 실행 시 BOJ_ROOT가 없으면 이 파일에서 읽어서 사용 → 어디서든 `boj` 동작 보장.

**boj open**  
- 문제 풀기를 시작할 때 **해당 문제 폴더만** 에디터 루트로 열기: `boj open 4949`.  
- 폴더가 없으면 `boj make`를 먼저 실행한 뒤, "생성 후 다시 boj open 4949" 안내.

---

## 📊 최종 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│  1. 문제 환경 생성                                           │
│     boj make 4949  (또는 Cursor 채팅: "백준 4949번 환경 만들어줘") │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. AI가 자동 생성                                           │
│     📁 4949-균형잡힌-세상/                                    │
│     ├── README.md, Solution.java                             │
│     └── test/ (Parse.java, test_cases.json)                 │
│     → boj open 4949 로 해당 폴더만 루트로 열기 (cursor/code)  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 에디터에서 알고리즘만 구현 (AI 도움 없이)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 테스트 & 제출                                             │
│     boj run 4949  / "제출해줘" → submit/Submit.java → 백준 제출 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. 리뷰 & 커밋                                               │
│     boj review 4949  또는 "리뷰해줘" → submit/REVIEW.md        │
│     boj commit 4949  → GitHub (필요한 파일만 자동 커밋)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 최종 폴더 구조

```
baekjoon/
├── .cursorrules        # AI 가이드라인
├── .gitignore          # 필요한 파일만 업로드
├── boj                 # CLI 통합 (run/commit/make/open/review, 설치 시 레포 경로 저장)
├── setup-boj-cli.sh    # boj 한 번 설치 — BOJ_ROOT·PATH 설정
├── README.md           # 사용 가이드
├── template/           # 공통 템플릿 (ParseAndCallSolve, Test 등)
│   └── submit/         # 제출 템플릿
│
├── 3273-두-수의-합/     # 문제별 폴더
│   ├── README.md       # ✅ 업로드
│   ├── Solution.java   # ✅ 업로드 (중심)
│   ├── test/           # ✅ 업로드 (테스트 재현용)
│   │   ├── Parse.java
│   │   └── test_cases.json
│   │
│   └── submit/         # ✅ 업로드 (백준 붙여넣기용)
│       ├── Submit.java
│       └── REVIEW.md
│
└── 1475-방-번호/
    └── ...
```

---

## 💡 핵심 학습 포인트

### 1. Agentic Workflow의 힘
단순히 "AI에게 코드 작성 요청"이 아닌, **AI가 스스로 판단하고 적절한 행동을 수행**하도록 설계

### 2. .cursorrules 활용
프로젝트별 컨텍스트와 규칙을 AI에게 전달하여 일관된 결과물 생성

### 3. 인간과 AI의 역할 분리
- **AI**: 반복적/보일러플레이트 작업 (환경 세팅, 파싱, 리뷰)
- **인간**: 핵심 알고리즘 설계 및 구현 (AI 도움 없이)

### 4. 피드백 루프 구축
풀이 → 제출 → 리뷰 → 학습 포인트 도출 → 다음 문제 추천

### 5. 관심사의 분리 (Separation of Concerns)
- **test/Parse.java**: JSON 입력 파싱 (테스트용)
- **Solution.java**: 순수 알고리즘 (비즈니스 로직)
- **template/Test.java**: 테스트 실행 (검증 담당, 공통)

이 원칙은 클린 아키텍처의 핵심이며, 코드의 테스트 용이성과 재사용성을 높임

---

## 📈 효과

| 항목 | Before | After |
|------|--------|-------|
| 환경 세팅 시간 | 5-10분 | 10초 |
| 수정 필요 파일 | 3-4개 | 1개 (Solution.java) |
| Solution 역할 | 파싱 + 알고리즘 | 순수 알고리즘만 |
| solve() 시그니처 | solve(String input) | solve(int n, int[] arr, int x) |
| 테스트 케이스 관리 | 코드에 하드코딩 | JSON 파일 |
| 코드 리뷰 | 없음 | submit/REVIEW.md 자동 생성 |
| 제출 코드 | 수동 병합 | submit/Submit.java 자동 생성 |
| GitHub 업로드 | 수동 | 스크립트 자동화 |
| 문제 설명 | AI 기억 의존 | 웹 검색으로 정확히 |
| 폴더 구조 | 모든 파일 혼재 | submit/ 폴더로 분리 |

---

## 📝 기술 노트: run.sh EXIT trap 이력

`run.sh`의 Java/Python 블록에서 `normalize_test_cases` 임시 파일(`$normalized`)과 복원용 백업을 정리하기 위해 **단일 EXIT trap**을 사용한다.

- **trap 한 번**: 복원(`test_cases_orig.json` → `test_cases.json`) + `test_cases_orig.json`, `test_cases_normalized.json`, `$normalized` 삭제. 중간에 exit해도 원본 복구 보장.
- 과거에는 "첫 trap(임시 파일만 삭제) → 두 번째 trap으로 교체(복원+삭제)" 방식이었으나, trap 교체 전 exit 시 복원이 안 되는 이슈를 막기 위해 **단일 trap(복원+정리)** 로 통합(7db149e).

---

## 🔮 향후 개선 아이디어

1. **자동 난이도 분류**: 문제 태그/난이도 기반 폴더 정리
2. **통계 대시보드**: 풀이 현황, 취약 유형 분석
3. **스케줄링**: 매일 추천 문제 자동 생성
4. **다른 플랫폼 확장**: LeetCode, 프로그래머스 지원

---

## 🛠️ 사용 기술

- **AI**: Cursor (Claude 기반)
- **언어**: Java, Bash, Python
- **도구**: Git, VSCode

---

*작성일: 2026-02-11*  
*최종 수정: 2026-02-19 (boj open 추가, ~/.config/boj/root로 전역 사용 보장)*
