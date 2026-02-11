#!/bin/bash

# 백준 Test 실행 스크립트
# 테스트 케이스 검증할 때 사용

TEST_CLASS="Test"

# 1. 기존 .class 파일 삭제
rm -f *.class

# 2. 컴파일 (Test.java와 Solution.java)
echo "🚀 컴파일 중..."
javac Test.java Solution.java

# 3. 컴파일 성공 여부 확인
if [ $? -eq 0 ]; then
    echo "✅ 컴파일 성공!"
    echo ""
    
    # 4. 테스트 실행
    java $TEST_CLASS
    
    # 5. .class 파일 삭제
    rm -f *.class
else
    echo "❌ 컴파일 실패! 코드를 확인하세요."
fi
