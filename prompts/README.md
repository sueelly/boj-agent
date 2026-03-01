# Prompts — 에이전트 독립 지시문

이 폴더는 **어떤 AI/에이전트를 쓰든** 동일한 워크플로우(문제 환경 생성, 제출용 코드, 리뷰)를 쓰기 위한 **지시문**을 담습니다. Cursor 전용이 아닙니다.

## 설정·템플릿 참조

- **Config**: 생성할 **언어**와 경로는 설정을 따릅니다. `~/.config/boj/lang` 또는 환경변수 `BOJ_LANG` (기본값: `java`). 다른 설정은 `~/.config/boj/` 참고.
- **Templates**: 프롬프트에서 “Parse는 다음 계약을 구현해야 한다”고만 쓰고, **실제 시그니처·파일 위치**는 프로젝트의 `templates/<lang>/` 를 참고하도록 하세요. 생성된 코드가 테스트 러너와 호환되려면 해당 언어의 `templates/<lang>/` 에 있는 인터페이스(또는 주석으로 적힌 계약)와 일치해야 합니다. 템플릿은 “공통 코드”(테스트 러너 + 계약)만 두고, 문제별로 생성하는 건 Solution / Parse / test_cases.json 입니다.

## 파일 역할

| 파일 | 용도 |
|------|------|
| **make-environment.md** | "백준 N번 문제 풀이 환경 만들어줘" 요청 시 사용. 폴더 구조, README/Solution/Parse/test_cases 생성 규칙, 웹 검색으로 문제 내용 확인 등 |
| **submit.md** | "제출해줘" 요청 시 사용. Solution → 제출용 코드(Submit.*) 생성 규칙 |
| **review.md** | "리뷰해줘" 요청 시 사용. Solution 분석, REVIEW.md 형식(내 코드 분석, 대표 풀이, 다음 단계) |

## 사용 방법

- **CLI(boj)**: `boj make 4949` / `boj review 4949` 시 설정된 에이전트에 해당 md 내용 + 요청 문장을 전달하도록 구현됨.
- **수동**: 사용 중인 에이전트(Cursor, Claude, ChatGPT, aider 등)의 시스템 프롬프트 또는 첫 사용자 메시지에 해당 md 내용을 붙여넣은 뒤, "백준 4949번 문제 풀이 환경 만들어줘"처럼 요청.
- **Cursor**: 이 레포를 Cursor로 열고, `.cursor/rules/`에서 이 prompts 폴더를 참조하는 룰을 두면, 채팅 시 자동으로 같은 규칙이 적용되도록 할 수 있음.

## 규칙

- 지시문은 **플랫폼 중립**으로 작성 (Cursor, agent CLI 등 구체 이름 회피).
- 수정 시 make-environment / submit / review 역할이 섞이지 않도록 파일별로 유지.
