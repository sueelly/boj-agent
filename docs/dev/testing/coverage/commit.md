# commit 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드
3. 옵션 파싱 (--message, --no-stats, --no-push)
4. git repo 확인
5. git user.email 확인
6. 문제 폴더 탐색
7. BOJ 통계 조회 (--no-stats 또는 세션 없으면 스킵)
8. 커밋 메시지 구성
9. 파일 목록 구성 (README.md, Solution.*, test/Parse.*, submit/Submit.*, submit/REVIEW.md)
10. git add (화이트리스트 기반)
11. git commit
12. 푸시 확인 (--no-push로 스킵 가능)

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

### 단위 테스트 (`tests/unit/test_commit.py`)
| 분기 | 클래스 | 테스트 메서드 |
|------|--------|-------------|
| CM1 | TestBuildCommitMessage | test_auto_message_with_stats |
| CM1 | TestBuildCommitMessage | test_auto_message_without_stats |
| CM2 | TestStageProblemFiles | test_stages_existing_files |
| CM3 | TestBuildCommitMessage | test_custom_message_overrides |
| CM4 | TestStageProblemFiles | test_stages_existing_files |
| CM5 | TestStageProblemFiles | test_stages_existing_files |
| CM6 | TestHasStagedChanges | test_returns_false_when_clean |
| CM7 | TestCheckGitRepo | test_raises_when_not_git_repo |
| CM8 | TestStageProblemFiles | test_returns_empty_when_no_files |
| CM9 | TestCheckGitEmail | test_raises_when_email_not_set |

### 통합 테스트 (`tests/integration/test_commit_py.py`)
| 분기 | 클래스 | 테스트 메서드 |
|------|--------|-------------|
| CM1 | TestCommitHappy | test_commit_with_no_stats |
| CM3 | TestCommitHappy | test_commit_with_custom_message |
| CM6 | TestCommitErrors | test_warning_when_nothing_to_commit |
| CM7 | TestCommitErrors | test_error_when_not_git_repo |
| CM8 | TestCommitErrors | test_error_when_problem_not_found |
| — | TestCommitPreStaged | test_preserves_pre_staged_changes |
