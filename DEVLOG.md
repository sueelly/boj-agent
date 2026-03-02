# DEVLOG

## 2026-03-02 — refactor(make): 로컬 A→B→C 파이프라인 도입 [#13]

**브랜치**: `refactor/issue-13-boj-make-local-pipeline`
**PR**: #22

### 변경 요약

`boj make`의 문제 수집·정규화·스켈레톤 생성을 에이전트 단일 위임에서 결정론적 3단계 파이프라인으로 교체.

### 배경

기존 방식은 에이전트가 BOJ 웹 검색부터 README 생성, Parse 서명 추론까지 모두 담당했다. 같은 문제번호를 실행해도 결과가 달라지고, 스냅샷 테스트가 불가능했다.

### 도입한 아키텍처

**A. Problem Fetcher** (`src/lib/boj_client.py`)
- BOJ HTML → `artifacts/problem.json`
- Python stdlib (`html.parser`, `urllib.request`, `json`) — 외부 의존성 없음
- `BOJ_CLIENT_TEST_HTML` 환경변수로 HTTP 스킵, 로컬 픽스처 파싱 (테스트 격리)
- void 요소(`<br>`, `<img>` 등) depth 버그 방지를 위해 `_VOID_ELEMENTS` frozenset 사용

**B. Statement Normalizer** (`src/lib/boj_normalizer.py`)
- `problem.json` → `README.md` (순수 함수, 결정론적)
- 동일 입력 → 항상 동일 출력 (스냅샷 테스트 가능)

**C. IO Adapter Generator** (에이전트)
- `prompts/make-skeleton.md` 프롬프트로 역할 제한
- `Solution.<ext>`, `test/Parse.<ext>`, `test_cases.json`, `artifacts/signature_review.md` 생성
- raw stdin blob 금지 규칙 프롬프트에 명시

**Gate Check**
- `solve(String input/raw/stdin)` 패턴 감지 → Warning 출력 (exit 0)

**Execution Verify**
- 에이전트 실행 후 `boj run N` 호출 → 실패 시 Warning

**signature_review.md 아카이브**
- 기존 파일 있으면 `signature_review.YYYYMMDD_HHMMSS.bak`으로 보존 후 신규 생성

### 추가된 파일

| 파일 | 역할 |
|------|------|
| `src/lib/boj_client.py` | Problem Fetcher |
| `src/lib/boj_normalizer.py` | Statement Normalizer |
| `prompts/make-skeleton.md` | 스켈레톤 에이전트 프롬프트 |
| `prompts/signature-review-template.md` | 3역할 리뷰 템플릿 |
| `tests/fixtures/boj_client/99999.html` | HTML 픽스처 |
| `tests/fixtures/boj_client/99999-problem.json` | 기대 problem.json |
| `tests/fixtures/boj_client/99999-readme.md` | 기대 README.md |
| `tests/integration/test_boj_make.sh` | MK1-MK5 통합 테스트 |

### 검증 방법

```bash
./tests/run_tests.sh
# 결과: 8개 통과, 0개 실패 (MK1-MK5 포함)
```

### 트레이드오프

- 스켈레톤 생성(C단계)은 여전히 에이전트 의존 — A·B가 결정론적이므로 C 실패 시 재현 가능
- `boj_normalizer.py`의 HTML 렌더링 포맷이 변경되면 픽스처 재생성 필요
