# /arch-setup — 아키텍처 테스트 자동 생성

Arguments: $ARGUMENTS

## 목표

- 규칙을 **문서(markdown)**로 적지 않고 **코드(테스트)**로 강제
- 아키텍처 위반 시 빌드 실패 → 100% 감지율
- 프로젝트 스택에 맞게 자동 생성

---

## Step 1 — 프로젝트 경로 및 스택 감지

```bash
PROJECT_DIR="${ARGUMENTS:-$(pwd)}"
cd "$PROJECT_DIR"

# 스택 감지
STACK=""
if [ -f "gradlew" ] && find . -name "*.kt" -not -path "*/build/*" | head -1 | grep -q "kt"; then
  STACK="kotlin-gradle"
elif [ -f "gradlew" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
  STACK="java-gradle"
elif [ -f "mvnw" ] || [ -f "pom.xml" ]; then
  STACK="java-maven"
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
  STACK="python"
elif [ -f "package.json" ]; then
  STACK="node"
fi
```

## Step 2 — 루트 패키지 및 레이어 구조 스캔

Java/Kotlin: `find src/main`으로 루트 패키지 및 레이어 디렉터리 감지
Python: 소스 루트 디렉터리명 감지

## Step 3 — 의존성 추가 (Java/Kotlin)

ArchUnit이 없으면 추가 안내:
- Gradle: `testImplementation("com.tngtech.archunit:archunit-junit5:1.3.0")`
- Maven: pom.xml에 archunit-junit5 의존성 추가
- Python: `pip install import-linter`

## Step 4 — 아키텍처 테스트 파일 생성

감지된 스택에 맞는 테스트 파일 생성:
- Java: `src/test/java/{패키지경로}/ArchitectureTest.java`
- Kotlin: `src/test/kotlin/{패키지경로}/ArchitectureTest.kt`
- Python: `tests/test_architecture.py`

검증 항목:
- 레이어 의존성 방향 (Controller → Service → Repository)
- 필드 주입(@Autowired) 금지 → 생성자 주입 강제
- Entity를 Controller에서 직접 반환 금지
- printStackTrace() 금지
- 네이밍 컨벤션 강제

## Step 5 — 테스트 실행 검증

```bash
if [[ "$STACK" == *gradle* ]]; then
  ./gradlew test --tests "*ArchitectureTest" 2>&1 | tail -20
elif [ "$STACK" = "java-maven" ]; then
  ./mvnw test -Dtest=ArchitectureTest 2>&1 | tail -20
elif [ "$STACK" = "python" ]; then
  pytest tests/test_architecture.py -v 2>&1 | tail -20
fi
```

## Step 6 — 결과 요약 출력

```
╔═══════════════════════════════════════════╗
║       ARCHITECTURE SETUP COMPLETE         ║
╚═══════════════════════════════════════════╝
Stack    : [감지된 스택]
Package  : [루트 패키지]
Layers   : [감지된 레이어 목록]

생성된 파일:
  ✓ [아키텍처 테스트 파일 경로]
```
