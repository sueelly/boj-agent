# 전체 워크플로우: 이슈 → PR → 머지

## 전체 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Issue 생성                         │
│              /issue feat|bug|refactor "제목"                 │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    작업 시작: /start N                       │
│  ① git pull origin main                                     │
│  ② 브랜치 생성: feat/issue-N-slug                           │
│  ③ 이슈 컨텍스트 로드 (Acceptance Criteria 출력)            │
│  ④ 이슈 라벨: in-progress                                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    개발 루프                                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   코드 작성 → /commit → 코드 작성 → /commit ...      │   │
│  │                                                     │   │
│  │   /commit은:                                        │   │
│  │   • 이슈 컨텍스트 파악 (gh issue view)              │   │
│  │   • diff 분석 → 논리 단위 추천                     │   │
│  │   • 커밋 메시지 자동 생성                          │   │
│  │   • 시크릿 스캔 → 문제 있으면 차단                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  중요 결정 시: /log 또는 자동 감지                   │   │
│  │  예: JWT vs Session 선택 → DECISIONS.md 자동 기록   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 /done (원스텝 완료)                          │
│                                                             │
│  Step 1: Risk Assessment                                    │
│    HIGH / MEDIUM / LOW 위험도 분류                          │
│                                                             │
│  Step 2: Pre-build Gate                                     │
│    브랜치 확인 + 시크릿 스캔                                │
│                                                             │
│  Step 3: Build Gate                ← 실패 시 즉시 중단     │
│    ./gradlew build (또는 mvn/npm/pip)                       │
│                                                             │
│  Step 4: Test Gate (Fresh)         ← 실패 시 즉시 중단     │
│    ./gradlew test (캐시 금지)                               │
│                                                             │
│  Step 5: Static Analysis           ← 경고만 (차단 안 함)   │
│    TODO/FIXME, printStackTrace 스캔                         │
│                                                             │
│  Step 6: Automated Review          ← CRITICAL 발견 시 중단 │
│    code-reviewer 에이전트 7점 체크리스트                    │
│                                                             │
│  Step 7: Observable Proof                                   │
│    VERIFICATION REPORT 생성                                 │
│                                                             │
│  → git push -u origin HEAD                                  │
│  → gh pr create (템플릿 자동 채움)                          │
│  → 이슈 라벨: in-progress → review                         │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  GitHub PR (자동 리뷰)                       │
│                                                             │
│  claude.yml 트리거:                                         │
│  • PR 오픈 시 → claude code-review 자동 실행                │
│  • @claude 멘션 → 요청 처리                                 │
│                                                             │
│  ci.yml 트리거:                                             │
│  • 빌드 + 테스트 + 아키텍처 테스트                         │
│  • 보안 스캔 (시크릿 하드코딩)                             │
│  • JUnit XML → PR 코멘트로 결과 표시                       │
│  (선택) sonarcloud.yml: PR 시 코드 품질 검사               │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      코드리뷰                               │
│                                                             │
│  리뷰어가 /review [PR번호] 실행 또는 수동 리뷰             │
│                                                             │
│  CRITICAL → 머지 차단 + 수정 요청                          │
│  MINOR    → 머지 가능 + 수정 권장                          │
│  PASS     → Approve                                         │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   main 머지 + 이슈 Close                     │
│                                                             │
│  "Closes #N" → PR 머지 시 이슈 자동 Close                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 브랜치 전략

```
main ──────────────────────────────────────────► (배포)
  │
  ├─ feat/issue-42-jwt-refresh ──────────► PR #45 → 머지
  │
  ├─ fix/issue-43-token-expiry ──────────► PR #46 → 머지
  │
  └─ refactor/issue-44-service-layer ───► PR #47 → 머지
```

**규칙**:
- main에 직접 커밋 금지 (pre-tool-use hook이 차단)
- 머지 커밋 금지 → feature 브랜치는 rebase 사용
- force push 금지

---

## 커밋 흐름 (feature 브랜치 내)

```
feat/issue-42-jwt-refresh
│
├─ feat(auth): add JWT token generation [#42]
│
├─ test(auth): add unit tests for JWT generation [#42]
│
├─ feat(auth): add refresh token rotation [#42]
│
└─ test(auth): add integration tests for token refresh [#42]
```

**커밋 형식**: `type(scope): imperative-verb noun [#N]`
- type: feat | fix | refactor | docs | test | chore | perf
- scope: 변경된 주요 모듈 (auth, queue, chat 등)
- 메시지: 명령형 현재형 ("add" not "added")

---

## 상황별 대응

### "내가 main에 있는데 작업을 시작하고 싶다"
```bash
/start 42
# 자동으로 main pull + 브랜치 생성
```

### "커밋하려는데 어떤 파일을 포함해야 할지 모르겠다"
```bash
/commit
# diff 분석 후 논리 단위 추천
```

### "verify에서 테스트가 실패한다"
```bash
# 실패한 테스트 확인 후 수정
./gradlew test --tests "*FailingTest" --info
# 수정 후 다시 /verify
```

### "verify에서 code-reviewer가 CRITICAL을 발견했다"
```bash
# CRITICAL 항목 수정 후 /verify 재실행
# MINOR는 수정 권장이지만 차단하지 않음
```

### "이미 PR이 있는데 추가 수정이 필요하다"
```bash
# 코드 수정
/commit  # 추가 커밋
git push  # 기존 PR에 반영됨
```

### "다른 사람의 PR을 리뷰해야 한다"
```bash
/review 45  # PR 번호
# code-reviewer 에이전트가 7점 체크리스트로 분석
```

---

## 자동화 구성 요소

| 구성요소 | 위치 | 역할 |
|---------|------|------|
| pre-tool-use hook | `.claude/hooks/pre-tool-use.sh` | 위험 명령어 실시간 차단 |
| post-edit hook | `.claude/hooks/post-edit.sh` | 파일 수정 후 즉시 경고 |
| stop hook | `.claude/hooks/stop.sh` | 세션 종료 요약 + 결정 기록 |
| code-reviewer | `.claude/agents/code-reviewer.md` | 읽기전용 7점 체크리스트 |
| test-writer | `.claude/agents/test-writer.md` | 테스트 자동 생성 |
| ci.yml | GitHub Actions | 빌드 + 테스트 + 보안 스캔 |
| sonarcloud.yml | GitHub Actions | (선택) PR 품질 검사 |
