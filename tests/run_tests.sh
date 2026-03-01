#!/usr/bin/env bash
# tests/ 전체 테스트 실행 (unit + integration)
# 사용: ./tests/run_tests.sh [--unit|--integration|--all]
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTEGRATION_DIR="$TESTS_DIR/integration"
UNIT_DIR="$TESTS_DIR/unit"

MODE="${1:---all}"
passed=0
failed=0

run_test_file() {
  local f="$1"
  local name
  name=$(basename "$f")
  echo "--- $name ---"
  if bash "$f"; then
    ((passed++)) || true
  else
    echo "FAILED: $name"
    ((failed++)) || true
  fi
  echo ""
}

echo "=========================================="
echo "BOJ CLI 테스트 실행"
echo "=========================================="
echo ""

if [[ "$MODE" == "--unit" || "$MODE" == "--all" ]]; then
  echo "=== 단위 테스트 ==="
  for f in "$UNIT_DIR"/test_*.sh; do
    [[ -f "$f" ]] && run_test_file "$f" || true
  done
fi

if [[ "$MODE" == "--integration" || "$MODE" == "--all" ]]; then
  echo "=== 통합 테스트 ==="
  for f in "$INTEGRATION_DIR"/test_*.sh; do
    [[ -f "$f" ]] && run_test_file "$f" || true
  done
fi

echo ""
echo "=========================================="
echo "최종 결과: ${passed}개 통과, ${failed}개 실패"
echo "=========================================="

if [[ $failed -gt 0 ]]; then
  exit 1
fi
exit 0
