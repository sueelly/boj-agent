# Boj-Agent

백준 알고리즘 문제 풀이를 **에이전트(AI)**와 함께 자동화하는 CLI.
문제 환경 생성, 로컬 테스트, 제출용 코드·리뷰까지 한 흐름으로 사용할 수 있고, **에이전트는 Cursor뿐 아니라 설정으로 갈아끼울 수 있습니다.**

## 빠른 시작

```bash
git clone <this-repo>
cd boj-agent
./src/setup-boj-cli.sh   # PATH에 boj 설치
boj setup                 # 초기 설정 (루트, 언어, 에이전트)
boj make 4949             # 환경 생성
boj open 4949             # 에디터로 풀기
boj run 4949              # 테스트
boj submit 4949 --open    # Submit.java 생성 + 제출 페이지 오픈
boj commit 4949           # 커밋
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

## 문서

- **사용 가이드**: [docs/user-guide.md](docs/user-guide.md)
- **엣지 케이스 매트릭스**: [docs/edge-cases.md](docs/edge-cases.md)
- **개발 기록**: [docs/DEVLOG.md](docs/DEVLOG.md)
- **에이전트 지시문**: [prompts/README.md](prompts/README.md)

## 구조

```
boj-agent/
├── src/
│   ├── boj                 # CLI 진입점 (7개 서브커맨드 디스패처)
│   ├── setup-boj-cli.sh    # 한 번 설치 (~/bin/boj 복사)
│   ├── lib/
│   │   └── config.sh       # 공통 설정 로더 (config_get/set, validate_lang 등)
│   └── commands/           # setup / make / open / run / submit / review / commit
├── templates/              # 언어별 공통 코드 (Java, Python, C++, C, Kotlin, Go, Rust ...)
│   ├── _common/
│   ├── languages.json      # 12개 언어 메타데이터
│   └── java/ python/ cpp/ c/ kotlin/ go/ rust/ ruby/ swift/ scala/ js/ ts/
├── prompts/                # 에이전트용 지시문 (환경 생성 / 제출 / 리뷰)
├── tests/
│   ├── run_tests.sh        # --unit | --integration | --all
│   ├── unit/               # config.sh 단위 테스트
│   └── integration/        # 명령어별 통합 테스트
└── docs/                   # 사용자 가이드, 엣지 케이스, 개발 기록
```

## 설정

`~/.config/boj/` 에 파일별로 저장됩니다.
환경변수(`BOJ_ROOT`, `BOJ_LANG`, `BOJ_AGENT`, `BOJ_SESSION`, `BOJ_USER`, `BOJ_EDITOR`)로 오버라이드 가능.

```bash
boj setup          # 대화형 설정
boj setup --check  # 현재 설정 확인
```

자세한 내용은 [docs/user-guide.md](docs/user-guide.md) 참고.
