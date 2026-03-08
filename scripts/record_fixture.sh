#!/usr/bin/env bash
# scripts/record_fixture.sh — 픽스처 자동 저장
# 사용: ./scripts/record_fixture.sh <problem_id> [--force]
# 1. curl로 BOJ HTML 다운로드 → tests/fixtures/<N>/raw.html
# 2. boj_client.py raw.html → tests/fixtures/<N>/problem.json
# 3. boj_normalizer.py problem.json → tests/fixtures/<N>/readme.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES_DIR="$REPO_ROOT/tests/fixtures"

usage() {
  echo "사용법: $0 <problem_id> [--force]"
  echo "  problem_id  BOJ 문제 번호 (숫자)"
  echo "  --force     기존 파일 덮어쓰기"
  exit 1
}

# 인수 파싱
PROBLEM_ID=""
FORCE=false

for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=true ;;
    [0-9]*) PROBLEM_ID="$arg" ;;
    -h|--help) usage ;;
    *) echo "Error: 알 수 없는 옵션: $arg" >&2; usage ;;
  esac
done

if [[ -z "$PROBLEM_ID" ]]; then
  echo "Error: 문제 번호를 입력하세요." >&2
  usage
fi

if [[ ! "$PROBLEM_ID" =~ ^[0-9]+$ ]]; then
  echo "Error: 문제 번호는 숫자여야 합니다: '$PROBLEM_ID'" >&2
  exit 1
fi

FIXTURE_DIR="$FIXTURES_DIR/$PROBLEM_ID"
HTML_FILE="$FIXTURE_DIR/raw.html"
JSON_FILE="$FIXTURE_DIR/problem.json"
README_FILE="$FIXTURE_DIR/readme.md"

# 이미 존재하면 --force 없이는 거부
if [[ -d "$FIXTURE_DIR" && "$FORCE" != "true" ]]; then
  echo "Error: '$FIXTURE_DIR' 이미 존재합니다. 덮어쓰려면 --force 사용." >&2
  exit 1
fi

mkdir -p "$FIXTURE_DIR"

echo "=== BOJ $PROBLEM_ID 픽스처 저장 ==="
echo ""

# 1. HTML 다운로드 (또는 로컬 파일 사용)
BOJ_URL="https://www.acmicpc.net/problem/$PROBLEM_ID"
if [[ -n "${BOJ_CLIENT_TEST_HTML:-}" && -f "$BOJ_CLIENT_TEST_HTML" ]]; then
  echo "[1/3] 로컬 HTML 사용: $BOJ_CLIENT_TEST_HTML"
  cp "$BOJ_CLIENT_TEST_HTML" "$HTML_FILE"
else
  echo "[1/3] HTML 다운로드: $BOJ_URL"
  if ! curl -s --max-time 15 \
      -H "User-Agent: Mozilla/5.0 (compatible; boj-agent/1.0)" \
      -o "$HTML_FILE" "$BOJ_URL"; then
    echo "Error: HTML 다운로드 실패" >&2
    exit 1
  fi
fi

if [[ ! -s "$HTML_FILE" ]]; then
  echo "Error: HTML이 비어 있습니다. 문제 번호 또는 파일 경로를 확인하세요." >&2
  exit 1
fi
echo "  ✓ raw.html ($(wc -c < "$HTML_FILE") bytes)"

# 2. boj_client.py → problem.json
echo "[2/3] problem.json 생성 중..."
TMP_OUT=$(mktemp -d)
trap 'rm -rf "$TMP_OUT"' EXIT

if ! BOJ_CLIENT_TEST_HTML="$HTML_FILE" \
    python3 "$REPO_ROOT/src/lib/boj_client.py" \
    --problem "$PROBLEM_ID" --out "$TMP_OUT" 2>/dev/null; then
  echo "Error: boj_client.py 실패" >&2
  exit 1
fi

if [[ ! -f "$TMP_OUT/problem.json" ]]; then
  echo "Error: problem.json 미생성" >&2
  exit 1
fi

cp "$TMP_OUT/problem.json" "$JSON_FILE"
echo "  ✓ problem.json"

# 3. boj_normalizer.py → readme.md
echo "[3/3] readme.md 생성 중..."
if ! python3 "$REPO_ROOT/src/lib/boj_normalizer.py" \
    --input "$JSON_FILE" --out "$README_FILE" 2>/dev/null; then
  echo "Error: boj_normalizer.py 실패" >&2
  exit 1
fi
echo "  ✓ readme.md"

echo ""
echo "완료: $FIXTURE_DIR"
echo "  - raw.html"
echo "  - problem.json"
echo "  - readme.md"
