---
name: done
description: 이슈 완료 원스텝: verify(7단계) → 미커밋 처리 → push → PR 생성 → 이슈 라벨 업데이트 → worktree 정리
tools:
  - Bash
  - Read
---

# 이슈 완료 (/done)

Arguments: $ARGUMENTS

## 1. 브랜치 확인

```bash
BRANCH=$(git branch --show-current)
ISSUE_NUM=$(echo "$BRANCH" | grep -oE 'issue-[0-9]+' | grep -oE '[0-9]+' || echo "")
```

main/master이면 중단. 이슈 번호 추출 실패 시 경고.

## 2. 7단계 검증 파이프라인 실행

/verify 스킬의 모든 단계를 실행.
BLOCKED 결과 시 전체 중단:
```
/done 실패: [실패 단계] 수정 후 재실행하세요.
```

## 3. 미커밋 변경사항 처리

```bash
git status --short
```

변경사항 있으면 /commit 스킬 흐름 실행 (커밋 메시지 추천 포함).

## 4. 브랜치 Push

```bash
git push -u origin HEAD
```

## 5. PR 생성

이슈 정보 가져오기:
```bash
gh issue view $ISSUE_NUM --json title,body,labels
git log main..HEAD --oneline
git diff main..HEAD --stat
```

PR 본문 자동 생성:
```
## Related Issue
Closes #[N]

## Type of Change
- [x] [이슈 라벨 기반 자동 선택]

## Summary
[이슈 제목 + 구현한 내용 요약]

## Changes Made
[git log --oneline 기반 변경사항]

## Test Evidence
[/verify Step 7 출력 결과 붙여넣기]

## Checklist
- [x] Commit messages follow conventional commits
- [x] Tests pass (/verify 통과)
- [x] No hardcoded secrets
- [x] No TODO/FIXME in changed files
```

```bash
gh pr create \
  --title "feat(scope): [이슈 제목] [#N]" \
  --body "[생성된 PR 본문]" \
  --base main
```

## 6. 이슈 상태 업데이트

```bash
gh issue edit $ISSUE_NUM \
  --remove-label "in-progress" \
  --add-label "review" 2>/dev/null || true
```

## 7. Worktree 정리 안내

현재 worktree에서 작업 중인지 확인:
```bash
git worktree list | grep "$(pwd)"
```

worktree 내에서 작업 중이면 정리 안내:
```
현재 worktree에서 작업 중입니다: [worktree 경로]
PR이 머지된 후 다음 명령어로 정리할 수 있습니다:

  git worktree remove [worktree 경로]
  git branch -d [브랜치명]

지금 worktree를 제거하시겠습니까? (keep/remove)
```

- **keep**: worktree 유지 (PR 리뷰 중 추가 수정 가능)
- **remove**: worktree 및 브랜치 즉시 삭제

> worktree가 아닌 일반 브랜치에서 작업 중이면 이 단계를 건너뜀.

## 8. 완료 요약

```
╔══════════════════════════════════════╗
║    /done 완료!                        ║
╚══════════════════════════════════════╝
이슈: #N [제목]
PR: [PR URL]
브랜치: [브랜치명]
Worktree: [worktree 경로 또는 "N/A"]
검증: PASS (7/7 단계)

→ @claude 멘션 또는 /review 로 코드리뷰를 진행하세요
```
