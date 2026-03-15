---
name: boj-setup
description: 백준 CLI 초기 설정. 루트 경로, 언어, 세션 쿠키 설정. "boj 설정해줘", "백준 세팅", "boj setup", "configure boj"
argument-hint: "[--check] [--session <cookie>] [--lang java|python] [--root <path>] [--username <name>]"
tools:
  - Bash
  - Read
---

# 백준 CLI 설정 (boj setup)

Arguments: $ARGUMENTS

## 1. boj CLI 설치 확인

```bash
command -v boj >/dev/null 2>&1 && echo "OK" || echo "NOT_FOUND"
```

boj CLI가 없으면:
"boj CLI가 설치되어 있지 않습니다. 설치 후 다시 시도하세요:"
```
pipx install boj-agent   # 권장
pip install boj-agent     # 또는
```
**즉시 중단.**

## 2. 인자 파싱

`$ARGUMENTS` 확인:
- `--check`: 현재 설정 상태 확인만 → `boj setup --check` 실행 후 종료
- 인자가 없으면: 대화형 설정 모드 진행

## 3. 대화형 설정 (인자 없을 때)

사용자에게 순서대로 질문:

1. **문제 저장 경로**: "백준 풀이를 저장할 디렉토리를 알려주세요. (기본: ~/boj)"
2. **기본 언어**: "기본 프로그래밍 언어를 선택하세요: java, python, cpp (기본: java)"
3. **BOJ 사용자명**: "백준 사용자명을 입력하세요. (커밋 통계용, 선택)"
4. **세션 쿠키**: "BOJ 세션 쿠키를 입력하세요. (문제 제출용, 선택 — 나중에 설정 가능)"

수집한 값으로 실행:
```bash
boj setup --root <path> --lang <lang> [--username <name>] [--session <cookie>]
```

## 4. 직접 인자 전달 시

```bash
boj setup $ARGUMENTS
```

## 5. 설정 검증

```bash
boj setup --check
```

설정 상태를 확인하고 결과를 표로 보여줌.

## 6. 완료 안내

"✅ 설정이 완료되었습니다! 이제 다음 명령으로 시작하세요:"
- `/boj-make <문제번호>` — 문제 환경 생성
- `/boj-solve <문제번호>` — 자동 풀이
