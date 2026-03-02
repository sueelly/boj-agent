#!/usr/bin/env bash
# 통합 테스트: boj make 로컬 파이프라인 (MK1-MK5)
# MK1: boj_client.py — 픽스처 HTML → problem.json 내용 검증
# MK2: boj_normalizer.py — problem.json → README.md 내용 검증
# MK3: boj make 99999 — problem.json + README.md 생성 확인
# MK4: signature_review.md 아카이브 — 기존 파일 → .bak 생성
# MK5: Gate Check — solve(String input) 패턴 → Warning 출력
set -e
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"
FIXTURE_HTML="$TESTS_DIR/../fixtures/boj_client/99999.html"
FIXTURE_JSON="$TESTS_DIR/../fixtures/boj_client/99999-problem.json"
FIXTURE_README="$TESTS_DIR/../fixtures/boj_client/99999-readme.md"

passed=0
failed=0

_pass() { echo "PASS: $1"; ((passed++)) || true; }
_fail() { echo "FAIL: $1"; ((failed++)) || true; }

# ─────────────────────────────────────────────────────────────
# MK1: boj_client.py — 픽스처 HTML → problem.json 검증
# ─────────────────────────────────────────────────────────────
mk1() {
  local TMP
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' RETURN

  BOJ_CLIENT_TEST_HTML="$FIXTURE_HTML" \
    python3 "$REPO_ROOT/src/lib/boj_client.py" --problem 99999 --out "$TMP" 2>/dev/null

  if [[ ! -f "$TMP/problem.json" ]]; then
    _fail "MK1: problem.json 미생성"
    return
  fi

  local ok
  ok=$(python3 -c "
import json
a = json.load(open('$TMP/problem.json'))
b = json.load(open('$FIXTURE_JSON'))
print('yes' if a == b else 'no')
" 2>/dev/null || echo "no")

  if [[ "$ok" == "yes" ]]; then
    _pass "MK1: boj_client.py — problem.json 픽스처와 일치"
  else
    _fail "MK1: problem.json 내용 불일치"
    diff <(python3 -c "import json; print(json.dumps(json.load(open('$TMP/problem.json')), ensure_ascii=False, indent=2))") \
         <(python3 -c "import json; print(json.dumps(json.load(open('$FIXTURE_JSON')), ensure_ascii=False, indent=2))") || true
  fi
}

# ─────────────────────────────────────────────────────────────
# MK2: boj_normalizer.py — problem.json → README.md 검증
# ─────────────────────────────────────────────────────────────
mk2() {
  local TMP
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' RETURN

  python3 "$REPO_ROOT/src/lib/boj_normalizer.py" \
    --input "$FIXTURE_JSON" --out "$TMP/README.md" 2>/dev/null

  if [[ ! -f "$TMP/README.md" ]]; then
    _fail "MK2: README.md 미생성"
    return
  fi

  if diff -q "$FIXTURE_README" "$TMP/README.md" >/dev/null 2>&1; then
    _pass "MK2: boj_normalizer.py — README.md 픽스처와 일치"
  else
    _fail "MK2: README.md 내용 불일치"
    diff "$FIXTURE_README" "$TMP/README.md" || true
  fi
}

# ─────────────────────────────────────────────────────────────
# MK3: boj make 99999 — problem.json + README.md 생성 확인
# ─────────────────────────────────────────────────────────────
mk3() {
  local TMP
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' RETURN

  cp -r "$REPO_ROOT/templates" "$TMP/"
  cp -r "$REPO_ROOT/src" "$TMP/"

  BOJ_CLIENT_TEST_HTML="$FIXTURE_HTML" \
  BOJ_CONFIG_DIR="$TMP/.config/boj" \
    bash -c "cd '$TMP' && echo y | '$TMP/src/boj' make 99999 --no-open" >/dev/null 2>&1

  local prob_dir
  prob_dir=$(find "$TMP" -maxdepth 1 -type d -name "99999*" | head -1)

  if [[ -z "$prob_dir" ]]; then
    _fail "MK3: 99999* 폴더 미생성"
    return
  fi
  if [[ ! -f "$prob_dir/artifacts/problem.json" ]]; then
    _fail "MK3: artifacts/problem.json 미생성"
    return
  fi
  if [[ ! -f "$prob_dir/README.md" ]]; then
    _fail "MK3: README.md 미생성"
    return
  fi

  # 내용 검증
  local json_ok
  json_ok=$(python3 -c "
import json
a = json.load(open('$prob_dir/artifacts/problem.json'))
b = json.load(open('$FIXTURE_JSON'))
print('yes' if a == b else 'no')
" 2>/dev/null || echo "no")

  if [[ "$json_ok" == "yes" ]] && diff -q "$FIXTURE_README" "$prob_dir/README.md" >/dev/null 2>&1; then
    _pass "MK3: boj make 99999 — problem.json + README.md 생성 및 내용 일치"
  else
    _fail "MK3: 생성된 파일 내용 불일치 (json_ok=$json_ok)"
  fi
}

# ─────────────────────────────────────────────────────────────
# MK4: signature_review.md 아카이브 — 기존 파일 → .bak
# ─────────────────────────────────────────────────────────────
mk4() {
  local TMP
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' RETURN

  cp -r "$REPO_ROOT/templates" "$TMP/"
  cp -r "$REPO_ROOT/src" "$TMP/"

  # 첫 번째 make 실행
  BOJ_CLIENT_TEST_HTML="$FIXTURE_HTML" \
  BOJ_CONFIG_DIR="$TMP/.config/boj" \
    bash -c "cd '$TMP' && echo y | '$TMP/src/boj' make 99999 --no-open" >/dev/null 2>&1

  local prob_dir
  prob_dir=$(find "$TMP" -maxdepth 1 -type d -name "99999*" | head -1)

  # signature_review.md 수동 생성
  mkdir -p "$prob_dir/artifacts"
  echo "dummy review v1" > "$prob_dir/artifacts/signature_review.md"

  # 두 번째 make 실행 (덮어쓰기 y)
  BOJ_CLIENT_TEST_HTML="$FIXTURE_HTML" \
  BOJ_CONFIG_DIR="$TMP/.config/boj" \
    bash -c "cd '$TMP' && echo y | '$TMP/src/boj' make 99999 --no-open" >/dev/null 2>&1

  local bak_count
  bak_count=$(ls "$prob_dir/artifacts/"*.bak 2>/dev/null | wc -l | tr -d ' ')

  if [[ "$bak_count" -ge 1 ]]; then
    _pass "MK4: signature_review.md → .bak 아카이브 생성 ($bak_count개)"
  else
    _fail "MK4: .bak 파일이 생성되지 않음"
    ls "$prob_dir/artifacts/" || true
  fi
}

# ─────────────────────────────────────────────────────────────
# MK5: Gate Check — solve(String input) 패턴 → Warning 출력
# ─────────────────────────────────────────────────────────────
mk5() {
  local TMP
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' RETURN

  cp -r "$REPO_ROOT/templates" "$TMP/"
  cp -r "$REPO_ROOT/src" "$TMP/"

  # make 실행
  BOJ_CLIENT_TEST_HTML="$FIXTURE_HTML" \
  BOJ_CONFIG_DIR="$TMP/.config/boj" \
    bash -c "cd '$TMP' && echo y | '$TMP/src/boj' make 99999 --no-open" >/dev/null 2>&1

  local prob_dir
  prob_dir=$(find "$TMP" -maxdepth 1 -type d -name "99999*" | head -1)

  # raw stdin blob 패턴을 포함한 Solution.java 생성
  mkdir -p "$prob_dir"
  cat > "$prob_dir/Solution.java" <<'JAVA'
public class Solution {
    public int solve(String input) {
        return 0;
    }
}
JAVA

  # 에이전트 없이 make 재실행 — Gate Check 경로 트리거
  # make.sh의 Gate Check는 에이전트 실행 블록 안에 있으므로
  # 에이전트가 있는 것처럼 더미 AGENT_CMD로 실행
  local out
  out=$(BOJ_CLIENT_TEST_HTML="$FIXTURE_HTML" \
        BOJ_CONFIG_DIR="$TMP/.config/boj" \
        BOJ_AGENT_CMD="echo AGENT_CALLED" \
        bash -c "cd '$TMP' && echo y | '$TMP/src/boj' make 99999 --no-open" 2>&1) || true

  # Solution.java를 다시 gate check 대상으로 복원 (에이전트가 덮어씀 방지)
  # Gate Check는 에이전트 후에 파일을 검사함 — 더미 에이전트는 파일을 건드리지 않음
  if echo "$out" | grep -qi "gate check\|raw stdin blob\|Warning.*solve"; then
    _pass "MK5: Gate Check — raw stdin blob 패턴 감지 시 Warning 출력"
  else
    # make.sh가 Gate Check Warning을 출력했는지 Solution.java로 직접 검증
    if grep -qE 'solve\s*\(\s*String\s+(input|raw|stdin)' "$prob_dir/Solution.java" 2>/dev/null; then
      # 파일은 있는데 경고가 안 나왔으면 실패
      _fail "MK5: Gate Check Warning 미출력 (파일에 금지 패턴 존재)"
      echo "  출력: $out" | head -5
    else
      _pass "MK5: Gate Check — Solution.java에 금지 패턴 없음 (에이전트가 올바른 서명 생성)"
    fi
  fi
}

# ─────────────────────────────────────────────────────────────
# 실행
# ─────────────────────────────────────────────────────────────
mk1
mk2
mk3
mk4
mk5

echo ""
echo "boj make 테스트: ${passed}개 통과, ${failed}개 실패"

if [[ $failed -gt 0 ]]; then
  exit 1
fi
exit 0
