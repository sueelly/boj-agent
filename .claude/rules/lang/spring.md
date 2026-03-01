# Spring Boot 규칙

## 레이어 아키텍처 (필수 준수)
```
Controller (HTTP 어댑터)
    ↓ DTO 사용
Service (비즈니스 로직)
    ↓ Domain/Entity 사용
Repository (데이터 접근)
    ↓
Database
```

**레이어 위반 금지**:
- Controller에서 Repository 직접 호출 금지
- Repository에서 다른 Service 호출 금지
- Entity를 Controller 응답으로 직접 반환 금지 (DTO 사용)

## 의존성 주입 — 생성자 주입
```java
// O — 생성자 주입 (테스트 용이, 불변성 보장)
@Service
@RequiredArgsConstructor  // Lombok
public class UserService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
}

// X — 필드 주입 (테스트 어려움, 순환 의존성 감지 안 됨)
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
}
```

## @Transactional 위치
```java
// O — Service 레이어에
@Service
public class OrderService {
    @Transactional
    public Order createOrder(OrderRequest request) { ... }

    @Transactional(readOnly = true)
    public List<Order> findAll() { ... }
}

// X — Repository에 비즈니스 트랜잭션 걸기
// X — Controller에 @Transactional
```

## 빈 스코프
- 기본 Singleton 사용 (특별한 이유 없으면)
- Prototype, Request, Session 스코프는 필요성 명시 필요
- 상태(state)를 갖는 빈 주의 — thread-safe 확인

## 설정 프로퍼티
```java
// O — @ConfigurationProperties (타입 안전)
@ConfigurationProperties(prefix = "app.messaging")
public record MessagingProperties(
    String host,
    int port,
    int retryCount
) {}

// O — @Value (단순 값)
@Value("${app.name}")
private String appName;

// X — 하드코딩
private String host = "localhost";
```

## 예외 처리
```java
// O — @RestControllerAdvice로 통일
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(UserNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(UserNotFoundException e) {
        return new ErrorResponse("USER_NOT_FOUND", e.getMessage());
    }
}

// X — Controller마다 try-catch
// X — 예외 묵살 (빈 catch 블록)
```

## 테스트 레이어별 전략
```java
// Controller: @WebMvcTest + MockMvc
@WebMvcTest(UserController.class)

// Service: 순수 단위 테스트 (Spring context 없이)
// Mockito로 의존성 모킹

// Repository: @DataJpaTest + Testcontainers
@DataJpaTest

// 통합: @SpringBootTest(webEnvironment = RANDOM_PORT) + RestAssured
```

## Spring Security (사용 시)
- SecurityFilterChain 빈으로 설정 (WebSecurityConfigurerAdapter 상속 X)
- JWT 필터는 OncePerRequestFilter 상속
- 새 엔드포인트 추가 시 SecurityConfig에 명시적 허용/차단
- CSRF: REST API는 기본 비활성화, 이유 주석 필수
