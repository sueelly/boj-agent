# Claude Code 범용 백엔드 보일러플레이트

여러 백엔드 프로젝트에서 공유하는 Claude Code 설정 레이어.
언어 무관(Java/Kotlin/Python), 검증 자동화, GitHub 워크플로우 완전 자동화.

---

## 빠른 시작

**첫 적용 시**: [docs/QUICKSTART.md](docs/QUICKSTART.md) 체크리스트를 따라 한 바퀴 돌려보세요.  
Hook 경로(`.claude/settings.json`)는 **워크스페이스 루트 기준 상대 경로**이므로, 다른 환경에 클론해도 동작합니다.

### 1. 보일러플레이트 활성화
```bash
# Claude Code 실행 (이 디렉토리에서)
claude
```
CLAUDE.md가 자동으로 로드됩니다.

### 2. 새 프로젝트에 적용
```bash
# 프로젝트 CLAUDE.md 복사
cp templates/project/CLAUDE.md /path/to/myproject/CLAUDE.md

# 아키텍처 테스트 생성 (프로젝트 루트에서)
cd /path/to/myproject
claude
/arch-setup

# GitHub 템플릿 복사 (Actions, 이슈/PR 템플릿, Dependabot)
cp -r templates/github/. /path/to/myproject/.github/
# dependabot.yml: 의존성 업데이트 PR 자동 생성(주 1회, 보안·마이너 버전). 사용 안 하면 해당 파일만 삭제.
```

### 3. (선택) PR 품질 검사 — SonarCloud
PR 올린 뒤 CI에서 품질 검사를 쓰려면 `workflows/sonarcloud.yml` 사용.  
SonarCloud에서 저장소 연결 후 `SONAR_TOKEN` 시크릿 추가. [docs/PR-REVIEW-AND-API.md](docs/PR-REVIEW-AND-API.md) 참고.

---

## 디렉토리 구조

```
claude/
├── CLAUDE.md                    # 에이전트 브레인 (언어 무관, 공통 워크플로우)
├── DECISIONS.md                 # append-only 의사결정 로그
├── README.md                    # 이 파일
│
├── .claude/
│   ├── settings.json            # hooks, permissions
│   ├── rules/                   # 규칙 파일 (경로별 자동 로드)
│   │   ├── git.md               # 브랜치/커밋/머지 규칙
│   │   ├── testing.md           # 테스트 원칙, AAA 패턴
│   │   ├── security.md          # 보안 규칙, 시크릿 관리
│   │   ├── api.md               # API 설계, 에러 응답 형식
│   │   └── lang/
│   │       ├── java.md          # Java 코딩 표준 (16+)
│   │       ├── kotlin.md        # Kotlin 코딩 표준
│   │       ├── spring.md        # Spring Boot 레이어 규칙
│   │       └── python.md        # Python 코딩 표준 (3.10+)
│   │
│   ├── skills/                  # 슬래시 커맨드
│   │   ├── start/               # /start <N>
│   │   ├── commit/              # /commit
│   │   ├── verify/              # /verify (7단계 파이프라인)
│   │   ├── done/                # /done
│   │   ├── pr/                  # /pr
│   │   ├── review/              # /review
│   │   ├── issue/               # /issue
│   │   ├── log/                 # /log
│   │   ├── test/                # /test
│   │   └── arch-setup/          # /arch-setup
│   │
│   ├── agents/
│   │   ├── code-reviewer.md     # 읽기전용 7점 체크리스트 리뷰
│   │   └── test-writer.md       # 언어 감지 후 테스트 생성
│   │
│   └── hooks/
│       ├── pre-tool-use.sh      # 위험 명령어 차단
│       ├── post-edit.sh         # 파일 수정 후 경고 (async)
│       └── stop.sh              # 세션 종료 요약 + 결정 기록
│
├── templates/
│   ├── arch/
│   │   ├── java/ArchitectureTest.java.template   # ArchUnit
│   │   ├── kotlin/ArchitectureTest.kt.template   # ArchUnit (Kotlin)
│   │   └── python/test_architecture.py.template  # pytest + AST
│   ├── github/
│   │   ├── workflows/
│   │   │   ├── ci.yml           # 빌드 + 테스트 + 보안 스캔
│   │   │   └── sonarcloud.yml   # (선택) PR 품질 검사
│   │   ├── PULL_REQUEST_TEMPLATE.md
│   │   └── ISSUE_TEMPLATE/
│   │       ├── feat.md
│   │       ├── bug.md
│   │       └── refactor.md
│   └── project/
│       └── CLAUDE.md            # 프로젝트별 CLAUDE.md 템플릿
│
└── docs/
    ├── HOW-TO-USE.md            # 무엇을, 언제, 어떻게
    ├── WORKFLOW.md              # 이슈→PR→머지 전체 흐름
    ├── VERIFICATION.md          # 7단계 파이프라인 상세
    └── AGENT-GUIDE.md           # 에이전트 동작 및 디버깅
```

---

## 슬래시 커맨드·검증 파이프라인

**상세 표·설명**: [docs/HOW-TO-USE.md](docs/HOW-TO-USE.md) (슬래시 커맨드), [docs/VERIFICATION.md](docs/VERIFICATION.md) (7단계 검증).

---

## 아키텍처 규칙 강제 방법

Channel Talk AI-native DDD 원칙: **문서가 아닌 코드로 강제**

```bash
# 새 프로젝트에서 한 번 실행
/arch-setup

# 생성되는 것:
# - ArchUnit 기반 아키텍처 테스트 (Java/Kotlin)
# - pytest + AST 기반 아키텍처 테스트 (Python)

# 강제하는 규칙:
# ✓ Controller → Service → Repository 방향 강제
# ✓ @Autowired 필드 주입 금지
# ✓ Entity를 Controller에서 반환 금지
# ✓ printStackTrace() 금지
# ✓ 네이밍 컨벤션 강제
# ✓ 순환 의존성 감지
```

---

## 지원 스택

| 언어 | 빌드 도구 | 테스트 | 아키텍처 테스트 |
|------|----------|--------|----------------|
| Java 16+ | Gradle / Maven | JUnit5 + Mockito | ArchUnit |
| Kotlin | Gradle | JUnit5 + MockK | ArchUnit |
| Python 3.10+ | pip / poetry | pytest | pytest + AST |

---

## 관련 문서

- [첫 적용 체크리스트](docs/QUICKSTART.md) — 5분 안에 한 바퀴
- [사용 가이드](docs/HOW-TO-USE.md) — 각 커맨드 상세 설명
- [전체 워크플로우](docs/WORKFLOW.md) — 이슈→PR→머지 흐름
- [검증 파이프라인](docs/VERIFICATION.md) — 7단계 상세, Branch protection 권장, 실패 시 복구
- [PR 리뷰 (verify + SonarCloud)](docs/PR-REVIEW-AND-API.md) — Step 6 리뷰, SonarCloud 설정
- [에이전트 가이드](docs/AGENT-GUIDE.md) — 에이전트 동작 및 디버깅
- [arch-setup vs post-edit 역할 분리](docs/ARCH-AND-HOOKS.md) — 규칙 강제 레이어 정리
- [의사결정 로그](DECISIONS.md) — 설계 결정 이력
