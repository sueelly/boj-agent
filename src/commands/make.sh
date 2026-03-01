#!/usr/bin/env bash
# boj make [문제번호] [옵션]
# 환경 생성: 에이전트 또는 에디터+클립보드 fallback
# 옵션:
#   --lang java|python|cpp|c|...   언어 override
#   --image-mode download|reference|skip  이미지 처리 방식
#   --output /path                 출력 경로 override
#   --no-open                      에디터 자동 오픈 안 함

ROOT="${1:?ROOT}"
PROBLEM_NUM="${2:?문제번호}"
shift 2

# 공통 라이브러리
# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"
boj_load_config

# 옵션 파싱
OPT_LANG=""
OPT_IMAGE_MODE=""
OPT_OUTPUT=""
OPT_NO_OPEN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang) OPT_LANG="$2"; shift 2 ;;
    --lang=*) OPT_LANG="${1#--lang=}"; shift ;;
    --image-mode) OPT_IMAGE_MODE="$2"; shift 2 ;;
    --image-mode=*) OPT_IMAGE_MODE="${1#--image-mode=}"; shift ;;
    --output) OPT_OUTPUT="$2"; shift 2 ;;
    --output=*) OPT_OUTPUT="${1#--output=}"; shift ;;
    --no-open) OPT_NO_OPEN=true; shift ;;
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

# 언어 유효성 검사
boj_validate_lang "$LANG" || exit 1

# 이미지 모드 유효성 검사
case "$IMAGE_MODE" in
  download|reference|skip) ;;
  *)
    echo -e "${RED}Error: --image-mode는 download|reference|skip 중 하나여야 합니다.${NC}" >&2
    exit 1 ;;
esac

# 출력 경로 검사
if [[ -n "$OPT_OUTPUT" && ! -d "$OPT_OUTPUT" ]]; then
  echo -e "${RED}Error: 출력 경로가 존재하지 않습니다: $OPT_OUTPUT${NC}" >&2
  exit 1
fi

# 이미 존재하는 문제 폴더 확인
EXISTING_DIR="$(boj_find_problem_dir "$OUTPUT_DIR" "$PROBLEM_NUM")"
if [[ -n "$EXISTING_DIR" ]]; then
  echo -e "${YELLOW}Warning: '$(basename "$EXISTING_DIR")' 폴더가 이미 있습니다.${NC}"
  read -p "  덮어쓰시겠습니까? (y/N): " overwrite_confirm
  if [[ ! "$overwrite_confirm" =~ ^[Yy]$ ]]; then
    echo "취소됨."
    exit 0
  fi
fi

URL="https://www.acmicpc.net/problem/$PROBLEM_NUM"

# 프롬프트 구성 (prompts/make-environment.md 기반 + 옵션 정보 포함)
build_prompt() {
  local prompt_file="$ROOT/prompts/make-environment.md"
  local user_request="백준 ${PROBLEM_NUM}번 문제 풀이 환경 만들어줘. ${URL}"
  local options_note="[설정] 언어: $LANG, 이미지 처리: $IMAGE_MODE, 출력 경로: $OUTPUT_DIR"

  if [[ -f "$prompt_file" ]]; then
    # prompts 파일 내용 + 사용자 요청 + 옵션
    echo "$(cat "$prompt_file")"
    echo ""
    echo "---"
    echo "$options_note"
    echo ""
    echo "$user_request"
  else
    echo "$user_request ($options_note)"
  fi
}

AGENT_CMD=""
if [[ -n "${BOJ_AGENT_CMD:-}" ]]; then
  AGENT_CMD="$BOJ_AGENT_CMD"
elif [[ -n "$boj_agent_cmd" ]]; then
  AGENT_CMD="$boj_agent_cmd"
fi

if [[ -n "$AGENT_CMD" ]]; then
  echo -e "${BLUE}🔄 에이전트로 환경 생성 요청 중...${NC}"
  echo -e "  문제: ${PROBLEM_NUM} | 언어: ${LANG} | 이미지: ${IMAGE_MODE}"
  echo ""
  PROMPT="$(build_prompt)"
  read -ra CMD <<< "$AGENT_CMD"
  (cd "$OUTPUT_DIR" && "${CMD[@]}" "$PROMPT")
  exit_code=$?

  if [[ $exit_code -ne 0 ]]; then
    echo -e "${RED}Error: 에이전트 실행 실패 (exit $exit_code). 수동으로 진행하세요.${NC}" >&2
    echo "  URL: $URL"
    exit 1
  fi

  # 생성 후 자체 검증: 폴더 생성 확인
  NEW_DIR="$(boj_find_problem_dir "$OUTPUT_DIR" "$PROBLEM_NUM")"
  if [[ -z "$NEW_DIR" ]]; then
    echo -e "${YELLOW}Warning: 문제 폴더가 생성되지 않은 것 같습니다. 에이전트 출력을 확인하세요.${NC}" >&2
  else
    echo ""
    echo -e "${GREEN}✅ 환경 생성 완료: $(basename "$NEW_DIR")${NC}"
    # 기본 파일 존재 확인
    local_lang_ext=""
    case "$LANG" in
      java) local_lang_ext="java" ;;
      python) local_lang_ext="py" ;;
      cpp) local_lang_ext="cpp" ;;
      c) local_lang_ext="c" ;;
      *) local_lang_ext="" ;;
    esac
    missing_files=()
    [[ ! -f "$NEW_DIR/README.md" ]] && missing_files+=("README.md")
    [[ -n "$local_lang_ext" && ! -f "$NEW_DIR/Solution.$local_lang_ext" ]] && missing_files+=("Solution.$local_lang_ext")
    [[ ! -f "$NEW_DIR/test/test_cases.json" ]] && missing_files+=("test/test_cases.json")

    if [[ ${#missing_files[@]} -gt 0 ]]; then
      echo -e "${YELLOW}Warning: 다음 파일이 없습니다 (README와 문제 내용 불일치 가능):${NC}" >&2
      for f in "${missing_files[@]}"; do
        echo -e "  ${YELLOW}✗ $f${NC}" >&2
      done
    fi

    # 에디터 오픈
    if [[ "$OPT_NO_OPEN" != "true" ]]; then
      boj_open_editor "$NEW_DIR" "$boj_editor" 2>/dev/null || true
    fi
  fi
else
  # fallback: 에디터 + 클립보드
  PROMPT="백준 ${PROBLEM_NUM}번 문제 풀이 환경 만들어줘. ${URL}"
  PROMPT="$PROMPT (언어: $LANG, 이미지: $IMAGE_MODE)"

  if command -v open &>/dev/null; then
    open "$URL"
  fi
  if command -v pbcopy &>/dev/null; then
    echo "$PROMPT" | pbcopy
    echo -e "${GREEN}📋 채팅에 붙여넣을 문구를 클립보드에 복사했습니다.${NC}"
  fi

  if [[ "$OPT_NO_OPEN" != "true" ]]; then
    boj_open_editor "$ROOT" "$boj_editor" 2>/dev/null || true
  fi

  echo ""
  echo -e "${YELLOW}👉 폴더를 에디터로 열었습니다. 채팅에 붙여넣기하면 AI가 문제 폴더를 만듭니다.${NC}"
  echo "   $PROMPT"
fi
