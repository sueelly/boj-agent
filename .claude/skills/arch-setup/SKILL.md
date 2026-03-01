---
name: arch-setup
description: 새 프로젝트에 아키텍처 테스트를 자동 생성. 스택 감지 후 ArchUnit(Java/Kotlin) 또는 pytest+AST(Python)로 규칙을 코드로 강제.
argument-hint: "[프로젝트 경로] (생략 시 현재 디렉토리)"
tools:
  - Bash
  - Read
  - Write
---

# /arch-setup — 아키텍처 테스트 자동 생성

Arguments: $ARGUMENTS

## 목표

Channel Talk AI-native DDD 원칙 적용:
- 규칙을 **문서(markdown)**로 적지 않고 **코드(테스트)**로 강제
- 아키텍처 위반 시 빌드 실패 → 100% 감지율
- 프로젝트 스택에 맞게 자동 생성

---

## Step 1 — 프로젝트 경로 및 스택 감지

```bash
PROJECT_DIR="${ARGUMENTS:-$(pwd)}"
cd "$PROJECT_DIR"

echo "=== 프로젝트 스택 감지 ==="

# 스택 감지
STACK=""
if [ -f "gradlew" ] && find . -name "*.kt" -not -path "*/build/*" | head -1 | grep -q "kt"; then
  STACK="kotlin-gradle"
  echo "감지: Kotlin + Gradle"
elif [ -f "gradlew" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
  STACK="java-gradle"
  echo "감지: Java + Gradle"
elif [ -f "mvnw" ] || [ -f "pom.xml" ]; then
  STACK="java-maven"
  echo "감지: Java + Maven"
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
  STACK="python"
  echo "감지: Python"
elif [ -f "package.json" ]; then
  STACK="node"
  echo "감지: Node.js"
fi

if [ -z "$STACK" ]; then
  echo "ERROR: 지원하는 스택을 감지할 수 없습니다."
  echo "지원: Java(Gradle/Maven), Kotlin(Gradle), Python, Node.js"
  exit 1
fi
```

---

## Step 2 — 루트 패키지 및 레이어 구조 스캔

스택별로 실제 소스 구조를 스캔하여 패키지/모듈명 추출:

### Java/Kotlin 프로젝트

```bash
if [[ "$STACK" == java-* ]] || [[ "$STACK" == kotlin-* ]]; then
  # 루트 패키지 감지 (예: com.example.myapp)
  ROOT_PKG=$(find src/main -name "*.java" -o -name "*.kt" 2>/dev/null \
    | head -20 \
    | xargs grep -l "^package " 2>/dev/null \
    | head -1 \
    | xargs grep "^package " 2>/dev/null \
    | head -1 \
    | awk '{print $2}' \
    | sed 's/;//' \
    | awk -F. '{print $1"."$2"."$3}')

  if [ -z "$ROOT_PKG" ]; then
    ROOT_PKG="com.example.app"
    echo "WARNING: 루트 패키지를 감지하지 못했습니다. 기본값 사용: $ROOT_PKG"
    echo "생성 후 ArchitectureTest에서 ROOT_PACKAGE를 직접 수정하세요."
  else
    echo "루트 패키지: $ROOT_PKG"
  fi

  # 레이어 감지 (controller, service, repository, domain 등)
  LAYERS=$(find src/main -type d 2>/dev/null \
    | sed "s|.*/||" \
    | sort -u \
    | grep -E "controller|service|repository|domain|handler|usecase|infra|adapter|port" \
    | tr '\n' ' ')
  echo "감지된 레이어: $LAYERS"
fi
```

### Python 프로젝트

```bash
if [ "$STACK" = "python" ]; then
  # 소스 루트 감지
  SRC_ROOT=$(find . -name "*.py" -not -path "./.venv/*" -not -path "./tests/*" -not -path "./test/*" \
    | head -5 \
    | awk -F/ '{print $2}' \
    | sort -u \
    | head -1)

  if [ -z "$SRC_ROOT" ]; then
    SRC_ROOT="src"
    echo "WARNING: 소스 루트를 감지하지 못했습니다. 기본값: $SRC_ROOT"
  else
    echo "소스 루트: $SRC_ROOT"
  fi
fi
```

---

## Step 3 — 의존성 추가 (Java/Kotlin)

ArchUnit이 없으면 자동으로 추가:

### Gradle (build.gradle.kts 또는 build.gradle)

```bash
if [[ "$STACK" == java-gradle ]] || [[ "$STACK" == kotlin-gradle ]]; then
  # Kotlin DSL 확인
  if [ -f "build.gradle.kts" ]; then
    if ! grep -q "archunit" build.gradle.kts; then
      echo ""
      echo "ArchUnit 의존성이 없습니다."
      echo "build.gradle.kts의 dependencies 블록에 다음을 추가하세요:"
      echo ""
      echo '    testImplementation("com.tngtech.archunit:archunit-junit5:1.3.0")'
      echo ""
      echo "또는 다음 명령으로 자동 추가할 수 있습니다 (수동 검토 권장):"
      echo '  sed -i '"'"'s/dependencies {/dependencies {\n    testImplementation("com.tngtech.archunit:archunit-junit5:1.3.0")/'"'"' build.gradle.kts'
    else
      echo "ArchUnit 이미 추가되어 있음 ✓"
    fi
  elif [ -f "build.gradle" ]; then
    if ! grep -q "archunit" build.gradle; then
      echo ""
      echo "ArchUnit 의존성이 없습니다."
      echo "build.gradle의 dependencies 블록에 다음을 추가하세요:"
      echo ""
      echo "    testImplementation 'com.tngtech.archunit:archunit-junit5:1.3.0'"
    else
      echo "ArchUnit 이미 추가되어 있음 ✓"
    fi
  fi
fi
```

### Maven (pom.xml)

```bash
if [ "$STACK" = "java-maven" ]; then
  if ! grep -q "archunit" pom.xml 2>/dev/null; then
    echo ""
    echo "ArchUnit 의존성이 없습니다."
    echo "pom.xml의 <dependencies>에 다음을 추가하세요:"
    echo ""
    cat << 'MAVEN_DEP'
<dependency>
    <groupId>com.tngtech.archunit</groupId>
    <artifactId>archunit-junit5</artifactId>
    <version>1.3.0</version>
    <scope>test</scope>
</dependency>
MAVEN_DEP
  else
    echo "ArchUnit 이미 추가되어 있음 ✓"
  fi
fi
```

### Python (import-linter)

```bash
if [ "$STACK" = "python" ]; then
  if ! pip show import-linter > /dev/null 2>&1; then
    echo ""
    echo "import-linter가 없습니다."
    echo "설치: pip install import-linter"
    echo "또는 requirements-dev.txt에 추가: import-linter"
  else
    echo "import-linter 이미 설치됨 ✓"
  fi
fi
```

---

## Step 4 — 아키텍처 테스트 파일 생성

감지된 스택과 루트 패키지 정보를 사용해 템플릿에서 실제 테스트 파일 생성:

### Java 프로젝트

```
생성 위치: src/test/java/{패키지경로}/ArchitectureTest.java
템플릿: 프로젝트 루트의 templates/arch/java/ArchitectureTest.java.template
       (루트 = git rev-parse --show-toplevel 또는 pwd. 보일러플레이트를 별도 레포로 둔 경우
        CLAUDE_BOILERPLATE_ROOT가 설정되어 있으면 ${CLAUDE_BOILERPLATE_ROOT}/templates/arch/... 사용)

치환 변수:
- {{ROOT_PACKAGE}} → 감지된 루트 패키지 (예: com.example.myapp)
- {{APP_CLASS_NAME}} → 감지된 @SpringBootApplication 클래스명
```

### Kotlin 프로젝트

```
생성 위치: src/test/kotlin/{패키지경로}/ArchitectureTest.kt
템플릿: 프로젝트 루트의 templates/arch/kotlin/ArchitectureTest.kt.template (위와 동일한 루트 규칙)

치환 변수:
- {{ROOT_PACKAGE}} → 감지된 루트 패키지
```

### Python 프로젝트

```
생성 위치: tests/test_architecture.py
템플릿: 프로젝트 루트의 templates/arch/python/test_architecture.py.template (위와 동일한 루트 규칙)

치환 변수:
- {{SRC_ROOT}} → 소스 루트 디렉토리명 (예: src, myapp)
```

파일 생성 후:
1. 생성된 파일 내용을 출력
2. `{{` 또는 `}}` 가 남아있으면 경고 (미치환 변수)
3. 기존 파일이 있으면 덮어쓰기 전에 확인

---

## Step 5 — 테스트 실행 검증

```bash
echo ""
echo "=== 아키텍처 테스트 실행 ==="

if [[ "$STACK" == *gradle* ]]; then
  ./gradlew test --tests "*ArchitectureTest" 2>&1 | tail -20
elif [ "$STACK" = "java-maven" ]; then
  ./mvnw test -Dtest=ArchitectureTest 2>&1 | tail -20
elif [ "$STACK" = "python" ]; then
  pytest tests/test_architecture.py -v 2>&1 | tail -20
fi
```

---

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

검증 항목:
  ✓ 레이어 의존성 방향 (Controller → Service → Repository)
  ✓ 필드 주입(@Autowired) 금지 → 생성자 주입 강제
  ✓ Entity를 Controller에서 직접 반환 금지
  ✓ printStackTrace() 금지
  ✓ 네이밍 컨벤션 강제
  [Python 추가] ✓ 임포트 방향 강제
  [Python 추가] ✓ 타입 힌트 검사
  [Python 추가] ✓ print() 사용 금지 (src/)

다음 단계:
  1. build.gradle.kts (또는 pom.xml)에 ArchUnit 의존성 추가 (안내 참조)
  2. 생성된 테스트 파일의 {{ROOT_PACKAGE}} 등 변수 확인
  3. ./gradlew test 실행해서 모든 아키텍처 테스트 통과 확인
  4. CI/CD 파이프라인에 포함 (ci.yml에 이미 포함됨)

규칙 위반 발견 시 → 빌드 실패로 즉시 감지
(Channel Talk AI-native DDD: 문서가 아닌 코드로 규칙 강제)
```
