# make 테스트 커버리지 (Python)

> `src/core/make.py` + `src/cli/boj_make.py` 기준.
> 참조: [COMMAND-SPEC.md](../../COMMAND-SPEC.md), [edge-cases.md](../../edge-cases.md) M1-M13

## 파이프라인 흐름

```
사전조건
├── ensure_setup()          — setup_done 플래그 확인, 없으면 boj setup 실행 [M9]
├── _validate_problem_id()  — 숫자, 양의 정수 검증
└── check_existing()        — 기존 폴더 존재 시 -f 없으면 ProblemExistsError [M3/M3a]

[Step 0] fetch_problem()    — BOJ HTML fetch → artifacts/problem.json [M1/M2/M5-M7]
    ├── _sanitize_title_slug()  — 제목 → 디렉터리 이름 (최대 30자)
    └── --image-mode 처리 (download/reference/skip)

[Step 1] generate_readme()  — problem.json → README.md

[Step 2] generate_spec()    — 에이전트 실행 → problem.spec.json [M10/M12]

[Step 3] generate_skeleton()— 에이전트 실행 → Solution + Parse [M8]

[Step 4] open_editor()      — --no-open 아니면 에디터 열기

[Step 5] cleanup_artifacts()— JSON 정리, 이미지 유지 [M13]
```

## edge-cases M1-M13 → 테스트 매핑

| ID | 케이스 | 상태 | 테스트 파일 | 테스트 메서드 |
|----|--------|------|-----------|-------------|
| M1 | BOJ 404 | ✅ | `test_client.py` | `test_404_raises_fetch_error` |
| M2 | 네트워크 실패 | ✅ | `test_make.py` | `TestFetchProblem.test_raises_when_html_fetch_fails` |
| M3 | 폴더 존재, -f 없음 | ✅ | `test_make.py` | `TestCheckExisting.test_raises_when_dir_exists_without_force` |
| M3a | 폴더 존재, -f 있음 | ✅ | `test_make.py` | `TestCheckExisting.test_allows_overwrite_when_force` |
| M4 | 쓰기 권한 없음 | ✅ | `test_make.py` | `TestFetchProblem.test_raises_on_permission_error` |
| M5 | image-mode reference | ✅ | `test_make.py` | `TestFetchProblem.test_image_mode_reference_keeps_urls` |
| M6 | 이미지 DL 실패 | ✅ | `test_make.py` | `TestFetchProblem.test_image_download_error_propagates` |
| M7 | 외부 도메인 이미지 | 🔮 | — | 이미지 도메인 필터 미구현 |
| M8 | 미지원 언어 | 🔮 | — | 언어 검증 로직 미구현 (generate_skeleton에 lang validation 없음) |
| M9 | setup_done 없음 | ✅ | `test_make.py` | `TestEnsureSetup.test_runs_setup_when_no_flag` |
| M10 | 에이전트 오류 | ✅ | `test_make.py` | `TestGenerateSpec.test_raises_on_agent_nonzero_exit` |
| M11 | README 자체검증 | 🔮 | — | 자체검증 로직 미구현 |
| M12 | spec 생성 실패 | ✅ | `test_make.py` | `TestGenerateSpec.test_raises_when_spec_file_missing` |
| M13 | --keep-artifacts | ✅ | `test_make.py` | `TestCleanupArtifacts.test_keeps_all_when_flag` |

## 함수별 단위 테스트 현황

| 함수 | 클래스 | 테스트 수 | 파일 |
|------|--------|----------|------|
| `_validate_problem_id` | `TestValidateProblemId` | 6 | `test_make.py` |
| `_sanitize_title_slug` | `TestSanitizeTitleSlug` | 5 | `test_make.py` |
| `ensure_setup` | `TestEnsureSetup` | 2 | `test_make.py` |
| `check_existing` | `TestCheckExisting` | 4 | `test_make.py` |
| `fetch_problem` | `TestFetchProblem` | 8 | `test_make.py` |
| `generate_readme` | `TestGenerateReadme` | 4 | `test_make.py` |
| `generate_spec` | `TestGenerateSpec` | 5 | `test_make.py` |
| `cleanup_artifacts` | `TestCleanupArtifacts` | 4 | `test_make.py` |

## 통합 테스트

| 클래스 | 테스트 수 | 파일 | 설명 |
|--------|----------|------|------|
| `TestMakePyIntegration` | 7 | `test_make_py.py` | 모킹 기반, happy path + M3/M3a/M9/M13 |

## 커버리지 범례

- ✅ 구현 완료 + 테스트 존재
- 🔮 기능 미구현 (향후 구현 시 테스트 추가)
