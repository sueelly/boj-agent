#!/usr/bin/env bash
# run_happy.sh — boj run 정상 동작 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── java_two_of_two_pass ─────────────────────────────────────────────────────
test_java_two_of_two_pass() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 2>&1)
  local exitcode=$?

  assert_exit_0 "java_two_of_two_pass: exit 0" "$exitcode"
  assert_output_contains "java_two_of_two_pass: 2/2 표시" "$out" "2/2"
  assert_output_contains "java_two_of_two_pass: passed 표시" "$out" "passed"

  teardown_tmp "$tmp"
}

# ── python_two_of_two_pass ───────────────────────────────────────────────────
test_python_two_of_two_pass() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # Python 솔루션 작성
  cat > "$tmp/99999/solution.py" << 'PYEOF'
class Solution:
    def solve(self, a: int, b: int) -> int:
        return a + b
PYEOF

  # Python용 parse.py 작성
  cat > "$tmp/99999/test/parse.py" << 'PYEOF'
from solution import Solution

def parse_and_solve(sol, input_str):
    parts = input_str.strip().split()
    a, b = int(parts[0]), int(parts[1])
    return str(sol.solve(a, b))
PYEOF

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 --lang python 2>&1)
  local exitcode=$?

  assert_exit_0 "python_two_of_two_pass: exit 0" "$exitcode"
  assert_output_contains "python_two_of_two_pass: 2/2 표시" "$out" "2/2"

  teardown_tmp "$tmp"
}

test_java_two_of_two_pass
test_python_two_of_two_pass

test_summary "run_happy"
