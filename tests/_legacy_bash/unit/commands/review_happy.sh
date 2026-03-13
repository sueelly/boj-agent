#!/usr/bin/env bash
# review_happy.sh — boj review 정상 동작 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── agent_called_with_solution ───────────────────────────────────────────────
agent_called_with_solution() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  local called_file="$tmp/agent_called.txt"
  local fake_agent="$tmp/fake_agent.sh"
  cat > "$fake_agent" << SHELL
#!/usr/bin/env bash
echo "agent_called:cwd=\$(pwd)" > "$called_file"
SHELL
  chmod +x "$fake_agent"

  local out
  out=$(cd "$tmp" && BOJ_AGENT_CMD="$fake_agent" "$tmp/src/boj" review 99999 2>&1)
  local exitcode=$?

  assert_exit_0 "agent_called_with_solution: exit 0" "$exitcode"
  assert_file_exists "agent_called_with_solution: 에이전트 호출됨" "$called_file"

  teardown_tmp "$tmp"
}

agent_called_with_solution

test_summary "review_happy"
