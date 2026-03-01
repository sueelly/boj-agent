# 사용 가이드 — 무엇을, 언제, 어떻게

## 빠른 참조: 슬래시 커맨드

| 커맨드 | 언제 | 무엇을 |
|--------|------|--------|
| `/issue feat "기능명"` | 새 기능 시작 전 | GitHub 이슈 생성 (feat 템플릿) |
| `/issue bug "버그명"` | 버그 발견 시 | GitHub 이슈 생성 (bug 템플릿) |
| `/start 42` | 이슈 작업 시작 시 | 브랜치 생성 + 이슈 컨텍스트 로드 |
| `/commit` | 논리적 단위 완성 시 | 스마트 커밋 (단위 추천 + 형식 검증) |
| `/verify` | PR 전 | 7단계 검증 파이프라인 |
| `/done` | 이슈 완료 시 | verify + commit + push + PR 원스텝 |
| `/pr` | PR만 만들 때 | verify 포함 PR 생성 |
| `/review` | 리뷰 요청받을 때 | code-reviewer 에이전트 리뷰 |
| `/test UserService.java` | 테스트 없는 코드 있을 때 | 테스트 자동 생성 |
| `/log "JWT 선택"` | 중요 결정 후 | DECISIONS.md에 기록 |
| `/arch-setup` | 새 프로젝트 시작 시 | 아키텍처 테스트 자동 생성 |

---

## 일일 워크플로우

### 일반적인 기능 개발 흐름
```
1. /issue feat "JWT 리프레시 토큰 구현"
   → GitHub 이슈 #42 생성됨

2. /start 42
   → feat/issue-42-jwt-refresh-token 브랜치 생성
   → 이슈 Acceptance Criteria 출력
   → 관련 파일 목록 출력

3. [개발]
   → 코드 작성
   → 중간 중간 /commit 으로 논리 단위 커밋

4. /commit
   → diff 분석 후 커밋 단위 추천
   → 메시지 형식 자동 생성: "feat(auth): add JWT refresh token rotation [#42]"

5. /done
   → 7단계 verify 자동 실행
   → PR 생성 (이슈 내용 자동 채움)
   → 이슈 라벨: "in-progress" → "review"
```

### 버그 수정 흐름
```
1. /issue bug "로그인 후 토큰이 만료되지 않는 버그"
   → GitHub 이슈 #43 생성됨

2. /start 43
   → fix/issue-43-token-expiry 브랜치 생성

3. [버그 재현 → 실패 테스트 작성 → 수정 → 테스트 통과]

4. /done
   → 전체 검증 + PR 생성
```

---

## 각 커맨드 상세

### `/start <N>` — 이슈 작업 시작
**입력**: 이슈 번호
**출력**:
- 브랜치 생성 (`feat/issue-N-slug`)
- 이슈 제목/본문/Acceptance Criteria 출력
- 관련 파일 검색 (이슈 키워드로 코드베이스 탐색)
- 이슈 라벨 `in-progress` 추가

**언제 쓰나**: 새 이슈 작업을 시작할 때. main에서 항상 실행.

**주의**: dirty working tree (미커밋 변경사항)가 있으면 stash 제안.

---

### `/commit` — 스마트 커밋
**입력**: 없음 (메시지를 직접 줄 수도 있음)
**출력**:
- 현재 이슈 + diff 분석
- 논리적 커밋 단위 추천 (여러 단위로 나눌 수 있으면 분리 제안)
- 커밋 메시지 자동 생성
- 형식 검증 후 커밋

**언제 쓰나**: 논리적으로 하나의 단위가 완성되었을 때.

**예시 추천 출력**:
```
다음 2개 커밋으로 나누는 것을 추천합니다:
1. feat(auth): add JWT token generation logic [#42]
   → TokenService.java, JwtUtil.java
2. test(auth): add unit tests for JWT generation [#42]
   → TokenServiceTest.java
```

---

### `/verify` — 7단계 검증
**입력**: `--quick` 옵션 (빌드/테스트 스킵, git/static만)
**출력**: VERIFICATION REPORT (PR에 붙여넣기 가능)

단계별 의미:
1. **Risk Assessment**: 변경 파일 경로로 HIGH/MEDIUM/LOW 분류
2. **Pre-build Gate**: 브랜치 확인, 시크릿 스캔
3. **Build Gate**: 컴파일/빌드 (실패 시 즉시 중단)
4. **Test Gate**: 테스트 실행 (캐시 불허, 항상 fresh)
5. **Static Analysis**: TODO/FIXME, printStackTrace 등
6. **Automated Review**: code-reviewer 에이전트 7점 체크리스트
7. **Observable Proof**: 검증 보고서 생성

**언제 쓰나**: PR 전. `/done`과 `/pr`이 내부적으로 호출.

---

### `/done` — 원스텝 완료
**입력**: 없음
**동작**: verify → (미커밋 있으면 commit) → push → PR 생성

**언제 쓰나**: 이슈 완료 시. 가장 자주 쓰는 커맨드.

---

### `/review` — 코드리뷰
**입력**: PR 번호 (생략 시 현재 브랜치 PR)
**출력**: CRITICAL/MINOR/SUGGESTION 분류 리뷰

**언제 쓰나**: 다른 사람의 PR 리뷰 요청을 받았을 때.

**중요**: code-reviewer 에이전트는 **읽기 전용**. 파일 수정 없음.

---

### `/test <파일>` — 테스트 생성
**입력**: 파일 경로 또는 클래스명
**출력**: 테스트 파일 생성 + 실행 결과

**언제 쓰나**: 테스트 없는 기존 코드에 테스트를 추가할 때.

---

### `/log "제목"` — 의사결정 기록
**입력**: 결정 제목
**출력**: DECISIONS.md에 append

**언제 쓰나**: A vs B를 비교 검토한 후 결정을 내렸을 때.
- 기술 스택 선택 (JWT vs Session)
- 아키텍처 패턴 선택
- API 설계 결정

**자동 감지**: 대화에서 중요한 결정이 이루어지면 Claude가 자동으로 `/tmp/claude-pending-decision.txt`에 기록하고, 세션 종료 시 자동으로 DECISIONS.md에 추가됩니다.

---

### `/arch-setup` — 아키텍처 테스트 생성
**입력**: 없음 (또는 프로젝트 경로)
**출력**: ArchUnit/pytest 기반 아키텍처 테스트 파일

**언제 쓰나**: 새 프로젝트 시작 시. 한 번만 실행.

**생성되는 것**:
- Java: `src/test/java/.../ArchitectureTest.java`
- Kotlin: `src/test/kotlin/.../ArchitectureTest.kt`
- Python: `tests/test_architecture.py`

**강제하는 규칙**:
- 레이어 의존성 방향
- @Autowired 필드 주입 금지
- printStackTrace 금지
- 네이밍 컨벤션
- 순환 의존성 감지

---

## 에이전트 vs 스킬 차이

| | 스킬 (/커맨드) | 에이전트 |
|--|--------|---------|
| 호출 방법 | 슬래시 커맨드 | 다른 스킬에서 자동 호출 |
| 파일 수정 | 가능 | code-reviewer: 불가 |
| 직접 호출 | 가능 | 불가 (간접만) |
| 예시 | `/verify`, `/commit` | code-reviewer, test-writer |

---

## hooks 동작

### pre-tool-use (위험 명령어 차단)
다음을 자동으로 차단합니다:
- `git push --force` / `git push -f`
- `git commit --no-verify`
- `git reset --hard`
- `curl ... | bash` (파이프 실행)
- `DROP TABLE`, `DELETE FROM` (SQL)

### post-edit (파일 수정 후 즉시 경고)
파일 저장 시 비동기로 실행:
- 하드코딩된 시크릿 패턴 감지 → 경고
- Java: `printStackTrace()`, `localhost` 하드코딩 → 경고
- Kotlin: `!!` 연산자, 과도한 `var` 사용 → 경고

### stop (세션 종료 시 요약)
Claude Code 세션 종료 시:
- 수정된 파일 목록 출력
- 미커밋 변경사항 알림
- 자동 감지된 의사결정을 DECISIONS.md에 추가
