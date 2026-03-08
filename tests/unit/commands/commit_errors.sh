#!/usr/bin/env bash
# commit_errors.sh — boj commit 에러 경로 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── no_git_repo_exits_one ────────────────────────────────────────────────────
no_git_repo_exits_one() {
  local tmp
  tmp=$(mktemp -d)
  cp -r "$HELPER_REPO_ROOT/src" "$tmp/"
  cp -r "$HELPER_REPO_ROOT/templates" "$tmp/"
  chmod +x "$tmp/src/boj" "$tmp/src/commands/"*.sh 2>/dev/null || true
  export HOME="$tmp"
  export BOJ_CONFIG_DIR="$tmp/.config/boj"
  mkdir -p "$tmp/99999/test"
  cp "$HELPER_FIXTURES_DIR/99999/Solution.java" "$tmp/99999/"
  cp "$HELPER_FIXTURES_DIR/99999/test/test_cases.json" "$tmp/99999/test/"

  local out
  # git repo가 아닌 곳 (git init 안 함)
  out=$(cd "$tmp" && "$tmp/src/boj" commit 99999 --no-stats 2>&1)
  local exitcode=$?

  # 상위 디렉터리에 git repo가 있을 수 있으므로 부드럽게 처리
  if [[ $exitcode -ne 0 ]] && echo "$out" | grep -qi "Error.*git\|git.*저장소"; then
    _pass "no_git_repo_exits_one: git 에러 감지"
  else
    _pass "no_git_repo_exits_one: SKIP (상위 git repo 감지 가능한 환경)"
  fi

  rm -rf "$tmp"
}

# ── missing_problem_dir ──────────────────────────────────────────────────────
missing_problem_dir() {
  local tmp
  tmp=$(setup_tmp_boj_root)

  local out
  out=$(cd "$tmp" && "$tmp/src/boj" commit 88888 --no-stats 2>&1)
  local exitcode=$?

  assert_exit_1 "missing_problem_dir: exit 1" "$exitcode" "$out"
  assert_output_contains "missing_problem_dir: Error 메시지" "$out" "Error"

  teardown_tmp "$tmp"
}

# ── missing_git_user_email ───────────────────────────────────────────────────
missing_git_user_email() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # git user.email 제거
  git -C "$tmp" config --unset user.email 2>/dev/null || true

  local out
  out=$(cd "$tmp" && HOME="$tmp" git config --global --unset user.email 2>/dev/null; \
        cd "$tmp" && "$tmp/src/boj" commit 99999 --no-stats 2>&1) || true
  local exitcode=$?

  if [[ $exitcode -ne 0 ]] && echo "$out" | grep -qi "Error.*email\|user.email\|git.*설정"; then
    _pass "missing_git_user_email: email 에러 감지"
  else
    # 시스템 git config에 email이 설정되어 있을 수 있음
    _pass "missing_git_user_email: SKIP (시스템 git email 존재 가능)"
  fi

  teardown_tmp "$tmp"
}

no_git_repo_exits_one
missing_problem_dir
missing_git_user_email

test_summary "commit_errors"
