# Java 코딩 표준 (Java 16+)

## 네이밍 규칙
- **클래스/인터페이스/열거형**: PascalCase — `UserRepository`, `OrderService`, `MessageType`
- **메서드/변수**: camelCase — `getUserById()`, `orderCount`, `isProcessed`
- **상수**: SCREAMING_SNAKE_CASE — `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT_MS`
- **패키지**: 소문자, 단어 구분 없음 — `org.example.userservice`
- **약어 지양**: `usr` → `user`, `mgr` → `manager`, `cnt` → `count`
- **의미 있는 이름**: `data`, `info`, `temp`, `obj` 금지

## 코드 포맷
- **들여쓰기**: 공백 4칸 (탭 금지)
- **한 줄 최대 120자**
- **중괄호 스타일**: K&R (같은 줄 열기)
  ```java
  // O
  if (condition) {
      doSomething();
  }
  // X
  if (condition)
  {
      doSomething();
  }
  ```
- **자동 포맷터 필수**: Google Java Format 또는 IntelliJ 기본 포맷터

## Java 핵심 규칙

### Null 처리
```java
// O — Optional 사용
Optional<User> findById(Long id);
return userRepo.findById(id)
    .orElseThrow(() -> new UserNotFoundException(id));

// X — null 직접 반환
User findById(Long id) { return null; }
```

### 불변 데이터 모델 (Java 16+)
```java
// O — Record 사용 (DTO, Value Object)
public record UserResponse(Long id, String name, String email) {}

// X — 클래스에 getter/setter
public class UserResponse {
    private Long id;
    // ...
}
```

### 컬렉션 처리
```java
// O — Stream API
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .toList();

// X — 명령형 for loop (단순 변환/필터에서)
List<String> names = new ArrayList<>();
for (User user : users) {
    if (user.isActive()) names.add(user.getName());
}
```

### 인터페이스 우선
```java
// O
List<String> list = new ArrayList<>();
Map<String, Integer> map = new HashMap<>();

// X
ArrayList<String> list = new ArrayList<>();
HashMap<String, Integer> map = new HashMap<>();
```

## 주석 & 문서화
- **이유를 설명**: 코드가 무엇을 하는지가 아닌 왜 하는지
  ```java
  // O: Retry is needed because the downstream service has transient failures
  // X: Retry 3 times
  ```
- **public API에 JavaDoc 필수**:
  ```java
  /**
   * Finds an active user by email.
   * @throws UserNotFoundException if user does not exist or is inactive
   */
  User findActiveByEmail(String email);
  ```
- **TODO 주석에 이슈 번호 포함**:
  ```java
  // TODO(#42): migrate to new auth system after v2 release
  ```
- **매직 넘버/문자열 → 상수**:
  ```java
  // O
  private static final int MAX_RETRY_COUNT = 5;
  // X
  if (retryCount > 5) { ... }
  ```

## 코드 구조
- **함수 단일 책임**: 권장 30줄 이하, 한 가지 일만
- **이른 반환 (Early Return)**: 중첩 줄이기
  ```java
  // O
  if (user == null) return Optional.empty();
  if (!user.isActive()) return Optional.empty();
  return Optional.of(process(user));

  // X (중첩 증가)
  if (user != null) {
      if (user.isActive()) {
          return Optional.of(process(user));
      }
  }
  return Optional.empty();
  ```
- **순환 복잡도**: 10 이하 권장
- `printStackTrace()` 금지 — SLF4J Logger 사용
- `localhost`/`127.0.0.1` 하드코딩 금지 — `@Value` 또는 application.yml
