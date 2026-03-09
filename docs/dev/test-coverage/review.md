# review 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드
3. 문제 폴더 탐색
4. Solution 파일 없으면 Warning (리뷰는 계속)
5. 에이전트 명령 확인 (BOJ_AGENT_CMD > 설정 파일)
6. prompts/review.md 존재 시 사용
7. 에이전트 있으면: cd PROBLEM_DIR && AGENT_CMD PROMPT
8. 에이전트 없으면: 클립보드 복사 + 에디터 열기 fallback

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| RV1 | 에이전트로 리뷰 요청 | happy |
| RV2 | 에이전트 없음 → 에디터 fallback | branches |
| RV3 | 문제 폴더 없음 → exit 1 | errors |

## 분기 → 테스트 매핑 테이블
| 분기 | 파일 | 테스트명 |
|------|------|---------|
| RV1 | tests/unit/commands/review_happy.sh | agent_called_with_solution |
| RV2 | tests/unit/commands/review_branches.sh | no_agent_fallback_to_editor |
| RV3 | tests/unit/commands/review_errors.sh | missing_problem_dir |
