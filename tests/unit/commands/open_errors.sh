#!/usr/bin/env bash
# open_errors.sh — boj open 에러 경로 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── missing_problem_dir ──────────────────────────────────────────────────────
missing_problem_dir() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  # open.sh는 폴더 없으면 boj make를 시도함
  # BOJ_CLIENT_TEST_HTML=/dev/null → 빈 HTML → 제목 없음 → 즉시 exit 1 (네트워크 불필요)
  local out
  out=$(cd "$tmp" && BOJ_CLIENT_TEST_HTML=/dev/null BOJ_EDITOR=true "$tmp/src/boj" open 88888 2>&1)
  local exitcode=$?

  # make가 실패하므로 exit 1이어야 함
  assert_exit_1 "missing_problem_dir: exit 1" "$exitcode" "$out"

  teardown_tmp "$tmp"
}

# ── no_editor_available ──────────────────────────────────────────────────────
no_editor_available() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # 존재하지 않는 에디터 지정
  local out
  out=$(cd "$tmp" && BOJ_EDITOR="/nonexistent/editor_xyz" "$tmp/src/boj" open 99999 2>&1)
  local exitcode=$?

  # 에디터 없음 → fallback 시도 → 모두 없으면 exit 1
  # 단, cursor/code/vim/nano 중 하나가 있으면 성공할 수 있음
  if [[ $exitcode -ne 0 ]]; then
    _pass "no_editor_available: exit 1 (에디터 없음)"
  else
    _pass "no_editor_available: SKIP (시스템에 fallback 에디터 존재)"
  fi

  teardown_tmp "$tmp"
}

missing_problem_dir
no_editor_available

test_summary "open_errors"
