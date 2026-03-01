# 테스트 규칙

## 핵심 원칙
- 모든 행동 변경에 테스트 필수 (순수 리팩토링 제외 — 기존 테스트가 통과해야)
- Observable Proof: 증거는 통과된 테스트 결과만. 스크린샷/수동 확인 불허
- 테스트는 구현이 아닌 행동을 검증

## 테스트 이름 규칙
```
should_<expectedBehavior>_when_<condition>
// 예시:
should_returnEmpty_when_queueIsEmpty()
should_throwException_when_messageExceedsMaxSize()
should_retryThreeTimes_when_deliveryFails()
```

## AAA 패턴 (필수)
```java
@Test
void should_returnToken_when_credentialsAreValid() {
    // Arrange
    String username = "testuser";
    String password = "password123";
    when(userRepo.findByUsername(username)).thenReturn(Optional.of(mockUser));

    // Act
    String token = authService.login(username, password);

    // Assert
    assertThat(token).isNotNull();
    assertThat(jwtUtil.validate(token)).isTrue();
}
```

## 테스트 피라미드
- 단위 테스트 > 통합 테스트 > E2E 테스트
- 빠른 피드백: 단위 테스트는 수 ms 내 완료
- 비동기 대기: Thread.sleep 금지 → Awaitility 사용

## 커버리지 요구사항
- 새 기능/버그 수정: 최소 1개 이상의 관련 테스트 필수
- 해피패스 + 실패패스 모두 커버
- 경계값(null, empty, max) 테스트 포함

## 언어별 프레임워크
- Java: JUnit5 + Mockito + AssertJ
- Kotlin: JUnit5 + MockK + Kotest (또는 AssertJ)
- Python: pytest + unittest.mock
- JavaScript/TypeScript: Jest 또는 Vitest

## 테스트 격리
- 테스트 간 공유 상태 없음 (각 테스트는 독립적)
- 외부 의존성(DB, HTTP) 모킹 또는 Testcontainers 사용
- 정적 메서드/전역 상태 의존 피하기
