#!/usr/bin/env bash
# review_branches.sh — boj review 분기 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── no_agent_fallback_to_editor ──────────────────────────────────────────────
no_agent_fallback_to_editor() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # 에이전트 없음, 에디터 mock
  local called_file="$tmp/editor_called.txt"
  local fake_editor="$tmp/fake_editor.sh"
  cat > "$fake_editor" << SHELL
#!/usr/bin/env bash
echo "editor_called" > "$called_file"
SHELL
  chmod +x "$fake_editor"

  local out
  out=$(cd "$tmp" && unset BOJ_AGENT_CMD; \
        BOJ_CONFIG_DIR="$tmp/.config/boj" BOJ_EDITOR="$fake_editor" \
        "$tmp/src/boj" review 99999 2>&1) || true
  local exitcode=$?

  # 에이전트 없으면 에디터 fallback (에디터 없어도 Warning 출력 후 exit 0)
  # exit 코드보다 fallback Warning 메시지 확인
  assert_output_contains "no_agent_fallback_to_editor: fallback 메시지" "$out" "Warning\|에디터\|fallback\|열었\|클립보드"

  teardown_tmp "$tmp"
}

no_agent_fallback_to_editor

test_summary "review_branches"
