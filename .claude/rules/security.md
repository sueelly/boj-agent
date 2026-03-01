# 보안 규칙

## 절대 금지
- 소스코드에 시크릿/비밀번호/API키 하드코딩
- SQL 쿼리 문자열 직접 연결 (인젝션 위험)
- 사용자 입력을 검증 없이 명령어/쿼리에 사용
- 에러 메시지에 스택 트레이스/시스템 정보 노출
- 개인정보(이메일, 비밀번호) 로그 출력

## 시크릿 관리
- 환경변수 사용: `System.getenv()`, `os.environ`
- 설정 파일 사용: application.yml, .env (gitignored)
- 프로덕션: AWS Secrets Manager, Vault, K8s Secrets
- `.env` 파일은 반드시 `.gitignore`에 추가

## 입력 검증 (모든 외부 입력)
- API 요청 파라미터: Bean Validation (@Valid, @NotNull 등)
- 파일 업로드: 타입, 크기 검증
- 경로 파라미터: 화이트리스트 검증
- 쿼리 파라미터: 타입 변환 후 사용

## 인증/인가 분리
- 인증(Authentication): 신원 확인 — 별도 레이어
- 인가(Authorization): 권한 확인 — 인증 후 별도 검사
- 새 엔드포인트에 반드시 접근제어 명시
- Security By Default: 기본은 차단, 허용을 명시적으로

## API 보안
- HTTPS 강제 (HTTP 리다이렉트)
- CORS 설정: 화이트리스트 기반
- Rate Limiting: 공개 엔드포인트에 필수
- 민감한 데이터 응답: 필요한 필드만 포함

## 의존성 보안
- 알려진 취약점 있는 버전 사용 금지
- 정기적 의존성 업데이트 (Dependabot 활용)
- 불필요한 의존성 추가 지양
