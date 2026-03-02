# commit 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드
3. 옵션 파싱 (--message, --no-stats)
4. git repo 확인
5. git user.email 확인
6. 문제 폴더 탐색
7. BOJ 통계 조회 (--no-stats 또는 세션 없으면 스킵)
8. 커밋 메시지 구성
9. 언어 감지 (Solution.java / solution.py / Solution.cpp 등)
10. 파일 목록 구성 (README.md, Solution.*, test/Parse.*, submit/Submit.*)
11. git add
12. git commit
13. 푸시 확인 (interactive)

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| CM1 | --no-stats → 통계 없이 커밋 생성 | happy |
| CM2 | Java 언어 파일 git add | happy |
| CM3 | --message "custom" → 메시지 포함 | branches |
| CM4 | Python solution.py staged | branches |
| CM5 | submit/ 존재 시 Submit.java staged | branches |
| CM6 | 변경사항 없음 → exit 0 + Warning: | branches |
| CM7 | git repo 없음 → exit 1 + Error: | errors |
| CM8 | 문제 폴더 없음 → exit 1 | errors |
| CM9 | git user.email 없음 → exit 1 | errors |

## 분기 → 테스트 매핑 테이블
| 분기 | 파일 | 테스트명 |
|------|------|---------|
| CM1 | tests/unit/commands/commit_happy.sh | commit_no_stats_creates_commit |
| CM2 | tests/unit/commands/commit_happy.sh | staged_files_list_java |
| CM3 | tests/unit/commands/commit_branches.sh | custom_message_flag |
| CM4 | tests/unit/commands/commit_branches.sh | python_solution_staged |
| CM5 | tests/unit/commands/commit_branches.sh | submit_folder_staged_if_exists |
| CM6 | tests/unit/commands/commit_branches.sh | no_changes_exits_zero |
| CM7 | tests/unit/commands/commit_errors.sh | no_git_repo_exits_one |
| CM8 | tests/unit/commands/commit_errors.sh | missing_problem_dir |
| CM9 | tests/unit/commands/commit_errors.sh | missing_git_user_email |
