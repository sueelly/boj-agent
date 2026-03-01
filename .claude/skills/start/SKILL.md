---
name: start
description: GitHub 이슈 N번 작업 시작. 브랜치 생성, 이슈 컨텍스트 로드, 아키텍처 규칙 확인.
argument-hint: "<issue-number>"
tools:
  - Bash
  - Read
---

# 이슈 작업 시작 (/start)

Arguments: $ARGUMENTS

## 1. 입력 검증

이슈 번호가 숫자인지 확인. 아니면:
"사용법: /start <이슈번호>  예: /start 42"

## 2. 현재 Git 상태 확인

```bash
git status --short
git stash list
```

dirty working tree 있으면:
"미저장 변경사항이 있습니다. stash 하시겠습니까? (git stash push -m 'WIP before issue-N')"

## 3. 이슈 정보 가져오기

```bash
gh issue view $ARGUMENTS --json title,body,labels,milestone,assignees
```

이슈가 없으면 에러 출력 후 중단.

## 4. main 브랜치 최신화

```bash
git checkout main
git pull origin main
```

## 5. 브랜치 생성

브랜치명 결정 규칙:
- 이슈 레이블에 따라: `feat/`, `fix/`, `refactor/`, `docs/` 접두사
- 제목을 kebab-case로: 특수문자 제거, 공백→하이픈, 최대 30자
- 형식: `feat/issue-N-title-slug`

```bash
git checkout -b feat/issue-N-title-slug
```

## 6. 이슈 상태 업데이트

```bash
gh issue edit $ARGUMENTS --add-label "in-progress"
```

## 7. 작업 컨텍스트 요약 출력

```
╔══════════════════════════════════════╗
║    이슈 #N 작업 시작                  ║
╚══════════════════════════════════════╝
제목: [이슈 제목]
브랜치: feat/issue-N-title-slug
라벨: [라벨들]

📋 Acceptance Criteria:
  [이슈 본문에서 체크리스트 항목 추출]

🏗️ 아키텍처 규칙:
  [프로젝트 CLAUDE.md의 규칙 요약]
  [아키텍처 테스트 파일 있으면 위치 안내]

🔍 관련 파일 (참고):
  [이슈 키워드로 관련 파일 grep 결과]

→ 다음 단계: 개발 후 /commit, 완료 시 /done
```

## 8. 관련 파일 힌트 제공

이슈 제목의 키워드로 관련 파일 검색:
```bash
grep -rl "keyword" src/ --include="*.java" --include="*.py" --include="*.kt" 2>/dev/null | head -10
```
