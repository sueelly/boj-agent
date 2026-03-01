---
name: test
description: test-writer 에이전트로 지정 파일/클래스의 테스트 자동 생성. 언어 자동 감지.
argument-hint: "<파일경로 또는 클래스명>"
tools:
  - Bash
  - Read
  - Write
---

# 테스트 생성 (/test)

Arguments: $ARGUMENTS

## 1. 대상 파일 확인

```bash
# 파일 직접 지정
TARGET="$ARGUMENTS"

# 클래스명으로 파일 찾기
if [ ! -f "$TARGET" ]; then
  find . -name "${TARGET}.java" -o -name "${TARGET}.kt" -o -name "test_${TARGET}.py" 2>/dev/null | head -5
fi
```

## 2. 파일 분석

대상 파일 읽기:
- public 메서드/함수 목록
- 의존성 (생성자 파라미터, 임포트)
- 기존 테스트 패턴 (컨벤션 파악)

```bash
# 기존 테스트 디렉토리 확인
ls src/test/ 2>/dev/null || ls tests/ 2>/dev/null || echo "테스트 디렉토리 없음"
```

## 3. test-writer 에이전트 호출

다음 정보를 제공:
- 대상 파일 전체 내용
- 기존 테스트 파일 예시 (컨벤션 파악용)
- 언어 (확장자로 감지)
- 프로젝트 테스트 프레임워크 (build.gradle/pyproject.toml에서 감지)

## 4. 테스트 파일 생성

test-writer가 생성한 테스트 파일을 적절한 위치에 저장:
- Java: `src/test/java/.../ClassName Test.java`
- Kotlin: `src/test/kotlin/.../ClassNameTest.kt`
- Python: `tests/test_module_name.py`

## 5. 생성된 테스트 실행

```bash
# Java/Kotlin
./gradlew test --tests "*ClassName*" 2>/dev/null || \
./mvnw test -Dtest="ClassName*" 2>/dev/null

# Python
pytest tests/test_module_name.py -v 2>/dev/null
```

결과 출력. 실패 시 test-writer에게 수정 요청.
