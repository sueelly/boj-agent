#!/usr/bin/env bash
# boj make [문제번호] [옵션]
# 환경 생성: A(Fetch) → B(Normalize) → C(Agent Skeleton)
# 옵션:
#   --lang java|python|cpp|c|...   언어 override
#   --image-mode download|reference|skip  이미지 처리 방식
#   --output /path                 출력 경로 override
#   --no-open                      에디터 자동 오픈 안 함

ROOT="${1:?ROOT}"
PROBLEM_NUM="${2:?문제번호}"
shift 2

# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"
boj_load_config

# ── 옵션 파싱 ────────────────────────────────────────────────────────────────
OPT_LANG=""
OPT_IMAGE_MODE=""
OPT_OUTPUT=""
OPT_NO_OPEN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang)         OPT_LANG="$2"; shift 2 ;;
    --lang=*)       OPT_LANG="${1#--lang=}"; shift ;;
    --image-mode)   OPT_IMAGE_MODE="$2"; shift 2 ;;
    --image-mode=*) OPT_IMAGE_MODE="${1#--image-mode=}"; shift ;;
    --output)       OPT_OUTPUT="$2"; shift 2 ;;
    --output=*)     OPT_OUTPUT="${1#--output=}"; shift ;;
    --no-open)      OPT_NO_OPEN=true; shift ;;
    -h|--help)
      echo "사용법: boj make <문제번호> [옵션]"
      echo "  --lang java|python|cpp|c|kotlin|go|rust|...  언어 override"
      echo "  --image-mode download|reference|skip          이미지 처리 방식 (기본: reference)"
      echo "  --output /path                                출력 경로 override"
      echo "  --no-open                                     에디터 자동 오픈 안 함"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

LANG="${OPT_LANG:-$boj_lang}"
IMAGE_MODE="${OPT_IMAGE_MODE:-reference}"
OUTPUT_DIR="${OPT_OUTPUT:-$ROOT}"

# ── 유효성 검사 ──────────────────────────────────────────────────────────────
boj_validate_lang "$LANG" || exit 1

case "$IMAGE_MODE" in
  download|reference|skip) ;;
  *)
    echo -e "${RED}Error: --image-mode는 download|reference|skip 중 하나여야 합니다.${NC}" >&2
    exit 1 ;;
esac

if [[ -n "$OPT_OUTPUT" && ! -d "$OPT_OUTPUT" ]]; then
  echo -e "${RED}Error: 출력 경로가 존재하지 않습니다: $OPT_OUTPUT${NC}" >&2
  exit 1
fi

# ── 언어 메타데이터 ───────────────────────────────────────────────────────────
_lang_ext() {
  case "$1" in
    java) echo "java" ;; python) echo "py" ;; cpp) echo "cpp" ;; c) echo "c" ;;
    kotlin) echo "kt" ;; go) echo "go" ;; rust) echo "rs" ;; ruby) echo "rb" ;;
    swift) echo "swift" ;; scala) echo "scala" ;; js) echo "js" ;; ts) echo "ts" ;;
    *) echo "" ;;
  esac
}
EXT="$(_lang_ext "$LANG")"
SUPPORTS_PARSE="false"
[[ "$LANG" == "java" || "$LANG" == "python" ]] && SUPPORTS_PARSE="true"

# ── 기존 폴더 확인 (네트워크 전) ─────────────────────────────────────────────
EXISTING_DIR="$(boj_find_problem_dir "$OUTPUT_DIR" "$PROBLEM_NUM")"
if [[ -n "$EXISTING_DIR" ]]; then
  echo -e "${YELLOW}Warning: '$(basename "$EXISTING_DIR")' 폴더가 이미 있습니다.${NC}"
  read -p "  덮어쓰시겠습니까? (y/N): " overwrite_confirm
  if [[ ! "$overwrite_confirm" =~ ^[Yy]$ ]]; then
    echo "취소됨."
    exit 0
  fi
fi

# ══════════════════════════════════════════════════════════════════════════════
# [A] Problem Fetcher: BOJ HTML → artifacts/problem.json
# ══════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}🔍 [A] BOJ ${PROBLEM_NUM}번 문제 정보 가져오는 중...${NC}"

TMP_FETCH=$(mktemp -d)
_PY_ERR=$(mktemp)
trap 'rm -f "$_PY_ERR"; rm -rf "$TMP_FETCH"' EXIT
if ! python3 "$ROOT/src/lib/boj_client.py" \
    --problem "$PROBLEM_NUM" \
    --out "$TMP_FETCH" \
    --image-mode "$IMAGE_MODE" 2>"$_PY_ERR"; then
  [[ -s "$_PY_ERR" ]] && cat "$_PY_ERR" >&2
  rm -f "$_PY_ERR"
  echo -e "${RED}Error: 문제 정보 가져오기 실패. 문제번호 또는 네트워크를 확인하세요.${NC}" >&2
  exit 1
fi
rm -f "$_PY_ERR"

TMP_JSON="$TMP_FETCH/problem.json"

# 제목 추출 (디렉터리 이름용)
PROBLEM_TITLE=$(python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print(d.get('title', ''))
except Exception:
    pass
" "$TMP_JSON" 2>/dev/null || echo "")

# ── 최종 디렉터리 결정 ────────────────────────────────────────────────────────
if [[ -n "$EXISTING_DIR" ]]; then
  PROBLEM_DIR="$EXISTING_DIR"
else
  if [[ -n "$PROBLEM_TITLE" ]]; then
    SLUG=$(python3 -c "
import re, sys
title = sys.argv[1]
slug = re.sub(r'[^\uAC00-\uD7A3a-zA-Z0-9 -]', '', title)
slug = re.sub(r' +', '-', slug.strip())
print(slug[:30])
" "$PROBLEM_TITLE" 2>/dev/null || echo "")
    PROBLEM_DIR="$OUTPUT_DIR/${PROBLEM_NUM}-${SLUG}"
  else
    PROBLEM_DIR="$OUTPUT_DIR/$PROBLEM_NUM"
  fi
fi

ARTIFACTS_DIR="$PROBLEM_DIR/artifacts"
mkdir -p "$ARTIFACTS_DIR"
cp "$TMP_JSON" "$ARTIFACTS_DIR/problem.json"
PROBLEM_JSON="$ARTIFACTS_DIR/problem.json"

echo -e "  ${GREEN}✓${NC} problem.json → artifacts/"

# ══════════════════════════════════════════════════════════════════════════════
# [B] Statement Normalizer: problem.json → README.md
# ══════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}📝 [B] README.md 생성 중...${NC}"

if ! python3 "$ROOT/src/lib/boj_normalizer.py" \
    --input "$PROBLEM_JSON" \
    --out "$PROBLEM_DIR/README.md" 2>/dev/null; then
  echo -e "${RED}Error: README.md 생성 실패${NC}" >&2
  exit 1
fi

echo -e "  ${GREEN}✓${NC} README.md 생성 완료"

# signature_review.md 아카이브 (기존 파일 보존)
SIG_REVIEW="$ARTIFACTS_DIR/signature_review.md"
if [[ -f "$SIG_REVIEW" ]]; then
  ARCHIVE_TS=$(date +%Y%m%d_%H%M%S)
  mv "$SIG_REVIEW" "${SIG_REVIEW%.md}.${ARCHIVE_TS}.bak"
  echo -e "  ${YELLOW}📦${NC} 기존 signature_review.md → .${ARCHIVE_TS}.bak"
fi

# ══════════════════════════════════════════════════════════════════════════════
# [C] IO Adapter Generator (Agent): 스켈레톤 생성
# ══════════════════════════════════════════════════════════════════════════════
AGENT_CMD=""
if [[ -n "${BOJ_AGENT_CMD:-}" ]]; then
  AGENT_CMD="$BOJ_AGENT_CMD"
elif [[ -n "$boj_agent_cmd" ]]; then
  AGENT_CMD="$boj_agent_cmd"
fi

if [[ -n "$AGENT_CMD" ]]; then
  echo -e "${BLUE}🤖 [C] 스켈레톤 생성 중 (에이전트)...${NC}"
  echo -e "  문제: ${PROBLEM_NUM} (${PROBLEM_TITLE}) | 언어: ${LANG} | SUPPORTS_PARSE: ${SUPPORTS_PARSE}"
  echo ""

  # 프롬프트 템플릿에 변수 치환 (Python으로 안전하게 처리)
  PROMPT=$(python3 - "$ROOT/prompts/make-skeleton.md" "$PROBLEM_JSON" \
      "$LANG" "$EXT" "$SUPPORTS_PARSE" "$PROBLEM_DIR" <<'PYEOF'
import sys, json, pathlib
template_path, json_path, lang, ext, supports_parse, problem_dir = sys.argv[1:]
template = pathlib.Path(template_path).read_text(encoding="utf-8")
problem  = json.loads(pathlib.Path(json_path).read_text(encoding="utf-8"))
result = template
result = result.replace("{{LANG}}", lang)
result = result.replace("{{EXT}}", ext)
result = result.replace("{{SUPPORTS_PARSE}}", supports_parse)
result = result.replace("{{PROBLEM_DIR}}", problem_dir)
result = result.replace("{{PROBLEM_JSON}}", json.dumps(problem, ensure_ascii=False, indent=2))
print(result, end="")
PYEOF
  )
  if [[ $? -ne 0 ]]; then
    echo -e "${RED}Error: 프롬프트 템플릿 생성 실패. prompts/make-skeleton.md 또는 artifacts/problem.json을 확인하세요.${NC}" >&2
    exit 1
  fi

  read -ra CMD <<< "$AGENT_CMD"
  (cd "$PROBLEM_DIR" && "${CMD[@]}" "$PROMPT")
  agent_exit=$?

  if [[ $agent_exit -ne 0 ]]; then
    echo -e "${YELLOW}Warning: 에이전트 실행 실패 (exit $agent_exit). 수동으로 진행하세요.${NC}" >&2
  fi

  # ── Gate Check: 단일 String/str 파라미터(raw stdin blob) 감지 ─────────────
  # Java: solve(String <any>), Python: solve(... : str) 단독 파라미터
  SOLUTION_FILE="$PROBLEM_DIR/Solution.$EXT"
  if [[ -f "$SOLUTION_FILE" ]]; then
    if grep -qE 'solve\s*\(\s*(String\s+\w+|(self\s*,\s*)?\w+\s*:\s*str)\s*\)' "$SOLUTION_FILE" 2>/dev/null; then
      echo -e "${YELLOW}Warning: Gate Check — solve()가 단일 String/str 파라미터(raw stdin blob)를 사용합니다.${NC}" >&2
      echo -e "  ${YELLOW}→ artifacts/signature_review.md를 확인하고 서명을 수정하세요.${NC}" >&2
    fi
  fi

  # ── Execution Verify: boj run ─────────────────────────────────────────────
  echo -e "${BLUE}🧪 Execution Verify: boj run ${PROBLEM_NUM}...${NC}"
  run_out=$( (cd "$ROOT" && "$ROOT/src/boj" run "$PROBLEM_NUM" 2>&1) || true)
  run_exit=$?
  echo "$run_out"
  if [[ $run_exit -ne 0 ]]; then
    echo -e "${YELLOW}Warning: boj run 실패 — Solution 구현 후 재실행하세요.${NC}" >&2
  fi

else
  # ── fallback: 에디터 + 클립보드 ──────────────────────────────────────────
  echo -e "${YELLOW}Warning: 에이전트 미설정. 에디터+클립보드 fallback.${NC}" >&2
  # 구분자는 실제 줄바꿈으로 구성. printf로 복사해 JSON 내 \n,\t,\\ 등이 해석되지 않도록 함
  PROMPT="백준 ${PROBLEM_NUM}번 스켈레톤 만들어줘. 언어: ${LANG}"$'\n\n'"$(cat "$PROBLEM_JSON")"
  if command -v pbcopy &>/dev/null; then
    printf '%s' "$PROMPT" | pbcopy
    echo -e "${GREEN}📋 problem.json 내용을 클립보드에 복사했습니다.${NC}"
  fi
fi

# ══════════════════════════════════════════════════════════════════════════════
# 요약
# ══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${GREEN}✅ boj make ${PROBLEM_NUM} 완료: $(basename "$PROBLEM_DIR")${NC}"
echo -e "  📁 $PROBLEM_DIR"
echo -e "  📄 README.md"
echo -e "  🔧 artifacts/problem.json"
if [[ -f "$SIG_REVIEW" ]]; then
  echo -e "  🔍 artifacts/signature_review.md"
fi

if [[ "$OPT_NO_OPEN" != "true" ]]; then
  boj_open_editor "$PROBLEM_DIR" "$boj_editor" 2>/dev/null || true
fi
