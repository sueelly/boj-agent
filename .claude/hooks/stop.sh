#!/usr/bin/env bash
# Stop hook: 세션 종료 시 요약 출력 + 자동 의사결정 로그 처리

set -euo pipefail

# DECISIONS.md는 현재 워크스페이스(프로젝트) 루트에 둠. 다른 환경 이식 가능하도록 절대 경로 사용 안 함.
REPO_ROOT=$(git -C "${PWD}" rev-parse --show-toplevel 2>/dev/null || pwd)
DECISIONS_FILE="${REPO_ROOT}/DECISIONS.md"
EDITS_LOG="/tmp/claude-session-edits.log"
PENDING_DECISION="/tmp/claude-pending-decision.txt"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     세션 완료: $(date '+%Y-%m-%d %H:%M')       ║"
echo "╚══════════════════════════════════════╝"

# 현재 브랜치 표시
BRANCH=$(git -C "${PWD}" branch --show-current 2>/dev/null || echo "N/A")
echo "브랜치: $BRANCH"

# 수정된 파일 목록
if [ -f "$EDITS_LOG" ]; then
  EDIT_COUNT=$(sort -u "$EDITS_LOG" | wc -l | tr -d ' ')
  if [ "$EDIT_COUNT" -gt 0 ]; then
    echo ""
    echo "📝 이 세션에서 수정된 파일 ($EDIT_COUNT개):"
    sort -u "$EDITS_LOG" | awk '{print "  " $2}' | head -20
    if [ "$EDIT_COUNT" -gt 20 ]; then
      echo "  ... 그 외 $((EDIT_COUNT - 20))개"
    fi
  fi
  rm -f "$EDITS_LOG"
fi

# 자동 의사결정 로그 처리
if [ -f "$PENDING_DECISION" ] && [ -s "$PENDING_DECISION" ]; then
  echo ""
  echo "💡 자동 감지된 의사결정:"
  cat "$PENDING_DECISION"
  echo ""

  # DECISIONS.md에 append
  if [ -f "$DECISIONS_FILE" ]; then
    cat "$PENDING_DECISION" >> "$DECISIONS_FILE"
    echo "→ DECISIONS.md에 자동 기록 완료"
  fi
  rm -f "$PENDING_DECISION"
fi

# 미커밋 변경사항 알림
DIRTY=$(git -C "${PWD}" status --short 2>/dev/null || echo "")
if [ -n "$DIRTY" ]; then
  echo ""
  echo "⚠️  미커밋 변경사항 존재:"
  echo "$DIRTY" | head -10
  DIRTY_COUNT=$(echo "$DIRTY" | wc -l | tr -d ' ')
  if [ "$DIRTY_COUNT" -gt 10 ]; then
    echo "  ... 그 외 $((DIRTY_COUNT - 10))개"
  fi
  echo ""
  echo "→ /commit 또는 /done 실행을 권장합니다"
fi

echo "════════════════════════════════════════"
exit 0
