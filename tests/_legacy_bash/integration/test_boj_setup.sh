#!/usr/bin/env bash
# 통합 테스트: boj setup --check
set -e
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# 임시 HOME으로 설정 (실제 ~/.config/boj 오염 방지)
export HOME="$TMP"
export BOJ_CONFIG_DIR="$TMP/.config/boj"

# --- 테스트 1: setup --check with no config ---
out=$("$REPO_ROOT/src/boj" setup --check 2>&1) || true
if echo "$out" | grep -q "미설정\|missing\|root"; then
  echo "PASS: setup --check 미설정 상태 표시"
else
  echo "FAIL: setup --check가 미설정을 표시하지 않음"
  echo "출력: $out"
  exit 1
fi

# --- 테스트 2: config.sh boj_config_set/get ---
source "$REPO_ROOT/src/lib/config.sh"

boj_config_set "lang" "python"
val="$(boj_config_get "lang" "java")"
if [[ "$val" == "python" ]]; then
  echo "PASS: config set/get 동작"
else
  echo "FAIL: config get 실패 (expected: python, got: $val)"
  exit 1
fi

# --- 테스트 3: 환경변수 우선순위 ---
BOJ_LANG="java" val="$(boj_config_get "lang" "cpp")"
if [[ "$val" == "java" ]]; then
  echo "PASS: 환경변수 우선순위"
else
  echo "FAIL: 환경변수 우선순위 실패 (got: $val)"
  exit 1
fi

# --- 테스트 4: 지원 언어 검증 ---
if boj_validate_lang "java" &>/dev/null; then
  echo "PASS: java 언어 유효성 통과"
else
  echo "FAIL: java 유효성 실패"
  exit 1
fi

if boj_validate_lang "fortran" &>/dev/null; then
  echo "FAIL: fortran이 유효로 통과됨 (기대: 실패)"
  exit 1
else
  echo "PASS: fortran 언어 유효성 실패 (올바른 동작)"
fi

echo ""
echo "PASS: test_boj_setup 모두 통과"
