---
name: boj-setup
description: 백준 CLI 초기 설정. 루트 경로, 언어, 세션 쿠키 설정. "boj 설정해줘", "백준 세팅", "boj setup", "configure boj"
argument-hint: "[--check] [--session <cookie>] [--lang java|python] [--root <path>] [--username <name>]"
tools:
  - Bash
  - Read
---

# 백준 CLI 설정 (boj setup)

Arguments: $ARGUMENTS

## 1. 사전 확인

```bash
command -v boj >/dev/null 2>&1 || echo "ERROR: boj CLI not found"
```

boj CLI가 없으면 즉시 중단:
"boj CLI가 설치되어 있지 않습니다. `pip install boj-agent` 또는 `src/setup-boj-cli.sh`로 설치하세요."

## 2. 인자 파싱

`$ARGUMENTS` 확인:
- 인자가 없으면: `boj setup` (대화형 설정 모드)
- `--check`: 현재 설정 상태 확인만

## 3. 실행

```bash
boj setup [옵션들]
```

설정 항목:
- `--root`: 문제 저장 루트 경로
- `--lang`: 기본 프로그래밍 언어 (java, python, cpp 등)
- `--session`: BOJ 로그인 세션 쿠키
- `--username`: BOJ 사용자명

## 4. 결과 안내

설정 완료 후: "설정이 완료되었습니다. `/boj-make <문제번호>`로 첫 문제를 시작하세요."
`--check` 모드: 현재 설정 상태를 표로 보여줌.
