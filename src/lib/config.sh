#!/usr/bin/env bash
# ======================================
# src/lib/config.sh — 공통 설정 로더
# ======================================
# 사용: source "$ROOT/src/lib/config.sh"
# 이후: boj_lang, boj_editor, boj_agent_cmd, boj_session, boj_user 변수 사용 가능

# 설정 디렉터리
BOJ_CONFIG_DIR="${BOJ_CONFIG_DIR:-$HOME/.config/boj}"

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 설정 파일에서 값 읽기 (환경변수 > 파일 > 기본값)
boj_config_get() {
  local key="$1"
  local default="${2:-}"
  local env_var="BOJ_$(echo "$key" | tr '[:lower:]' '[:upper:]')"
  # 환경변수 확인
  if [[ -n "${!env_var:-}" ]]; then
    echo "${!env_var}"
    return 0
  fi
  # 파일 확인
  local file="$BOJ_CONFIG_DIR/$key"
  if [[ -f "$file" ]]; then
    cat "$file"
    return 0
  fi
  # 기본값
  echo "$default"
}

# 설정 파일에 값 저장
boj_config_set() {
  local key="$1"
  local value="$2"
  mkdir -p "$BOJ_CONFIG_DIR" 2>/dev/null || {
    echo -e "${RED}Error: 설정 디렉터리에 쓸 수 없습니다: $BOJ_CONFIG_DIR${NC}" >&2
    return 1
  }
  echo "$value" > "$BOJ_CONFIG_DIR/$key"
}

# 모든 설정 로드
boj_load_config() {
  boj_lang="$(boj_config_get lang java)"
  boj_editor="$(boj_config_get editor code)"
  boj_agent_cmd="$(boj_config_get agent "")"
  boj_session="$(boj_config_get session "")"
  boj_user="$(boj_config_get user "")"
}

# 설정 상태 확인 및 표시
boj_check_config() {
  echo -e "${BLUE}=== BOJ CLI 설정 상태 ===${NC}"
  echo ""

  local root_ok=false
  local root_val
  root_val="$(boj_config_get root "")"
  if [[ -n "$root_val" && -d "$root_val" ]]; then
    echo -e "  root:    ${GREEN}✓${NC} $root_val"
    root_ok=true
  else
    echo -e "  root:    ${RED}✗ 미설정${NC} (boj setup 실행)"
  fi

  local lang_val
  lang_val="$(boj_config_get lang java)"
  echo -e "  lang:    ${GREEN}✓${NC} $lang_val"

  local editor_val
  editor_val="$(boj_config_get editor code)"
  echo -e "  editor:  ${GREEN}✓${NC} $editor_val"

  local agent_val
  agent_val="$(boj_config_get agent "")"
  if [[ -n "$agent_val" ]]; then
    echo -e "  agent:   ${GREEN}✓${NC} $agent_val"
  else
    echo -e "  agent:   ${YELLOW}미설정${NC} (make/review는 에디터+클립보드 fallback)"
  fi

  local session_val
  session_val="$(boj_config_get session "")"
  if [[ -n "$session_val" ]]; then
    echo -e "  session: ${GREEN}✓${NC} (설정됨)"
  else
    echo -e "  session: ${YELLOW}미설정${NC} (commit 통계, submit 등 제한)"
  fi

  local user_val
  user_val="$(boj_config_get user "")"
  if [[ -n "$user_val" ]]; then
    echo -e "  user:    ${GREEN}✓${NC} $user_val"
  else
    echo -e "  user:    ${YELLOW}미설정${NC}"
  fi

  echo ""
  local git_name git_email
  git_name="$(git config --global user.name 2>/dev/null || echo '')"
  git_email="$(git config --global user.email 2>/dev/null || echo '')"
  if [[ -n "$git_name" && -n "$git_email" ]]; then
    echo -e "  git:     ${GREEN}✓${NC} $git_name <$git_email>"
  else
    echo -e "  git:     ${YELLOW}미설정${NC} (git config --global user.name/email 필요)"
  fi
}

# 에디터 실행
boj_open_editor() {
  local path="$1"
  local editor="${2:-$(boj_config_get editor code)}"
  if command -v "$editor" &>/dev/null; then
    "$editor" "$path"
    return 0
  fi
  # fallback
  for ed in cursor code vim nano; do
    if command -v "$ed" &>/dev/null; then
      "$ed" "$path"
      return 0
    fi
  done
  echo -e "${RED}Error: 에디터를 찾을 수 없습니다. --editor 또는 ~/.config/boj/editor 설정.${NC}" >&2
  return 1
}

# BOJ 지원 언어 목록
BOJ_SUPPORTED_LANGS="java python cpp c kotlin go rust ruby swift scala js ts"

# 언어 유효성 검사
boj_validate_lang() {
  local lang="$1"
  for supported in $BOJ_SUPPORTED_LANGS; do
    [[ "$lang" == "$supported" ]] && return 0
  done
  echo -e "${RED}Error: 지원하지 않는 언어: $lang${NC}" >&2
  echo -e "지원 언어: $BOJ_SUPPORTED_LANGS" >&2
  return 1
}

# 문제 폴더 찾기
boj_find_problem_dir() {
  local root="$1"
  local problem_num="$2"
  find "$root" -maxdepth 1 -type d -name "${problem_num}*" | head -1
}

# 문제 폴더 검증
boj_require_problem_dir() {
  local root="$1"
  local problem_num="$2"
  local dir
  dir="$(boj_find_problem_dir "$root" "$problem_num")"
  if [[ -z "$dir" || ! -d "$dir" ]]; then
    echo -e "${RED}Error: '${problem_num}'로 시작하는 폴더가 없습니다.${NC}" >&2
    local existing
    existing=$(ls -d "$root"/[0-9]*/ 2>/dev/null | sed 's|.*/||' | sed 's|/$||' | head -10)
    if [[ -n "$existing" ]]; then
      echo "존재하는 문제 폴더:" >&2
      echo "$existing" >&2
    fi
    return 1
  fi
  echo "$dir"
}
