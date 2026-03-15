---
name: boj-submit
description: 백준 제출용 단일 파일 생성. Solution + Parse 병합. "N번 제출 파일 만들어줘", "boj submit", "generate submit file"
argument-hint: "<문제번호> [--lang java|python|cpp] [--open] [--force]"
tools:
  - Bash
  - Read
---

# 백준 제출 파일 생성 (boj submit)

Arguments: $ARGUMENTS

## 1. 사전 확인

```bash
command -v boj >/dev/null 2>&1 || echo "ERROR: boj CLI not found"
```

boj CLI가 없으면 즉시 중단:
"boj CLI가 설치되어 있지 않습니다. `pip install boj-agent` 또는 `src/setup-boj-cli.sh`로 설치하세요."

## 2. 인자 파싱

`$ARGUMENTS`에서 문제번호(필수)와 옵션 플래그 추출.
문제번호가 없으면: "사용법: /boj-submit <문제번호> [--lang java|python|cpp] [--open] [--force]"

## 3. 실행

```bash
boj submit <문제번호> [옵션들]
```

`--open` 플래그가 있으면 BOJ 제출 페이지를 브라우저에서 열어줌.

## 4. 결과 안내

성공 시 생성된 `submit/Submit.*` 파일 경로 표시.
"제출 파일이 생성되었습니다. BOJ에 제출하려면 `--open` 옵션을 사용하세요."
