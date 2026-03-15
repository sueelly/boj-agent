# boj-agent Claude Code Plugin

백준(BOJ) 문제 풀이 자동화 CLI를 Claude Code에서 바로 사용할 수 있는 플러그인입니다.

## 전제조건

`boj` CLI가 PATH에 설치되어 있어야 합니다:

```bash
pip install boj-agent
# 또는
./src/setup-boj-cli.sh
```

설치 후 초기 설정:
```bash
boj setup
```

## 설치 방법

### 방법 1: 플러그인 마켓플레이스

```bash
# Claude Code에서
/plugin marketplace add sueelly/boj-agent
/plugin install boj-agent
```

### 방법 2: 로컬 플러그인

```bash
# 레포 클론 후 플러그인 디렉토리 지정
claude --plugin-dir /path/to/boj-agent/.claude-plugin
```

### 방법 3: 수동 복사

```bash
# 스킬 파일들을 프로젝트에 직접 복사
cp -r .claude-plugin/skills/boj-* your-project/.claude/skills/
```

## 사용법

### 슬래시 커맨드

| 커맨드 | 설명 | 예시 |
|--------|------|------|
| `/boj-make <N>` | 문제 환경 생성 | `/boj-make 1000` |
| `/boj-run <N>` | 테스트 실행 | `/boj-run 1000` |
| `/boj-commit <N>` | 풀이 커밋 | `/boj-commit 1000` |
| `/boj-review <N>` | 코드 리뷰 | `/boj-review 1000` |
| `/boj-submit <N>` | 제출 파일 생성 | `/boj-submit 1000` |
| `/boj-open <N>` | 에디터에서 열기 | `/boj-open 1000` |
| `/boj-setup` | 초기 설정 | `/boj-setup --check` |
| `/boj-solve <N>` | 전체 자동 풀이 | `/boj-solve 1000` |

### 자연어 트리거

슬래시 커맨드 없이도 자연어로 사용 가능합니다:

```
"백준 1000번 만들어줘"     → boj-make 자동 실행
"1000번 테스트 돌려줘"     → boj-run 자동 실행
"백준 1000번 풀어줘"       → boj-solve 자동 실행 (전체 워크플로우)
"1000번 리뷰해줘"          → boj-review 자동 실행
```

## 워크플로우

### 수동 (단계별)
```
/boj-make 1000          # 1. 문제 fetch + 스켈레톤 생성
[Solution 작성]          # 2. 풀이 코드 작성
/boj-run 1000           # 3. 테스트 실행
/boj-review 1000        # 4. 코드 리뷰 (선택)
/boj-commit 1000        # 5. 커밋
/boj-submit 1000        # 6. 제출 파일 생성
```

### 자동 (한 번에)
```
/boj-solve 1000         # 위 전체 과정을 자동 실행
```

## 스킬 목록

| 스킬 | 파일 | 설명 |
|------|------|------|
| boj-make | `skills/boj-make/SKILL.md` | BOJ에서 문제 fetch → README + 스켈레톤 코드 생성 |
| boj-run | `skills/boj-run/SKILL.md` | 컴파일 + test_cases.json 기반 테스트 실행 |
| boj-commit | `skills/boj-commit/SKILL.md` | 파일 스테이징 + BOJ 통계 포함 커밋 |
| boj-review | `skills/boj-review/SKILL.md` | AI 코드 리뷰 (시간복잡도, 엣지케이스 분석) |
| boj-submit | `skills/boj-submit/SKILL.md` | Solution + Parse 병합한 단일 제출 파일 생성 |
| boj-open | `skills/boj-open/SKILL.md` | 문제 폴더를 에디터에서 열기 |
| boj-setup | `skills/boj-setup/SKILL.md` | 루트 경로, 언어, 세션 쿠키 등 초기 설정 |
| boj-solve | `skills/boj-solve/SKILL.md` | 전체 워크플로우 자동 실행 (make→풀이→run→commit→submit) |
