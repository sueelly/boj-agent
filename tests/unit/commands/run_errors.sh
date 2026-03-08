#!/usr/bin/env bash
# run_errors.sh — boj run 에러 경로 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── missing_problem_dir ──────────────────────────────────────────────────────
missing_problem_dir() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 88888 2>&1)
  local exitcode=$?

  assert_exit_1 "missing_problem_dir: exit 1" "$exitcode" "$out"

  teardown_tmp "$tmp"
}

# ── missing_solution_file ────────────────────────────────────────────────────
missing_solution_file() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # Solution.java 삭제
  rm -f "$tmp/99999/Solution.java"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 2>&1)
  local exitcode=$?

  assert_exit_1 "missing_solution_file: exit 1" "$exitcode" "$out"
  assert_output_contains "missing_solution_file: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

# ── missing_test_cases_json ──────────────────────────────────────────────────
missing_test_cases_json() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  rm -f "$tmp/99999/test/test_cases.json"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 2>&1)
  local exitcode=$?

  assert_exit_1 "missing_test_cases_json: exit 1" "$exitcode" "$out"

  teardown_tmp "$tmp"
}

# ── unsupported_lang_cpp ─────────────────────────────────────────────────────
unsupported_lang_cpp() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 --lang cpp 2>&1)
  local exitcode=$?

  assert_exit_1 "unsupported_lang_cpp: exit 1" "$exitcode" "$out"
  assert_output_contains "unsupported_lang_cpp: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

# ── compile_error_reported ───────────────────────────────────────────────────
compile_error_reported() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # 컴파일 에러가 있는 Solution.java로 교체
  cat > "$tmp/99999/Solution.java" << 'JAVA'
public class Solution {
    public int solve(int a, int b) {
        SYNTAX ERROR HERE
    }
}
JAVA

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 2>&1)
  local exitcode=$?

  assert_exit_1 "compile_error_reported: exit 1" "$exitcode" "$out"

  teardown_tmp "$tmp"
}

missing_problem_dir
missing_solution_file
missing_test_cases_json
unsupported_lang_cpp
compile_error_reported

test_summary "run_errors"
