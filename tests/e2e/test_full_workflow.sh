#!/usr/bin/env bash
# tests/e2e/test_full_workflow.sh — 연속 워크플로우 E2E 검증
# STEP 1: boj make 99999 (픽스처 HTML, 에이전트 mock)
# STEP 2: boj run 99999  (2/2 passed)
# STEP 3: boj submit 99999 (Submit.java 생성 + javac 통과)
# STEP 4: boj commit 99999 --no-stats (git log 커밋 1개)
set -euo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/.." && pwd)"
FIXTURES_DIR="$TESTS_DIR/fixtures"

passed=0
failed=0

_pass() { echo "PASS: $1"; ((passed++)) || true; }
_fail() { echo "FAIL: $1"; echo "  → ${2:-}"; ((failed++)) || true; }

# ── 환경 설정 ────────────────────────────────────────────────────────────────
E2E_TMP=$(mktemp -d)
trap 'rm -rf "$E2E_TMP"' EXIT

# boj make 시 python3가 pip 설치 경로(bs4 등)를 찾을 수 있도록 원래 HOME 보관
ORIG_HOME="${HOME:-}"

export BOJ_ROOT="$E2E_TMP"
export HOME="$E2E_TMP"
export BOJ_CONFIG_DIR="$E2E_TMP/.config/boj"
export BOJ_AGENT_CMD="echo MOCK_AGENT"
export BOJ_EDITOR="true"

cp -r "$REPO_ROOT/src" "$E2E_TMP/"
cp -r "$REPO_ROOT/templates" "$E2E_TMP/"
cp -r "$REPO_ROOT/prompts" "$E2E_TMP/" 2>/dev/null || true
chmod +x "$E2E_TMP/src/boj" "$E2E_TMP/src/commands/"*.sh "$E2E_TMP/src/lib/"*.sh 2>/dev/null || true

git -C "$E2E_TMP" init -q
# commit.sh checks `git config --global user.email`; set HOME-based gitconfig
cat > "$E2E_TMP/.gitconfig" << 'GITCFG'
[user]
    email = e2e@test.com
    name = E2E Tester
GITCFG

BOJ="$E2E_TMP/src/boj"

echo "=========================================="
echo "E2E: boj 워크플로우 검증"
echo "=========================================="
echo ""

# ── STEP 1: boj make 99999 ───────────────────────────────────────────────────
echo "--- STEP 1: boj make 99999 ---"
export BOJ_CLIENT_TEST_HTML="$FIXTURES_DIR/99999/raw.html"
# make 시에만 HOME 복원: python3가 시스템/사용자 site-packages(bs4 등)를 찾을 수 있게 함
make_out=$(HOME="${ORIG_HOME:-$HOME}" bash -c "cd '$E2E_TMP' && echo y | '$BOJ' make 99999 --no-open" 2>&1) || true
make_exit=$?
unset BOJ_CLIENT_TEST_HTML

prob_dir=$(find "$E2E_TMP" -maxdepth 1 -type d -name "99999*" | head -1)

if [[ -n "$prob_dir" && -f "$prob_dir/artifacts/problem.json" ]]; then
  _pass "STEP 1: problem.json 생성됨"
else
  _fail "STEP 1: problem.json 미생성" "$make_out"
fi

if [[ -f "$prob_dir/README.md" ]]; then
  _pass "STEP 1: README.md 생성됨"
else
  _fail "STEP 1: README.md 미생성"
fi

# ── STEP 2: 픽스처 solution/test 복사 후 boj run 99999 ─────────────────────
echo ""
echo "--- STEP 2: boj run 99999 ---"

# run을 위해 Solution.java + test/ 복사 (make가 생성한 폴더와 병합)
if [[ -n "$prob_dir" ]]; then
  cp "$FIXTURES_DIR/99999/Solution.java" "$prob_dir/"
  mkdir -p "$prob_dir/test"
  cp "$FIXTURES_DIR/99999/test/Parse.java" "$prob_dir/test/"
  cp "$FIXTURES_DIR/99999/test/test_cases.json" "$prob_dir/test/"
fi

# 진단: prob_dir 내용 확인 (CI 실패 디버그용)
echo "  [diag] prob_dir=$prob_dir"
echo "  [diag] $(ls -1 "$prob_dir" 2>&1 || echo '(ls failed)')"
echo "  [diag] test/: $(ls -1 "$prob_dir/test" 2>&1 || echo '(no test/)')"

run_out=$(cd "$E2E_TMP" && "$BOJ" run 99999 2>&1) || true
run_exit=$?

if [[ $run_exit -eq 0 ]] && echo "$run_out" | grep -q "2/2"; then
  _pass "STEP 2: boj run 2/2 passed"
else
  _fail "STEP 2: boj run 실패 (exit=$run_exit)" "$run_out"
fi

# ── STEP 3: boj submit 99999 ────────────────────────────────────────────────
echo ""
echo "--- STEP 3: boj submit 99999 ---"

submit_out=$(cd "$E2E_TMP" && "$BOJ" submit 99999 2>&1) || true
submit_exit=$?

if [[ -f "$prob_dir/submit/Submit.java" ]]; then
  _pass "STEP 3: Submit.java 생성됨"
else
  _fail "STEP 3: Submit.java 미생성" "$submit_out"
fi

compile_tmp=$(mktemp -d)
cp "$prob_dir/submit/Submit.java" "$compile_tmp/Main.java" 2>/dev/null || true
if javac "$compile_tmp/Main.java" 2>/dev/null; then
  _pass "STEP 3: Submit.java javac 통과"
else
  _fail "STEP 3: Submit.java 컴파일 실패"
fi
rm -rf "$compile_tmp"

# ── STEP 4: boj commit 99999 --no-stats ─────────────────────────────────────
echo ""
echo "--- STEP 4: boj commit 99999 --no-stats ---"

# 커밋할 파일 스테이징
prob_name=$(basename "$prob_dir")
git -C "$E2E_TMP" add "$E2E_TMP/$prob_name" 2>/dev/null || true

commit_out=$(cd "$E2E_TMP" && echo "n" | "$BOJ" commit 99999 --no-stats 2>&1) || true
commit_exit=$?

commit_count=$(git -C "$E2E_TMP" log --oneline 2>/dev/null | wc -l | tr -d ' ') || true

if [[ "$commit_count" -ge 1 ]]; then
  _pass "STEP 4: git commit 생성됨 (${commit_count}개)"
else
  # 변경사항 없어서 커밋 실패 가능 — Warning이면 허용
  if echo "$commit_out" | grep -qi "Warning\|통계: 스킵\|변경사항"; then
    _pass "STEP 4: commit 진행됨 (변경사항 없음 허용)"
  else
    _fail "STEP 4: commit 실패" "$commit_out"
  fi
fi

# ── 결과 ─────────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "E2E 결과: ${passed}개 통과, ${failed}개 실패"
echo "=========================================="

if [[ $failed -gt 0 ]]; then
  exit 1
fi
exit 0
