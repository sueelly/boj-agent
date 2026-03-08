#!/usr/bin/env bash
# make_errors.sh — boj make 에러 경로 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── invalid_lang_exits_one ───────────────────────────────────────────────────
invalid_lang_exits_one() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(cd "$tmp" && \
        BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        "$tmp/src/boj" make 99999 --lang fortran 2>&1)
  local exitcode=$?

  assert_exit_1 "invalid_lang_exits_one: exit 1" "$exitcode" "$out"
  assert_output_contains "invalid_lang_exits_one: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

# ── network_failure_exits_one ────────────────────────────────────────────────
network_failure_exits_one() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  # BOJ_CLIENT_TEST_HTML 미설정 + 네트워크 차단 환경에서 boj_client 실패 시뮬레이션
  # 존재하지 않는 파일을 TEST_HTML로 지정
  local out
  out=$(cd "$tmp" && \
        BOJ_CLIENT_TEST_HTML="/nonexistent/html_file.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        "$tmp/src/boj" make 99999 --no-open 2>&1)
  local exitcode=$?

  assert_exit_1 "network_failure_exits_one: exit 1" "$exitcode" "$out"
  assert_output_contains "network_failure_exits_one: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

# ── invalid_output_path ──────────────────────────────────────────────────────
invalid_output_path() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(cd "$tmp" && \
        BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        "$tmp/src/boj" make 99999 --output /nonexistent/path 2>&1)
  local exitcode=$?

  assert_exit_1 "invalid_output_path: exit 1" "$exitcode" "$out"
  assert_output_contains "invalid_output_path: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

invalid_lang_exits_one
network_failure_exits_one
invalid_output_path

test_summary "make_errors"
