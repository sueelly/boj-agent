# Prompts — 에이전트 지시문

이 폴더는 **어떤 AI/에이전트를 쓰든** 동일한 워크플로우를 쓰기 위한 **지시문**을 담습니다.

## 설정·템플릿 참조

- **Config**: 생성할 **언어**와 경로는 설정을 따릅니다. `~/.config/boj/lang` 또는 환경변수 `BOJ_LANG` (기본값: `java`).
- **Templates**: `templates/<lang>/` 에 언어별 테스트 러너와 인터페이스 계약이 있음. 생성된 코드가 테스트 러너와 호환되려면 해당 계약을 준수해야 합니다.

## 파일 역할

| 파일 | 사용처 | 용도 |
|------|--------|------|
| **make-skeleton.md** | `src/commands/make.sh` | problem.json 기반 스켈레톤(Solution, Parse, test_cases.json) 생성 + 서명 리뷰 루프 |
| **review.md** | `src/commands/review.sh` | Solution 분석 → submit/REVIEW.md 생성 (내 코드 분석, 대표 풀이, 다음 단계) |

## 사용 방법

- **CLI(boj)**: `boj make 4949` 시 make.sh가 problem.json을 가져오고 README.md를 생성한 뒤, make-skeleton.md에 변수를 치환하여 에이전트에 전달. `boj review 4949` 시 review.md를 에이전트에 전달.
- **수동**: 사용 중인 에이전트의 시스템 프롬프트에 해당 md 내용을 붙여넣어 사용.

## 규칙

- 지시문은 **플랫폼 중립**으로 작성 (특정 에이전트 이름 회피).
- make-skeleton / review 역할이 섞이지 않도록 파일별로 유지.
