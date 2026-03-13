#!/usr/bin/env bash
# setup_errors.sh — boj setup 에러 경로 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── invalid_lang_exits_one ───────────────────────────────────────────────────
invalid_lang_exits_one() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  # boj_validate_lang을 직접 호출하여 유효하지 않은 언어 검증
  local out
  out=$(cd "$tmp" && BOJ_CONFIG_DIR="$tmp/.config/boj" \
        bash -c "source '$tmp/src/lib/config.sh'; boj_validate_lang fortran" 2>&1)
  local exitcode=$?

  assert_exit_1 "invalid_lang_exits_one: exit 1" "$exitcode" "$out"
  assert_output_contains "invalid_lang_exits_one: Error 메시지" "$out" "Error\|지원하지 않"

  teardown_tmp "$tmp"
}

# ── nonexistent_root_exits_one ───────────────────────────────────────────────
nonexistent_root_exits_one() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  # --output 플래그로 존재하지 않는 경로 전달 (make 커맨드 경로 검증 활용)
  local out
  out=$(cd "$tmp" && "$tmp/src/boj" make 99999 --output /nonexistent/path/xyz 2>&1)
  local exitcode=$?

  assert_exit_1 "nonexistent_root_exits_one: exit 1" "$exitcode" "$out"
  assert_output_contains "nonexistent_root_exits_one: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

invalid_lang_exits_one
nonexistent_root_exits_one

test_summary "setup_errors"
