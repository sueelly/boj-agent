#!/usr/bin/env bash
# boj review [문제번호] — 리뷰 요청 (에이전트 또는 에디터+클립보드)

ROOT="${1:?ROOT}"
PROBLEM_NUM="${2:?문제번호}"
shift 2

# 공통 라이브러리
# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"
boj_load_config

PROBLEM_DIR="$(boj_require_problem_dir "$ROOT" "$PROBLEM_NUM")" || exit 1

# Solution 파일 경고 (없어도 리뷰는 진행)
if ! ls "$PROBLEM_DIR"/Solution.* &>/dev/null; then
  echo -e "${YELLOW}Warning: Solution 파일이 없습니다. 리뷰할 코드가 없을 수 있습니다.${NC}" >&2
fi

AGENT_CMD=""
if [[ -n "${BOJ_AGENT_CMD:-}" ]]; then
  AGENT_CMD="$BOJ_AGENT_CMD"
elif [[ -n "$boj_agent_cmd" ]]; then
  AGENT_CMD="$boj_agent_cmd"
fi

# prompts/review.md 가 있으면 사용
REVIEW_PROMPT="리뷰해줘"
if [[ -f "$ROOT/prompts/review.md" ]]; then
  REVIEW_PROMPT="$(cat "$ROOT/prompts/review.md")

---
리뷰해줘"
fi

if [[ -n "$AGENT_CMD" ]]; then
  echo -e "${BLUE}🔄 에이전트로 리뷰 요청 중... (작업 디렉터리: $PROBLEM_DIR)${NC}"
  read -ra CMD <<< "$AGENT_CMD"
  if ! (cd "$PROBLEM_DIR" && "${CMD[@]}" "$REVIEW_PROMPT"); then
    echo -e "${RED}Error: 에이전트 실행 실패. 수동으로 리뷰를 요청하세요.${NC}" >&2
    exit 1
  fi
else
  if command -v pbcopy &>/dev/null; then
    echo "리뷰해줘" | pbcopy
    echo -e "${GREEN}📋 '리뷰해줘' 를 클립보드에 복사했습니다.${NC}"
  fi
  boj_open_editor "$PROBLEM_DIR" "$boj_editor" 2>/dev/null || true
  echo ""
  echo -e "${YELLOW}👉 해당 문제 폴더를 에디터로 열었습니다. 리뷰는 채팅에서 '리뷰해줘' 요청하세요.${NC}"
fi
