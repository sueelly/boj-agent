# pytest Characterization Test Strategy

> Python 재작성(`docs/rewrite-plan.md`) 전에 현재 Bash CLI의 동작을 pytest로 고정(freeze)하는 특성화 테스트 전략.
> 이 문서만 읽으면 누구든 일관된 스타일로 테스트를 작성할 수 있어야 한다.

---

## 1. 디렉터리 구조

```
tests/
  characterization/           # Python 재작성용 특성화 테스트 (신규)
    conftest.py               # 공통 fixture, marker 정의
    test_make.py              # boj make 동작 고정
    test_run.py               # boj run 동작 고정
    test_commit.py            # boj commit 동작 고정
    test_submit.py            # boj submit 동작 고정
    test_open.py              # boj open 동작 고정
    test_review.py            # boj review 동작 고정
    test_setup.py             # boj setup 동작 고정
  fixtures/                   # 공유 픽스처 데이터
    99999/                    # 기본 A+B (네트워크 불필요)
    1000/                     # 이미지 없는 문제
    6588/                     # 파싱 어려운 문제
    9495/                     # 파싱 어려운 문제
    <N>/                      # 추가 시 동일 구조
      raw.html                # BOJ HTML 원본 (record_fixture.sh로 캡처)
      problem.json            # boj_client.py 파싱 결과
      readme.md               # boj_normalizer.py 생성 결과
      Solution.java           # Java 풀이 (run/submit 검증용)
      solution.py             # Python 풀이
      test/
        Parse.java            # Java IO 어댑터
        parse.py              # Python IO 어댑터
        test_cases.json       # 테스트 케이스
    99999-fixture/            # 레거시 픽스처 (기존 Bash 테스트용, 전환 후 제거)
    boj_client/               # boj_client.py 단위 테스트용 (99999.html, problem.json 등)
  unit/                       # 기존 Bash 단위 테스트 (전환 기간 유지)
    test_boj_client.py        # Python 단위 테스트 (유지)
    test_boj_client.sh        # Bash 단위 테스트 (전환 후 제거)
    test_config.sh            # config 단위 테스트 (전환 후 제거)
    commands/                 # 커맨드별 Bash 단위 테스트 (전환 후 제거)
    lib/                      # 테스트 헬퍼 (test_helper.sh)
  integration/                # 기존 Bash 통합 테스트 (전환 기간 유지)
  e2e/                        # 기존 E2E (전환 기간 유지)
  harness/                    # 다언어 매트릭스 하네스 (Phase 1 범위 외)
  lib/                        # 테스트 유틸리티 (matrix_helpers.sh)
  run_tests.sh                # 전체 테스트 실행 스크립트
```

---

## 2. 픽스처 관례

### 2.1 디렉터리 레이아웃

모든 픽스처는 `tests/fixtures/{problem_num}/` 하위에 위치한다.

| 파일 | 역할 | 필수 |
|------|------|------|
| `raw.html` | BOJ에서 캡처한 HTML 원본 | 예 |
| `problem.json` | `boj_client.py`가 파싱한 결과 | 예 |
| `readme.md` | `boj_normalizer.py`가 생성한 README | 예 |
| `Solution.java` | Java 풀이 (컴파일/실행 검증용) | run/submit 테스트 시 |
| `solution.py` | Python 풀이 | run 테스트 시 |
| `test/Parse.java` | Java IO 어댑터 | Java run 테스트 시 |
| `test/parse.py` | Python IO 어댑터 | Python run 테스트 시 |
| `test/test_cases.json` | 입출력 테스트 케이스 | run 테스트 시 |

### 2.2 새 픽스처 추가

```bash
# 1. 실제 BOJ에서 캡처
scripts/record_fixture.sh <problem_num>

# 2. Solution/Parse 파일은 수동 작성
# 3. 이후 모든 파라미터라이즈드 테스트에 자동 편입
```

`record_fixture.sh`는 `tests/fixtures/{N}/` 하위에 `raw.html`, `problem.json`, `readme.md`를 저장한다.
Solution/Parse 파일은 사람이 작성한다 — 이들은 "정답"이 아니라 "동작하는 풀이"이다.

### 2.3 픽스처 불변성

픽스처 파일은 한 번 커밋하면 변경하지 않는다.
BOJ HTML 구조가 바뀌면 새 픽스처를 추가하고, 기존 것은 회귀 테스트로 유지한다.

---

## 3. 격리 규칙

### 3.1 네트워크 금지 원칙

특성화 테스트는 기본적으로 **네트워크 접속 없이** 실행되어야 한다.

격리를 위해 다음 환경변수를 사용한다:

| 환경변수 | 역할 |
|----------|------|
| `BOJ_CLIENT_TEST_HTML` | 설정하면 HTTP 요청 대신 로컬 HTML 파일을 읽음 |
| `BOJ_BASE_URL_OVERRIDE` | BOJ 기본 URL을 로컬 서버로 교체 |
| `BOJ_LOGIN_URL_OVERRIDE` | 로그인 URL을 로컬 서버로 교체 |
| `BOJ_CONFIG_DIR` | 설정 디렉터리를 임시 경로로 격리 |
| `BOJ_ROOT` | BOJ 작업 루트를 임시 디렉터리로 격리 |
| `BOJ_AGENT_CMD` | 에이전트를 mock 명령으로 교체 (예: `echo MOCK`) — **full 격리에서만 설정** |
| `BOJ_EDITOR` | 에디터를 `true`로 교체 (UI 방지) |

### 3.1.1 2단계 격리 정책

커맨드별로 에이전트 격리 수준을 분리한다:

| 격리 수준 | 대상 커맨드 | BOJ fetch | Agent | Marker |
|-----------|------------|-----------|-------|--------|
| **full** | run, commit, open, setup, submit | 우회 | 모킹 (`echo MOCK`) | 없음 |
| **agent** | make, review | 우회 | **실제 실행** (`BOJ_AGENT_CMD` 필요) | `@pytest.mark.agent` |

- **full 격리**: `BOJ_AGENT_CMD=echo MOCK`으로 에이전트를 우회. 폴더 구조, JSON 생성, exit code 등 구조적 동작만 검증.
- **agent 격리**: `BOJ_AGENT_CMD`를 설정하지 않아 실제 에이전트가 실행됨. signature_review.md 생성, 코드 리뷰 피드백 등 에이전트 동작을 검증.
- `@pytest.mark.agent` 테스트는 CI에서 기본 제외 (credential + 비용). 로컬 `/verify` 단계에서만 실행.
- `BOJ_AGENT_CMD`는 setup 커맨드에서 설정하며, 미설정 시 기본값을 사용한다.

### 3.2 conftest.py 공통 fixture

```python
# tests/characterization/conftest.py

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
BOJ_CMD = REPO_ROOT / "src" / "boj"


@pytest.fixture
def boj_env(tmp_path):
    """격리된 BOJ 환경을 생성한다.

    - src/, templates/, prompts/ 를 임시 디렉터리에 복사
    - git init
    - 환경변수 격리
    """
    for d in ("src", "templates", "prompts"):
        src = REPO_ROOT / d
        if src.exists():
            shutil.copytree(src, tmp_path / d)

    # 실행 권한
    for sh in (tmp_path / "src").rglob("*.sh"):
        sh.chmod(0o755)
    (tmp_path / "src" / "boj").chmod(0o755)

    # git init
    subprocess.run(
        ["git", "init", "-q"], cwd=tmp_path, check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=tmp_path, check=True, capture_output=True,
    )

    env = os.environ.copy()
    env.update({
        "BOJ_ROOT": str(tmp_path),
        "HOME": str(tmp_path),
        "BOJ_CONFIG_DIR": str(tmp_path / ".config" / "boj"),
        "BOJ_EDITOR": "true",
    })

    return tmp_path, env


@pytest.fixture
def fixture_path():
    """픽스처 경로 헬퍼."""
    def _get(problem_num: int | str) -> Path:
        p = FIXTURES_DIR / str(problem_num)
        assert p.exists(), f"Fixture not found: {p}"
        return p
    return _get


def run_boj(env, *args, input_text: str | None = None) -> subprocess.CompletedProcess:
    """격리 환경에서 boj CLI를 실행한다."""
    tmp_path = Path(env["BOJ_ROOT"])
    return subprocess.run(
        [str(tmp_path / "src" / "boj"), *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        input=input_text,
        timeout=30,
    )
```

### 3.3 파일시스템 격리

- 모든 테스트는 `tmp_path` (pytest 내장) 사용
- `HOME`을 `tmp_path`로 설정하여 `~/.config/boj/` 격리
- 테스트 간 상태 공유 없음 — 각 테스트는 독립적

---

## 4. 테스트 네이밍

```python
def test_<behavior>_when_<condition>(boj_env, fixture_path):
    """한 줄 한국어 설명."""
```

**예시:**

```python
def test_creates_problem_json_when_valid_html(boj_env, fixture_path):
    """유효한 HTML로 make 실행 시 problem.json이 생성된다."""

def test_exits_one_when_problem_dir_missing(boj_env):
    """문제 폴더가 없으면 exit 1로 종료한다."""

def test_passes_two_of_two_when_correct_solution(boj_env, fixture_path):
    """정답 Solution으로 run 실행 시 2/2 통과한다."""
```

---

## 5. AAA 패턴 (필수)

모든 테스트는 **Arrange / Act / Assert** 구조를 따른다.
주석으로 구분하지 않아도 되지만, 세 단계가 명확히 드러나야 한다.

```python
def test_creates_readme_when_valid_problem(boj_env, fixture_path):
    """유효한 문제 데이터로 make 실행 시 README.md가 생성된다."""
    # Arrange
    tmp_path, env = boj_env
    env["BOJ_CLIENT_TEST_HTML"] = str(fixture_path(99999) / "raw.html")

    # Act
    result = run_boj(env, "make", "99999", "--no-open")

    # Assert
    prob_dir = next(tmp_path.glob("99999*"), None)
    assert prob_dir is not None, "문제 디렉터리 미생성"
    assert (prob_dir / "README.md").exists(), "README.md 미생성"
```

---

## 6. 테스트 매트릭스

각 커맨드별로 **happy path / error path / edge case** 세 범주를 커버한다.
`docs/edge-cases.md`의 엣지케이스 매트릭스가 기준이다.

### 6.1 커맨드별 커버리지 기준

| 커맨드 | Happy Path | Error Path | Edge Case | 참조 |
|--------|-----------|-----------|-----------|------|
| `make` | 문제 폴더·JSON·README 생성 | 404, 네트워크 실패, 잘못된 언어 | 기존 폴더 덮어쓰기, 에이전트 미설정 | M1-M12 |
| `run` | Java 2/2 통과, Python 2/2 통과 | 폴더·솔루션·테스트 없음, 컴파일 오류 | id 없는 케이스 자동 보완, 부분 통과 | R1-R12 |
| `commit` | 커밋 생성 | git 아님, 폴더 없음, email 미설정 | 변경사항 없음, --no-stats | CT1-CT9 |
| `submit` | Submit.java 생성 + 컴파일 | 솔루션 없음, 미지원 언어 | Parse 없는 경우, --force | SB1-SB10 |
| `open` | 에디터 호출 | 폴더 없음 | --editor 플래그 | O1-O4 |
| `review` | 에이전트 호출 | 폴더 없음 | 에이전트 미설정 fallback | RV1-RV4 |
| `setup` | 설정 저장 | 잘못된 언어, 잘못된 경로 | --check, 부분 설정 | S1-S8 |

### 6.2 파라미터라이즈드 패턴

픽스처를 자동 순회하여 모든 문제에 대해 동일한 테스트를 실행한다:

```python
import pytest
from pathlib import Path

FIXTURES = sorted(
    p.name for p in (Path(__file__).parent.parent / "fixtures").iterdir()
    if p.is_dir() and (p / "raw.html").exists()
)


@pytest.mark.parametrize("problem_num", FIXTURES)
def test_make_creates_problem_json(boj_env, problem_num):
    """모든 픽스처에 대해 make가 problem.json을 생성한다."""
    tmp_path, env = boj_env
    fixture = Path(__file__).parent.parent / "fixtures" / problem_num
    env["BOJ_CLIENT_TEST_HTML"] = str(fixture / "raw.html")

    result = run_boj(env, "make", problem_num, "--no-open")

    prob_dir = next(tmp_path.glob(f"{problem_num}*"), None)
    assert prob_dir is not None
    assert (prob_dir / "artifacts" / "problem.json").exists()


@pytest.mark.parametrize("problem_num", [
    p for p in FIXTURES
    if (Path(__file__).parent.parent / "fixtures" / p / "Solution.java").exists()
])
def test_run_java_passes(boj_env, fixture_path, problem_num):
    """Java Solution이 있는 모든 픽스처에 대해 run이 통과한다."""
    # ...
```

---

## 7. Marker 규약

### 7.1 `@pytest.mark.network`

인터넷 접속이 필요한 테스트에 부착한다. 기본 실행에서 제외된다.

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "network: requires internet access")

# pytest.ini 또는 pyproject.toml
# [tool.pytest.ini_options]
# addopts = "-m 'not network'"
```

```python
@pytest.mark.network
def test_live_fetch_problem_1010(boj_env):
    """실제 BOJ에서 이미지 포함 문제 1010을 가져온다."""
```

네트워크 테스트는 **1010** (이미지 포함)과 **10951** (EOF 파싱) 두 문제에 한정한다.

### 7.2 `@pytest.mark.agent`

실제 에이전트 실행이 필요한 테스트에 부착한다. CI에서 기본 제외되며, 로컬 `/verify`에서만 실행한다.

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "agent: requires real agent execution (costly/slow)")
```

```python
@pytest.mark.agent
def test_make_generates_signature_review(boj_env, fixture_path):
    """make 실행 후 signature_review.md가 생성되고 PASS 판정이다."""
    tmp_path, env = boj_env
    env["BOJ_CLIENT_TEST_HTML"] = str(fixture_path(99999) / "raw.html")

    result = run_boj(env, "make", "99999", "--no-open")

    prob_dir = next(tmp_path.glob("99999*"))
    review = prob_dir / "artifacts" / "signature_review.md"
    assert review.exists(), "signature_review.md 미생성"
    assert "PASS" in review.read_text(), "signature_review.md에서 PASS 판정 없음"
```

### 7.3 `@pytest.mark.xfail`

현재 미지원이거나 알려진 취약 동작을 문서화한다.
재작성 후 xfail이 pass로 바뀌면 제거한다.

```python
@pytest.mark.xfail(reason="submit.sh sed 기반 Java 접합이 inner class에서 깨짐")
def test_submit_with_inner_class(boj_env, fixture_path):
    """Solution에 inner class가 있을 때 Submit.java가 올바르게 생성된다."""
```

### 7.4 `@pytest.mark.slow`

실행 시간이 5초 이상인 테스트에 부착한다.

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: takes > 5 seconds")
```

---

## 8. subprocess 호출 패턴

특성화 테스트는 현재 Bash CLI를 subprocess로 호출하여 동작을 고정한다.

```python
def run_boj(env, *args, input_text=None):
    """boj CLI를 격리 환경에서 실행한다."""
    tmp_path = Path(env["BOJ_ROOT"])
    return subprocess.run(
        [str(tmp_path / "src" / "boj"), *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        input=input_text,
        timeout=30,
    )
```

### 8.1 단언 패턴

```python
# exit code 검증
assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"

# stdout 내용 검증
assert "2/2" in result.stdout

# stderr 에러 메시지 검증
assert "Error:" in result.stderr

# 파일 생성 검증
assert (prob_dir / "artifacts" / "problem.json").exists()

# 파일 내용 검증 (스냅샷 대신 구조적 검증)
import json
data = json.loads((prob_dir / "artifacts" / "problem.json").read_text())
assert data["problem_num"] == "99999"
assert len(data["samples"]) > 0
```

### 8.2 피해야 할 패턴

```python
# X — 느슨한 문자열 매칭
assert "pass" in result.stdout.lower()  # "bypass"도 매칭됨

# O — 구체적 매칭
assert "2/2" in result.stdout
assert result.stdout.count("passed") >= 1

# X — 에러 메시지 전체 비교 (변경에 취약)
assert result.stderr == "Error: Solution.java를 찾을 수 없습니다.\n"

# O — 핵심 키워드만 검증
assert "Error:" in result.stderr
assert "Solution.java" in result.stderr
```

---

## 9. pyproject.toml 설정

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-m 'not network and not agent' -v --tb=short"
markers = [
    "network: requires internet access to BOJ",
    "agent: requires real agent execution (costly/slow)",
    "slow: takes > 5 seconds",
    "xfail: known broken behavior (document for rewrite)",
]
```

---

## 10. 커맨드별 테스트 작성 가이드

### 10.1 boj make

make는 두 가지 테스트 전략을 사용한다:

#### A. 모킹 테스트 (fast, CI용)

`BOJ_AGENT_CMD=echo MOCK`으로 에이전트를 우회. 폴더 구조, JSON 생성, README 생성 등 구조적 동작만 검증한다.

```python
def test_make_creates_structure(boj_env, fixture_path):
    """make 실행 시 폴더·JSON·README가 생성된다."""
    tmp_path, env = boj_env
    env["BOJ_CLIENT_TEST_HTML"] = str(fixture_path(99999) / "raw.html")
    env["BOJ_AGENT_CMD"] = "echo MOCK"

    result = run_boj(env, "make", "99999", "--no-open")

    assert result.returncode == 0
    prob_dir = next(tmp_path.glob("99999*"))
    assert (prob_dir / "artifacts" / "problem.json").exists()
    assert (prob_dir / "README.md").exists()
```

#### B. 에이전트 테스트 (`@pytest.mark.agent`)

실제 에이전트가 실행되어 signature_review.md 생성, 점수 PASS 확인, 기준 미달 시 재생성 루프를 검증한다.

```python
@pytest.mark.agent
def test_make_generates_signature_review(boj_env, fixture_path):
    """make 실행 후 signature_review.md가 생성되고 PASS 판정이다."""
    tmp_path, env = boj_env
    env["BOJ_CLIENT_TEST_HTML"] = str(fixture_path(99999) / "raw.html")
    # BOJ_AGENT_CMD를 설정하지 않아 실제 에이전트 실행

    result = run_boj(env, "make", "99999", "--no-open")

    assert result.returncode == 0
    prob_dir = next(tmp_path.glob("99999*"))
    review = prob_dir / "artifacts" / "signature_review.md"
    assert review.exists(), "signature_review.md 미생성"
    assert "PASS" in review.read_text(), "signature_review.md에서 PASS 판정 없음"
```

### 10.2 boj run

**전제**: 문제 폴더 + Solution + Parse + test_cases.json이 존재해야 한다.
make를 먼저 실행하거나, 픽스처를 직접 복사한다.

```python
def test_run_java_happy(boj_env, fixture_path):
    tmp_path, env = boj_env
    fix = fixture_path(99999)

    # make로 폴더 생성
    env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
    run_boj(env, "make", "99999", "--no-open")
    prob_dir = next(tmp_path.glob("99999*"))

    # 픽스처에서 솔루션/테스트 복사
    shutil.copy(fix / "Solution.java", prob_dir)
    shutil.copytree(fix / "test", prob_dir / "test", dirs_exist_ok=True)

    # run 실행
    result = run_boj(env, "run", "99999")
    assert result.returncode == 0
    assert "2/2" in result.stdout
```

### 10.3 boj submit

submit은 에이전트 연동이 없다. 하드코딩된 Java 접합 로직(sed/grep)이 정상 동작하는지 검증한다.
항상 `BOJ_AGENT_CMD=echo MOCK`으로 에이전트를 모킹한다.

```python
def test_submit_java_compiles(boj_env, fixture_path):
    """submit이 Submit.java를 생성하고 컴파일이 성공한다."""
    tmp_path, env = boj_env
    env["BOJ_AGENT_CMD"] = "echo MOCK"
    fix = fixture_path(99999)

    # make로 폴더 생성
    env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
    run_boj(env, "make", "99999", "--no-open")
    prob_dir = next(tmp_path.glob("99999*"))

    # 픽스처에서 솔루션 복사
    shutil.copy(fix / "Solution.java", prob_dir)

    # submit 실행
    result = run_boj(env, "submit", "99999")
    assert result.returncode == 0
    assert (prob_dir / "submit" / "Submit.java").exists()

    # 컴파일 검증
    compile_result = subprocess.run(
        ["javac", str(prob_dir / "submit" / "Submit.java")],
        capture_output=True,
    )
    assert compile_result.returncode == 0
```

### 10.4 boj commit

**주의**: git 상태에 의존. `git add` + 변경사항 스테이징 필요.

```python
def test_commit_creates_git_commit(boj_env, fixture_path):
    # ... (make + 파일 생성 후)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    result = run_boj(env, "commit", "99999", "--no-stats", input_text="n\n")
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=tmp_path, capture_output=True, text=True,
    )
    assert log.stdout.strip() != ""  # 커밋 1개 이상
```

### 10.5 boj open

에디터/브라우저 호출은 `BOJ_EDITOR=true`로 대체하여 실행 여부만 확인한다.
`BOJ_AGENT_CMD=echo MOCK`으로 에이전트를 모킹한다.

### 10.6 boj review

review는 두 가지 테스트 전략을 사용한다:

#### A. 모킹 테스트 (fast, CI용)

`BOJ_AGENT_CMD=echo MOCK`으로 에이전트를 우회. 에이전트 미설정 fallback 동작, 폴더 없음 에러 등 구조적 동작만 검증한다.

```python
def test_review_exits_one_when_no_problem_dir(boj_env):
    """문제 폴더가 없으면 exit 1로 종료한다."""
    tmp_path, env = boj_env
    env["BOJ_AGENT_CMD"] = "echo MOCK"

    result = run_boj(env, "review", "99999")
    assert result.returncode != 0
    assert "Error:" in result.stderr
```

#### B. 에이전트 테스트 (`@pytest.mark.agent`)

실제 에이전트가 코드 리뷰 피드백을 stdout으로 출력하는지 검증한다.

```python
@pytest.mark.agent
def test_review_outputs_feedback(boj_env, fixture_path):
    """review 실행 시 에이전트가 코드 리뷰 피드백을 출력한다."""
    tmp_path, env = boj_env
    fix = fixture_path(99999)
    env["BOJ_CLIENT_TEST_HTML"] = str(fix / "raw.html")
    # BOJ_AGENT_CMD를 설정하지 않아 실제 에이전트 실행

    # make로 폴더 생성 + 솔루션 복사
    run_boj(env, "make", "99999", "--no-open")
    prob_dir = next(tmp_path.glob("99999*"))
    shutil.copy(fix / "Solution.java", prob_dir)

    result = run_boj(env, "review", "99999")
    assert result.returncode == 0
    assert len(result.stdout.strip()) > 0, "리뷰 피드백이 비어 있음"
```

### 10.7 boj setup

대화형 명령은 `input_text` 파라미터로 stdin을 제공한다.
`BOJ_AGENT_CMD=echo MOCK`으로 에이전트를 모킹한다.

---

## 11. 기존 Bash 테스트와의 관계

| 계층 | 현재 (Bash) | 목표 (Python) |
|------|------------|--------------|
| 단위 | `tests/unit/commands/*.sh` | `tests/characterization/test_*.py` |
| 단위 (설정) | `tests/unit/test_config.sh` | `tests/characterization/test_setup.py` |
| 단위 (헬퍼) | `tests/unit/lib/test_helper.sh` | pytest fixture로 대체 (`conftest.py`) |
| 통합 | `tests/integration/*.sh` | 동일 파일에 통합 (subprocess 호출) |
| E2E | `tests/e2e/test_full_workflow.sh` | `tests/e2e/test_full_workflow.py` (Python 전환) |
| 하네스 | `tests/harness/*.sh` | Phase 1 범위 외 (다언어 지원 시 재구성) |
| Python 단위 | `tests/unit/test_boj_client.py` | 유지 (그대로) |
| 레거시 픽스처 | `tests/fixtures/99999-fixture/` | `tests/fixtures/99999/`로 통합 후 제거 |

**전환 전략:**

1. `tests/characterization/` 테스트를 먼저 작성 (현재 Bash CLI 동작 고정)
2. Python 재작성 시 동일 테스트가 새 Python 코드를 검증
3. 모든 characterization 테스트가 Python 구현으로 통과하면 Bash 테스트 제거

기존 Bash 테스트는 전환이 완료될 때까지 `tests/run_tests.sh`에서 계속 실행된다.

---

## 12. CI 설정

```yaml
# .github/workflows/ci.yml 에 추가
- name: Run characterization tests
  run: |
    python3 -m pytest tests/characterization/ -v --tb=short
```

CI에서는 `not network and not agent` marker로 네트워크 테스트와 에이전트 테스트를 자동 제외한다.
네트워크 테스트는 수동 트리거 또는 별도 워크플로우로만 실행한다.

---

*최종 업데이트: 2026-03-08*
