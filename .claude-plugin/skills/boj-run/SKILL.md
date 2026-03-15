---
name: boj-run
description: 백준 문제 테스트 실행. 컴파일 + 테스트케이스 검증. "N번 돌려줘", "테스트 실행", "boj run", "run tests"
argument-hint: "<문제번호> [--lang java|python]"
tools:
  - Bash
  - Read
---

# 백준 문제 테스트 실행 (boj run)

Arguments: $ARGUMENTS

## 1. 사전 확인

```bash
command -v boj >/dev/null 2>&1 || echo "ERROR: boj CLI not found"
```

boj CLI가 없으면 즉시 중단:
"boj CLI가 설치되어 있지 않습니다. `pip install boj-agent` 또는 `src/setup-boj-cli.sh`로 설치하세요."

## 2. 인자 파싱

`$ARGUMENTS`에서 문제번호(필수) 추출.
문제번호가 없으면: "사용법: /boj-run <문제번호> [--lang java|python]"

## 3. 실행

```bash
boj run <문제번호> [옵션들]
```

## 4. 결과 분석

- **전체 통과**: "모든 테스트가 통과했습니다! `/boj-commit <문제번호>`로 커밋하세요."
- **실패 있음**: 실패한 테스트케이스의 입력/기대값/실제값을 분석하고 수정 방향 제안.
