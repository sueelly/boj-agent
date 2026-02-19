#!/bin/bash

# ======================================
# 백준 테스트 실행 스크립트
# ======================================
# 사용법: ./run.sh [문제번호]
# 예시: ./run.sh 4949
# 예시: ./run.sh 3273
# ======================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ $# -lt 1 ]; then
    echo "사용법: ./run.sh [문제번호]"
    echo "예시: ./run.sh 4949"
    echo ""
    echo "존재하는 문제 폴더:"
    ls -d [0-9]*/ 2>/dev/null | sed 's|/$||'
    exit 1
fi

INPUT="$1"
PROBLEM_DIR=$(find . -maxdepth 1 -type d -name "${INPUT}*" | head -1 | sed 's|^\./||')

if [ -z "$PROBLEM_DIR" ] || [ "$PROBLEM_DIR" = "." ]; then
    echo "Error: '${INPUT}'로 시작하는 폴더를 찾을 수 없습니다."
    ls -d [0-9]*/ 2>/dev/null | sed 's|/$||'
    exit 1
fi

if [ ! -f "$PROBLEM_DIR/test/Parse.java" ] || [ ! -f "$PROBLEM_DIR/test/test_cases.json" ]; then
    echo "Error: $PROBLEM_DIR/test/Parse.java 또는 test/test_cases.json 이 없습니다."
    exit 1
fi

cd "$PROBLEM_DIR"
TEMPLATE="../template"
javac -cp ".:$TEMPLATE" "$TEMPLATE/ParseAndCallSolve.java" "$TEMPLATE/Test.java" Solution.java test/Parse.java

if [ $? -eq 0 ]; then
    java -cp ".:test:$TEMPLATE" Test
fi

rm -f *.class test/*.class
