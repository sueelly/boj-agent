---
name: done
description: 이슈 완료 원스텝: verify(7단계) → 미커밋 처리 → push → PR 생성 → 이슈 라벨 업데이트
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
  --add-label "review"
```

## 7. 완료 요약

```
╔══════════════════════════════════════╗
║    /done 완료!                        ║
╚══════════════════════════════════════╝
이슈: #N [제목]
PR: [PR URL]
브랜치: [브랜치명]
검증: PASS (7/7 단계)

→ @claude 멘션 또는 /review 로 코드리뷰를 진행하세요
```
