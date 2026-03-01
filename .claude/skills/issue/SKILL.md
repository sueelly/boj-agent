---
name: issue
description: GitHub 이슈 생성. 타입(feat/bug/refactor)에 맞는 템플릿 자동 적용.
argument-hint: "feat|bug|refactor \"이슈 제목\""
tools:
  - Bash
---

# GitHub 이슈 생성 (/issue)

Arguments: $ARGUMENTS

## 1. 입력 파싱

$ARGUMENTS에서 타입과 제목 추출:
- `feat "사용자 인증 JWT 구현"` → type=feat, title="사용자 인증 JWT 구현"
- `bug "로그인 실패 시 500 오류"` → type=bug, title="로그인 실패 시 500 오류"
- `refactor "UserService 레이어 분리"` → type=refactor
- 타입 없으면 feat으로 기본값

## 2. 현재 레이블 및 마일스톤 확인

```bash
gh label list --json name -q '.[].name'
gh api repos/{owner}/{repo}/milestones --jq '.[].title' 2>/dev/null || echo ""
```

## 3. 이슈 본문 생성

**feat 타입**:
```markdown
## Summary
[사용자가 제공한 설명 또는 제목에서 추론]

## Acceptance Criteria
- [ ] [기준 1 - 구체적이고 테스트 가능]
- [ ] [기준 2]
- [ ] 관련 테스트 통과

## Technical Approach (optional)
[구현 방향 - 있으면 포함]

## Priority
- [ ] High (이번 스프린트 필수)
- [ ] Medium (이번 스프린트 목표)
- [ ] Low (다음 스프린트)
```

**bug 타입**:
```markdown
## Describe the Bug
[무엇이 잘못되었는가]

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behavior
[어떻게 동작해야 하는가]

## Actual Behavior
[실제로 어떻게 동작하는가]

## Environment
- Branch:
- Error/Stack trace:

## Fix Acceptance Criteria
- [ ] 원래 동작 복원
- [ ] 회귀 테스트 추가
```

**refactor 타입**:
```markdown
## What to Refactor
[어떤 코드/모듈을 변경하는가]

## Why
[기술 부채, 유지보수성, 성능, 또는 다른 기능 준비]

## Scope
- In scope: [포함 범위]
- Out of scope: [제외 범위]

## Acceptance Criteria
- [ ] 기존 테스트 모두 통과 (행동 변경 없음)
- [ ] [구체적 품질 지표 - 예: "메서드 길이 30줄 이하"]

## Risk Level
- [ ] Low - 독립된 변경
- [ ] Medium - 공유 코드 영향
- [ ] High - 여러 레이어 영향
```

## 4. 이슈 생성

```bash
gh issue create \
  --title "[feat/bug/refactor] [제목]" \
  --body "[생성된 본문]" \
  --label "[타입 라벨]"
```

성공 시 이슈 URL과 번호 출력:
"이슈 #N 생성됨: [URL]
→ /start N 으로 작업을 시작하세요"
