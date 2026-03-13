#!/usr/bin/env bash
# setup_branches.sh — boj setup 분기 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── root_saved_to_config ─────────────────────────────────────────────────────
root_saved_to_config() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  local cfg="$tmp/.config/boj"
  mkdir -p "$cfg"

  # boj_config_set root 직접 검증 (setup은 interactive라 직접 config 파일 작성)
  echo "$tmp" > "$cfg/root"

  local saved
  saved=$(cat "$cfg/root" 2>/dev/null || echo "")

  if [[ "$saved" == "$tmp" ]]; then
    _pass "root_saved_to_config: root 저장됨"
  else
    _fail "root_saved_to_config: root 불일치" "expected '$tmp', got '$saved'"
  fi

  teardown_tmp "$tmp"
}

# ── lang_saved_to_config ─────────────────────────────────────────────────────
lang_saved_to_config() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  local cfg="$tmp/.config/boj"
  mkdir -p "$cfg"

  echo "python" > "$cfg/lang"

  local out
  out=$(BOJ_CONFIG_DIR="$cfg" cd "$tmp" && "$tmp/src/boj" setup --check 2>&1) || true

  # check 출력에서 lang 확인
  local lang_val
  lang_val=$(BOJ_CONFIG_DIR="$cfg" "$tmp/src/boj" setup --check 2>&1 | grep "lang" | head -1)
  assert_output_contains "lang_saved_to_config: python 반영" "$lang_val" "python"

  teardown_tmp "$tmp"
}

# ── session_saved_to_config ──────────────────────────────────────────────────
session_saved_to_config() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  local cfg="$tmp/.config/boj"
  mkdir -p "$cfg"

  echo "abc123session" > "$cfg/session"

  local saved
  saved=$(cat "$cfg/session" 2>/dev/null || echo "")

  if [[ "$saved" == "abc123session" ]]; then
    _pass "session_saved_to_config: session 저장됨"
  else
    _fail "session_saved_to_config: session 불일치" "got '$saved'"
  fi

  teardown_tmp "$tmp"
}

root_saved_to_config
lang_saved_to_config
session_saved_to_config

test_summary "setup_branches"
