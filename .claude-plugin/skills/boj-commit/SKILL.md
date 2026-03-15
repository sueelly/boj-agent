---
name: boj-commit
description: 백준 풀이 커밋. BOJ 통계(메모리/시간) 자동 포함. "N번 커밋해줘", "boj commit", "commit solution"
argument-hint: "<문제번호> [--message <msg>] [--no-stats]"
tools:
  - Bash
  - Read
---

# 백준 풀이 커밋 (boj commit)

Arguments: $ARGUMENTS

## 1. 사전 확인 (필수)

```bash
command -v boj >/dev/null 2>&1 && echo "CLI_OK" || echo "CLI_NOT_FOUND"
cat ~/.config/boj/root 2>/dev/null || echo "SETUP_NEEDED"
```

- `CLI_NOT_FOUND` → "boj CLI가 설치되어 있지 않습니다. `pipx install boj-agent`로 설치하세요." **즉시 중단.**
- `SETUP_NEEDED` → "boj 초기 설정이 필요합니다." → `/boj-setup` 스킬을 먼저 실행하도록 안내. **즉시 중단.**

## 2. 인자 파싱

`$ARGUMENTS`에서 문제번호(필수)와 옵션 플래그 추출.
문제번호가 없으면: "사용법: /boj-commit <문제번호> [--message <msg>] [--no-stats]"

## 3. 실행

```bash
boj commit <문제번호> [옵션들]
```

커밋 메시지에 BOJ Accepted 통계(메모리, 시간)가 자동 포함됨.
통계 fetch 실패 시에도 커밋은 정상 진행.

## 4. 결과 안내

성공 시: "커밋 완료. `/boj-submit <문제번호>`로 제출 파일을 생성하거나, push하세요."
