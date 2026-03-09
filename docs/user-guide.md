# Boj-Agent 사용 가이드

백준 알고리즘 문제 풀이를 **에이전트(AI)**와 함께 자동화하는 CLI입니다.
어떤 에이전트를 쓰든 설정(`~/.config/boj/`)으로 갈아끼울 수 있습니다.

## 폴더 구조

```
boj-agent/
├── src/
│   ├── boj                 # CLI 진입점
│   ├── setup-boj-cli.sh    # 한 번 설치
│   ├── lib/
│   │   └── config.sh       # 공통 설정 라이브러리
│   └── commands/           # setup, make, open, run, submit, review, commit
├── templates/              # 언어별 공통 코드 (테스트 러너 + 계약)
│   ├── _common/
│   ├── languages.json      # 언어 메타데이터
│   └── java/ python/ cpp/ c/ kotlin/
├── prompts/                # 에이전트용 지시문 (환경 생성 / 제출 / 리뷰)
├── tests/                  # 단위 + 통합 테스트
└── docs/                   # 사용자 가이드, 엣지 케이스
```

문제별 폴더는 `BOJ_ROOT` 아래에 생성됩니다:

```
[BOJ_ROOT]/
└── [문제번호]-[문제제목]/
    ├── README.md
    ├── Solution.*
    ├── test/
    │   ├── Parse.*          # 입력 파싱 + sol.solve() 호출
    │   └── test_cases.json
    └── submit/
        ├── Submit.*         # BOJ 제출용 단일 파일
        └── REVIEW.md
```

## 설치

```bash
cd <boj-agent 레포>
./src/setup-boj-cli.sh
```

설치 후 `~/bin/boj`에 복사되고 레포 경로는 `~/.config/boj/root`에 저장됩니다.
필요 시 PATH에 `$HOME/bin`을 추가하세요.

## 초기 설정

```bash
boj setup
```

대화형으로 다음을 설정합니다:
- BOJ_ROOT (문제 풀이 루트 경로, 현재 디렉터리 기본)
- 기본 언어 (java/python/cpp/c/kotlin/go 등)
- BOJ 세션 쿠키 (`JSESSIONID` — commit 통계, 자동 확인용)
- BOJ 사용자 ID (commit 통계용)
- 에이전트 명령 (make/review 시 호출할 CLI, 예: `claude -p --`)

```bash
boj setup --check   # 현재 설정 상태 한눈에 확인
```

## 명령어 상세

### `boj make <문제번호>` — 환경 생성

에이전트를 통해 문제 폴더 전체를 자동 생성합니다.

```bash
boj make 4949                     # 기본 (설정된 언어 사용)
boj make 4949 --lang python       # 언어 지정
boj make 4949 --image-mode skip   # 문제 이미지 처리 방식 (download|reference|skip)
boj make 4949 --output ~/problems # 저장 위치 지정 (기본: BOJ_ROOT)
boj make 4949 --no-open           # 에디터 자동 오픈 없이
```

에이전트(`boj_agent_cmd`) 미설정 시: 프롬프트를 클립보드에 복사하고 에디터를 엽니다.

### `boj open <문제번호>` — 에디터로 열기

문제 폴더만 에디터 루트로 열어 풀이에 집중합니다.

```bash
boj open 4949                     # 설정된 에디터 사용
boj open 4949 --editor cursor     # 에디터 지정 (code/cursor/vim/nano)
```

### `boj run <문제번호>` — 테스트 실행

`test/test_cases.json`의 케이스를 순서대로 실행합니다.

```bash
boj run 4949                      # 기본 언어 사용
boj run 4949 --lang java          # 언어 지정
```

`test_cases.json` 형식:
```json
{
  "problem": {
    "number": 1000,
    "title": "A+B",
    "link": "https://www.acmicpc.net/problem/1000"
  },
  "solution": {
    "method": "solve",
    "inputType": "String",
    "outputType": "int"
  },
  "testCases": [
    { "id": 1, "description": "예제 1", "input": "1 1\n", "expected": "2" },
    { "id": 2, "description": "예제 2", "input": "3 4\n", "expected": "7" }
  ]
}
```

`testCases` 배열 내 `id`나 `description`이 누락된 경우 실행 시 자동 채워집니다 (파일 비파괴).

지원 언어: java (컴파일 후 실행), python (python3).

### `boj submit <문제번호>` — 제출용 파일 생성

`Solution.*`과 `Parse.*`를 합쳐 BOJ 제출용 단일 파일을 생성합니다.

```bash
boj submit 4949                   # 기본 언어 사용
boj submit 4949 --lang python     # 언어 지정
boj submit 4949 --open            # 생성 후 제출 페이지 자동 오픈
boj submit 4949 --force           # 기존 Submit 파일 확인 없이 덮어쓰기
```

Java의 경우:
- `import` 중복 제거 (sort -u)
- `public class Solution` → `class Solution` 변환
- `implements ParseAndCallSolve` 제거
- `@Override` 제거
- `javac` 컴파일 검증 (실패 시 경고만, 파일은 생성됨)

생성 경로: `<문제폴더>/submit/Submit.<ext>`

### `boj review <문제번호>` — 코드 리뷰

에이전트를 통해 `Submit.*` 또는 `Solution.*`을 리뷰하고 `REVIEW.md`를 생성합니다.

```bash
boj review 4949
```

`prompts/review.md`가 있으면 해당 지시문을 프롬프트 앞에 첨부합니다.
에이전트 미설정 시: 프롬프트를 클립보드에 복사합니다.

### `boj commit <문제번호>` — 커밋

문제 폴더 파일들을 자동 스테이징 후 커밋합니다.

```bash
boj commit 4949                   # BOJ 통계 포함 커밋
boj commit 4949 "추가 메시지"     # 커밋 메시지 앞에 추가
boj commit 4949 --no-stats        # BOJ 통계 없이 커밋
boj commit 4949 --message "msg"   # 커밋 메시지 지정
```

자동 스테이징 파일: `README.md`, `Solution.*`, `test/test_cases.json`, `test/Parse.*`, `submit/REVIEW.md`, `submit/Submit.*`

BOJ 통계 (session/user 설정 시): Accepted 여부, 메모리, 시간이 커밋 메시지에 포함됩니다.
세션 미설정이나 네트워크 오류 시 통계 없이 커밋합니다.

## 설정 (`~/.config/boj/`)

| 파일 | 환경변수 | 설명 |
|------|----------|------|
| `root` | `BOJ_ROOT` | 문제 풀이 루트 경로 |
| `lang` | `BOJ_LANG` | 기본 언어 (java/python/cpp/c/kotlin/go/rust 등) |
| `agent` | `BOJ_AGENT` | make/review 에이전트 명령 (예: `claude -p --`) |
| `editor` | `BOJ_EDITOR` | 에디터 (code/cursor/vim/nano, 기본: code) |
| `session` | `BOJ_SESSION` | BOJ JSESSIONID 쿠키 (commit 통계용) |
| `user` | `BOJ_USER` | BOJ 사용자 ID (commit 통계용) |

환경변수가 파일보다 우선합니다.

## 지원 언어

| 언어 | 확장자 | run | submit |
|------|--------|-----|--------|
| java | .java | ✓ | ✓ |
| python | .py | ✓ | ✓ |

## 워크플로우

```
boj setup           ← 최초 1회
    ↓
boj make 4949       ← 에이전트로 환경 생성 (README, Solution, test/)
    ↓
boj open 4949       ← 에디터로 풀기
    ↓
boj run 4949        ← 로컬 테스트
    ↓
boj submit 4949 --open  ← Submit 파일 생성 + 제출 페이지 오픈
    ↓
boj review 4949     ← (선택) 리뷰
    ↓
boj commit 4949     ← 커밋 (BOJ 통계 포함)
```

## 테스트 실행

```bash
./tests/run_tests.sh           # 전체 (단위 + 통합)
./tests/run_tests.sh --unit    # 단위 테스트만
./tests/run_tests.sh --integration  # 통합 테스트만
```
