#!/bin/bash

# 백준 Main 실행 스크립트

# 컴파일
javac Main.java Solution.java

if [ $? -eq 0 ]; then
    echo "💡 입력을 직접 입력하세요 (Ctrl+D로 종료)"
    echo "=========================================="
    java Main
    echo "=========================================="
fi

# 항상 .class 파일 삭제
rm -f *.class
