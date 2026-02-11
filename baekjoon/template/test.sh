#!/bin/bash

# 백준 Test 실행 스크립트

# 컴파일
javac Test.java Solution.java

if [ $? -eq 0 ]; then
    java Test
fi

# 항상 .class 파일 삭제
rm -f *.class
