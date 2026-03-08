#!/usr/bin/env bash
# submit_branches.sh — boj submit 분기 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── java_with_parse_included ─────────────────────────────────────────────────
java_with_parse_included() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  cd "$tmp" && "$tmp/src/boj" submit 99999 2>/dev/null || true

  local submit_content
  submit_content=$(cat "$tmp/99999/submit/Submit.java" 2>/dev/null || echo "")

  assert_output_contains "java_with_parse_included: Parse 클래스" "$submit_content" "class Parse"
  assert_output_contains "java_with_parse_included: parseAndCallSolve" "$submit_content" "parseAndCallSolve"

  teardown_tmp "$tmp"
}

# ── java_without_parse ───────────────────────────────────────────────────────
java_without_parse() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # Parse.java 제거
  rm -f "$tmp/99999/test/Parse.java"

  cd "$tmp" && "$tmp/src/boj" submit 99999 2>/dev/null || true

  assert_file_exists "java_without_parse: Submit.java 생성됨" "$tmp/99999/submit/Submit.java"

  local submit_content
  submit_content=$(cat "$tmp/99999/submit/Submit.java" 2>/dev/null || echo "")
  assert_output_contains "java_without_parse: Main 클래스 존재" "$submit_content" "public class Main"

  teardown_tmp "$tmp"
}

# ── force_overwrites_existing ────────────────────────────────────────────────
force_overwrites_existing() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # 기존 Submit.java 생성
  mkdir -p "$tmp/99999/submit"
  echo "// old content" > "$tmp/99999/submit/Submit.java"

  # --force로 덮어쓰기
  cd "$tmp" && "$tmp/src/boj" submit 99999 --force 2>/dev/null || true

  local content
  content=$(cat "$tmp/99999/submit/Submit.java" 2>/dev/null || echo "")
  assert_output_not_contains "force_overwrites_existing: 기존 내용 제거" "$content" "// old content"
  assert_output_contains "force_overwrites_existing: 새 Main 클래스" "$content" "public class Main"

  teardown_tmp "$tmp"
}

# ── python_stub_generated ────────────────────────────────────────────────────
python_stub_generated() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # Python 솔루션 추가
  cat > "$tmp/99999/solution.py" << 'PYEOF'
class Solution:
    def solve(self, a: int, b: int) -> int:
        return a + b
PYEOF

  cd "$tmp" && "$tmp/src/boj" submit 99999 --lang python 2>/dev/null || true

  assert_file_exists "python_stub_generated: Submit.py 생성" "$tmp/99999/submit/Submit.py"

  teardown_tmp "$tmp"
}

# ── cpp_stub_generated ───────────────────────────────────────────────────────
cpp_stub_generated() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # C++ 솔루션 추가
  cat > "$tmp/99999/Solution.cpp" << 'CPPEOF'
int solve(int a, int b) { return a + b; }
CPPEOF

  cd "$tmp" && "$tmp/src/boj" submit 99999 --lang cpp 2>/dev/null || true

  assert_file_exists "cpp_stub_generated: Submit.cpp 생성" "$tmp/99999/submit/Submit.cpp"

  teardown_tmp "$tmp"
}

java_with_parse_included
java_without_parse
force_overwrites_existing
python_stub_generated
cpp_stub_generated

test_summary "submit_branches"
