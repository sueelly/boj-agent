# make 테스트 커버리지 (Python)

> `src/core/make.py` + `src/cli/boj_make.py` 기준.
> 참조: [COMMAND-SPEC.md](../../../COMMAND-SPEC.md), [edge-cases.md](../edge-cases.md) M1-M16

## 파이프라인 흐름

```
사전조건
├── setup_done 가드          — 디스패처(src/boj)에서 공통 처리 (C1) [M9]
├── _validate_problem_id()  — 숫자, 양의 정수 검증
└── check_existing()        — 기존 폴더 존재 시 -f 없으면 ProblemExistsError [M3/M3a]

[Step 0] fetch_problem()    — BOJ HTML fetch → artifacts/problem.json [M1/M2/M5-M7]
    ├── _sanitize_title_slug()  — 제목 → 디렉터리 이름 (최대 30자)
    └── --image-mode 처리 (download/reference/skip)

[Step 1] generate_readme()  — problem.json → README.md

[Step 2] open_editor()      — README 직후 선오픈 (spec 이전) [M14/M15/M16]
    ├── --no-open이면 스킵
    └── 에디터 미설정이면 스킵

[Step 3] generate_spec()    — 에이전트 실행 → problem.spec.json [M10/M12]

[Step 4] generate_skeleton()— 에이전트 stdout JSON manifest → 파일 생성 [M8/M14-M16]
    ├── _get_lang_meta()        — languages.json에서 ext/supports_parse 추출
    ├── template_vars 치환      — {{LANG}}, {{EXT}} 등 플레이스홀더 → 실제 값
    ├── _extract_json_manifest()— stdout에서 JSON 추출 (3단계 파싱)
    ├── _write_skeleton_files() — manifest["files"] → 파일 쓰기
    └── _generate_test_cases_fallback() — samples → test_cases.json (에이전트 실패 시)
[Step 5] cleanup_artifacts()— 화이트리스트 기반 정리 [M13/M13a]
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
| M9 | setup_done 없음 | ✅ | `test_setup_guard.py` | `TestSetupGuard.test_shows_setup_message_when_no_setup_done` |
| M10 | 에이전트 exit nonzero + stderr | ✅ | `test_run_agent.py` | `TestGenerateSpecErrorFlow.test_agent_stderr_surfaced_in_error` |
| M10a | 에이전트 exit 0 + stdout 있음 | ✅ | `test_run_agent.py` | `TestGenerateSpecErrorFlow.test_agent_success_but_no_spec_shows_stdout` |
| M10b | 에이전트 exit nonzero + stderr 비어있음 | ✅ | `test_run_agent.py` | `TestGenerateSpecErrorFlow.test_agent_fails_but_empty_stderr_shows_returncode` |
| M10c | 에이전트 exit 0 + 출력 없음 | ✅ | `test_run_agent.py` | `TestGenerateSpecErrorFlow.test_agent_success_no_output_no_spec_gives_base_message` |
| M11 | README 자체검증 | 🔮 | — | 자체검증 로직 미구현 |
| M12 | spec 생성 실패 | ✅ | `test_make.py` | `TestGenerateSpec.test_raises_when_spec_file_missing` |
| M13 | --keep-artifacts | ✅ | `test_make.py` | `TestCleanupArtifacts.test_keeps_all_when_flag` |
| M13a | 화이트리스트 정리 | ✅ | `test_make.py` | `TestCleanupArtifacts.test_keeps_whitelisted_deletes_rest` |
| M14 | skeleton stdout JSON manifest | ✅ | `test_make.py` | `TestGenerateSkeleton.test_writes_files_from_agent_stdout` |
| M14a | skeleton 빈 stdout / 비-JSON | ✅ | `test_make.py` | `TestWriteSkeletonFiles.test_returns_false_on_empty_stdout` |
| M14b | skeleton 에이전트 실패 + fallback | ✅ | `test_make.py` | `TestGenerateSkeleton.test_fallback_test_cases_when_agent_fails` |
| M15 | test_cases.json fallback | ✅ | `test_make.py` | `TestGenerateTestCasesFallback.test_generates_from_samples` |
| M15a | samples 없을 때 fallback 스킵 | ✅ | `test_make.py` | `TestGenerateTestCasesFallback.test_skips_when_no_samples` |
| M16 | template_vars 치환 | ✅ | `test_make.py` | `TestGenerateSkeleton.test_template_vars_substituted` |
| M17 | 에디터 선오픈 (README 직후) | ✅ | `test_make.py` | `TestRunPipelineCallOrder.test_open_editor_called_after_readme_before_spec` |
| M18 | --no-open 이면 선오픈 없음 | ✅ | `test_make.py` | `TestRunPipelineCallOrder.test_no_open_skips_editor_entirely` |
| M19 | 에디터 미설정 이면 선오픈 없음 | ✅ | `test_make.py` | `TestRunPipelineCallOrder.test_no_editor_config_skips_early_open` |
| M20 | PyPI 리소스 접근 | ✅ | `test_resources.py` | `TestResourceAccess.*`, `TestResourceAccessIsolated.*` |

## 함수별 단위 테스트 현황

| 함수 | 클래스 | 테스트 수 | 파일 |
|------|--------|----------|------|
| `_validate_problem_id` | `TestValidateProblemId` | 6 | `test_make.py` |
| `_sanitize_title_slug` | `TestSanitizeTitleSlug` | 5 | `test_make.py` |
| `check_existing` | `TestCheckExisting` | 4 | `test_make.py` |
| `fetch_problem` | `TestFetchProblem` | 8 | `test_make.py` |
| `generate_readme` | `TestGenerateReadme` | 4 | `test_make.py` |
| `generate_spec` | `TestGenerateSpec` | 5 | `test_make.py` |
| `cleanup_artifacts` | `TestCleanupArtifacts` | 6 | `test_make.py` |
| `_get_lang_meta` | `TestGetLangMeta` | 4 | `test_make.py` |
| `_extract_json_manifest` | `TestExtractJsonManifest` | 5 | `test_make.py` |
| `_write_skeleton_files` | `TestWriteSkeletonFiles` | 3 | `test_make.py` |
| `_generate_test_cases_fallback` | `TestGenerateTestCasesFallback` | 3 | `test_make.py` |
| `generate_skeleton` | `TestGenerateSkeleton` | 3 | `test_make.py` |
| `run_agent` | `TestRunAgentCommand` | 4 | `test_run_agent.py` |
| `run_agent` | `TestRunAgentErrorHandling` | 2 | `test_run_agent.py` |
| `generate_spec` (에러 흐름) | `TestGenerateSpecErrorFlow` | 6 | `test_run_agent.py` |

## 통합 테스트

| 클래스 | 테스트 수 | 파일 | 설명 |
|--------|----------|------|------|
| `TestMakePyIntegration` | 7 | `test_make_py.py` | 모킹 기반, happy path + M3/M3a/M9/M13 |

## 커버리지 범례

- ✅ 구현 완료 + 테스트 존재
- 🔮 기능 미구현 (향후 구현 시 테스트 추가)
