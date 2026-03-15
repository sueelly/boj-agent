---
name: boj-review
description: 백준 풀이 코드 리뷰. AI가 시간복잡도, 엣지케이스, 개선점 분석. "N번 리뷰해줘", "코드 봐줘", "boj review", "review solution"
argument-hint: "<문제번호>"
tools:
  - Bash
  - Read
---

# 백준 풀이 코드 리뷰 (boj review)

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
문제번호가 없으면: "사용법: /boj-review <문제번호>"

## 3. 실행

```bash
boj review <문제번호>
```

## 4. 결과 안내

리뷰 결과가 `submit/REVIEW.md`에 저장되면 해당 파일을 읽어서 핵심 내용 요약.
다음 단계: "리뷰를 반영한 후 `/boj-run <문제번호>`로 다시 테스트하세요."
