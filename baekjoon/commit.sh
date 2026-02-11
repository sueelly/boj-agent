#!/bin/bash

# ======================================
# 백준 문제 풀이 GitHub 커밋 스크립트
# ======================================
# 사용법: ./commit.sh [문제번호] [커밋메시지(선택)]
# 예시: ./commit.sh 10808
# 예시: ./commit.sh 10808 "첫 번째 풀이"
# ======================================

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 스크립트 위치
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 인자 확인
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: 문제 번호를 입력해주세요.${NC}"
    echo ""
    echo "사용법: ./commit.sh [문제번호] [커밋메시지(선택)]"
    echo "예시: ./commit.sh 10808"
    exit 1
fi

INPUT="$1"

# 문제 번호로 시작하는 폴더 찾기
PROBLEM_DIR=$(find . -maxdepth 1 -type d -name "${INPUT}*" | head -1 | sed 's|^\./||')

# 폴더를 찾지 못한 경우
if [ -z "$PROBLEM_DIR" ] || [ "$PROBLEM_DIR" = "." ]; then
    echo -e "${RED}Error: '${INPUT}'로 시작하는 폴더를 찾을 수 없습니다.${NC}"
    echo ""
    echo "존재하는 문제 폴더:"
    ls -d [0-9]*/ 2>/dev/null | sed 's|/$||'
    exit 1
fi

# 커밋 메시지 설정
COMMIT_MSG="${2:-"$PROBLEM_DIR 풀이 완료"}"

echo -e "${BLUE}📁 문제 폴더: $PROBLEM_DIR${NC}"
echo -e "${BLUE}💬 커밋 메시지: $COMMIT_MSG${NC}"
echo ""

# Git 상태 확인
echo -e "${YELLOW}📋 변경된 파일:${NC}"
git status --short "$PROBLEM_DIR"
echo ""

# 파일 추가
echo -e "${BLUE}➕ 파일 추가 중...${NC}"
git add "$PROBLEM_DIR/README.md" 2>/dev/null
git add "$PROBLEM_DIR/REVIEW.md" 2>/dev/null
git add "$PROBLEM_DIR/Solution.java" 2>/dev/null
git add "$PROBLEM_DIR/Submit.java" 2>/dev/null
git add "$PROBLEM_DIR/test_cases.json" 2>/dev/null

# 커밋
echo -e "${BLUE}📝 커밋 중...${NC}"
git commit -m "$COMMIT_MSG"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 커밋 완료!${NC}"
    echo ""
    
    # 푸시 여부 확인
    read -p "GitHub에 푸시하시겠습니까? (y/N): " push_confirm
    if [[ "$push_confirm" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🚀 푸시 중...${NC}"
        git push
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 푸시 완료!${NC}"
        else
            echo -e "${RED}❌ 푸시 실패${NC}"
        fi
    else
        echo "푸시를 건너뛰었습니다. 나중에 'git push'로 푸시하세요."
    fi
else
    echo -e "${YELLOW}⚠️ 커밋할 변경사항이 없거나 실패했습니다.${NC}"
fi
