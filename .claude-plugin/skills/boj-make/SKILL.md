---
name: boj-make
description: 백준 문제 환경 생성. 문제 fetch + README + 스켈레톤 코드 생성. "백준 N번 만들어줘", "문제 N번 세팅", "boj make", "create BOJ problem"
argument-hint: "<문제번호> [--lang java|python|cpp] [--no-open]"
tools:
  - Bash
  - Read
---

# 백준 문제 환경 생성 (boj make)

Arguments: $ARGUMENTS

## 1. 사전 확인

```bash
command -v boj >/dev/null 2>&1 || echo "ERROR: boj CLI not found"
```

boj CLI가 없으면 즉시 중단하고 안내:
"boj CLI가 설치되어 있지 않습니다. `pip install boj-agent` 또는 `src/setup-boj-cli.sh`로 설치하세요."

## 2. 인자 파싱

`$ARGUMENTS`에서 문제번호(필수)와 옵션 플래그 추출.
문제번호가 없으면: "사용법: /boj-make <문제번호> [--lang java|python|cpp] [--no-open]"

## 3. 실행

```bash
boj make <문제번호> [옵션들]
```

## 4. 결과 확인

성공 시 생성된 README.md를 읽어서 문제 내용 요약 표시.

```bash
# 생성된 문제 디렉토리 찾기
ls -d *<문제번호>*/ 2>/dev/null
```

## 5. 다음 단계 안내

"문제 환경이 생성되었습니다. Solution 파일을 작성한 후 `/boj-run <문제번호>`로 테스트하세요."
