#!/usr/bin/env bash
# 통합 테스트: boj submit 99999
set -e
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"
FIXTURE_DIR="$TESTS_DIR/../fixtures/99999"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

export HOME="$TMP"
export BOJ_CONFIG_DIR="$TMP/.config/boj"
export BOJ_ROOT="$TMP"

cp -r "$REPO_ROOT/templates" "$TMP/"
cp -r "$REPO_ROOT/src" "$TMP/"
chmod +x "$TMP/src/boj" "$TMP/src/commands/"*.sh "$TMP/src/lib/"*.sh 2>/dev/null || true
cp -r "$FIXTURE_DIR" "$TMP/99999"

# boj 명령을 TMP 안에서 실행 (find_boj_root가 TMP를 루트로 인식하도록)
BOJ="$TMP/src/boj"

# --- 테스트 1: 정상 Submit.java 생성 ---
out=$((cd "$TMP" && "$BOJ" submit 99999) 2>&1)
exitcode=$?

if [[ $exitcode -ne 0 ]]; then
  echo "FAIL: boj submit 99999 failed (exit $exitcode)"
  echo "$out"
  exit 1
fi

SUBMIT_FILE="$TMP/99999/submit/Submit.java"
if [[ ! -f "$SUBMIT_FILE" ]]; then
  echo "FAIL: Submit.java가 생성되지 않았습니다"
  echo "$out"
  exit 1
fi
echo "PASS: Submit.java 생성됨"

# --- 테스트 2: Submit.java에 Main 클래스 포함 ---
if grep -q "public class Main" "$SUBMIT_FILE"; then
  echo "PASS: Main 클래스 포함"
else
  echo "FAIL: Main 클래스 없음"
  cat "$SUBMIT_FILE"
  exit 1
fi

# --- 테스트 3: 컴파일 가능한지 확인 ---
COMPILE_TMP=$(mktemp -d)
cp "$SUBMIT_FILE" "$COMPILE_TMP/Main.java"
if javac "$COMPILE_TMP/Main.java" 2>/dev/null; then
  echo "PASS: Submit.java 컴파일 성공"
else
  echo "FAIL: Submit.java 컴파일 실패"
  cat "$SUBMIT_FILE"
  rm -rf "$COMPILE_TMP"
  exit 1
fi
rm -rf "$COMPILE_TMP"

# --- 테스트 4: Solution.java 없을 때 에러 ---
TMP2=$(mktemp -d)
trap 'rm -rf "$TMP" "$TMP2"' EXIT
mkdir -p "$TMP2/99999-no-solution"
cp -r "$FIXTURE_DIR/test" "$TMP2/99999-no-solution/"
cp -r "$REPO_ROOT/templates" "$TMP2/"
cp -r "$REPO_ROOT/src" "$TMP2/"
chmod +x "$TMP2/src/boj" "$TMP2/src/commands/"*.sh "$TMP2/src/lib/"*.sh 2>/dev/null || true

BOJ2="$TMP2/src/boj"
out2=$((cd "$TMP2" && "$BOJ2" submit 99999) 2>&1) || true
if echo "$out2" | grep -qi "Error.*Solution\|Solution.*없\|없습니다"; then
  echo "PASS: Solution.java 없을 때 에러 메시지"
else
  echo "FAIL: Solution.java 없을 때 적절한 에러 없음"
  echo "출력: $out2"
  exit 1
fi

# --- 테스트 5: 문제 폴더 없을 때 에러 ---
out3=$((cd "$TMP" && "$BOJ" submit 88888) 2>&1) || true
if echo "$out3" | grep -qi "Error\|없습니다"; then
  echo "PASS: 문제 폴더 없을 때 에러"
else
  echo "FAIL: 문제 폴더 없을 때 에러 없음"
  echo "출력: $out3"
  exit 1
fi

echo ""
echo "PASS: test_boj_submit 모두 통과"
