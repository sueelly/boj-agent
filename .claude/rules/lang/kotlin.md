# Kotlin 코딩 표준

## 네이밍 규칙
- **클래스/인터페이스/object**: PascalCase — `UserRepository`, `MessageProcessor`
- **함수/변수**: camelCase — `getUserById()`, `isProcessed`
- **상수 (companion object)**: SCREAMING_SNAKE_CASE — `MAX_RETRY_COUNT`
- **패키지**: 소문자 — `org.example.service`
- **약어 지양**: 의미 있는 이름 사용

## 코드 포맷
- **들여쓰기**: 공백 4칸
- **한 줄 최대 120자**
- **중괄호**: K&R 스타일
- **자동 포맷터**: ktlint 또는 IntelliJ Kotlin 포맷터 필수

## Kotlin 핵심 규칙

### 불변성 우선
```kotlin
// O — val 우선
val userId = 42L
val users = listOf<User>()

// X — var는 정말 필요한 경우만
var counter = 0  // 루프 카운터 등 변경 필요한 경우만
```

### Null 안전성 — !! 금지
```kotlin
// O — 안전한 null 처리
val name = user?.name ?: "Anonymous"
val result = user?.let { process(it) } ?: defaultValue
val user = findUser(id) ?: throw UserNotFoundException(id)
requireNotNull(config) { "Config must not be null" }

// X — !! 사용 금지 (NullPointerException 위험)
val name = user!!.name
```

### 데이터 모델 — data class
```kotlin
// O — data class (equals, hashCode, copy 자동 생성)
data class UserResponse(
    val id: Long,
    val name: String,
    val email: String
)

// O — sealed class for algebraic types
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Failure(val error: Exception) : Result<Nothing>()
}
```

### 확장 함수로 유틸리티 구성
```kotlin
// O — 확장 함수
fun String.isValidEmail(): Boolean = contains('@') && contains('.')
fun List<User>.activeUsers(): List<User> = filter { it.isActive }

// X — static 유틸 클래스
object StringUtils {
    fun isValidEmail(s: String): Boolean { ... }
}
```

### 컬렉션 처리
```kotlin
// O — Kotlin 표준 라이브러리
val activeNames = users
    .filter { it.isActive }
    .map { it.name }
    .sortedBy { it }

val total = orders.sumOf { it.amount }
val grouped = users.groupBy { it.department }
```

### 함수형 스타일
```kotlin
// O — when 표현식
val status = when (code) {
    200 -> "OK"
    404 -> "Not Found"
    else -> "Unknown"
}

// O — scope functions
user?.apply {
    name = "Updated"
    updatedAt = Instant.now()
}
val result = someObject.let { transform(it) }
```

## 주석 & 문서화
- **public API에 KDoc 필수**:
  ```kotlin
  /**
   * Finds an active user by email.
   * @throws UserNotFoundException if user does not exist or is inactive
   */
  fun findActiveByEmail(email: String): User
  ```
- **이유를 설명** (코드가 하는 것이 아닌 왜 하는지)
- **TODO에 이슈 번호**: `// TODO(#42): migrate after v2`

## 코드 구조
- **함수 단일 책임**: 권장 30줄 이하
- **이른 반환**: `?: return` 활용
- `printStackTrace()` 금지 — Logger 사용
