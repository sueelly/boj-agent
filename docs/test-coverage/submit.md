# submit 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드
3. 옵션 파싱 (--lang, --open, --force)
4. 언어별 파일 확장자 결정
5. Solution 파일 존재 확인
6. submit/ 폴더 생성
7. 기존 Submit 파일 존재 확인 (--force 아니면 확인 요청)
8. 언어별 Submit 생성
   - Java: imports 추출 + Main 클래스 + Parse 병합
   - Python: 헤더 + Solution 내용 + main 블록
   - cpp: bits/stdc++.h + Solution 내용 + main
   - c: stdio.h + Solution 내용 + main
   - kotlin/go: 에이전트 안내
9. Java: javac 컴파일 검증
10. --open: 제출 페이지 브라우저 열기

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| SB1 | Java Submit.java 생성 | happy |
| SB2 | 생성된 Submit.java javac 통과 | happy |
| SB3 | Parse.java 있으면 병합 | branches |
| SB4 | Parse.java 없어도 Submit 생성 | branches |
| SB5 | --force → 기존 Submit.java 덮어씀 | branches |
| SB6 | --lang python → submit/Submit.py 생성 | branches |
| SB7 | --lang cpp → submit/Submit.cpp 생성 | branches |
| SB8 | Solution.java 없음 → exit 1 | errors |
| SB9 | 미지원 언어 --lang pascal → exit 1 | errors |
| SB10 | Submit 이미 있고 --force 없음 → exit 0 (취소) | errors |

## 분기 → 테스트 매핑 테이블
| 분기 | 파일 | 테스트명 |
|------|------|---------|
| SB1 | tests/unit/commands/submit_happy.sh | java_submit_generated |
| SB2 | tests/unit/commands/submit_happy.sh | java_submit_compiles |
| SB3 | tests/unit/commands/submit_branches.sh | java_with_parse_included |
| SB4 | tests/unit/commands/submit_branches.sh | java_without_parse |
| SB5 | tests/unit/commands/submit_branches.sh | force_overwrites_existing |
| SB6 | tests/unit/commands/submit_branches.sh | python_stub_generated |
| SB7 | tests/unit/commands/submit_branches.sh | cpp_stub_generated |
| SB8 | tests/unit/commands/submit_errors.sh | missing_solution_exits_one |
| SB9 | tests/unit/commands/submit_errors.sh | unsupported_lang_exits_one |
| SB10 | tests/unit/commands/submit_errors.sh | existing_no_force_exits_zero |
