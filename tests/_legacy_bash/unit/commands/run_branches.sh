#!/usr/bin/env bash
# run_branches.sh — boj run 분기 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── test_cases_no_id_auto_assigned ──────────────────────────────────────────
test_cases_no_id_auto_assigned() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # id 없는 test_cases.json으로 교체
  cat > "$tmp/99999/test/test_cases.json" << 'EOF'
{
  "testCases": [
    {"input": "1 2", "expected": "3"},
    {"input": "10 20", "expected": "30"}
  ]
}
EOF

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 2>&1)
  local exitcode=$?

  assert_exit_0 "test_cases_no_id_auto_assigned: exit 0" "$exitcode"
  assert_output_contains "test_cases_no_id_auto_assigned: 통과" "$out" "2/2"

  teardown_tmp "$tmp"
}

# ── lang_override_flag ───────────────────────────────────────────────────────
lang_override_flag() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # Python 솔루션 추가 (Java 폴더에 Python 솔루션 공존)
  cat > "$tmp/99999/solution.py" << 'PYEOF'
class Solution:
    def solve(self, a: int, b: int) -> int:
        return a + b
PYEOF
  cat > "$tmp/99999/test/parse.py" << 'PYEOF'
from solution import Solution
def parse_and_solve(sol, inp):
    a, b = map(int, inp.strip().split())
    return str(sol.solve(a, b))
PYEOF

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 --lang python 2>&1)
  local exitcode=$?

  assert_exit_0 "lang_override_flag: exit 0" "$exitcode"
  assert_output_contains "lang_override_flag: 통과" "$out" "2/2"

  teardown_tmp "$tmp"
}

# ── partial_pass_shows_count ─────────────────────────────────────────────────
partial_pass_shows_count() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # 1번만 통과, 2번은 실패하는 test_cases.json
  cat > "$tmp/99999/test/test_cases.json" << 'EOF'
{
  "testCases": [
    {"id": 1, "input": "1 2", "expected": "3"},
    {"id": 2, "input": "1 2", "expected": "999"}
  ]
}
EOF

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run 99999 2>&1) || true

  assert_output_contains "partial_pass_shows_count: 1/2 표시" "$out" "1/2"

  teardown_tmp "$tmp"
}

test_cases_no_id_auto_assigned
lang_override_flag
partial_pass_shows_count

test_summary "run_branches"
