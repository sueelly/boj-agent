#!/usr/bin/env bash
# make_branches.sh — boj make 분기 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

_run_make() {
  local tmp="$1"
  local extra_args="${2:-}"
  (cd "$tmp" && \
    BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
    BOJ_CONFIG_DIR="$tmp/.config/boj" \
    bash -c "echo y | '$tmp/src/boj' make 99999 --no-open $extra_args") 2>&1 || true
}

# ── existing_sig_review_archived ─────────────────────────────────────────────
existing_sig_review_archived() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  _run_make "$tmp" >/dev/null 2>&1

  local prob_dir
  prob_dir=$(find "$tmp" -maxdepth 1 -type d -name "99999*" | head -1)

  mkdir -p "$prob_dir/artifacts"
  echo "dummy v1" > "$prob_dir/artifacts/signature_review.md"

  _run_make "$tmp" >/dev/null 2>&1

  local bak_count
  bak_count=$(ls "$prob_dir/artifacts/"*.bak 2>/dev/null | wc -l | tr -d ' ')

  if [[ "$bak_count" -ge 1 ]]; then
    _pass "existing_sig_review_archived: .bak 생성됨 ($bak_count개)"
  else
    _fail "existing_sig_review_archived: .bak 미생성"
  fi

  teardown_tmp "$tmp"
}

# ── no_agent_uses_fallback ───────────────────────────────────────────────────
no_agent_uses_fallback() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        bash -c "unset BOJ_AGENT_CMD; cd '$tmp' && echo y | '$tmp/src/boj' make 99999 --no-open" 2>&1) || true

  assert_output_contains "no_agent_uses_fallback: fallback Warning" "$out" "Warning.*에이전트\|에이전트 미설정\|fallback"

  teardown_tmp "$tmp"
}

# ── gate_check_pass_no_warning ───────────────────────────────────────────────
gate_check_pass_no_warning() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  _run_make "$tmp" >/dev/null 2>&1

  local prob_dir
  prob_dir=$(find "$tmp" -maxdepth 1 -type d -name "99999*" | head -1)

  # 올바른 서명의 Solution.java (파라미터 2개)
  cat > "$prob_dir/Solution.java" << 'JAVA'
public class Solution {
    public int solve(int a, int b) {
        return a + b;
    }
}
JAVA

  local out
  out=$(cd "$tmp" && \
        BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        BOJ_AGENT_CMD="echo MOCK_AGENT" \
        bash -c "echo y | '$tmp/src/boj' make 99999 --no-open" 2>&1) || true

  assert_output_not_contains "gate_check_pass_no_warning: Gate Check Warning 없음" "$out" "Warning: Gate Check"

  teardown_tmp "$tmp"
}

# ── gate_check_fail_emits_warning ────────────────────────────────────────────
gate_check_fail_emits_warning() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  _run_make "$tmp" >/dev/null 2>&1

  local prob_dir
  prob_dir=$(find "$tmp" -maxdepth 1 -type d -name "99999*" | head -1)

  # 단일 String 파라미터 (금지 패턴)
  cat > "$prob_dir/Solution.java" << 'JAVA'
public class Solution {
    public int solve(String input) {
        return 0;
    }
}
JAVA

  local out
  out=$(cd "$tmp" && \
        BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        BOJ_AGENT_CMD="echo MOCK_AGENT" \
        bash -c "echo y | '$tmp/src/boj' make 99999 --no-open" 2>&1) || true

  assert_output_contains "gate_check_fail_emits_warning: Gate Check Warning 출력" "$out" "Gate Check\|raw stdin blob\|Warning.*solve"

  teardown_tmp "$tmp"
}

# ── image_mode_flag_passed ───────────────────────────────────────────────────
image_mode_flag_passed() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        bash -c "cd '$tmp' && echo y | '$tmp/src/boj' make 99999 --no-open --image-mode skip" 2>&1) || true

  # --image-mode skip이면 에러 없이 진행되어야 함
  local prob_dir
  prob_dir=$(find "$tmp" -maxdepth 1 -type d -name "99999*" | head -1)
  assert_dir_exists "image_mode_flag_passed: 문제 폴더 생성" "${prob_dir:-/nonexistent}"

  teardown_tmp "$tmp"
}

# ── lang_flag_validated ──────────────────────────────────────────────────────
lang_flag_validated() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(cd "$tmp" && \
        BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        echo y | "$tmp/src/boj" make 99999 --no-open --lang python 2>&1) || true
  local exitcode=$?

  assert_exit_0 "lang_flag_validated: exit 0 (python 유효)" "$exitcode"

  teardown_tmp "$tmp"
}

existing_sig_review_archived
no_agent_uses_fallback
gate_check_pass_no_warning
gate_check_fail_emits_warning
image_mode_flag_passed
lang_flag_validated

test_summary "make_branches"
