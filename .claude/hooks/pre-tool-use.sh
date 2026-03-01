#!/usr/bin/env bash
# PreToolUse hook: 위험 명령어 차단 및 정책 검증
# stdin: JSON with {"tool_name": "...", "tool_input": {...}}
# exit 0 = allow, exit 2 = block

set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_name', ''))
" 2>/dev/null || echo "")

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

# Bash 도구에만 적용
if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

# === 즉시 차단 패턴 ===
# grep -E 사용: 리터럴 . * $ 는 bash에서 \\ . \\ * \\ $ 로 전달
BLOCKED_PATTERNS=(
  "git push --force"
  "git push -f "
  "git push -f$"
  "git commit --no-verify"
  "git reset --hard"
  "git checkout -- \\."
  "git checkout -- \\*"
  "git clean -f"
  "rm -rf /"
  "rm -rf ~"
  "rm -rf \\\$HOME"
  "curl .* \| bash"
  "curl .* \| sh"
  "wget .* \| bash"
  "wget .* \| sh"
  "DROP TABLE"
  "DELETE FROM.*WHERE.*1=1"
  "TRUNCATE TABLE"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern" 2>/dev/null; then
    echo "BLOCKED: '$pattern' 패턴이 감지되어 차단됨." >&2
    echo "이 명령이 필요하다면 터미널에서 직접 실행하세요." >&2
    exit 2
  fi
done

# === main/master 직접 push 차단 ===
if echo "$COMMAND" | grep -qE "git push.*origin (main|master)$" 2>/dev/null; then
  CURRENT_BRANCH=$(git -C "${PWD}" branch --show-current 2>/dev/null || echo "")
  if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo "BLOCKED: main/master 브랜치에서 직접 push 금지." >&2
    echo "PR을 통해 병합하세요: /done 또는 /pr 실행" >&2
    exit 2
  fi
fi

# === 경고: git add -A 또는 git add . ===
if echo "$COMMAND" | grep -qE '^git add (-A|\.)$' 2>/dev/null; then
  STAGED=$(git -C "${PWD}" diff --stat 2>/dev/null | tail -1 || echo "")
  echo "WARNING: 'git add -A' 또는 'git add .' 는 모든 파일을 스테이징합니다." >&2
  echo "특정 파일을 명시적으로 추가하는 것을 권장합니다." >&2
  echo "현재 변경사항: $(git -C "${PWD}" diff --name-only 2>/dev/null | head -10 || echo 'N/A')" >&2
  # 차단하지 않고 경고만
fi

exit 0
