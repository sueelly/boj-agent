#!/usr/bin/env bash
# submit_happy.sh — boj submit 정상 동작 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── java_submit_generated ────────────────────────────────────────────────────
java_submit_generated() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" submit 99999 2>&1)
  local exitcode=$?

  assert_exit_0 "java_submit_generated: exit 0" "$exitcode"
  assert_file_exists "java_submit_generated: Submit.java 생성" "$tmp/99999/submit/Submit.java"
  assert_output_contains "java_submit_generated: Main 클래스" "$(cat "$tmp/99999/submit/Submit.java" 2>/dev/null)" "public class Main"

  teardown_tmp "$tmp"
}

# ── java_submit_compiles ─────────────────────────────────────────────────────
java_submit_compiles() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  cd "$tmp" && "$tmp/src/boj" submit 99999 2>/dev/null || true

  local compile_tmp
  compile_tmp=$(mktemp -d)
  cp "$tmp/99999/submit/Submit.java" "$compile_tmp/Main.java" 2>/dev/null || true

  if javac "$compile_tmp/Main.java" 2>/dev/null; then
    _pass "java_submit_compiles: javac 성공"
  else
    _fail "java_submit_compiles: javac 실패" "Submit.java가 컴파일되지 않습니다"
  fi

  rm -rf "$compile_tmp"
  teardown_tmp "$tmp"
}

java_submit_generated
java_submit_compiles

test_summary "submit_happy"
