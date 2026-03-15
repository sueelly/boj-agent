---
name: boj-open
description: 백준 문제 폴더를 에디터에서 열기. "N번 열어줘", "문제 열어", "boj open", "open problem"
argument-hint: "<문제번호> [--editor code|cursor|vim]"
tools:
  - Bash
---

# 백준 문제 열기 (boj open)

Arguments: $ARGUMENTS

## 1. 사전 확인 (필수)

```bash
command -v boj >/dev/null 2>&1 && echo "CLI_OK" || echo "CLI_NOT_FOUND"
cat ~/.config/boj/root 2>/dev/null || echo "SETUP_NEEDED"
```

- `CLI_NOT_FOUND` → "boj CLI가 설치되어 있지 않습니다. `pipx install boj-agent`로 설치하세요." **즉시 중단.**
- `SETUP_NEEDED` → "boj 초기 설정이 필요합니다." → `/boj-setup` 스킬을 먼저 실행하도록 안내. **즉시 중단.**

## 2. 인자 파싱

`$ARGUMENTS`에서 문제번호(필수) 추출.
문제번호가 없으면: "사용법: /boj-open <문제번호> [--editor code|cursor|vim]"

## 3. 실행

```bash
boj open <문제번호> [옵션들]
```

문제 폴더가 없으면 `boj make`를 먼저 자동 실행함.

## 4. 결과 안내

"문제 폴더를 에디터에서 열었습니다."
