---
name: verify
description: PR 전 필수 7단계 검증 파이프라인. 위험도 평가부터 Observable Proof까지. /done과 /pr이 내부적으로 호출함.
argument-hint: "[--quick] (quick 옵션: 빌드/테스트 스킵, git/static만 검사)"
tools:
  - Bash
  - Read
---

# 7단계 검증 파이프라인 (7-Step Verification Pipeline)

Arguments: $ARGUMENTS

## 옵션 처리

- `$ARGUMENTS`에 `--quick`가 포함되어 있으면:
  - **Step 3 (Build Gate)** 생략
  - **Step 4 (Test Gate)** 생략
  - Step 2까지 실행 후 Step 5 → Step 6 → Step 7 진행
- `--quick`는 PR 전 full verify 대체 불가. PR 전에는 반드시 옵션 없이 `/verify` 실행.

---

현재 상태 파악:
- 현재 브랜치: `git branch --show-current`
- 변경 파일 목록: `git diff main..HEAD --name-only`

---

## Step 1 — Risk Assessment (위험도 평가)

변경된 파일 목록을 분석해 위험도를 결정:

```bash
CHANGED=$(git diff main..HEAD --name-only 2>/dev/null)
```

위험도 분류:
- **HIGH**: 다음 경로/패턴 포함 시
  - `**/security/**`, `**/auth/**`, `**/config/Security*`
  - `**/migration/**`, `**/*.sql`, `**/schema*`
  - `**/controller/**` + API 응답 형식 변경
  - 공유 라이브러리/코어 모듈 변경
- **MEDIUM**: 다음 포함 시
  - `**/service/**`, `**/handler/**`
  - 새 엔드포인트 추가
- **LOW**: 다음만 포함 시
  - `**/test/**`, `**/*Test*`, `**/*Spec*`
  - `*.md`, `*.txt`, `*.yml` (설정 제외)
  - 주석만 변경

위험도 출력 후 이후 게이트 강도 결정.

---

## Step 2 — Pre-build Qualification Gate

빌드 전 빠른 차단 조건 확인:

```bash
# 브랜치 확인
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "BLOCKED: main/master 브랜치에서 verify 불허. 기능 브랜치를 사용하세요."
  exit 1
fi

# 의도치 않은 파일 확인
git status --short

# 시크릿 하드코딩 스캔 (실패 시 차단)
SECRETS=$(grep -rn "(password|secret|api_key)\s*=\s*['\"][^$\{\(]" src/ 2>/dev/null || true)
if [ -n "$SECRETS" ]; then
  echo "BLOCKED: 하드코딩된 시크릿 발견:"
  echo "$SECRETS"
  exit 1
fi
```

HIGH 위험도 시 추가 경고 출력.

---

## 빌드/테스트 도구 감지 (Step 3·4 공통)

아래 로직으로 도구를 감지한 뒤, **Step 3**에서는 빌드 명령만, **Step 4**에서는 테스트 명령만 실행.

| 감지 조건 | 빌드 명령 | 테스트 명령 |
|-----------|-----------|-------------|
| `gradlew` | `./gradlew build -x test --quiet` | `./gradlew test` |
| `mvnw` | `./mvnw compile -q` | `./mvnw test` |
| `package.json` | `npm run build` | `npm test` |
| `pyproject.toml` 또는 `setup.py` | `pip install -e . -q` | `pytest -v` |
| `Makefile`에 build:/test: | `make build` | `make test` |
| 없음 | WARNING 출력 후 스킵 | WARNING 출력 후 스킵 |

---

## Step 3 — Build Gate

**$ARGUMENTS에 `--quick`가 있으면 이 단계를 건너뛰고 Step 5로 진행.**

위 "빌드/테스트 도구 감지" 표의 **빌드 명령**을 실행. 빌드 실패 시 에러 출력 후 전체 파이프라인 중단.

---

## Step 4 — Test Gate (Fresh Validation)

**$ARGUMENTS에 `--quick`가 있으면 이 단계를 건너뛰고 Step 5로 진행.**

위 "빌드/테스트 도구 감지" 표의 **테스트 명령**을 실행 (캐시 불허, 항상 새로 실행).

검증: 실패 0개 필수. 실패 시 테스트 이름·에러 메시지 출력. 테스트 수 0개면 "테스트가 없습니다. 신규 기능에 테스트를 추가하세요." 경고.

---

## Step 5 — Static Analysis Gate

```bash
# TODO/FIXME/HACK 목록 (경고, 차단 안 함)
TODOS=$(grep -rn "TODO\|FIXME\|HACK\|XXX" src/ 2>/dev/null | grep -v "^Binary" || true)
if [ -n "$TODOS" ]; then
  echo "NOTE: TODO/FIXME 발견 (참고용, 차단 안 함):"
  echo "$TODOS" | head -10
fi

# Java: printStackTrace 감지
if [ -d "src/main/java" ]; then
  STACKTRACE=$(grep -rn "printStackTrace()" src/main/ 2>/dev/null || true)
  if [ -n "$STACKTRACE" ]; then
    echo "WARNING: printStackTrace() 발견 — SLF4J Logger 사용 권장:"
    echo "$STACKTRACE"
  fi
fi

# Kotlin: !! 사용 감지
if find . -name "*.kt" -not -path "*/test/*" | head -1 | grep -q "kt"; then
  NULL_ASSERT=$(grep -rn "!!" src/main/ 2>/dev/null | grep -v "//.*!!" || true)
  if [ -n "$NULL_ASSERT" ]; then
    echo "WARNING: !! (not-null assertion) 발견:"
    echo "$NULL_ASSERT" | head -5
  fi
fi
```

HIGH 위험도 + TODO 존재 시 경고: "HIGH 위험도 변경에 TODO 미해결. 검토 권장."

---

## Step 6 — Automated Review Gate

code-reviewer 에이전트를 호출해 7점 체크리스트 실행:

```bash
DIFF=$(git diff main..HEAD 2>/dev/null)
```

위험도별 통과 기준:
- HIGH: CRITICAL 0개 필수
- MEDIUM: CRITICAL 0개 필수, MINOR 목록 출력
- LOW: CRITICAL 0개 필수 (MINOR는 정보용)

CRITICAL 발견 시 파이프라인 중단.

---

## Step 7 — Observable Proof 출력

PR에 붙여넣을 수 있는 검증 리포트 생성:

```
╔═══════════════════════════════════════════╗
║         VERIFICATION REPORT               ║
╚═══════════════════════════════════════════╝
Risk Level : [HIGH/MEDIUM/LOW]
Branch     : [브랜치명]
Timestamp  : [날짜 시간]

Step 1  Risk Assessment   : [결과]
Step 2  Pre-build Gate    : [PASS/FAIL]
Step 3  Build             : [PASS/FAIL] ([에러 수] errors)
Step 4  Tests             : [PASS/FAIL] ([통과] passed, [실패] failed, [스킵] skipped)
Step 5  Static Analysis   : [PASS/WARN] ([TODO 수] TODOs)
Step 6  Code Review       : [PASS/FAIL] ([CRITICAL 수] critical, [MINOR 수] minor)

═══════════════════════════════════════════
VERDICT: [APPROVED — PR 생성 가능 / BLOCKED — 수정 후 재실행]
```

BLOCKED 시 실패한 단계와 해결 방법 명시.
