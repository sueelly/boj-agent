# 스마트 커밋 (Smart Commit)

Arguments: $ARGUMENTS

## 1. 브랜치 안전 확인

```bash
BRANCH=$(git branch --show-current)
```

main 또는 master 브랜치이면 즉시 중단:
"BLOCKED: main/master 브랜치에서 직접 커밋 불가. /start <N>으로 작업 브랜치를 먼저 생성하세요."

## 2. 현재 작업 컨텍스트 파악

```bash
# 브랜치에서 이슈 번호 추출 (feat/issue-42-xxx → 42)
ISSUE_NUM=$(git branch --show-current | grep -oE 'issue-[0-9]+' | grep -oE '[0-9]+' || echo "")

# 이슈 내용 파악
gh issue view $ISSUE_NUM --json title,body 2>/dev/null || echo "이슈를 찾을 수 없음"

# 이미 커밋된 내용 확인
git log main..HEAD --oneline 2>/dev/null || echo "(첫 번째 커밋)"

# 전체 변경사항 통계
git diff --stat 2>/dev/null
git diff --staged --stat 2>/dev/null
```

## 3. 변경사항 분석 및 커밋 단위 추천

staged와 unstaged 변경사항을 모두 분석:

```bash
git diff --name-only          # unstaged
git diff --staged --name-only  # staged
```

파일을 논리적 단위로 그룹핑:
- **구현 + 테스트 쌍**: `UserService.java` + `UserServiceTest.java` → 하나의 커밋
- **독립적 리팩토링**: 별도 커밋 권장
- **설정 변경**: `application.yml`, `build.gradle` → 별도 커밋
- **문서 변경**: `.md` 파일 → 별도 `docs:` 커밋

2개 이상 논리 단위로 나뉠 경우 분리 제안:
```
다음 N개 커밋으로 나누는 것을 추천합니다:
1. feat(auth): add JWT token generation [#42]
   → [TokenService.java, TokenServiceTest.java]
2. test(auth): add integration tests for auth flow [#42]
   → [AuthIntegrationTest.java]
```

## 4. 시크릿 스캔

staged 파일 검사:
```bash
git diff --staged | grep -E "(password|secret|api_key)\s*=\s*['\"][^$\{\(]"
```
발견 시 즉시 중단. 해당 라인 출력.

## 5. 커밋 메시지 결정

**$ARGUMENTS가 제공된 경우**: 형식 검증만 수행
**$ARGUMENTS가 없는 경우**: 이슈 내용 + diff에서 메시지 자동 추론

메시지 형식 검증:
- 패턴: `^(feat|fix|refactor|docs|test|chore|perf)(\(.+\))?: .{10,72}$`
- scope: 변경된 주요 모듈/패키지에서 추론
- 이슈번호 `[#N]` 자동 추가 (없으면)
- 메시지는 명령형 현재형 (add, fix, update)

## 6. 최종 확인 및 실행

추천 커밋 메시지와 staged 파일 목록 보여주기:
```
커밋 예정:
  메시지: feat(auth): add JWT token generation [#42]
  파일: UserService.java, UserServiceTest.java

계속할까요? (수정하려면 원하는 메시지 입력)
```

확인 후 실행:
```bash
git commit -m "feat(auth): add JWT token generation [#42]"
```

성공 시: "커밋 완료. /done 으로 PR을 생성하거나 계속 개발하세요."
