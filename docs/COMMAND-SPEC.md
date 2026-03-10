# 명령어 로직 정의서

> 각 명령어의 실제 코드 동작 플로우를 기술합니다.
> 코드 참조: `src/commands/*.sh`, `src/lib/config.sh`, `src/boj`

---

## 진입점: `src/boj`

```
1. ~/.config/boj/root에서 BOJ_ROOT 로드 (환경변수 없으면)
2. find_boj_root(): cwd에서 위로 올라가며 templates/java/Test.java 탐색 → BOJ_ROOT fallback
3. setup이면 ROOT 탐색 실패해도 실행 허용
4. 서브커맨드 디스패치: exec "$ROOT/src/commands/$SUBCOMMAND.sh" "$ROOT" "$PROBLEM_NUM" "${@:3}"
```

**지원 명령어**: setup, make, open, run, submit, commit, review

---

## 공통: 설정 모듈

### Bash (레거시): `src/lib/config.sh`

전환 완료 시까지 유지. 기존 Bash 명령어에서 사용.

### Python (신규): `src/core/config.py`

Bash config.sh를 대체하는 Python 구현. 모든 Python 명령어에서 사용.

### 설정 우선순위
환경변수 `BOJ_<KEY>` > `$BOJ_CONFIG_DIR/<key>` 파일 > 기본값

### Python 주요 함수

| 함수 | 역할 |
|------|------|
| `config_get(key, default)` | 설정값 읽기 (우선순위 적용) |
| `config_set(key, value)` | `$BOJ_CONFIG_DIR/<key>`에 저장 |
| `is_setup_done()` | `setup_done` 플래그 파일 존재 여부 |
| `mark_setup_done()` | `setup_done` 플래그 파일 생성 |
| `check_config()` | 전체 설정 상태 표시 (--check용) |
| `validate_lang(lang)` | 지원 언어 검증 (java, python) |
| `validate_path(path)` | 경로 존재 여부 검증 |
| `get_agent_command(name)` | agent 이름 → 실행 명령어 매핑 |
| `get_git_config(key)` | git config --global 값 읽기 |
| `set_git_config(key, value)` | git config --global 값 쓰기 |

### Bash 주요 함수 (레거시)

| 함수 | 역할 |
|------|------|
| `boj_config_get(key, default)` | 설정값 읽기 (우선순위 적용) |
| `boj_config_set(key, value)` | `$BOJ_CONFIG_DIR/<key>`에 저장 |
| `boj_load_config()` | lang, editor, agent, session, user 일괄 로드 |
| `boj_check_config()` | 전체 설정 상태 표시 (--check용) |
| `boj_validate_lang(lang)` | 지원 언어 목록 검증 |
| `boj_find_problem_dir(root, num)` | `find $root -maxdepth 1 -type d -name "${num}*"` |
| `boj_require_problem_dir(root, num)` | 폴더 없으면 Error + 존재하는 폴더 목록 출력 |
| `boj_open_editor(path, editor)` | 설정 에디터 → cursor/code → vim/nano 순 fallback |

### 환경변수

| 변수 | 역할 | 비고 |
|------|------|------|
| `BOJ_CONFIG_DIR` | 설정 디렉터리 (기본: `~/.config/boj`) | |
| `BOJ_SOLUTION_ROOT` | 문제 풀이 루트 | 신규 (기존 `BOJ_ROOT` 대체) |
| `BOJ_AGENT_ROOT` | agent 폴더 루트 | 신규 |
| `BOJ_PROG_LANG` | 기본 언어 | 신규 (기존 `BOJ_LANG` 대체) |
| `BOJ_AGENT` | 에이전트 명령 | |
| `BOJ_EDITOR` | 에디터 | |
| `BOJ_USERNAME` | BOJ 사용자 ID | 신규 (기존 `BOJ_USER` 대체) |
| `BOJ_ROOT` | (레거시) 문제 풀이 루트 | Bash 명령어에서만 사용 |
| `BOJ_LANG` | (레거시) 기본 언어 | Bash 명령어에서만 사용 |

### 설정 키 매핑

| config 파일 | 환경변수 | 기본값 | 용도 |
|-------------|----------|--------|------|
| `boj_solution_root` | `BOJ_SOLUTION_ROOT` | (없음) | 문제 풀이 루트 경로 |
| `boj_agent_root` | `BOJ_AGENT_ROOT` | (없음) | agent 폴더 루트 경로 |
| `prog_lang` | `BOJ_PROG_LANG` | `java` | 기본 프로그래밍 언어 |
| `editor` | `BOJ_EDITOR` | `code` | 에디터 실행 명령 |
| `agent` | `BOJ_AGENT` | (없음) | 에이전트 실행 명령 |
| `username` | `BOJ_USERNAME` | (없음) | BOJ 사용자 ID |
| `setup_done` | - | - | 설정 완료 플래그 파일 |

---

## `boj setup`

**파일**: `src/commands/setup.sh`

### 모드
- `--check`: `boj_check_config()` 호출 후 종료
- `--session|--lang|--root|--username`: 비대화형 set 모드
- 인자 없음: 대화형 5단계 설정

### 대화형 플로우
```
[1/5] BOJ_ROOT 경로 설정 (기존값 있으면 변경 확인)
[2/5] 기본 언어 선택 (boj_validate_lang 검증)
[3/5] Git user.name/email 확인 (미설정 시 입력 안내)
[4/5] BOJ 세션 쿠키 (3가지 방법: 자동 로그인 / 직접 입력 / 스킵)
      + BOJ 사용자 ID 입력
[5/5] 에이전트 명령 입력 (미입력 시 에디터+클립보드 fallback)
```

### 비대화형 플래그
- `--session <값>`: 세션 쿠키 직접 저장
- `--username <아이디>`: `BOJ_LOGIN_PASSWORD` 환경변수로 자동 로그인
- `--lang <언어>`: 기본 언어 저장
- `--root <경로>`: 레포 루트 저장

---

## `boj make <문제번호>`

**파일**: `src/commands/make.sh`
**플래그**: `--lang`, `--image-mode download|reference|skip`, `--output /path`, `--no-open`

### 3단계 파이프라인

```
[A] Problem Fetcher: BOJ HTML → artifacts/problem.json
    ├── python3 src/lib/boj_client.py --problem N --out TMP --image-mode MODE
    ├── 제목 추출 → 디렉터리 이름 생성 (N-slug, 최대 30자)
    ├── 기존 폴더 있으면 덮어쓰기 확인
    └── artifacts/ 폴더 생성, problem.json 복사

[B] Statement Normalizer: problem.json → README.md
    ├── python3 src/lib/boj_normalizer.py --input problem.json --out README.md
    └── 기존 signature_review.md 있으면 .bak으로 아카이브

[C] IO Adapter Generator (Agent): 스켈레톤 생성
    ├── 에이전트 있음:
    │   ├── prompts/make-skeleton.md 템플릿에 변수 치환 (Python)
    │   ├── cd $PROBLEM_DIR && $AGENT_CMD "$PROMPT"
    │   ├── Gate Check: solve(String) 단일 파라미터 감지 → 경고
    │   └── Execution Verify: boj run 자동 실행 → 실패 시 경고만
    └── 에이전트 없음:
        ├── problem.json 내용을 클립보드 복사 (pbcopy)
        └── 에디터 fallback 안내
```

### 요약 출력 + 에디터 오픈
`--no-open`이 아니면 `boj_open_editor` 호출

---

## `boj run <문제번호>`

**파일**: `src/commands/run.sh`
**플래그**: `--lang`

### 플로우

```
1. 문제 폴더 찾기 (boj_require_problem_dir)
2. test/test_cases.json 존재 확인
3. normalize_test_cases(): id/description 없는 케이스 자동 보완
   ├── 원본 → test_cases_orig.json 백업
   ├── 정규화 → test_cases_normalized.json → test_cases.json 교체
   └── EXIT trap: 원본 복구 + 임시파일 삭제

4. 언어별 실행:
   ├── java:
   │   ├── test/Parse.java, Solution.java, templates/java/Test.java 존재 확인
   │   ├── javac -cp ".:$TEMPLATE" (ParseAndCallSolve + Test + Solution + Parse)
   │   ├── java -cp ".:test:$TEMPLATE" Test
   │   └── .class 파일 삭제
   ├── python:
   │   ├── solution.py 또는 Solution.py 존재 확인
   │   ├── templates/python/test_runner.py 존재 확인
   │   └── cd $PROBLEM_DIR && python3 $TEMPLATE/test_runner.py
   ├── cpp/c:
   │   └── "테스트 러너 미구현" 안내 메시지 + exit 1
   └── 기타:
       └── "지원되지 않는 언어" 에러
```

### trap 메커니즘
단일 EXIT trap으로 원본 복구 + 정리. Java/Python 각각 동일 패턴.

---

## `boj submit <문제번호>`

**파일**: `src/commands/submit.sh`
**플래그**: `--lang`, `--open`, `--force`

### 플로우

```
1. 문제 폴더 찾기
2. Solution 파일 존재 확인 (Python은 solution.py 우선)
3. submit/ 폴더 자동 생성
4. 기존 Submit 파일 존재 시: --force 아니면 덮어쓰기 확인

5. 언어별 생성:
   ├── java (generate_java_submit):
   │   ├── Solution + Parse의 import 합산 → sort -u로 중복 제거
   │   ├── public class Main { main() { ... } } 생성
   │   ├── Parse 있으면: parser.parseAndCallSolve(sol, input) 호출
   │   ├── Parse 없으면: TODO 주석으로 stdin 파싱 안내
   │   ├── Solution 클래스: public class → class 변환, import/package 제거
   │   ├── Parse 클래스: implements ParseAndCallSolve 제거, @Override 제거
   │   └── javac 컴파일 검증 (실패 시 경고만)
   ├── python (generate_python_submit):
   │   ├── #!/usr/bin/env python3 + import sys 헤더
   │   ├── Solution 내용 그대로 추가
   │   └── if __name__ == "__main__": 블록 (TODO)
   ├── cpp (generate_cpp_submit):
   │   ├── #include <bits/stdc++.h> 헤더
   │   ├── Solution에서 #include 제거 후 추가
   │   └── int main() { ... } TODO
   ├── c (generate_c_submit):
   │   ├── stdio/stdlib/string.h 헤더
   │   └── int main() { ... } TODO
   └── kotlin/go:
       └── 에이전트 안내 + 클립보드 복사

6. --open이면 제출 페이지 브라우저 오픈 (open/xdg-open)
```

---

## `boj commit <문제번호>`

**파일**: `src/commands/commit.sh`
**플래그**: `--message "..."`, `--no-stats`

### 플로우

```
1. git repo 확인 (git rev-parse)
2. git user.email 확인
3. 문제 폴더 찾기

4. BOJ 통계 조회 (fetch_boj_stats):
   ├── --no-stats → "[BOJ 통계: 스킵]"
   ├── session 없음 → "[BOJ 통계: 세션 없음]"
   ├── user 없음 → "[BOJ 통계: 사용자 ID 없음]"
   └── curl로 BOJ 상태 페이지 조회 (max-time 5초):
       ├── OnlineJudge + bojautologin 쿠키 모두 전송
       ├── grep으로 메모리(KB)/시간(ms) 파싱
       ├── 성공 → "[✓ Nms NKB]"
       └── 실패 → 사유별 메시지 (네트워크/파싱/Accepted 없음)

5. 커밋 메시지 구성:
   ├── --message 지정 → 그대로 사용
   └── 미지정 → "문제이름 풀이 완료 [BOJ 통계]"

6. git add (명시적 파일 목록):
   README.md, Solution.*, test/test_cases.json, test/Parse.*,
   submit/REVIEW.md, submit/Submit.*

7. git commit -m "$COMMIT_MSG"
8. 푸시 확인 프롬프트 (y/N)
```

---

## `boj open <문제번호>`

**파일**: `src/commands/open.sh`
**플래그**: `--editor code|cursor|vim|...`

### 플로우

```
1. 문제 폴더 찾기
2. 폴더 없으면:
   ├── boj make 자동 실행
   └── 생성 후 다시 열기
3. boj_open_editor(PROBLEM_DIR, EDITOR_CMD)
```

---

## `boj review <문제번호>`

**파일**: `src/commands/review.sh`

### 플로우

```
1. 문제 폴더 찾기 (boj_require_problem_dir)
2. Solution.* 없으면 Warning (리뷰는 계속)
3. prompts/review.md 있으면 프롬프트에 포함

4. 에이전트 있음:
   └── cd $PROBLEM_DIR && $AGENT_CMD "$REVIEW_PROMPT"
5. 에이전트 없음:
   ├── "리뷰해줘" 클립보드 복사
   └── 에디터로 문제 폴더 열기
```

---

*최종 업데이트: 2026-03-09*
