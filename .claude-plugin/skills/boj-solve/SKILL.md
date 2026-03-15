---
name: boj-solve
description: 백준 문제 자동 풀이. 문제 생성부터 풀이, 테스트, 커밋까지 전체 워크플로우. "백준 N번 풀어줘", "N번 문제 풀어", "solve BOJ N", "solve problem N"
argument-hint: "<문제번호> [--lang java|python]"
tools:
  - Bash
  - Read
  - Write
  - Edit
---

# 백준 문제 자동 풀이 (boj solve)

Arguments: $ARGUMENTS

## 1. 사전 확인 (필수)

```bash
command -v boj >/dev/null 2>&1 && echo "CLI_OK" || echo "CLI_NOT_FOUND"
cat ~/.config/boj/root 2>/dev/null || echo "SETUP_NEEDED"
```

- `CLI_NOT_FOUND` → "boj CLI가 설치되어 있지 않습니다. `pipx install boj-agent`로 설치하세요." **즉시 중단.**
- `SETUP_NEEDED` → "boj 초기 설정이 필요합니다." → `/boj-setup` 스킬을 먼저 실행하도록 안내. **즉시 중단.**

## 2. 인자 파싱

`$ARGUMENTS`에서 문제번호(필수) 추출.
문제번호가 없으면: "사용법: /boj-solve <문제번호> [--lang java|python]"

## 3. BOJ_ROOT 확인

```bash
BOJ_ROOT=$(cat ~/.config/boj/root)
```

이후 모든 파일 경로는 `$BOJ_ROOT` 기준으로 참조.

## 4. 문제 환경 생성

```bash
boj make <문제번호> --no-open [--lang <lang>]
```

## 5. 문제 분석

생성된 README.md를 읽고 문제를 이해한다:
- 입력/출력 형식
- 제약 조건
- 예제 입출력

```bash
PROBLEM_DIR=$(ls -d "$BOJ_ROOT"/*<문제번호>*/ 2>/dev/null | head -1)
```

README.md와 test_cases.json을 읽어서 문제 파악.

## 6. 풀이 작성

문제 분석 결과를 바탕으로 Solution 파일을 작성한다.
- Java: `Solution.java` + 필요시 `Parse.java`
- Python: `solution.py`

알고리즘 선택 시 시간/공간 복잡도를 고려하고, 제약 조건에 맞는 효율적인 풀이를 작성.

## 7. 테스트

```bash
boj run <문제번호>
```

### 실패 시 수정 루프 (최대 3회)

1. 실패한 테스트케이스의 입력/기대값/실제값 분석
2. Solution 파일 수정
3. `boj run <문제번호>` 재실행
4. 3회 실패 시 중단하고 현재 상태 보고

## 8. 커밋

모든 테스트 통과 시:
```bash
boj commit <문제번호>
```

## 9. 제출 파일 생성

```bash
boj submit <문제번호>
```

## 10. 완료 보고

```
✅ 백준 <문제번호> 풀이 완료
- 문제: <문제 제목>
- 언어: <사용 언어>
- 테스트: 전체 통과
- 커밋: <커밋 해시>
- 제출 파일: submit/Submit.<ext>
```
