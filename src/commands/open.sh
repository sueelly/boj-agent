#!/usr/bin/env bash
# boj open [문제번호] [옵션]
# 해당 문제 폴더를 에디터 루트로 열기
# 옵션:
#   --editor code|cursor|vim|...  에디터 override

ROOT="${1:?ROOT}"
PROBLEM_NUM="${2:?문제번호}"
shift 2

# 공통 라이브러리
# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"
boj_load_config

# 옵션 파싱
OPT_EDITOR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --editor) OPT_EDITOR="$2"; shift 2 ;;
    --editor=*) OPT_EDITOR="${1#--editor=}"; shift ;;
    -h|--help)
      echo "사용법: boj open <문제번호> [옵션]"
      echo "  --editor code|cursor|vim|...  에디터 override (기본: ~/.config/boj/editor)"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

EDITOR_CMD="${OPT_EDITOR:-$boj_editor}"

PROBLEM_DIR=$(boj_find_problem_dir "$ROOT" "$PROBLEM_NUM")
if [[ -z "$PROBLEM_DIR" || ! -d "$PROBLEM_DIR" ]]; then
  echo -e "${YELLOW}📁 '${PROBLEM_NUM}' 문제 폴더가 없습니다. 먼저 환경을 생성합니다.${NC}"
  echo "   생성 후: boj open $PROBLEM_NUM"
  if [[ -x "$ROOT/src/boj" ]]; then
    exec "$ROOT/src/boj" make "$PROBLEM_NUM"
  fi
  exit 1
fi

boj_open_editor "$PROBLEM_DIR" "$EDITOR_CMD" || exit 1
echo -e "${GREEN}✅ 해당 문제 폴더를 에디터로 열었습니다: $(basename "$PROBLEM_DIR")${NC}"
