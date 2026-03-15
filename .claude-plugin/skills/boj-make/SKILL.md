---
name: boj-make
description: 백준 문제 환경 생성. 문제 fetch + README + 스켈레톤 코드 생성. "백준 N번 만들어줘", "문제 N번 세팅", "boj make", "create BOJ problem"
argument-hint: "<문제번호> [--lang java|python|cpp] [--no-open]"
tools:
  - Bash
  - Read
---

# 백준 문제 환경 생성 (boj make)

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
문제번호가 없으면: "사용법: /boj-make <문제번호> [--lang java|python|cpp] [--no-open]"

## 3. 실행

```bash
boj make <문제번호> [옵션들]
```

## 4. 결과 확인

성공 시 생성된 README.md를 읽어서 문제 내용 요약 표시.

```bash
BOJ_ROOT=$(cat ~/.config/boj/root)
ls -d "$BOJ_ROOT"/*<문제번호>*/ 2>/dev/null
```

## 5. 다음 단계 안내

"문제 환경이 생성되었습니다. Solution 파일을 작성한 후 `/boj-run <문제번호>`로 테스트하세요."
