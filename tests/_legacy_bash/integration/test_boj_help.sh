#!/usr/bin/env bash
# 통합 테스트: boj --help
set -e
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cp -r "$REPO_ROOT/templates" "$TMP/"
cp -r "$REPO_ROOT/src" "$TMP/"

export BOJ_ROOT="$TMP"
out=$("$TMP/src/boj" --help 2>&1)
exitcode=$?

if [[ $exitcode -ne 0 ]]; then
  echo "FAIL: boj --help exited $exitcode"
  echo "$out"
  exit 1
fi
if ! echo "$out" | grep -q "run"; then
  echo "FAIL: output did not contain 'run'"
  echo "$out"
  exit 1
fi
if ! echo "$out" | grep -q "commit"; then
  echo "FAIL: output did not contain 'commit'"
  exit 1
fi
echo "PASS: boj --help"
