# review 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드 (solution_root, boj_agent_root, agent, editor)
3. 문제 폴더 탐색 (find_problem_dir)
4. Solution 파일 탐색 (find_solution_file) — 없으면 Warning (리뷰는 계속)
5. 프롬프트 빌드 (build_review_prompt: 템플릿 + Solution 내용)
6. 에이전트 명령 확인 (config_get("agent") → AGENT_COMMANDS 매핑)
7. 에이전트 있으면: run_review → stdout을 submit/REVIEW.md로 저장
8. 에이전트 없으면: 클립보드 복사 + 에디터 열기 fallback

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| RV1 | 에이전트로 리뷰 요청 + REVIEW.md 저장 | happy |
| RV2 | Solution 없음 → Warning (리뷰 계속) | warnings |
| RV3 | 문제 폴더 없음 → BojError (exit 1) | errors |
| RV4 | 에이전트 실행 실패 → BojError (exit 1) | errors |
| RV5 | 에이전트 없음 → 에디터 fallback | branches |
| RV6 | 에이전트 stdout 빈 경우 → REVIEW.md 미생성 | branches |

## 분기 → 테스트 매핑 테이블

### Python 단위 테스트 (tests/unit/test_review.py)
| 분기 | 클래스 | 테스트명 |
|------|--------|---------|
| — | TestFindSolutionFile | test_finds_java_solution |
| — | TestFindSolutionFile | test_finds_python_solution_lowercase |
| — | TestFindSolutionFile | test_finds_python_solution_uppercase |
| — | TestFindSolutionFile | test_returns_none_when_missing |
| — | TestFindSolutionFile | test_finds_any_solution_when_lang_none |
| — | TestFindSolutionFile | test_returns_none_when_no_solution_and_lang_none |
| — | TestBuildReviewPrompt | test_includes_template_content |
| — | TestBuildReviewPrompt | test_includes_solution_content |
| RV2 | TestBuildReviewPrompt | test_prompt_without_solution |
| — | TestBuildReviewPrompt | test_prompt_without_template |
| — | TestBuildReviewPrompt | test_prompt_ends_with_review_request |
| RV1 | TestRunReview | test_calls_subprocess_with_correct_args |
| RV4 | TestRunReview | test_raises_boj_error_when_agent_fails |
| RV4 | TestRunReview | test_raises_boj_error_when_command_not_found |
| — | TestClipboardFallback | test_returns_true_when_pbcopy_available |
| — | TestClipboardFallback | test_returns_false_when_no_clipboard_tool |
| — | TestWriteReviewFile | test_creates_submit_dir_and_writes_file |
| — | TestWriteReviewFile | test_overwrites_existing_review |
| — | TestWriteReviewFile | test_handles_unicode_content |
| RV3 | TestReview | test_raises_boj_error_when_problem_dir_missing |
| RV2 | TestReview | test_warns_when_solution_missing |
| RV1 | TestReview | test_calls_agent_when_configured (+ REVIEW.md 생성 검증) |
| RV6 | TestReview | test_does_not_write_review_when_stdout_empty |
| RV5 | TestReview | test_falls_back_to_clipboard_when_no_agent |

### Python 통합 테스트 (tests/integration/test_review_py.py)
| 분기 | 클래스 | 테스트명 |
|------|--------|---------|
| RV5 | TestReviewHappy | test_review_exits_zero_without_agent |
| RV1 | TestReviewHappy | test_review_with_echo_agent (+ REVIEW.md 생성 검증) |
| RV2 | TestReviewWarnings | test_warns_when_solution_missing |
| RV3 | TestReviewErrors | test_exits_one_when_problem_dir_missing |
| RV4 | TestReviewErrors | test_exits_one_when_agent_fails |

### Bash 레거시 테스트 (tests/_legacy_bash/)
| 분기 | 파일 | 테스트명 |
|------|------|---------|
| RV1 | tests/_legacy_bash/unit/commands/review_happy.sh | agent_called_with_solution |
| RV5 | tests/_legacy_bash/unit/commands/review_branches.sh | no_agent_fallback_to_editor |
| RV3 | tests/_legacy_bash/unit/commands/review_errors.sh | missing_problem_dir |
