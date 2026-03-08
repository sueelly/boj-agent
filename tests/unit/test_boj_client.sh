#!/usr/bin/env bash
# boj_client.py HTTP fetch 테스트 실행기
# 로컬 HTTP 서버 기반 (A) + 실제 BOJ (B, BOJ_SESSION 있을 때만)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

python3 tests/unit/test_boj_client.py -v
