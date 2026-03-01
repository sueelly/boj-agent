#!/usr/bin/env bash
# PostToolUse hook: 파일 수정 후 즉시 경고 및 세션 로그 기록
# Write, Edit, MultiEdit 이벤트에서 실행 (async)
# stdin: JSON with tool details

set -euo pipefail

INPUT=$(cat)

FILE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {})
# Write/Edit uses file_path, MultiEdit uses edits[0].file_path
fp = ti.get('file_path', '')
if not fp:
    edits = ti.get('edits', [])
    if edits:
        fp = edits[0].get('file_path', '')
print(fp)
" 2>/dev/null || echo "")

[ -z "$FILE" ] && exit 0
[ ! -f "$FILE" ] && exit 0

# 세션 편집 로그 기록 (stop hook에서 집계)
EDITS_LOG="/tmp/claude-session-edits.log"
echo "$(date '+%H:%M:%S') $FILE" >> "$EDITS_LOG"

# === 시크릿 패턴 감지 (모든 언어) ===
SECRET_PATTERNS=(
  "(password|passwd|pwd)\s*=\s*['\"][^$\{\(]"
  "(secret|api_secret)\s*=\s*['\"][^$\{\(]"
  "(api_key|apikey|access_key)\s*=\s*['\"][^$\{\(]"
  "(private_key|privatekey)\s*=\s*['\"][^$\{\(]"
  "-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
  if grep -qEi "$pattern" "$FILE" 2>/dev/null; then
    echo "WARNING: [$FILE] 하드코딩된 시크릿 의심 패턴 발견." >&2
    echo "  환경변수 또는 설정 파일을 사용하세요. 커밋 전 반드시 확인." >&2
    break
  fi
done

# === Java 특화 경고 ===
if [[ "$FILE" == *.java ]]; then
  if grep -q "printStackTrace()" "$FILE" 2>/dev/null; then
    echo "NOTE: [$FILE] printStackTrace() 발견 — SLF4J Logger 사용을 권장합니다." >&2
  fi
  if grep -qE '"localhost"|"127\.0\.0\.1"' "$FILE" 2>/dev/null; then
    echo "NOTE: [$FILE] 'localhost' 하드코딩 — 설정 프로퍼티(@Value 또는 application.yml)를 사용하세요." >&2
  fi
  if grep -qE "@Autowired" "$FILE" 2>/dev/null; then
    if ! grep -qE "^\s+@Autowired\s*$" "$FILE" 2>/dev/null; then
      echo "NOTE: [$FILE] @Autowired 필드 주입 발견 — 생성자 주입 방식을 권장합니다." >&2
    fi
  fi
fi

# === Python 특화 경고 ===
if [[ "$FILE" == *.py ]]; then
  if grep -qE "^def [a-zA-Z_]+\([^)]*\)\s*:" "$FILE" 2>/dev/null; then
    if grep -qE "^def [a-zA-Z_]+\([^)]*\)\s*:" "$FILE" 2>/dev/null && \
       ! grep -qE "^def [a-zA-Z_]+\([^)]*\)\s*->" "$FILE" 2>/dev/null; then
      # 타입 힌트 없는 함수가 있는 경우 (간단한 휴리스틱)
      :  # 경고 생략 (너무 많은 false positive 방지)
    fi
  fi
fi

# === Kotlin 특화 경고 ===
if [[ "$FILE" == *.kt ]]; then
  if grep -qE "!!" "$FILE" 2>/dev/null; then
    echo "NOTE: [$FILE] !! (not-null assertion) 발견 — ?.let{} 또는 ?: 사용을 권장합니다." >&2
  fi
  if grep -qE "^\s+var " "$FILE" 2>/dev/null; then
    COUNT=$(grep -cE "^\s+var " "$FILE" 2>/dev/null || echo 0)
    if [ "$COUNT" -gt 3 ]; then
      echo "NOTE: [$FILE] var 선언 ${COUNT}개 발견 — val 우선 사용을 권장합니다." >&2
    fi
  fi
fi

exit 0
