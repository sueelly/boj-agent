#!/usr/bin/env bash
# tests/unit/lib/test_helper.sh — 단위 테스트 공통 헬퍼
# 사용: source "$TESTS_DIR/unit/lib/test_helper.sh"

HELPER_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HELPER_FIXTURES_DIR="$HELPER_REPO_ROOT/tests/fixtures"

# 글로벌 카운터
_PASS=0
_FAIL=0

_pass() { echo "PASS: $1"; ((_PASS++)) || true; }
_fail() { echo "FAIL: $1"; ((_FAIL++)) || true; echo "  → ${2:-}"; }

# 테스트 결과 출력 및 exit
test_summary() {
  local name="${1:-테스트}"
  echo ""
  echo "$name: ${_PASS}개 통과, ${_FAIL}개 실패"
  if [[ $_FAIL -gt 0 ]]; then
    exit 1
  fi
  exit 0
}

# ── tmp BOJ root 설정 ────────────────────────────────────────────────────────

# 빈 BOJ root (git init + src/templates 복사)
setup_tmp_boj_root() {
  local tmp
  tmp=$(mktemp -d)
  cp -r "$HELPER_REPO_ROOT/src" "$tmp/"
  cp -r "$HELPER_REPO_ROOT/templates" "$tmp/"
  cp -r "$HELPER_REPO_ROOT/prompts" "$tmp/" 2>/dev/null || true
  chmod +x "$tmp/src/boj" "$tmp/src/commands/"*.sh "$tmp/src/lib/"*.sh 2>/dev/null || true
  git -C "$tmp" init -q 2>/dev/null || true
  git -C "$tmp" config user.email "test@test.com" 2>/dev/null || true
  git -C "$tmp" config user.name "Tester" 2>/dev/null || true
  export HOME="$tmp"
  export BOJ_CONFIG_DIR="$tmp/.config/boj"
  echo "$tmp"
}

# 픽스처 복사 (fixture_id 폴더를 tmp root에 복사)
copy_fixture() {
  local tmp="$1"
  local fixture_id="$2"
  local dest_name="${3:-$fixture_id}"
  local src="$HELPER_FIXTURES_DIR/$fixture_id"
  if [[ ! -d "$src" ]]; then
    echo "ERROR: fixture '$fixture_id' not found at $src" >&2
    return 1
  fi
  cp -r "$src" "$tmp/$dest_name"
}

teardown_tmp() {
  local tmp="$1"
  rm -rf "$tmp"
}

# ── assert 헬퍼 ──────────────────────────────────────────────────────────────

assert_exit_0() {
  local name="$1"
  local actual_exit="$2"
  if [[ "$actual_exit" -eq 0 ]]; then
    _pass "$name"
  else
    _fail "$name" "exit=$actual_exit (expected 0)"
  fi
}

assert_exit_1() {
  local name="$1"
  local actual_exit="$2"
  local output="${3:-}"
  if [[ "$actual_exit" -ne 0 ]]; then
    if [[ -z "$output" ]] || echo "$output" | grep -qi "Error:"; then
      _pass "$name"
    else
      _fail "$name" "exit=$actual_exit but no 'Error:' in output: $output"
    fi
  else
    _fail "$name" "exit=0 (expected non-zero)"
  fi
}

assert_output_contains() {
  local name="$1"
  local output="$2"
  local pattern="$3"
  if echo "$output" | grep -qi "$pattern"; then
    _pass "$name"
  else
    _fail "$name" "pattern '$pattern' not found in: $(echo "$output" | head -3)"
  fi
}

assert_output_not_contains() {
  local name="$1"
  local output="$2"
  local pattern="$3"
  if ! echo "$output" | grep -qi "$pattern"; then
    _pass "$name"
  else
    _fail "$name" "unexpected pattern '$pattern' found in output"
  fi
}

assert_file_exists() {
  local name="$1"
  local path="$2"
  if [[ -f "$path" ]]; then
    _pass "$name"
  else
    _fail "$name" "file not found: $path"
  fi
}

assert_file_not_exists() {
  local name="$1"
  local path="$2"
  if [[ ! -f "$path" ]]; then
    _pass "$name"
  else
    _fail "$name" "file should not exist: $path"
  fi
}

assert_dir_exists() {
  local name="$1"
  local path="$2"
  if [[ -d "$path" ]]; then
    _pass "$name"
  else
    _fail "$name" "directory not found: $path"
  fi
}

# ── mock 헬퍼 ────────────────────────────────────────────────────────────────

# 에이전트 mock: BOJ_AGENT_CMD=echo 로 설정
mock_agent_cmd() {
  export BOJ_AGENT_CMD="echo MOCK_AGENT"
}

# 에이전트 없음
no_agent_cmd() {
  unset BOJ_AGENT_CMD
}

# 에디터 mock (아무것도 안 하는 명령)
mock_editor() {
  export BOJ_EDITOR="true"
}
