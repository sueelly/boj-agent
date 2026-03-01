#!/usr/bin/env bash
# boj commit [문제번호] [옵션]
# - 문제 폴더 파일 자동 git add
# - BOJ Accepted 통계(memory/time) 조회해 commit message 포함
# - 조회 실패 시 fallback (commit은 항상 진행)

ROOT="${1:?ROOT}"
PROBLEM_NUM="${2:?문제번호}"
shift 2

# 공통 라이브러리
# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"
boj_load_config

# 옵션 파싱
OPT_MSG=""
OPT_NO_STATS=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --message|-m) OPT_MSG="$2"; shift 2 ;;
    --message=*) OPT_MSG="${1#--message=}"; shift ;;
    --no-stats) OPT_NO_STATS=true; shift ;;
    -h|--help)
      echo "사용법: boj commit <문제번호> [옵션]"
      echo "  --message \"...\"  커밋 메시지 직접 지정"
      echo "  --no-stats       BOJ 통계 조회 스킵"
      exit 0 ;;
    --) shift; OPT_MSG="$*"; break ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *) OPT_MSG="$*"; break ;;
  esac
done

# git repo 확인
if ! git -C "$ROOT" rev-parse --git-dir &>/dev/null; then
  echo -e "${RED}Error: git 저장소가 아닙니다: $ROOT${NC}" >&2
  exit 1
fi

# git user 확인
git_email="$(git config --global user.email 2>/dev/null || echo '')"
if [[ -z "$git_email" ]]; then
  echo -e "${RED}Error: git user.email이 설정되지 않았습니다. boj setup 또는 git config --global user.email 실행.${NC}" >&2
  exit 1
fi

# 문제 폴더 찾기
PROBLEM_DIR="$(boj_require_problem_dir "$ROOT" "$PROBLEM_NUM")" || exit 1
PROBLEM_NAME="$(basename "$PROBLEM_DIR")"

echo -e "${BLUE}📁 문제 폴더: $PROBLEM_NAME${NC}"

# ======= BOJ 통계 조회 =======
BOJ_STATS=""

fetch_boj_stats() {
  local session="${boj_session:-}"
  local user="${boj_user:-}"

  if [[ "$OPT_NO_STATS" == "true" ]]; then
    BOJ_STATS="[BOJ 통계: 스킵]"
    return 0
  fi

  if [[ -z "$session" ]]; then
    BOJ_STATS="[BOJ 통계: 세션 없음]"
    return 0
  fi

  if [[ -z "$user" ]]; then
    BOJ_STATS="[BOJ 통계: 사용자 ID 없음]"
    return 0
  fi

  local status_url="https://www.acmicpc.net/status?problem_id=${PROBLEM_NUM}&user_id=${user}&result_id=4"
  echo -e "${BLUE}BOJ 통계 조회 중...${NC}"

  local response
  # setup에서 'bojautologin' 또는 'OnlineJudge' 쿠키 값 중 하나를 저장하므로
  # 두 쿠키 키에 모두 동일 값을 전송하여 어느 경우든 인증되도록 함
  response=$(curl -s --max-time 5 \
    -H "Cookie: OnlineJudge=$session; bojautologin=$session" \
    -H "User-Agent: Mozilla/5.0 (compatible; boj-agent/1.0)" \
    "$status_url" 2>/dev/null) || {
    BOJ_STATS="[BOJ 통계: 네트워크 오류]"
    return 0
  }

  if [[ -z "$response" ]]; then
    BOJ_STATS="[BOJ 통계: 응답 없음]"
    return 0
  fi

  # 메모리/시간 파싱 (BSD grep 호환: -oE + sed, macOS 기본 grep에 -P 없음)
  local memory time_ms
  memory=$(echo "$response" | grep -oE '<td>[0-9]+ KB</td>' | head -1 | sed -n 's/<td>\([0-9]*\) KB<\/td>/\1/p' 2>/dev/null || echo "")
  time_ms=$(echo "$response" | grep -oE '<td>[0-9]+ ms</td>' | head -1 | sed -n 's/<td>\([0-9]*\) ms<\/td>/\1/p' 2>/dev/null || echo "")

  if [[ -n "$memory" && -n "$time_ms" ]]; then
    BOJ_STATS="[✓ ${time_ms}ms ${memory}KB]"
    echo -e "${GREEN}✓ 통계: ${time_ms}ms / ${memory}KB${NC}"
  else
    # Accepted 결과 없는 경우 (grep -E: | 는 alternation)
    if echo "$response" | grep -E -q "맞았습니다|Accepted"; then
      BOJ_STATS="[BOJ 통계: 파싱 실패]"
    else
      BOJ_STATS="[BOJ 통계: Accepted 없음]"
    fi
  fi
}

fetch_boj_stats

# ======= 커밋 메시지 구성 =======
if [[ -n "$OPT_MSG" ]]; then
  COMMIT_MSG="$OPT_MSG"
else
  COMMIT_MSG="${PROBLEM_NAME} 풀이 완료 $BOJ_STATS"
fi

echo -e "${BLUE}💬 커밋 메시지: $COMMIT_MSG${NC}"
echo ""

# ======= 변경 파일 표시 =======
echo -e "${YELLOW}📋 변경된 파일:${NC}"
git -C "$ROOT" status --short -- "$PROBLEM_NAME" 2>/dev/null | head -20

echo ""

# ======= git add (문제 폴더 파일) =======
echo -e "${BLUE}➕ 파일 추가 중...${NC}"

# 언어 감지
lang_ext=""
if [[ -f "$PROBLEM_DIR/Solution.java" ]]; then lang_ext="java"
elif [[ -f "$PROBLEM_DIR/Solution.py" ]]; then lang_ext="py"
elif [[ -f "$PROBLEM_DIR/Solution.cpp" ]]; then lang_ext="cpp"
elif [[ -f "$PROBLEM_DIR/Solution.c" ]]; then lang_ext="c"
elif [[ -f "$PROBLEM_DIR/Solution.kt" ]]; then lang_ext="kt"
elif [[ -f "$PROBLEM_DIR/Solution.go" ]]; then lang_ext="go"
fi

# 핵심 파일들만 명시적으로 add
files_to_add=()
[[ -f "$PROBLEM_DIR/README.md" ]] && files_to_add+=("$PROBLEM_NAME/README.md")
[[ -n "$lang_ext" && -f "$PROBLEM_DIR/Solution.$lang_ext" ]] && files_to_add+=("$PROBLEM_NAME/Solution.$lang_ext")
[[ -f "$PROBLEM_DIR/test/test_cases.json" ]] && files_to_add+=("$PROBLEM_NAME/test/test_cases.json")
[[ -n "$lang_ext" && -f "$PROBLEM_DIR/test/Parse.$lang_ext" ]] && files_to_add+=("$PROBLEM_NAME/test/Parse.$lang_ext")
[[ -f "$PROBLEM_DIR/submit/REVIEW.md" ]] && files_to_add+=("$PROBLEM_NAME/submit/REVIEW.md")
[[ -n "$lang_ext" && -f "$PROBLEM_DIR/submit/Submit.$lang_ext" ]] && files_to_add+=("$PROBLEM_NAME/submit/Submit.$lang_ext")

if [[ ${#files_to_add[@]} -gt 0 ]]; then
  if ! git -C "$ROOT" add "${files_to_add[@]}"; then
    echo -e "${YELLOW}Warning: 일부 파일 스테이징 실패. 수동으로 git add를 확인하세요.${NC}" >&2
  fi
fi

# ======= 커밋 실행 =======
echo -e "${BLUE}📝 커밋 중...${NC}"
if git -C "$ROOT" commit -m "$COMMIT_MSG"; then
  echo ""
  echo -e "${GREEN}✅ 커밋 완료!${NC}"
  echo ""
  read -p "GitHub에 푸시하시겠습니까? (y/N): " push_confirm
  if [[ "$push_confirm" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🚀 푸시 중...${NC}"
    (cd "$ROOT" && git push) && echo -e "${GREEN}✅ 푸시 완료!${NC}" || echo -e "${RED}❌ 푸시 실패${NC}"
  else
    echo "푸시를 건너뛰었습니다. 나중에 'git push'로 푸시하세요."
  fi
else
  echo -e "${YELLOW}⚠️ 커밋할 변경사항이 없거나 실패했습니다.${NC}"
fi
