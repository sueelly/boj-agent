#!/usr/bin/env bash
# make_happy.sh — boj make 정상 동작 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── pipeline_a_generates_problem_json ────────────────────────────────────────
pipeline_a_generates_problem_json() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
        BOJ_CONFIG_DIR="$tmp/.config/boj" \
        bash -c "cd '$tmp' && echo y | '$tmp/src/boj' make 99999 --no-open" 2>&1) || true

  local prob_dir
  prob_dir=$(find "$tmp" -maxdepth 1 -type d -name "99999*" | head -1)

  assert_dir_exists "pipeline_a_generates_problem_json: 문제 폴더 생성" "${prob_dir:-/nonexistent}"
  assert_file_exists "pipeline_a_generates_problem_json: problem.json 생성" "${prob_dir:-/nonexistent}/artifacts/problem.json"

  teardown_tmp "$tmp"
}

# ── pipeline_b_generates_readme ──────────────────────────────────────────────
pipeline_b_generates_readme() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  BOJ_CLIENT_TEST_HTML="$HELPER_FIXTURES_DIR/99999/raw.html" \
    BOJ_CONFIG_DIR="$tmp/.config/boj" \
    bash -c "cd '$tmp' && echo y | '$tmp/src/boj' make 99999 --no-open" >/dev/null 2>&1 || true

  local prob_dir
  prob_dir=$(find "$tmp" -maxdepth 1 -type d -name "99999*" | head -1)

  assert_file_exists "pipeline_b_generates_readme: README.md 생성" "${prob_dir:-/nonexistent}/README.md"

  teardown_tmp "$tmp"
}

pipeline_a_generates_problem_json
pipeline_b_generates_readme

test_summary "make_happy"
