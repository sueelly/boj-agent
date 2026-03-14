# Boj-Agent 사용 가이드

백준 알고리즘 문제 풀이를 **에이전트(AI)**와 함께 자동화하는 CLI입니다.
어떤 에이전트를 쓰든 설정(`~/.config/boj/`)으로 갈아끼울 수 있습니다.

## 폴더 구조

```
boj-agent/
├── src/
│   ├── boj                 # CLI 진입점
│   ├── setup-boj-cli.sh    # [deprecated] → scripts/install.py
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
git clone <boj-agent 레포 URL>
cd boj-agent
python3 scripts/install.py
```

설치 스크립트가 다음을 수행합니다:
1. `boj-agent` 파일을 `~/.local/share/boj-agent/`로 복사
2. `~/bin/boj`에 CLI 명령어 설치
3. `~/.config/boj/`에 설정 저장
4. PATH 자동 추가 (`~/.zshrc` 등에 `export PATH="$HOME/bin:$PATH"` **한 줄**이 없을 때만 추가. 주석에만 `$HOME/bin`이 있는 경우는 예전에 스킵 버그가 있었음 — 재설치 또는 아래 한 줄 수동 추가 권장)
5. `boj setup` 자동 실행 — **zsh/bash 서브프로세스**에서 해당 rc(`.zshrc` 등)를 `source`한 뒤 실행해, 방금 넣은 PATH와 셸 환경에 맞춤
6. 터미널에 안내: `export PATH="$HOME/bin:$PATH"` + `source ~/.zshrc` (부모 셸은 스크립트가 대신 못 바꿈)

옵션:
```bash
python3 scripts/install.py --force       # 기존 설치 덮어쓰기
python3 scripts/install.py --skip-setup  # boj setup 자동 실행 건너뛰기
```

설치 후에도 `boj: command not found` 이면:

1. `grep -n 'export PATH' ~/.zshrc` 로 **`export PATH="…/bin:$PATH"`** 형태가 **맨 앞에 bin이 오는 줄**이 있는지 확인한다. 없으면 한 줄 추가: `export PATH="$HOME/bin:$PATH"`
2. `source ~/.zshrc` 또는 새 터미널
3. 그래도 안 되면 `~/bin/boj setup --check` 로 동작 확인 후, `echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc`

## 초기 설정

```bash
boj setup
```

대화형 6단계 설정 마법사:
1. 레포 루트 경로 (BOJ_SOLUTION_ROOT)
2. 기본 언어 (java/python)
3. 에이전트 (claude/copilot/cursor/gemini/opencode/기타)
4. Git 연동 (user.name/email + repo 설정)
5. BOJ 사용자 ID (commit 통계용)
6. 에디터 명령 (boj open에 사용)

```bash
boj setup --check              # 현재 설정 상태 한눈에 확인
boj setup --lang python        # 기본 언어만 변경
boj setup --root ~/solutions   # 루트 경로만 변경
boj setup --agent claude       # 에이전트 설정 (자동 매핑)
boj setup --username myid      # BOJ 사용자 ID 설정
boj setup --editor vim         # 에디터 설정
```

## 명령어 상세

### `boj make <문제번호>` — 환경 생성

에이전트를 통해 문제 폴더 전체를 자동 생성합니다.
`boj setup`이 완료되지 않은 상태에서 실행하면 자동으로 setup을 먼저 실행합니다.

```bash
boj make 4949                     # 기본 (설정된 언어 사용)
boj make 4949 --lang python       # 언어 지정
boj make 4949 --image-mode skip   # 문제 이미지 처리 방식 (download|reference|skip)
boj make 4949 --no-open           # 에디터 자동 오픈 없이
boj make 4949 --keep-artifacts    # 중간 산출물(problem.json, problem.spec.json) 유지
boj make 4949 -f                  # 이미 존재하는 문제 폴더 덮어쓰기
```

> **참고**: README.md가 생성되면 에디터가 즉시 열립니다. spec/skeleton 생성(40초~2분)을 기다리는 동안 문제 본문을 바로 읽을 수 있습니다.
>
> **참고**: 이미 존재하는 문제 폴더에 `boj make`를 실행하면 안내 메시지와 함께 중단됩니다.
> 덮어쓰려면 `-f` 옵션을 사용하세요.

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
| `solution_root` | `BOJ_SOLUTION_ROOT` | 문제 풀이 루트 경로 |
| `boj_agent_root` | `BOJ_AGENT_ROOT` | agent 폴더 루트 경로 |
| `prog_lang` | `BOJ_PROG_LANG` | 기본 언어 (java/python) |
| `agent` | `BOJ_AGENT` | make/review 에이전트 명령 (예: `claude -p --`) |
| `editor` | `BOJ_EDITOR` | 에디터 (code/cursor/vim/nano, 기본: code) |
| `username` | `BOJ_USERNAME` | BOJ 사용자 ID (commit 통계용) |
| `setup_done` | - | 설정 완료 플래그 (파일 유무로 판단) |

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
