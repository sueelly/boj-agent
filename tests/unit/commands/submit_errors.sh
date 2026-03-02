#!/usr/bin/env bash
# submit_errors.sh — boj submit 에러 경로 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── missing_solution_exits_one ───────────────────────────────────────────────
missing_solution_exits_one() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # Solution.java 삭제
  rm -f "$tmp/99999/Solution.java"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" submit 99999 2>&1)
  local exitcode=$?

  assert_exit_1 "missing_solution_exits_one: exit 1" "$exitcode" "$out"
  assert_output_contains "missing_solution_exits_one: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

# ── unsupported_lang_exits_one ───────────────────────────────────────────────
unsupported_lang_exits_one() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" submit 99999 --lang pascal 2>&1)
  local exitcode=$?

  assert_exit_1 "unsupported_lang_exits_one: exit 1" "$exitcode" "$out"
  assert_output_contains "unsupported_lang_exits_one: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

# ── existing_no_force_exits_zero ─────────────────────────────────────────────
existing_no_force_exits_zero() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # 기존 Submit.java 생성
  mkdir -p "$tmp/99999/submit"
  echo "// existing" > "$tmp/99999/submit/Submit.java"

  # --force 없이 "n" 입력 → 취소
  local out
  out=$(cd "$tmp" && echo "n" | "$tmp/src/boj" submit 99999 2>&1)
  local exitcode=$?

  assert_exit_0 "existing_no_force_exits_zero: exit 0 (취소)" "$exitcode"
  assert_output_contains "existing_no_force_exits_zero: 취소 메시지" "$out" "취소\|Warning\|이미"

  # 기존 파일 내용 유지 확인
  local content
  content=$(cat "$tmp/99999/submit/Submit.java" 2>/dev/null || echo "")
  assert_output_contains "existing_no_force_exits_zero: 기존 파일 유지" "$content" "existing"

  teardown_tmp "$tmp"
}

missing_solution_exits_one
unsupported_lang_exits_one
existing_no_force_exits_zero

test_summary "submit_errors"
