#!/usr/bin/env bash
# setup_happy.sh — boj setup 정상 동작 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── check_shows_current_config ───────────────────────────────────────────────
check_shows_current_config() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" setup --check 2>&1)
  local exitcode=$?

  assert_exit_0 "check_shows_current_config: exit 0" "$exitcode"
  assert_output_contains "check_shows_current_config: 설정 출력" "$out" "lang\|BOJ CLI\|설정"

  teardown_tmp "$tmp"
}

check_shows_current_config

test_summary "setup_happy"
