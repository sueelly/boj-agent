# 에이전트 동작 원리 및 관찰 방법

## 에이전트 vs 스킬

### 스킬 (슬래시 커맨드)
- 위치: `.claude/skills/<name>/SKILL.md`
- 직접 호출: `/verify`, `/commit`, `/start 42`
- Claude가 SKILL.md 지침을 따라 직접 실행
- 파일 수정 가능

### 에이전트
- 위치: `.claude/agents/<name>.md`
- 간접 호출: 스킬이 필요할 때 자동으로 생성(spawn)
- 별도 컨텍스트에서 독립 실행
- `disallowedTools`로 능력 제한 가능

---

## code-reviewer 에이전트

### 언제 호출되나
1. `/review` 스킬 실행 시
2. `/verify` Step 6 (Automated Review Gate)에서 자동 호출
3. `/done` → `/verify` → Step 6에서 자동 호출

### 핵심 제약
```yaml
disallowedTools:
  - Write
  - Edit
  - MultiEdit
  - Bash
```
**파일을 절대 수정하지 않습니다**. 이것은 문서 규칙이 아닌 구조적 제약입니다.

### 동작 관찰 방법
```bash
# /verify 실행 후 Step 6 출력을 주목
/verify

# code-reviewer가 실행되면 다음 형태로 출력됨:
# === code-reviewer 에이전트 시작 ===
# [분석 중...]
# CRITICAL: [문제점]
# MINOR: [문제점]
# VERDICT: PASS / BLOCKED
```

### 거짓 양성(False Positive) 처리
code-reviewer가 잘못된 CRITICAL을 발견한 경우:
```java
// 이 @Autowired는 레거시 코드와의 호환성 유지를 위해 필요
// TODO(#99): 생성자 주입으로 전환 예정
@Autowired
private LegacyService legacyService;
```
이유를 주석으로 설명하면 다음 리뷰에서 CRITICAL 대신 SUGGESTION으로 처리됩니다.

---

## test-writer 에이전트

### 언제 호출되나
- `/test <파일경로>` 스킬 실행 시만

### 동작 순서
1. 대상 파일 읽기 + 언어 감지
2. 기존 테스트 파일 탐색 (컨벤션 파악)
3. public 메서드 목록 추출
4. 테스트 케이스 설계 (해피패스 + 실패패스 + 경계값)
5. 테스트 파일 생성
6. 테스트 실행 + 결과 보고

### 생성 품질 확인
```bash
# 생성 후 직접 실행
./gradlew test --tests "*UserServiceTest" --info
```

**주의**: test-writer가 생성한 테스트는 반드시 직접 검토하세요.
- 모킹이 너무 세밀하면 구현이 아닌 내부를 테스트하게 됨
- 통합 테스트가 필요한 경우 별도로 작성

---

## Hooks 동작 원리

### pre-tool-use — 실행 전 차단

```
Claude가 Bash 도구 호출 준비
         ↓
pre-tool-use.sh 실행 (stdin으로 JSON 입력)
         ↓
차단 패턴 검사 (git push --force 등)
         ↓
exit 0 → 정상 진행
exit 2 → 차단 + 에러 메시지 출력
```

**디버깅**: 예상치 못한 차단이 발생하면
```bash
cat .claude/hooks/pre-tool-use.sh
# 차단 패턴 목록 확인
```

### post-edit — 수정 후 비동기 경고

```
Claude가 파일 수정 (Write/Edit)
         ↓
post-edit.sh 비동기 실행 (async: true)
         ↓
수정된 파일 경로 추출
         ↓
시크릿 패턴 스캔 + 언어별 경고
         ↓
경고 출력 (차단하지 않음)
         ↓
/tmp/claude-session-edits.log에 기록
```

**세션 편집 로그 확인**:
```bash
cat /tmp/claude-session-edits.log
# 형식: HH:MM:SS /path/to/file
```

### stop — 세션 종료 요약

```
Claude Code 세션 종료 (Ctrl+C 또는 자연 종료)
         ↓
stop.sh 실행
         ↓
세션 편집 파일 목록 출력
         ↓
/tmp/claude-pending-decision.txt 존재 확인
         ↓
존재하면 DECISIONS.md에 자동 append
         ↓
미커밋 변경사항 출력
```

---

## 의사결정 자동 로깅 시스템

### 2-파트 설계

**Part 1 — 실시간 기록 (CLAUDE.md 지시)**:
대화 중 Claude가 중요 결정을 내릴 때:
```bash
# Claude가 자동으로 실행하는 Bash:
cat >> /tmp/claude-pending-decision.txt << EOF
## [2026-03-01] feat/issue-42: JWT vs Session 선택

**컨텍스트**: REST API 인증 구현
**결정**: Stateless JWT (15분 만료) + Refresh Token
**검토한 대안**: Redis 세션, Opaque Token
**근거**: 수평 확장 용이, 배포 유연성
**트레이드오프**: 개별 토큰 즉시 무효화 불가
**이슈**: #42

---
EOF
```

**Part 2 — 영속화 (stop hook)**:
세션 종료 시 자동으로 `DECISIONS.md`에 append.

### 왜 이 설계인가
- **신뢰성**: 결정 시점에 즉시 기록 (사후 재구성 불필요)
- **자동화**: 사용자가 `/log` 호출 안 해도 자동 저장
- **영속성**: stop hook이 임시 파일을 영구 파일로 이동

### 수동 기록이 더 좋은 경우
대화 중 자동 감지로는 포착되지 않는 결정이 있을 때:
```bash
/log "PostgreSQL vs MongoDB 선택"
# 상세 내용을 대화로 입력하면 구조화해서 저장
```

---

## 에이전트 행동이 예상과 다를 때

### code-reviewer가 너무 관대하다
- 이슈 컨텍스트를 제공하지 않았을 수 있음
- `/review`에 PR 번호를 명시해보세요: `/review 45`

### code-reviewer가 너무 엄격하다
- 위험도(Risk Level)를 확인하세요
- HIGH 위험도에서는 더 엄격하게 검토

### test-writer가 컴파일 안 되는 테스트를 생성한다
- 기존 테스트 파일을 충분히 읽지 못했을 수 있음
- 기존 테스트 파일 경로를 명시해주세요: `/test UserService.java`

### hook이 정상적인 명령을 차단한다
```bash
# 차단된 명령과 이유 확인
cat .claude/hooks/pre-tool-use.sh | grep -A2 "BLOCKED_PATTERNS"

# 일시적으로 직접 실행 (hook 우회가 아닌 터미널에서 직접)
# Claude Code 밖에서 터미널을 열고 실행
```

---

## 모델 설정

| 에이전트 | 모델 | 이유 |
|---------|------|------|
| code-reviewer | claude-opus-4-5 | 깊은 코드 이해, 미묘한 보안 문제 감지 |
| test-writer | claude-sonnet-4-5 | 빠른 코드 생성, 속도/품질 균형 |

모델은 `.claude/agents/` 파일의 frontmatter에서 변경 가능합니다.
