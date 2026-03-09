# make 테스트 커버리지

## 로직 흐름 (단계별)
1. ROOT / PROBLEM_NUM 인수 수신
2. config 로드
3. 옵션 파싱 (--lang, --image-mode, --output, --no-open)
4. 언어 유효성 검사
5. image-mode 유효성 검사 (download|reference|skip)
6. --output 경로 유효성 검사
7. 기존 폴더 존재 확인 → 덮어쓰기 확인
8. [A] boj_client.py 실행 → problem.json 생성
9. 문제 폴더 / 제목 slug 결정
10. [B] boj_normalizer.py → README.md 생성
11. signature_review.md 아카이브 (.bak)
12. [C] 에이전트 실행 (BOJ_AGENT_CMD)
    - Gate Check: solve(String x) 단일 blob 감지 → Warning
    - Execution Verify: boj run 실행
13. 에이전트 없음 → 에디터+클립보드 fallback
14. --no-open 아니면 에디터 열기

## 분기 목록
| ID | 분기 | 경로 |
|----|------|------|
| MK1 | boj_client.py 정상 → problem.json 생성 | happy |
| MK2 | boj_normalizer.py 정상 → README.md 생성 | happy |
| MK3 | 기존 signature_review.md → .bak 아카이브 | branches |
| MK4 | 에이전트 없음 → 에디터+클립보드 fallback | branches |
| MK5 | gate check PASS (파라미터 ≥2) → Warning 없음 | branches |
| MK6 | gate check FAIL (solve(String x)) → Warning 출력 | branches |
| MK7 | --image-mode 플래그 boj_client에 전달 | branches |
| MK8 | --lang python 설정 적용 | branches |
| MK9 | 미지원 언어 --lang fortran → exit 1 | errors |
| MK10 | boj_client.py 실패 → exit 1 | errors |
| MK11 | --output 존재하지 않는 경로 → exit 1 | errors |

## 분기 → 테스트 매핑 테이블
| 분기 | 파일 | 테스트명 |
|------|------|---------|
| MK1 | tests/unit/commands/make_happy.sh | pipeline_a_generates_problem_json |
| MK2 | tests/unit/commands/make_happy.sh | pipeline_b_generates_readme |
| MK3 | tests/unit/commands/make_branches.sh | existing_sig_review_archived |
| MK4 | tests/unit/commands/make_branches.sh | no_agent_uses_fallback |
| MK5 | tests/unit/commands/make_branches.sh | gate_check_pass_no_warning |
| MK6 | tests/unit/commands/make_branches.sh | gate_check_fail_emits_warning |
| MK7 | tests/unit/commands/make_branches.sh | image_mode_flag_passed |
| MK8 | tests/unit/commands/make_branches.sh | lang_flag_validated |
| MK9 | tests/unit/commands/make_errors.sh | invalid_lang_exits_one |
| MK10 | tests/unit/commands/make_errors.sh | network_failure_exits_one |
| MK11 | tests/unit/commands/make_errors.sh | invalid_output_path |
