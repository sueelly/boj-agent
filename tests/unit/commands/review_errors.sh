#!/usr/bin/env bash
# review_errors.sh — boj review 에러 경로 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── missing_problem_dir ──────────────────────────────────────────────────────
missing_problem_dir() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(cd "$tmp" && BOJ_EDITOR=true "$tmp/src/boj" review 88888 2>&1)
  local exitcode=$?

  assert_exit_1 "missing_problem_dir: exit 1" "$exitcode" "$out"
  assert_output_contains "missing_problem_dir: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

missing_problem_dir

test_summary "review_errors"
