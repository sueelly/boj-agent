#!/usr/bin/env bash
# tests/lib/matrix_helpers.sh — 다언어 매트릭스 테스트 공통 함수

MATRIX_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MATRIX_FIXTURES_DIR="$MATRIX_REPO_ROOT/tests/fixtures"

# fixture_has_solution <fixture_id> <lang>
# lang에 맞는 솔루션 파일이 있는지 확인
fixture_has_solution() {
  local fixture_id="$1"
  local lang="$2"
  local fixture_dir="$MATRIX_FIXTURES_DIR/$fixture_id"

  case "$lang" in
    java)
      [[ -f "$fixture_dir/Solution.java" && -f "$fixture_dir/test/Parse.java" ]] ;;
    python)
      [[ -f "$fixture_dir/solution.py" && -f "$fixture_dir/test/parse.py" ]] ;;
    *)
      return 1 ;;
  esac
}

# run_one_fixture <fixture_id> <lang>
# tmp repo 생성 → 픽스처 복사 → boj run → 결과 확인
run_one_fixture() {
  local fixture_id="$1"
  local lang="$2"
  local fixture_dir="$MATRIX_FIXTURES_DIR/$fixture_id"

  local tmp
  tmp=$(mktemp -d)
  cp -r "$MATRIX_REPO_ROOT/src" "$tmp/"
  cp -r "$MATRIX_REPO_ROOT/templates" "$tmp/"
  chmod +x "$tmp/src/boj" "$tmp/src/commands/"*.sh "$tmp/src/lib/"*.sh 2>/dev/null || true
  export HOME="$tmp"
  export BOJ_CONFIG_DIR="$tmp/.config/boj"

  cp -r "$fixture_dir" "$tmp/$fixture_id"

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" run "$fixture_id" --lang "$lang" 2>&1) || true
  local exitcode=$?

  rm -rf "$tmp"

  if [[ $exitcode -eq 0 ]] && echo "$out" | grep -qi "passed\|통과"; then
    echo "PASS: run $fixture_id ($lang)"
    return 0
  else
    echo "FAIL: run $fixture_id ($lang) — exit=$exitcode"
    echo "  출력: $(echo "$out" | head -3)"
    return 1
  fi
}

# make_one_fixture <fixture_id> <lang>
# tmp repo → raw.html 사용 → boj make → 파일 생성 확인
make_one_fixture() {
  local fixture_id="$1"
  local lang="$2"
  local fixture_dir="$MATRIX_FIXTURES_DIR/$fixture_id"

  if [[ ! -f "$fixture_dir/raw.html" ]]; then
    echo "SKIP: make $fixture_id ($lang) — raw.html 없음"
    return 0
  fi

  local tmp
  tmp=$(mktemp -d)
  cp -r "$MATRIX_REPO_ROOT/src" "$tmp/"
  cp -r "$MATRIX_REPO_ROOT/templates" "$tmp/"
  cp -r "$MATRIX_REPO_ROOT/prompts" "$tmp/" 2>/dev/null || true
  chmod +x "$tmp/src/boj" "$tmp/src/commands/"*.sh "$tmp/src/lib/"*.sh 2>/dev/null || true
  export HOME="$tmp"
  export BOJ_CONFIG_DIR="$tmp/.config/boj"

  local out
  out=$(BOJ_CLIENT_TEST_HTML="$fixture_dir/raw.html" \
        bash -c "cd '$tmp' && echo y | '$tmp/src/boj' make '$fixture_id' --lang '$lang' --no-open" 2>&1) || true
  local exitcode=$?

  local prob_dir
  prob_dir=$(find "$tmp" -maxdepth 1 -type d -name "${fixture_id}*" | head -1)

  rm -rf "$tmp"

  if [[ $exitcode -eq 0 && -n "$prob_dir" ]]; then
    echo "PASS: make $fixture_id ($lang)"
    return 0
  else
    echo "FAIL: make $fixture_id ($lang) — exit=$exitcode"
    echo "  출력: $(echo "$out" | head -3)"
    return 1
  fi
}
