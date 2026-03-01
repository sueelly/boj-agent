---
name: review
description: 현재 PR 또는 지정 PR을 code-reviewer 에이전트로 리뷰. 읽기전용 - 절대 코드 수정 안 함.
argument-hint: "[PR번호] - 생략 시 현재 브랜치 PR"
tools:
  - Bash
  - Read
disallowedTools:
  - Write
  - Edit
  - MultiEdit
---

# PR 코드리뷰 (/review)

Arguments: $ARGUMENTS

## 1. PR 정보 수집

```bash
# PR 번호 결정
if [ -n "$ARGUMENTS" ]; then
  PR_NUM="$ARGUMENTS"
else
  PR_NUM=$(gh pr view --json number --jq '.number' 2>/dev/null)
fi

# PR 정보
gh pr view $PR_NUM --json title,body,files,additions,deletions,baseRefName

# diff 가져오기
gh pr diff $PR_NUM

# 연결된 이슈 정보
ISSUE_NUM=$(gh pr view $PR_NUM --json body --jq '.body' | grep -oE '#[0-9]+' | head -1 | tr -d '#')
gh issue view $ISSUE_NUM --json title,body 2>/dev/null || true
```

## 2. 위험도 평가

변경 파일 목록과 크기 분석:
- +1000줄 이상 변경: "대규모 변경 - 상세 리뷰 필요"
- 보안/인증 파일 포함: "HIGH RISK - 보안 관점 집중"
- 테스트 파일만: "LOW RISK"

## 3. code-reviewer 에이전트 호출

다음 정보를 code-reviewer에게 전달:
- PR diff 전체
- 이슈 Acceptance Criteria
- 프로젝트 CLAUDE.md의 아키텍처 규칙
- 위험도 평가 결과

code-reviewer는 7점 체크리스트로 분석:
1. 정확성 (이슈 요구사항 충족)
2. 테스트 커버리지
3. 에러 처리
4. 보안
5. API 계약 유지
6. 아키텍처 규칙 준수
7. 코드 품질 (복잡도, 네이밍)

## 4. 결과 출력 및 GitHub 코멘트

리뷰 결과:
```
╔═══════════════════════════════════════╗
║    PR #N 코드리뷰 결과                 ║
╚═══════════════════════════════════════╝

CRITICAL (머지 차단):
  ❌ [file:line] 내용

MINOR (수정 권장):
  ⚠️ [file:line] 내용

SUGGESTION (선택):
  💡 내용

통과 항목: [깨끗한 항목들]

최종 판정: [APPROVED / CHANGES_REQUESTED]
```

GitHub PR에 리뷰 코멘트 추가:
```bash
gh pr review $PR_NUM \
  --[approve|request-changes] \
  --body "[리뷰 결과]"
```

CRITICAL 있으면: `--request-changes`
없으면: `--approve`
