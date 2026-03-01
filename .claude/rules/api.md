# API 설계 규칙

## 브레이킹 체인지 금지
- 기존 응답 필드 이름 변경/제거 금지
- 기존 엔드포인트 URL 변경 시 버전 관리 필수
- 필드 추가는 허용 (하위 호환)
- 타입 변경(string → int)은 브레이킹 체인지

## HTTP 상태코드 표준
```
200 OK          - 조회/업데이트 성공
201 Created     - 리소스 생성 성공 (Location 헤더 포함)
204 No Content  - 삭제 성공 (body 없음)
400 Bad Request - 클라이언트 입력 오류 (검증 실패)
401 Unauthorized - 인증 필요 (토큰 없음/만료)
403 Forbidden   - 인가 거부 (권한 부족)
404 Not Found   - 리소스 없음
409 Conflict    - 중복/충돌 (이미 존재하는 리소스)
422 Unprocessable - 형식은 맞지만 의미론적 오류
429 Too Many Requests - Rate limit 초과
500 Internal Error - 서버 오류 (예상치 못한 예외)
```

## 에러 응답 형식 (표준)
```json
{
  "code": "DOMAIN_ERROR_CODE",
  "message": "사용자에게 보여줄 메시지",
  "details": [
    { "field": "email", "reason": "이미 사용 중인 이메일입니다" }
  ]
}
```
- `code`: 머신 리더블 에러 코드 (ALL_CAPS_SNAKE_CASE)
- `message`: 사람이 읽을 수 있는 메시지
- `details`: 배열 (필드별 검증 오류 등, 선택)

## RESTful 설계
- 리소스 이름: 복수 명사 (`/users`, `/messages`)
- 동사 URL 지양 (`/getUser` → `GET /users/{id}`)
- 중첩: 최대 2단계 (`/users/{id}/orders`)
- 필터/정렬/페이지네이션: 쿼리 파라미터

## 문서화
- 새 엔드포인트에 OpenAPI/Swagger 어노테이션 필수
- Request/Response 예시 포함
- 인증 요구사항 명시

## 버전 관리
- URL 버전: `/api/v1/`, `/api/v2/`
- 브레이킹 체인지 시 새 버전 생성
- 이전 버전은 최소 N개월 유지 (팀/프로젝트 정책 따름)
