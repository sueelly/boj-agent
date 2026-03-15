# Boj-Agent

백준 알고리즘 문제 풀이를 **에이전트(AI)**와 함께 자동화하는 Python CLI.
문제 환경 생성, 로컬 테스트, 제출용 코드·리뷰까지 한 흐름으로 사용할 수 있고, **에이전트는 설정으로 갈아끼울 수 있습니다.**

## 빠른 시작

```bash
pip install boj-agent        # PyPI 설치
boj setup                    # 초기 설정 (루트, 언어, 에이전트)
boj make 4949                # 환경 생성
boj open 4949                # 에디터로 풀기
boj run 4949                 # 테스트
boj submit 4949 --open       # Submit 파일 생성 + 제출 페이지 오픈
boj review 4949              # 코드 리뷰
boj commit 4949              # 커밋 (BOJ 통계 포함)
```

개발 모드 설치:
```bash
git clone <this-repo>
cd boj-agent
pip install -e ".[dev]"
```

## 명령어

| 명령 | 설명 |
|------|------|
| `boj setup` | 초기 설정 (git, BOJ 세션, 에이전트, 기본 언어) |
| `boj make <N>` | 에이전트로 문제 환경 생성 |
| `boj open <N>` | 문제 폴더를 에디터 루트로 열기 |
| `boj run <N>` | 로컬 테스트 실행 |
| `boj submit <N>` | 제출용 Submit 파일 생성 |
| `boj review <N>` | 에이전트로 코드 리뷰 요청 |
| `boj commit <N>` | 문제 폴더 커밋 (BOJ 통계 자동 포함) |

주요 옵션 (전체 목록은 `boj <명령> --help`):

```bash
boj make   4949 --lang python       # 언어 지정
boj submit 4949 --open              # 제출 페이지 자동 오픈
boj submit 4949 --force             # 기존 Submit 파일 덮어쓰기
boj commit 4949 --no-stats          # BOJ 통계 없이 커밋
boj open   4949 --editor cursor     # 에디터 지정
boj setup  --check                  # 현재 설정 상태 확인
```

## 구조

```
boj-agent/
├── src/
│   ├── boj                 # CLI 진입점 (Bash 디스패처 → Python 라우팅)
│   ├── core/               # Python 핵심 로직 (순수 함수, CLI 없음)
│   ├── cli/                # CLI 래퍼 (core 위 얇은 레이어)
│   ├── commands/           # [legacy] Bash 서브커맨드 (fallback용)
│   └── lib/                # [legacy] Bash 공통 라이브러리
├── templates/              # 언어별 런타임 코드 (테스트 러너 + 계약)
├── prompts/                # 에이전트용 지시문
├── tests/                  # pytest 단위 + 통합 테스트
└── docs/                   # 문서
```

## 설정

`~/.config/boj/` 에 파일별로 저장됩니다.
환경변수로 오버라이드 가능합니다.

| 파일 | 환경변수 | 설명 |
|------|----------|------|
| `solution_root` | `BOJ_SOLUTION_ROOT` | 문제 풀이 루트 경로 |
| `prog_lang` | `BOJ_PROG_LANG` | 기본 언어 (java/python) |
| `agent` | `BOJ_AGENT` | 에이전트 명령 (예: `claude -p --`) |
| `editor` | `BOJ_EDITOR` | 에디터 (code/cursor/vim/nano) |
| `username` | `BOJ_USERNAME` | BOJ 사용자 ID (commit 통계용) |

```bash
boj setup          # 대화형 설정
boj setup --check  # 현재 설정 확인
```

## 지원 언어

| 언어 | 확장자 | run | submit |
|------|--------|-----|--------|
| java | .java | O | O |
| python | .py | O | O |

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
boj submit 4949     ← Submit 파일 생성
    ↓
boj review 4949     ← (선택) 리뷰
    ↓
boj commit 4949     ← 커밋 (BOJ 통계 포함)
```

## Claude Code 플러그인

boj-agent를 Claude Code에서 스킬로 사용할 수 있습니다.
자연어("백준 1000번 풀어줘")나 슬래시 커맨드(`/boj-make 1000`)로 호출 가능합니다.

```bash
# 플러그인 로드
claude --plugin-dir .claude-plugin

# 또는 마켓플레이스에서 설치
/plugin marketplace add sueelly/boj-agent
/plugin install boj-agent
```

| 스킬 | 설명 |
|------|------|
| `/boj-make <N>` | 문제 환경 생성 |
| `/boj-run <N>` | 테스트 실행 |
| `/boj-commit <N>` | 풀이 커밋 (BOJ 통계 포함) |
| `/boj-review <N>` | 코드 리뷰 |
| `/boj-submit <N>` | 제출 파일 생성 |
| `/boj-open <N>` | 에디터에서 열기 |
| `/boj-setup` | 초기 설정 |
| `/boj-solve <N>` | 전체 자동 풀이 (make→풀이→run→commit→submit) |

자세한 내용은 [.claude-plugin/README.md](.claude-plugin/README.md) 참고.

## 테스트

```bash
./tests/run_tests.sh                    # 전체 (단위 + 통합)
./tests/run_tests.sh --unit             # 단위만
./tests/run_tests.sh --integration      # 통합만
python -m pytest tests/unit/            # pytest 직접 실행
```

## 문서

- **사용 가이드**: [docs/user-guide.md](docs/user-guide.md)
- **아키텍처**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **엣지 케이스**: [docs/dev/testing/edge-cases.md](docs/dev/testing/edge-cases.md)
- **개발 기록**: [docs/records/DEVLOG.md](docs/records/DEVLOG.md)
- **에이전트 지시문**: [prompts/README.md](prompts/README.md)

자세한 내용은 [docs/user-guide.md](docs/user-guide.md) 참고.
