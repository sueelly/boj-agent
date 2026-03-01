#!/usr/bin/env bash
# 통합 테스트: boj run 99999 (픽스처 사용)
set -e
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"
FIXTURE_DIR="$TESTS_DIR/../fixtures/99999-fixture"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

cp -r "$REPO_ROOT/templates" "$TMP/"
cp -r "$REPO_ROOT/src" "$TMP/"
cp -r "$FIXTURE_DIR" "$TMP/99999-fixture"

cd "$TMP"
out=$("$TMP/src/boj" run 99999 2>&1) || true
exitcode=$?

if [[ $exitcode -ne 0 ]]; then
  echo "FAIL: boj run 99999 exited $exitcode"
  echo "$out"
  exit 1
fi
if ! echo "$out" | grep -q "2/2"; then
  echo "FAIL: expected 2/2 passed"
  echo "$out"
  exit 1
fi
if ! echo "$out" | grep -qi "passed"; then
  echo "FAIL: output did not contain passed/Passed"
  echo "$out"
  exit 1
fi
echo "PASS: boj run 99999"
