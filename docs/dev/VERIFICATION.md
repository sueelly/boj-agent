# 7단계 검증 파이프라인 상세 설명

## 왜 검증이 중요한가

> "AI가 생성한 코드의 48%만이 커밋 전에 리뷰됩니다."
> "일반적인 문서 기반 규칙은 AI/팀원 모두 거의 따르지 않습니다."

이 파이프라인은 Tony Lee의 7-step verification pipeline을 기반으로:
- **Observable Proof**: 검증의 증거는 통과된 테스트 결과만 (스크린샷 불허)
- **Fresh Validation**: 새 커밋마다 반드시 재실행 (캐시된 결과 불허)
- **구조가 규칙을 강제**: 문서가 아닌 gates로 위험 행동 차단
- **로컬과 CI 일치**: 로컬 `/verify`와 GitHub Actions CI는 동일한 빌드/테스트 명령을 사용하도록 설계됨. "CI에서만 실패하는 경우"는 환경 차이일 수 있으니 로컬에서 같은 명령으로 재현 후 수정.

---

## Step 1 — Risk Assessment (위험도 평가)

**목적**: 이후 게이트의 강도를 결정

**분류 기준**:

| 위험도 | 조건 | 예시 |
|--------|------|------|
| HIGH | 인증/보안 파일, DB 마이그레이션, 공유 라이브러리 | SecurityConfig.java, *.sql, auth/ |
| MEDIUM | 서비스 레이어, 새 엔드포인트 | service/, handler/, 새 @RestController |
| LOW | 테스트만, 문서, 설정값 | *Test*.java, *.md, *.yml (설정 제외) |

**게이트 강도**:
- HIGH: code-reviewer에서 CRITICAL 0개 필수 + MINOR도 목록 출력
- MEDIUM: CRITICAL 0개 필수, MINOR 출력 (차단 안 함)
- LOW: CRITICAL 0개 필수, MINOR/SUGGESTION은 정보용만

---

## Step 2 — Pre-build Qualification Gate

**목적**: 비용이 큰 빌드/테스트 전에 빠르게 차단

**검사 항목**:
1. **브랜치 확인**: main/master에서 실행 시 즉시 차단
2. **스테이징 확인**: `git status --short` — 의도치 않은 파일 없는지
3. **시크릿 스캔**: `grep -rn "password\s*=\s*['"]..."` 패턴 감지

**실패 시**: 이후 단계 진행 불가 (즉시 중단)

---

## Step 3 — Build Gate

**목적**: 컴파일/빌드 오류 조기 발견

**자동 감지 & 실행**:
| 파일 | 실행 명령 |
|------|----------|
| `gradlew` | `./gradlew build -x test --quiet` |
| `mvnw` | `./mvnw compile -q` |
| `package.json` | `npm run build` |
| `pyproject.toml` / `setup.py` | `pip install -e . -q` |
| `Makefile` (build 타겟) | `make build` |

**실패 시**: 빌드 에러 출력 후 전체 파이프라인 중단

---

## Step 4 — Test Gate (Fresh Validation)

**목적**: 실제 테스트로 구현 정확성 검증

**핵심 원칙**:
- **절대 캐시 불허**: 새 커밋마다 처음부터 재실행
- **0개 실패 필수**: 실패 시 이름 + 에러 메시지 출력
- **테스트 수 경고**: 0개면 "새 기능에 테스트 없음" 경고

**실행**:
| 파일 | 실행 명령 |
|------|----------|
| `gradlew` | `./gradlew test` |
| `mvnw` | `./mvnw test` |
| `package.json` | `npm test` |
| `pyproject.toml` / `pytest.ini` | `pytest -v` |

**왜 Fresh인가**:
- 로컬 캐시는 환경 의존성을 숨길 수 있음
- CI에서 실패하는 테스트가 로컬에서 통과하는 경우 방지
- "내 컴퓨터에서는 됐는데" 문제 사전 차단

---

## Step 5 — Static Analysis Gate

**목적**: 코드 품질 이슈 조기 발견 (경고 위주, 차단 최소화)

**검사 항목**:

| 항목 | 동작 | 이유 |
|------|------|------|
| TODO/FIXME/HACK | 경고 (차단 안 함) | 인지는 해야 하지만 차단은 과도 |
| HIGH 위험도 + TODO | 경고 강조 | HIGH 변경에 미해결 TODO는 위험 |
| `printStackTrace()` | 경고 | SLF4J Logger 사용 권장 |
| Kotlin `!!` | 경고 | NullPointerException 위험 |

**설계 원칙**: Static Analysis는 경고 레이어. CRITICAL 차단은 Step 6 (자동 리뷰)에서.

---

## Step 6 — Automated Review Gate

**목적**: 7점 체크리스트로 구조적 문제 감지

**code-reviewer 에이전트 호출** (읽기 전용 — 파일 수정 없음):

| # | 항목 | CRITICAL 조건 |
|---|------|--------------|
| 1 | 정확성 | Acceptance Criteria 미충족 |
| 2 | 테스트 커버리지 | 기능 추가인데 테스트 없음 |
| 3 | 에러 처리 | 예외 묵살 (빈 catch/except + pass) |
| 4 | 보안 | 하드코딩 시크릿, 인증 누락 |
| 5 | API 계약 | 기존 필드 제거/이름 변경 |
| 6 | 아키텍처 | 레이어 위반 (Controller→Repository 직접 호출) |
| 7 | 코드 품질 | 순환 복잡도 과다, 의미없는 네이밍 |

**CRITICAL 발견 시**: 파이프라인 즉시 중단. 수정 후 재실행 필요.

---

## Step 7 — Observable Proof

**목적**: PR에 붙여넣기 가능한 검증 증거 생성

**출력 형식**:
```
╔═══════════════════════════════════════════╗
║         VERIFICATION REPORT               ║
╚═══════════════════════════════════════════╝
Risk Level : MEDIUM
Branch     : feat/issue-42-jwt-refresh
Timestamp  : 2026-03-01 14:30:22

Step 1  Risk Assessment   : MEDIUM (새 인증 엔드포인트)
Step 2  Pre-build Gate    : PASS
Step 3  Build             : PASS (0 errors)
Step 4  Tests             : PASS (52 passed, 0 failed, 0 skipped)
Step 5  Static Analysis   : PASS (2 TODOs noted)
Step 6  Code Review       : PASS (0 critical, 1 minor noted)

═══════════════════════════════════════════
VERDICT: APPROVED — PR 생성 가능
```

**왜 텍스트인가**:
- 스크린샷은 조작 가능하고 시간이 지나면 의미 없음
- 텍스트 결과는 CI 로그와 비교 검증 가능
- PR 히스토리에 영구 기록됨

---

## 권장: GitHub Branch protection

main에 직접 푸시 금지는 pre-tool-use hook으로 막지만, **GitHub Branch protection**에서 "main에 대한 PR만 허용" + "Require status checks to pass (CI)"를 켜두면 이중 안전장치가 됨. 저장소 Settings → Branches → Add rule → main/master → Require a pull request before merging, Require status checks to pass.

---

## 자주 묻는 질문

### "verify가 너무 오래 걸린다. 빠른 방법은?"
```bash
/verify --quick
# git 상태 + 시크릿 스캔만. 빌드/테스트 스킵.
# 단, PR 전에는 반드시 full verify 실행해야 함.
```

### "같은 코드인데 왜 매번 테스트를 다시 실행해야 하나?"
Fresh Validation의 핵심 이유:
- 다른 브랜치 변경, 의존성 업데이트, 환경 변화로 기존에 통과한 테스트가 실패할 수 있음
- "마지막으로 테스트했을 때 됐으니까 괜찮다"는 착각을 방지

### "code-reviewer가 CRITICAL을 발견했는데 무시할 수 있나?"
없습니다. CRITICAL은 파이프라인 차단. 다음 방법으로만 해결 가능:
1. 문제를 수정하고 재실행
2. 거짓 양성(false positive)이라면 해당 항목에 이유를 주석으로 설명

### "아키텍처 테스트(ArchitectureTest)와 Step 6 리뷰의 차이는?"
- **ArchitectureTest**: 컴파일 타임/테스트 타임에 자동 강제. 100% 감지.
- **Step 6 code-reviewer**: LLM 기반 의미론적 리뷰. 패턴 감지 + 컨텍스트 이해.

두 레이어가 보완관계: ArchTest는 구조적 위반을, code-reviewer는 의미적 문제를 잡음.

### "/verify 또는 CI 실패 시 다음 단계는?"
- **Step 4 테스트 실패**: 로컬에서 동일 명령으로 재현 후 수정. 예: `./gradlew test --tests '*FailingTest*' --info` 또는 `pytest path/to/test_file.py -v`. 실패한 테스트 이름과 에러 메시지를 보고 수정한 뒤 `/verify` 재실행.
- **Step 3 빌드 실패**: 빌드 로그에서 컴파일/의존성 에러 확인. `./gradlew build -x test` 또는 `npm run build` 등으로 로컬 재현.
- **Step 6 code-reviewer CRITICAL**: 해당 항목 수정 후 `/verify` 재실행. 거짓 양성이라면 해당 코드에 이유를 주석으로 명시.
- **CI에서만 실패**: 로컬 `/verify`와 CI는 같은 빌드/테스트 명령을 쓰도록 설계되어 있음. Node/Java/Python 버전, 캐시, 환경 변수 차이를 확인하고, 로컬에서 동일 명령으로 재현해 수정.
