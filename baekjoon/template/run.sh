#!/bin/bash

# 백준 Main 실행 스크립트
# 표준 입력으로 직접 테스트할 때 사용

MAIN_CLASS="Main"

# 1. 기존 .class 파일 삭제
rm -f *.class

# 2. 컴파일 (Main.java와 Solution.java)
echo "🚀 컴파일 중..."
javac Main.java Solution.java

# 3. 컴파일 성공 여부 확인
if [ $? -eq 0 ]; then
    echo "✅ 컴파일 성공! 실행 중..."
    echo "=========================================="
    echo "💡 입력을 직접 입력하세요 (Ctrl+D로 종료)"
    echo "=========================================="
    
    # 4. 실행
    java $MAIN_CLASS
    
    echo "=========================================="
    
    # 5. .class 파일 삭제
    rm -f *.class
else
    echo "❌ 컴파일 실패! 코드를 확인하세요."
fi
