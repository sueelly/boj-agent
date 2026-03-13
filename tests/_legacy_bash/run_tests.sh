#!/usr/bin/env bash
# tests/ 전체 테스트 실행 (unit + integration + e2e + matrix)
# 사용: ./tests/run_tests.sh [--unit|--integration|--e2e|--matrix|--all]
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTEGRATION_DIR="$TESTS_DIR/integration"
UNIT_DIR="$TESTS_DIR/unit"
UNIT_CMD_DIR="$TESTS_DIR/unit/commands"
E2E_DIR="$TESTS_DIR/e2e"
HARNESS_DIR="$TESTS_DIR/harness"

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
  for f in "$UNIT_CMD_DIR"/*.sh; do
    [[ -f "$f" ]] && run_test_file "$f" || true
  done
fi

if [[ "$MODE" == "--integration" || "$MODE" == "--all" ]]; then
  echo "=== 통합 테스트 ==="
  for f in "$INTEGRATION_DIR"/test_*.sh; do
    [[ -f "$f" ]] && run_test_file "$f" || true
  done
fi

if [[ "$MODE" == "--e2e" || "$MODE" == "--all" ]]; then
  echo "=== E2E 테스트 ==="
  for f in "$E2E_DIR"/test_*.sh; do
    [[ -f "$f" ]] && run_test_file "$f" || true
  done
fi

if [[ "$MODE" == "--matrix" ]]; then
  echo "=== 다언어 매트릭스 테스트 ==="
  [[ -f "$HARNESS_DIR/lang_compat.sh" ]] && run_test_file "$HARNESS_DIR/lang_compat.sh" || true
  [[ -f "$HARNESS_DIR/run_matrix.sh" ]] && run_test_file "$HARNESS_DIR/run_matrix.sh" || true
fi

echo ""
echo "=========================================="
echo "최종 결과: ${passed}개 통과, ${failed}개 실패"
echo "=========================================="

if [[ $failed -gt 0 ]]; then
  exit 1
fi
exit 0
