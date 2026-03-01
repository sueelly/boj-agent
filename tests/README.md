# Tests

## 실행

```bash
./tests/run_tests.sh
```

## 구성

- **fixtures/** — 테스트용 더미 문제
  - `99999-fixture/` — Java: 두 정수 a,b 입력 → a+b 출력. `boj run` 통합 테스트용.
- **integration/** — 통합 테스트
  - `test_boj_help.sh` — `boj --help` 출력 및 종료 코드
  - `test_boj_run.sh` — 임시 디렉터리에 templates + 픽스처 복사 후 `boj run 99999` 실행, 2/2 통과 확인

## 요구사항

- Java 11+ (픽스처가 Java이므로 `boj run` 테스트에 필요)
- Bash
