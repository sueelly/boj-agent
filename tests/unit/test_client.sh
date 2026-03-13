#!/usr/bin/env bash
# client.py HTTP fetch 테스트 실행기
# 로컬 HTTP 서버 기반 (A) + 실제 BOJ (B, BOJ_SESSION 있을 때만)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

python3 -m pytest tests/unit/test_client.py -v
