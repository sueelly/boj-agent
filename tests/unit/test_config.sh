#!/usr/bin/env bash
# 단위 테스트: src/lib/config.sh 함수 검증
set -e
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

export HOME="$TMP"
export BOJ_CONFIG_DIR="$TMP/.config/boj"

source "$REPO_ROOT/src/lib/config.sh"

pass=0
fail=0

check() {
  local name="$1" actual="$2" expected="$3"
  if [[ "$actual" == "$expected" ]]; then
    echo "PASS: $name"
    ((pass++)) || true
  else
    echo "FAIL: $name (expected='$expected', got='$actual')"
    ((fail++)) || true
  fi
}

# --- boj_config_get 기본값 ---
val="$(boj_config_get nonexistent_key "default_val")"
check "기본값 반환" "$val" "default_val"

# --- boj_config_set/get ---
boj_config_set "testkey" "testvalue"
val="$(boj_config_get "testkey" "default")"
check "set/get" "$val" "testvalue"

# --- 환경변수 우선순위 ---
BOJ_TESTKEY="env_val" val="$(boj_config_get "testkey" "default")"
check "환경변수 우선" "$val" "env_val"
unset BOJ_TESTKEY

# --- 언어 유효성: 지원 언어 ---
for lang in java python cpp c kotlin go rust ruby swift scala js ts; do
  boj_validate_lang "$lang" &>/dev/null && echo "PASS: validate_lang $lang" && ((pass++)) || true || { echo "FAIL: validate_lang $lang"; ((fail++)) || true; }
done

# --- 언어 유효성: 미지원 언어 ---
for lang in fortran pascal cobol; do
  if ! boj_validate_lang "$lang" &>/dev/null; then
    echo "PASS: 미지원언어 reject $lang"
    ((pass++)) || true
  else
    echo "FAIL: 미지원언어 $lang 통과됨"
    ((fail++)) || true
  fi
done

# --- boj_find_problem_dir: 존재하는 폴더 ---
mkdir -p "$TMP/4949-괄호의-값"
result="$(boj_find_problem_dir "$TMP" "4949")"
if [[ -n "$result" && "$result" == "$TMP/4949-괄호의-값" ]]; then
  echo "PASS: find_problem_dir 존재"
  ((pass++)) || true
else
  echo "FAIL: find_problem_dir (got: $result)"
  ((fail++)) || true
fi

# --- boj_find_problem_dir: 존재하지 않는 폴더 ---
result="$(boj_find_problem_dir "$TMP" "99998")"
if [[ -z "$result" ]]; then
  echo "PASS: find_problem_dir 없음"
  ((pass++)) || true
else
  echo "FAIL: find_problem_dir 없는 폴더 반환됨 (got: $result)"
  ((fail++)) || true
fi

echo ""
echo "=========================================="
echo "단위테스트 결과: ${pass}개 통과, ${fail}개 실패"
if [[ $fail -gt 0 ]]; then
  exit 1
fi
