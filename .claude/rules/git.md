# Git 워크플로우 규칙

## 브랜치 네이밍
- 기능: `feat/issue-N-short-description`
- 버그픽스: `fix/issue-N-short-description`
- 리팩토링: `refactor/issue-N-short-description`
- 문서: `docs/issue-N-short-description`
- slug는 kebab-case, 최대 30자

## 커밋 규칙
- 형식: `<type>(<scope>): <imperative-present-tense> [#N]`
- type: feat | fix | refactor | docs | test | chore | perf
- scope: 변경된 주요 모듈/패키지 (예: auth, queue, chat)
- 메시지: 명령형 현재형 (add, fix, update — 과거형 X)
- 이슈번호 [#N] 필수 (브랜치명에서 자동 추출)
- 예시: `feat(auth): add JWT refresh token rotation [#42]`

## 금지 사항
- `git add -A` 또는 `git add .` — 특정 파일 명시 권장
- 머지 커밋 in feature 브랜치 — rebase 사용
- `git push --force` — 히스토리 파괴 금지
- main/master 직접 push — PR 필수

## 커밋 전 체크리스트
1. `git diff --staged` 로 변경사항 확인
2. 의도치 않은 파일 포함 여부 확인
3. TODO/FIXME/하드코딩 시크릿 없는지 확인
4. 이슈번호가 메시지에 포함되었는지 확인

## Stash 정책
- 작업 전환 시 stash 활용
- stash 목록 주기적 정리: `git stash list`
- stash에 설명 추가: `git stash push -m "설명"`
