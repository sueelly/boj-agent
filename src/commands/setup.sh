#!/usr/bin/env bash
# boj setup [--check] [--session <값>] [--lang <언어>] [--root <경로>] — 초기 설정/인증 저장
# 최초 1회 실행으로 루트, 기본 언어, git, BOJ 세션, 에이전트 명령 저장
# 비대화형: --session, --lang, --root 플래그로 직접 설정 가능

ROOT="${1:?ROOT}"
shift
MODE="interactive"
OPT_SESSION=""
OPT_LANG_SET=""
OPT_ROOT_SET=""
OPT_USERNAME=""

# 옵션 파싱
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check|-c) MODE="check"; shift ;;
    --session)  OPT_SESSION="$2"; MODE="set"; shift 2 ;;
    --session=*) OPT_SESSION="${1#--session=}"; MODE="set"; shift ;;
    --lang)     OPT_LANG_SET="$2"; MODE="set"; shift 2 ;;
    --lang=*)   OPT_LANG_SET="${1#--lang=}"; MODE="set"; shift ;;
    --root)     OPT_ROOT_SET="$2"; MODE="set"; shift 2 ;;
    --root=*)   OPT_ROOT_SET="${1#--root=}"; MODE="set"; shift ;;
    --username) OPT_USERNAME="$2"; MODE="set"; shift 2 ;;
    --username=*) OPT_USERNAME="${1#--username=}"; MODE="set"; shift ;;
    -h|--help)
      echo "사용법: boj setup [옵션]"
      echo "  --check                현재 설정 표시"
      echo "  --session <값>         BOJ 세션 쿠키(OnlineJudge) 직접 저장"
      echo "  --username <아이디>    BOJ 아이디로 자동 로그인 후 세션 저장 (비밀번호는 BOJ_LOGIN_PASSWORD 환경변수)"
      echo "  --lang <언어>          기본 언어 저장"
      echo "  --root <경로>          레포 루트 경로 저장"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# 공통 라이브러리 로드
# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"

if [[ "$MODE" == "check" ]]; then
  boj_check_config
  exit 0
fi

# ── 비대화형 set 모드 ─────────────────────────────────────────────────────────
if [[ "$MODE" == "set" ]]; then
  # --username → BOJ_LOGIN_PASSWORD 환경변수로 자동 로그인 후 세션 저장
  if [[ -n "$OPT_USERNAME" ]]; then
    if [[ -z "${BOJ_LOGIN_PASSWORD:-}" ]]; then
      echo -e "${RED}Error: --username 사용 시 BOJ_LOGIN_PASSWORD 환경변수를 설정하세요${NC}" >&2
      exit 1
    fi
    echo "BOJ 로그인 중..."
    if ! python3 "$ROOT/src/lib/boj_client.py" \
        --login --username "$OPT_USERNAME" --save; then
      exit 1
    fi
    echo -e "${GREEN}✓ 로그인 완료 및 session 저장됨${NC}"
  fi
  if [[ -n "$OPT_SESSION" ]]; then
    if ! boj_config_set session "$OPT_SESSION"; then exit 1; fi
    echo -e "${GREEN}✓ session 저장됨${NC}"
  fi
  if [[ -n "$OPT_LANG_SET" ]]; then
    if ! boj_validate_lang "$OPT_LANG_SET"; then exit 1; fi
    if ! boj_config_set lang "$OPT_LANG_SET"; then exit 1; fi
    echo -e "${GREEN}✓ lang 저장됨: $OPT_LANG_SET${NC}"
  fi
  if [[ -n "$OPT_ROOT_SET" ]]; then
    if [[ ! -d "$OPT_ROOT_SET" ]]; then
      echo -e "${RED}Error: 경로가 존재하지 않습니다: $OPT_ROOT_SET${NC}" >&2
      exit 1
    fi
    if ! boj_config_set root "$OPT_ROOT_SET"; then exit 1; fi
    echo -e "${GREEN}✓ root 저장됨: $OPT_ROOT_SET${NC}"
  fi
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
  if ! boj_config_set root "$new_root"; then
    echo -e "  ${RED}설정 저장 실패. 권한 또는 디스크 공간을 확인하세요.${NC}" >&2
    exit 1
  fi
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
    if ! boj_config_set lang "$new_lang"; then
      echo -e "  ${RED}설정 저장 실패.${NC}" >&2
      exit 1
    fi
    echo -e "  ${GREEN}✓ 저장: $new_lang${NC}"
  else
    echo -e "  ${YELLOW}유효하지 않아 기본값 java 유지${NC}"
    if ! boj_config_set lang "java"; then
      echo -e "  ${RED}설정 저장 실패.${NC}" >&2
      exit 1
    fi
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
  echo "  설정 방법을 선택하세요:"
  echo "    1) 아이디/비밀번호로 자동 로그인"
  echo "    2) 세션 쿠키 직접 입력"
  echo "    0) 스킵"
  read -p "  선택 [1/2/0]: " session_method
  case "$session_method" in
    1)
      read -p "  BOJ 아이디: " boj_username
      read -s -p "  BOJ 비밀번호: " boj_password
      echo ""
      if [[ -n "$boj_username" && -n "$boj_password" ]]; then
        echo "  로그인 중..."
        if ! BOJ_LOGIN_PASSWORD="$boj_password" python3 "$ROOT/src/lib/boj_client.py" \
            --login --username "$boj_username" --save; then
          echo -e "  ${RED}로그인 실패. 아이디/비밀번호를 확인하세요.${NC}" >&2
          echo "  스킵 (나중에 boj setup 으로 재시도 가능)"
        else
          echo -e "  ${GREEN}✓ 로그인 완료 및 session 저장됨${NC}"
        fi
      else
        echo "  스킵"
      fi
      ;;
    2)
      echo "  방법: 브라우저 → acmicpc.net 로그인 → F12 → Application → Cookies → OnlineJudge 값 복사"
      read -p "  세션 쿠키 값: " new_session
      if [[ -n "$new_session" ]]; then
        if ! boj_config_set session "$new_session"; then
          echo -e "  ${RED}설정 저장 실패.${NC}" >&2
          exit 1
        fi
        echo -e "  ${GREEN}✓ 저장됨${NC}"
      else
        echo "  스킵"
      fi
      ;;
    *)
      echo "  스킵 (나중에 boj setup 으로 추가 가능)"
      ;;
  esac
fi

# BOJ 사용자 ID (세션과 독립 — commit 통계용)
current_user="$(boj_config_get user "")"
if [[ -z "$current_user" ]]; then
  read -p "  BOJ 사용자 ID (통계 조회용, 없으면 Enter 스킵): " new_user
  if [[ -n "$new_user" ]]; then
    if ! boj_config_set user "$new_user"; then
      echo -e "  ${RED}설정 저장 실패.${NC}" >&2
      exit 1
    fi
    echo -e "  ${GREEN}✓ 저장됨${NC}"
  fi
else
  echo "  사용자 ID: $current_user"
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
    if ! boj_config_set agent "$new_agent"; then
      echo -e "  ${RED}설정 저장 실패.${NC}" >&2
      exit 1
    fi
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
