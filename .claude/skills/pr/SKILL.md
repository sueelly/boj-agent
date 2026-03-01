---
name: pr
description: 현재 브랜치로 PR 생성. verify 파이프라인 통과 필수. PR 템플릿 자동 채움.
tools:
  - Bash
  - Read
---

# PR 생성 (/pr)

Arguments: $ARGUMENTS

## 1. 전제 조건 확인

```bash
BRANCH=$(git branch --show-current)
ISSUE_NUM=$(echo "$BRANCH" | grep -oE 'issue-[0-9]+' | grep -oE '[0-9]+' || echo "")
```

- main/master 브랜치이면 중단
- 이미 PR 있으면 URL 출력 후 중단: `gh pr view --json url`

## 2. 7단계 검증 파이프라인

/verify 스킬 실행. BLOCKED 시 중단.

## 3. Push

```bash
git push -u origin HEAD
```

## 4. PR 메타데이터 수집

```bash
gh issue view $ISSUE_NUM --json title,body,labels 2>/dev/null
git log main..HEAD --oneline
git diff main..HEAD --stat
```

## 5. PR 생성

PR 제목 형식: `<type>(<scope>): <이슈 제목> [#N]`

```bash
gh pr create \
  --title "[생성된 제목]" \
  --body "[PR 본문]" \
  --base main
```

성공 시 PR URL 출력.

## 6. 이슈 라벨 업데이트

```bash
gh issue edit $ISSUE_NUM --remove-label "in-progress" --add-label "review"
```
