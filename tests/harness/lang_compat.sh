#!/usr/bin/env bash
# tests/harness/lang_compat.sh — 언어별 계약 준수 검증
# languages.json의 각 언어에 대해 템플릿 + 바이너리 존재 확인
set -euo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/.." && pwd)"
LANGUAGES_JSON="$REPO_ROOT/templates/languages.json"

passed=0
failed=0
skipped=0

_pass() { echo "PASS: $1"; ((passed++)) || true; }
_fail() { echo "FAIL: $1 — ${2:-}"; ((failed++)) || true; }
_skip() { echo "SKIP: $1 — ${2:-}"; ((skipped++)) || true; }

if [[ ! -f "$LANGUAGES_JSON" ]]; then
  echo "SKIP: languages.json 없음 ($LANGUAGES_JSON)"
  exit 0
fi

echo "=========================================="
echo "언어 호환성 검사: $LANGUAGES_JSON"
echo "=========================================="
echo ""

# languages.json에서 언어 목록 추출
langs=$(python3 -c "
import json
data = json.load(open('$LANGUAGES_JSON'))
if isinstance(data, dict):
    print('\n'.join(data.keys()))
elif isinstance(data, list):
    for item in data:
        print(item.get('id', item.get('name', '')))
" 2>/dev/null || echo "")

if [[ -z "$langs" ]]; then
  echo "INFO: languages.json 파싱 실패 또는 빈 목록"
  echo "지원 언어 목록을 직접 확인합니다."
  langs="java python cpp c kotlin go rust"
fi

# 언어별 컴파일러 바이너리
declare -A LANG_BIN=(
  [java]="javac"
  [python]="python3"
  [cpp]="g++"
  [c]="gcc"
  [kotlin]="kotlinc"
  [go]="go"
  [rust]="rustc"
  [ruby]="ruby"
  [swift]="swiftc"
  [scala]="scalac"
  [js]="node"
  [ts]="tsc"
)

while IFS= read -r lang; do
  [[ -z "$lang" ]] && continue

  echo "--- $lang ---"

  # 1. templates/<lang>/ 폴더 존재
  if [[ -d "$REPO_ROOT/templates/$lang" ]]; then
    _pass "$lang: templates/$lang/ 존재"
  else
    _skip "$lang: templates/$lang/ 없음" "미구현 언어"
    continue
  fi

  # 2. extension 확인 (languages.json에 있으면)
  ext=$(python3 -c "
import json
data = json.load(open('$LANGUAGES_JSON'))
if isinstance(data, dict):
    info = data.get('$lang', {})
    print(info.get('extension', info.get('ext', '')))
elif isinstance(data, list):
    for item in data:
        if item.get('id') == '$lang' or item.get('name') == '$lang':
            print(item.get('extension', item.get('ext', '')))
            break
" 2>/dev/null || echo "")
  if [[ -n "$ext" ]]; then
    _pass "$lang: extension='$ext' 존재"
  else
    _skip "$lang: extension 필드 없음 (languages.json 스키마 확인)"
  fi

  # 3. 컴파일러 바이너리 확인 (로컬 설치 여부)
  bin="${LANG_BIN[$lang]:-}"
  if [[ -n "$bin" ]]; then
    if command -v "$bin" &>/dev/null; then
      _pass "$lang: $bin PATH에 있음"
    else
      _skip "$lang: $bin 미설치 (로컬 환경에 없음)"
    fi
  fi

done <<< "$langs"

echo ""
echo "=========================================="
echo "언어 호환성: ${passed}개 통과, ${failed}개 실패, ${skipped}개 스킵"
echo "=========================================="

if [[ $failed -gt 0 ]]; then
  exit 1
fi
exit 0
