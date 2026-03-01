#!/usr/bin/env bash
# boj setup [--check] — 초기 설정/인증 저장
# 최초 1회 실행으로 루트, 기본 언어, git, BOJ 세션, 에이전트 명령 저장

ROOT="${1:?ROOT}"
shift
MODE="interactive"

# 옵션 파싱
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check|-c) MODE="check"; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# 공통 라이브러리 로드
# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"

if [[ "$MODE" == "check" ]]; then
  boj_check_config
  exit 0
fi

# ======= 대화형 설정 =======
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  BOJ CLI 초기 설정${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# --- 1. BOJ_ROOT ---
current_root="$(boj_config_get root "")"
echo -e "${YELLOW}[1/5] 레포 루트 경로${NC}"
if [[ -n "$current_root" ]]; then
  echo "  현재: $current_root"
  read -p "  변경하시겠습니까? (y/N): " change_root
  if [[ ! "$change_root" =~ ^[Yy]$ ]]; then
    echo "  유지: $current_root"
  else
    current_root=""
  fi
fi
if [[ -z "$current_root" ]]; then
  echo "  boj-agent 레포 루트 경로를 입력하세요."
  echo "  (현재 디렉터리: $(pwd))"
  read -p "  경로 [$(pwd)]: " new_root
  new_root="${new_root:-$(pwd)}"
  if [[ ! -d "$new_root" ]]; then
    echo -e "${RED}Error: 경로가 존재하지 않습니다: $new_root${NC}" >&2
    exit 1
  fi
  boj_config_set root "$new_root"
  echo -e "  ${GREEN}✓ 저장: $new_root${NC}"
fi

echo ""

# --- 2. 기본 언어 ---
echo -e "${YELLOW}[2/5] 기본 언어 (make/run/submit 기본값)${NC}"
current_lang="$(boj_config_get lang java)"
if [[ -n "$current_lang" ]]; then
  echo "  현재: $current_lang"
  read -p "  변경하시겠습니까? (y/N): " change_lang
  if [[ ! "$change_lang" =~ ^[Yy]$ ]]; then
    echo "  유지: $current_lang"
  else
    current_lang=""
  fi
fi
if [[ -z "$current_lang" ]]; then
  echo "  make/run/submit 시 사용할 기본 언어를 입력하세요."
  echo "  예: java, python, cpp, c, kotlin, go, rust, ruby, swift, scala, js, ts"
  read -p "  기본 언어 [java]: " new_lang
  new_lang="${new_lang:-java}"
  if boj_validate_lang "$new_lang" 2>/dev/null; then
    boj_config_set lang "$new_lang"
    echo -e "  ${GREEN}✓ 저장: $new_lang${NC}"
  else
    echo -e "  ${YELLOW}유효하지 않아 기본값 java 유지${NC}"
    boj_config_set lang "java"
  fi
fi

echo ""

# --- 3. Git 정보 확인 ---
echo -e "${YELLOW}[3/5] Git 사용자 정보${NC}"
git_name="$(git config --global user.name 2>/dev/null || echo '')"
git_email="$(git config --global user.email 2>/dev/null || echo '')"
if [[ -n "$git_name" && -n "$git_email" ]]; then
  echo -e "  ${GREEN}✓${NC} $git_name <$git_email>"
else
  echo -e "  ${YELLOW}미설정${NC}. git config --global 으로 설정하세요:"
  if [[ -z "$git_name" ]]; then
    read -p "  git user.name: " new_git_name
    if [[ -n "$new_git_name" ]]; then
      git config --global user.name "$new_git_name"
      echo -e "  ${GREEN}✓ 저장됨${NC}"
    fi
  fi
  if [[ -z "$git_email" ]]; then
    read -p "  git user.email: " new_git_email
    if [[ -n "$new_git_email" ]]; then
      git config --global user.email "$new_git_email"
      echo -e "  ${GREEN}✓ 저장됨${NC}"
    fi
  fi
fi

echo ""

# --- 4. BOJ 세션 쿠키 ---
echo -e "${YELLOW}[4/5] BOJ 세션 쿠키${NC}"
current_session="$(boj_config_get session "")"
if [[ -n "$current_session" ]]; then
  echo -e "  ${GREEN}✓${NC} 이미 설정됨"
  read -p "  변경하시겠습니까? (y/N): " change_session
  if [[ ! "$change_session" =~ ^[Yy]$ ]]; then
    echo "  유지"
    skip_session=true
  fi
fi
if [[ "${skip_session:-false}" != "true" ]]; then
  echo "  BOJ 세션 쿠키가 있으면 commit 통계 조회 등이 가능합니다."
  echo "  방법:"
  echo "    1. 브라우저에서 acmicpc.net 로그인"
  echo "    2. 개발자도구(F12) → Application → Cookies"
  echo "    3. 'bojautologin' 또는 'OnlineJudge' 쿠키 값 복사"
  read -p "  세션 쿠키 값 (없으면 Enter 스킵): " new_session
  if [[ -n "$new_session" ]]; then
    boj_config_set session "$new_session"
    echo -e "  ${GREEN}✓ 저장됨${NC}"
  else
    echo "  스킵 (나중에 boj setup 으로 추가 가능)"
  fi

  # BOJ 사용자 ID
  current_user="$(boj_config_get user "")"
  if [[ -z "$current_user" ]]; then
    read -p "  BOJ 사용자 ID (통계 조회용, 없으면 Enter 스킵): " new_user
    if [[ -n "$new_user" ]]; then
      boj_config_set user "$new_user"
      echo -e "  ${GREEN}✓ 저장됨${NC}"
    fi
  else
    echo "  사용자 ID: $current_user"
  fi
fi

echo ""

# --- 5. 에이전트 명령 ---
echo -e "${YELLOW}[5/5] 에이전트 명령 (make/review에 사용)${NC}"
current_agent="$(boj_config_get agent "")"
if [[ -n "$current_agent" ]]; then
  echo "  현재: $current_agent"
  read -p "  변경하시겠습니까? (y/N): " change_agent
  if [[ ! "$change_agent" =~ ^[Yy]$ ]]; then
    echo "  유지"
    current_agent="KEEP"
  fi
fi
if [[ "$current_agent" != "KEEP" ]]; then
  echo "  에이전트 CLI 명령을 입력하세요."
  echo "  예: claude -p --  (Claude Code CLI)"
  echo "      agent chat -f -p --  (Cursor Agent)"
  echo "  없으면 Enter → 에디터+클립보드 fallback"
  read -p "  에이전트 명령: " new_agent
  if [[ -n "$new_agent" ]]; then
    boj_config_set agent "$new_agent"
    echo -e "  ${GREEN}✓ 저장됨${NC}"
  else
    echo "  미설정 (에디터+클립보드 fallback 사용)"
  fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 설정 완료!${NC}"
echo ""
echo "확인: boj setup --check"
echo "시작: boj make 4949"
