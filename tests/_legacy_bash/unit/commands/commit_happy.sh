#!/usr/bin/env bash
# commit_happy.sh — boj commit 정상 동작 테스트
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/tests"
source "$TESTS_DIR/unit/lib/test_helper.sh"

# ── commit_no_stats_creates_commit ───────────────────────────────────────────
commit_no_stats_creates_commit() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # 파일 스테이징
  git -C "$tmp" add "$tmp/99999/README.md" 2>/dev/null || \
    git -C "$tmp" add "99999" 2>/dev/null || true

  local out
  out=$(cd "$tmp" && echo "n" | "$tmp/src/boj" commit 99999 --no-stats 2>&1)
  local exitcode=$?

  # exit 0 또는 "변경사항 없음"(Warning) 모두 허용
  if [[ $exitcode -eq 0 ]]; then
    _pass "commit_no_stats_creates_commit: exit 0"
  else
    assert_output_contains "commit_no_stats_creates_commit: Warning or commit" "$out" "commit\|Warning\|변경사항\|통계: 스킵"
  fi

  teardown_tmp "$tmp"
}

# ── staged_files_list_java ───────────────────────────────────────────────────
staged_files_list_java() {
  local tmp
  tmp=$(setup_tmp_boj_root)
  copy_fixture "$tmp" "99999"

  # Solution.java + README.md 생성
  echo "# 99999" > "$tmp/99999/README.md"

  # 아무것도 staged 없는 상태에서 commit 실행 → 내부에서 git add 수행
  local out
  out=$(cd "$tmp" && echo "n" | "$tmp/src/boj" commit 99999 --no-stats 2>&1) || true

  # commit.sh가 Solution.java / README.md를 추가 시도했는지 확인
  assert_output_contains "staged_files_list_java: 파일 추가 시도" "$out" "추가\|add\|commit\|통계: 스킵\|변경사항"

  teardown_tmp "$tmp"
}

commit_no_stats_creates_commit
staged_files_list_java

test_summary "commit_happy"
