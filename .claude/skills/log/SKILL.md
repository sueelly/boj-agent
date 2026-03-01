---
name: log
description: 의사결정을 DECISIONS.md에 기록. 컨텍스트/결정/대안/근거/트레이드오프 포함.
argument-hint: "\"결정 제목 또는 내용\""
tools:
  - Bash
  - Read
  - Write
---

# 의사결정 기록 (/log)

Arguments: $ARGUMENTS

## 1. 현재 컨텍스트 수집

```bash
BRANCH=$(git branch --show-current)
DATE=$(date '+%Y-%m-%d')
ISSUE_NUM=$(echo "$BRANCH" | grep -oE 'issue-[0-9]+' | grep -oE '[0-9]+' || echo "?")
```

## 2. 결정 정보 수집

$ARGUMENTS가 있으면 제목으로 사용.
없으면 다음 항목 대화로 수집:
- 컨텍스트: 왜 이 결정이 필요했는가?
- 결정: 선택한 방법은?
- 검토한 대안: 고려했지만 선택하지 않은 것들
- 근거: 이 방법을 선택한 이유
- 트레이드오프: 이 선택의 단점

## 3. DECISIONS.md에 append

프로젝트 루트의 DECISIONS.md 사용 (`git rev-parse --show-toplevel` 또는 pwd).  
**기록 형식**: CLAUDE.md의 "자동 의사결정 감지" 섹션과 동일 (컨텍스트, 결정, 검토한 대안, 근거, 트레이드오프, 이슈).

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
DECISIONS_FILE="${REPO_ROOT}/DECISIONS.md"
# 위 형식으로 $DATE, $BRANCH, $TITLE, $CONTEXT, $DECISION, $ALTERNATIVES, $RATIONALE, $TRADEOFFS, $ISSUE_NUM 채워 append
```

## 4. 확인

```
✅ 의사결정 기록 완료:
   파일: DECISIONS.md
   제목: [$DATE] $BRANCH: $TITLE
```
