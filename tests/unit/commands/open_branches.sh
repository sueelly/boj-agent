#!/usr/bin/env bash
# open_branches.sh — boj open 분기 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── editor_env_var_used ──────────────────────────────────────────────────────
editor_env_var_used() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # 에디터 mock: 실행된 에디터 이름을 파일에 기록
  local called_file="$tmp/editor_called.txt"
  local fake_editor="$tmp/fake_editor.sh"
  cat > "$fake_editor" << SHELL
#!/usr/bin/env bash
echo "editor_called:\$@" > "$called_file"
SHELL
  chmod +x "$fake_editor"

  local out
  out=$(cd "$tmp" && BOJ_EDITOR="$fake_editor" "$tmp/src/boj" open 99999 2>&1)
  local exitcode=$?

  assert_exit_0 "editor_env_var_used: exit 0" "$exitcode"
  assert_file_exists "editor_env_var_used: 에디터 호출됨" "$called_file"

  teardown_tmp "$tmp"
}

# ── editor_flag_overrides ────────────────────────────────────────────────────
editor_flag_overrides() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  local called_file="$tmp/editor_called2.txt"
  local fake_editor="$tmp/fake_editor2.sh"
  cat > "$fake_editor" << SHELL
#!/usr/bin/env bash
echo "editor_called:\$@" > "$called_file"
SHELL
  chmod +x "$fake_editor"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" open 99999 --editor "$fake_editor" 2>&1)
  local exitcode=$?

  assert_exit_0 "editor_flag_overrides: exit 0" "$exitcode"
  assert_file_exists "editor_flag_overrides: --editor 플래그 에디터 호출됨" "$called_file"

  teardown_tmp "$tmp"
}

editor_env_var_used
editor_flag_overrides

test_summary "open_branches"
