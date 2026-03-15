# BOJ-Agent: 백준 문제 풀이 CLI

## 프로젝트 개요
Bash + Python 혼합 CLI로 BOJ 문제 풀이 자동화.
명령어 7개: `make`, `open`, `run`, `commit`, `review`, `submit`, `setup`.
Python 코어로 전환 완료 (docs/ARCHITECTURE.md 참고).

## 절대 규칙
- main에 직접 커밋 금지 — 항상 브랜치 + PR
- 테스트 없이 PR 금지 — 증거 = 통과된 테스트 결과
- 모든 작업은 GitHub 이슈 번호와 연결
- 커밋 형식: `feat|fix|refactor|docs|test|chore(scope): message [#N]`
- force push 금지
- 불확실한 결정은 추측 말고 질문

## 빌드/테스트
```bash
./tests/run_tests.sh                    # 전체 (단위 + 통합)
./tests/run_tests.sh --unit             # 단위만
./tests/run_tests.sh --integration      # 통합만
BOJ_ROOT=. src/boj run 99999           # 픽스처 직접 테스트
python -m pytest tests/unit/test_boj_client.py  # Python 단위
javac templates/java/*.java             # Java 템플릿 컴파일
```

## 프로젝트 구조
```
src/
  boj                       # CLI 진입점 (Bash 디스패처 → Python 라우팅)
  core/                     # Python 핵심 로직 (순수 함수, CLI 없음)
    config.py, client.py, make.py, run.py, commit.py, submit.py
    open.py, review.py, normalizer.py, exceptions.py
  cli/                      # CLI 래퍼 (core 위 얇은 레이어)
    main.py, boj_setup.py, boj_make.py, boj_run.py, boj_commit.py
    boj_submit.py, boj_open.py, boj_review.py
  commands/                 # [legacy fallback] Bash 서브커맨드
    make.sh, run.sh, commit.sh, submit.sh, setup.sh, open.sh, review.sh
  lib/                      # [legacy] 공통 라이브러리
    config.sh, boj_client.py, boj_normalizer.py
templates/
  java/                     # Test.java, ParseAndCallSolve.java (런타임 인프라)
  python/                   # test_runner.py (런타임 인프라)
  cpp/, c/, kotlin/          # 스텁만 존재 (런타임 미지원)
  _common/test_cases.json    # 스키마 예시
  languages.json             # 언어 메타데이터
tests/
  run_tests.sh               # 전체 테스트 실행
  unit/                      # Python pytest + Bash 단위 테스트
  integration/               # Python/Bash 통합 테스트
  fixtures/                  # 테스트 픽스처 (99999, 1000, 6588, 9495, boj_client/)
docs/
  ARCHITECTURE.md            # 현재 구조 + 목표 구조 (Option C)
  COMMAND-SPEC.md            # 명령어별 로직 정의서
  user-guide.md              # 사용자 가이드
  dev/                       # 개발 프로세스 가이드
    WORKFLOW.md, VERIFICATION.md
    testing/                 # 테스트 문서 (통합)
      strategy.md, edge-cases.md, coverage/
  records/
    DEVLOG.md                # 변경 기록
prompts/                     # 에이전트 지시문 (make-skeleton, review, submit)
scripts/                     # 유틸리티 (record_fixture.sh)
```

## 설정 우선순위
1. 환경변수 (`BOJ_ROOT`, `BOJ_LANG`, `BOJ_AGENT_CMD`, `BOJ_EDITOR`, `BOJ_SESSION`, `BOJ_USER`)
2. `$BOJ_CONFIG_DIR/` 파일 (기본: `~/.config/boj/`)
3. 기본값 (lang=java, editor=code)

## 에러 처리
- `Error:` → exit 1 (계속 불가)
- `Warning:` → exit 0 (계속 가능)
- BOJ 통계 실패 → commit 진행, 메시지에 실패 이유 포함
- 에이전트 없음 → 에디터 + 클립보드 fallback

## 언어별 규칙
- **Bash**: snake_case 함수, UPPER_SNAKE_CASE 전역, `set -euo pipefail` 지양
- **Java(템플릿)**: Java 11+ 호환, 외부 라이브러리 금지
- **Python**: 3.10+, 표준 라이브러리만 (boj_client는 requests+bs4 예외)

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
