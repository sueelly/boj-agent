#!/usr/bin/env bash
# tests/harness/run_matrix.sh — (fixture × lang) 조합 매트릭스 테스트
set -euo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$TESTS_DIR/lib/matrix_helpers.sh"

passed=0
failed=0
skipped=0

_record() {
  local result="$1"
  case "$result" in
    PASS*) ((passed++)) || true ;;
    FAIL*) ((failed++)) || true ;;
    SKIP*) ((skipped++)) || true ;;
  esac
}

echo "=========================================="
echo "다언어 매트릭스 테스트"
echo "=========================================="
echo ""

# 매트릭스 범위
FIXTURES=(99999 1000 6588 9495)
LANGS=(java python)

for fixture in "${FIXTURES[@]}"; do
  for lang in "${LANGS[@]}"; do
    echo "--- fixture=$fixture lang=$lang ---"

    # boj run
    if fixture_has_solution "$fixture" "$lang"; then
      result=$(run_one_fixture "$fixture" "$lang" 2>&1) || true
      echo "$result"
      _record "$result"
    else
      echo "SKIP: run $fixture ($lang) — solution 파일 없음"
      ((skipped++)) || true
    fi

    # boj make
    result=$(make_one_fixture "$fixture" "$lang" 2>&1) || true
    echo "$result"
    _record "$result"

    echo ""
  done
done

echo "=========================================="
echo "매트릭스 결과: ${passed}개 통과, ${failed}개 실패, ${skipped}개 스킵"
echo "=========================================="

if [[ $failed -gt 0 ]]; then
  exit 1
fi
exit 0
