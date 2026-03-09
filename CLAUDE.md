# BOJ-Agent: 백준 문제 풀이 CLI

## 프로젝트 개요
Bash 스크립트 기반 BOJ 문제 풀이 자동화 CLI. 명령어: `make`, `open`, `run`, `commit`, `review`, `submit`, `setup`.

## 절대 규칙 (예외 없음)
- main/master에 직접 커밋 금지. 항상 브랜치 사용
- 테스트 없이 PR 금지. 증거 = 통과된 테스트 결과
- 모든 작업은 GitHub 이슈 번호와 연결
- 커밋 형식: `feat|fix|refactor|docs|test|chore(scope): message [#N]`
- force push 금지
- 불확실한 결정(스키마 변경, BOJ API 연동 방식, 인증 로직)은 추측 말고 질문

## 빌드/테스트 명령
```bash
# 전체 테스트 실행
./tests/run_tests.sh

# 단일 명령 테스트
./tests/integration/test_boj_run.sh
./tests/integration/test_boj_help.sh

# BOJ run 직접 테스트 (픽스처 사용)
BOJ_ROOT=. src/boj run 99999

# Java 템플릿 컴파일 확인
javac templates/java/*.java
```

## 프로젝트 구조
```
src/
  boj                   # CLI 진입점 (서브커맨드 디스패처)
  setup-boj-cli.sh      # 설치 스크립트
  commands/             # make, run, commit, open, review, submit, setup
  lib/
    config.sh           # 공통 설정 로더 (env > 파일 > 기본값)
    boj_client.py       # BOJ HTML fetch + 파싱 (Python)
    boj_normalizer.py   # problem.json → README.md (Python)
templates/              # 언어별 테스트 러너 + 인터페이스 + 스텁
  _common/              # test_cases.json 스키마 예시
  java/                 # Test.java, ParseAndCallSolve.java (런타임)
  python/               # test_runner.py (런타임)
  cpp/, c/, kotlin/     # 스텁만 존재
  languages.json        # 언어 메타데이터
tests/
  run_tests.sh          # 전체 테스트 실행
  integration/          # 명령어별 통합 테스트
  unit/                 # 단위 테스트 (Bash + test_boj_client.py)
  fixtures/             # 테스트 픽스처 (99999, 1000, 6588, 9495)
docs/
  ARCHITECTURE.md       # 현재 구조 + 목표 구조 (Option C)
  COMMAND-SPEC.md       # 명령어별 로직 정의서
  user-guide.md         # 사용자 가이드
  edge-cases.md         # 엣지케이스 매트릭스 (구현/테스트 기준)
  dev/                  # 개발 프로세스 가이드
    WORKFLOW.md, AGENT-GUIDE.md, HOW-TO-USE.md, VERIFICATION.md
    QUICKSTART.md, issues.md, test-strategy.md, rewrite-plan.md
    test-coverage/
  records/              # 기록
    DEVLOG.md           # 변경 기록 (구조화 + Legacy 여정)
prompts/                # 에이전트 지시문 (make-skeleton, review, submit)
```

## 언어별 규칙
- **Bash**: 함수명 snake_case, 전역변수 UPPER_SNAKE_CASE, `set -euo pipefail` 지양 (서브셸 오류 처리 직접)
- **Java(템플릿)**: Java 11+ 호환 유지, 외부 라이브러리 금지 (BOJ 제출 환경 기준)
- **Python(템플릿)**: Python 3.10+ 호환, 표준 라이브러리만

## 설정 우선순위
1. 환경변수 (`BOJ_ROOT`, `BOJ_LANG`, `BOJ_AGENT_CMD`, `BOJ_EDITOR`)
2. `~/.config/boj/` 파일 (root, lang, agent, editor, session)
3. 기본값 (lang=java, editor=code)

## 에러 처리 규칙
- `Error:` 접두사 → exit 1 (계속 불가)
- `Warning:` 접두사 → exit 0 (계속 가능)
- BOJ 통계 조회 실패 → commit은 진행, 메시지에 실패 이유 포함
- 에이전트 없음 → 에디터 + 클립보드 fallback

## 워크플로우
```
/issue → /start <N> → [개발] → /commit → /verify → /done
```

## 슬래시 커맨드
| 커맨드 | 용도 |
|--------|------|
| `/start <N>` | 이슈 N 작업 시작: 브랜치 생성 + 컨텍스트 로드 |
| `/commit` | 스마트 커밋: 단위 추천 + 형식 검증 + 커밋 실행 |
| `/verify` | 7단계 검증 파이프라인 (PR 전 필수) |
| `/done` | verify + commit + push + PR 원스텝 완료 |
| `/pr` | PR 생성 (verify 포함) |
| `/review` | code-reviewer 에이전트로 현재 PR 리뷰 |
| `/issue` | GitHub 이슈 생성 |
| `/log` | 의사결정 DECISIONS.md에 기록 |
| `/test <file>` | test-writer 에이전트로 테스트 생성 |

## 규칙 파일 참조
@.claude/rules/git.md
@.claude/rules/security.md
@.claude/rules/testing.md

## 자동 의사결정 감지
대화 중 다음 결정 시 `/tmp/claude-pending-decision.txt`에 기록:
- BOJ API/크롤링 방식 선택
- 언어별 템플릿 구조 선택
- 인증 방식 선택 (세션쿠키 vs OAuth 등)
- Submit.java 생성 전략 (병합 vs 변환)

기록 형식:
```
## [YYYY-MM-DD] BRANCH: 결정 제목
**컨텍스트**: 왜 필요했는가
**결정**: 선택한 방법
**검토한 대안**: 검토했지만 선택하지 않은 것들
**근거**: 이유
**트레이드오프**: 단점
**이슈**: #N
---
```
