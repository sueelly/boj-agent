---
name: start
description: GitHub 이슈 N번 작업 시작. 브랜치 생성, worktree 격리, 이슈 컨텍스트 로드, 아키텍처 규칙 확인.
argument-hint: "<issue-number> [--no-worktree]"
tools:
  - Bash
  - Read
---

# 이슈 작업 시작 (/start)

Arguments: $ARGUMENTS

## 1. 입력 검증

인수에서 이슈 번호와 플래그 파싱:
- 첫 번째 숫자 인수 → 이슈 번호
- `--no-worktree` → worktree 생성 없이 기존 방식(브랜치만 생성)

이슈 번호가 없으면:
"사용법: /start <이슈번호> [--no-worktree]  예: /start 42"

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
git fetch origin main
```

> 다른 worktree에서 main이 checkout 되어 있을 수 있으므로 `git checkout main` 대신 `git fetch`만 수행.

## 5. 브랜치 생성

브랜치명 결정 규칙:
- 이슈 레이블에 따라: `feat/`, `fix/`, `refactor/`, `docs/` 접두사
- 제목을 kebab-case로: 특수문자 제거, 공백→하이픈, 최대 30자
- 형식: `feat/issue-N-title-slug`

```bash
git branch feat/issue-N-title-slug origin/main
```

## 6. Worktree 생성 (기본 동작)

**`--no-worktree` 플래그가 없으면 (기본)**:

### 6a. 기존 worktree 확인

```bash
git worktree list | grep "issue-N"
```

이미 해당 이슈의 worktree가 존재하면 재사용:
"기존 worktree를 발견했습니다: [경로]. 해당 worktree를 사용합니다."

### 6b. 새 worktree 생성

```bash
git worktree add .claude/worktrees/issue-N-slug feat/issue-N-title-slug
```

- worktree 경로: `.claude/worktrees/issue-N-slug` (리포지토리 루트 기준)
- 브랜치는 Step 5에서 생성한 것을 사용

### 6c. 작업 디렉터리 이동 안내

worktree가 생성되면 사용자에게 안내:
```
Worktree 생성 완료: .claude/worktrees/issue-N-slug
이후 작업은 해당 worktree에서 진행하세요.
```

**`--no-worktree` 플래그가 있으면**:

기존 방식으로 브랜치만 checkout:
```bash
git checkout feat/issue-N-title-slug
```

## 7. 이슈 상태 업데이트

```bash
gh issue edit $ISSUE_NUM --add-label "in-progress" 2>/dev/null || true
```

> `in-progress` 라벨이 없으면 무시.

## 8. 작업 컨텍스트 요약 출력

```
╔══════════════════════════════════════╗
║    이슈 #N 작업 시작                  ║
╚══════════════════════════════════╝
제목: [이슈 제목]
브랜치: feat/issue-N-title-slug
Worktree: .claude/worktrees/issue-N-slug
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

> `--no-worktree` 모드이면 `Worktree:` 줄은 생략.

## 9. 관련 파일 힌트 제공

이슈 제목의 키워드로 관련 파일 검색:
```bash
grep -rl "keyword" src/ --include="*.java" --include="*.py" --include="*.kt" 2>/dev/null | head -10
```
