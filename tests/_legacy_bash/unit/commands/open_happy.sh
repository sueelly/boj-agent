#!/usr/bin/env bash
# open_happy.sh — boj open 정상 동작 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── opens_existing_problem_dir ───────────────────────────────────────────────
opens_existing_problem_dir() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"
  mock_editor  # BOJ_EDITOR=true (아무것도 안 함)

  local out
  out=$(cd "$tmp" && BOJ_EDITOR=true "$tmp/src/boj" open 99999 2>&1)
  local exitcode=$?

  assert_exit_0 "opens_existing_problem_dir: exit 0" "$exitcode"
  assert_output_contains "opens_existing_problem_dir: 성공 메시지" "$out" "열었\|open\|✅"

  teardown_tmp "$tmp"
}

opens_existing_problem_dir

test_summary "open_happy"
