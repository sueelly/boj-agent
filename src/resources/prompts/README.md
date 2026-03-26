# Prompts — 에이전트 지시문

이 폴더는 **어떤 AI/에이전트를 쓰든** 동일한 워크플로우를 쓰기 위한 **지시문**을 담습니다.

## 설정·템플릿 참조

- **Config**: 생성할 **언어**와 경로는 설정을 따릅니다. `~/.config/boj/lang` 또는 환경변수 `BOJ_LANG` (기본값: `java`).
- **Templates**: `templates/<lang>/` 에 언어별 테스트 러너와 인터페이스 계약이 있음. 생성된 코드가 테스트 러너와 호환되려면 해당 계약을 준수해야 합니다.

## 파일 역할

| 파일 | 사용처 | 용도 |
|------|--------|------|
| **make-spec.md** | `boj make` Step 2 | README + problem.json → problem.spec.json 생성. 에이전트 실행 시 전달되며 `reference/spec/` 참조. |
| **make-skeleton.md** | `boj make` Step 3, `src/commands/make.sh` | problem.spec.json 기반 Solution·Parse·test_cases.json 생성. |
| **make-parse-and-tests.md** | (미사용) | **[deprecated]** make 파이프라인에서 사용하지 않음. Parse·테스트 생성은 make-skeleton으로 통합됨. 참고용으로만 유지. |
| **review.md** | `src/commands/review.sh` | Solution 분석 → submit/REVIEW.md 생성 (내 코드 분석, 대표 풀이, 다음 단계). |

## 사용 방법

- **CLI(boj)**: `boj make <문제번호>` 시 Step 2에서 make-spec.md, Step 3에서 make-skeleton.md가 에이전트에 전달됨. `boj review <문제번호>` 시 review.md를 에이전트에 전달.
- **수동**: 사용 중인 에이전트의 시스템 프롬프트에 해당 md 내용을 붙여넣어 사용.

## 규칙

- 지시문은 **플랫폼 중립**으로 작성 (특정 에이전트 이름 회피).
- make-spec / make-skeleton / review 역할이 섞이지 않도록 파일별로 유지.
