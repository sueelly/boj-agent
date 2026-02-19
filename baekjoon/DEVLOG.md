# 🤖 AI를 활용한 알고리즘 문제 풀이 자동화 여정

> 백준 알고리즘 문제 풀이 환경을 AI(Cursor)를 활용해 자동화한 과정을 기록합니다.

---

## 📌 배경: 왜 자동화가 필요했나?

백준(Baekjoon) 온라인 저지는 플랫폼 내에서 테스트 코드 실행이 불가능합니다. 
따라서 매번 문제를 풀 때마다:

1. 폴더 생성
2. 문제 내용 복사
3. 입력 파싱 코드 작성
4. 테스트 케이스 직접 실행
5. 제출용 코드 정리

이런 반복적인 작업이 필요했고, **알고리즘 구현에만 집중하고 싶다**는 생각에서 자동화를 시작했습니다.

---

## 🔄 진화 과정

### 1단계: 기본 템플릿 방식

**접근**: 템플릿 폴더를 만들고 수동으로 복사해서 사용

```
template/
├── Main.java       # 직접 수정 필요
├── Solution.java   # 직접 수정 필요
├── Test.java       # 직접 수정 필요
├── run.sh
└── test.sh
```

**문제점**:
- 매번 폴더명 직접 작성
- README.md 수동 작성
- Main.java, Test.java 매번 수정 필요
- 입력 형식 파악 후 직접 파싱 코드 작성

---

### 2단계: 스크립트 자동화 (new_problem.sh)

**개선**: 백준 문제 링크만 입력하면 폴더 자동 생성

```bash
./new_problem.sh https://www.acmicpc.net/problem/10808
```

**구현**:
- `scrape_problem.py`: 백준 페이지에서 문제 내용 스크래핑
- `new_problem.sh`: 폴더 생성 + 템플릿 복사 + README 작성

**문제점**:
- 여전히 Main.java, Test.java 수동 수정 필요
- 입력 형식에 맞는 파싱 로직 직접 작성
- 스크래핑 스크립트 유지보수 필요

---

### 3단계: Agentic Workflow 도입 🚀

**핵심 아이디어**: 
> "템플릿을 복사하는 게 아니라, AI가 문제를 분석해서 적합한 코드를 직접 생성하면 어떨까?"

**변화**:

| 기존 | Agentic 방식 |
|------|-------------|
| 템플릿 복사 후 수동 수정 | AI가 문제 분석 → 코드 자동 생성 |
| Main.java 직접 파싱 구현 | AI가 입력 형식 분석하여 생성 |
| Test.java 직접 수정 | JSON 파일에 케이스만 추가 |
| 반복적인 보일러플레이트 | 알고리즘 구현에만 집중 |

**구현**:

1. **`.cursorrules` 파일 생성**
   - AI가 참조하는 가이드라인
   - 폴더 구조, 파일 형식, 네이밍 규칙 정의
   - 문제 생성 / 코드 리뷰 워크플로우 정의

2. **JSON 기반 테스트 시스템**
   ```json
   {
     "testCases": [
       {"id": 1, "input": "baekjoon", "expected": "1 1 0 0 ..."}
     ]
   }
   ```
   - Test.java는 수정 불필요 (범용 테스트 러너)
   - 테스트 케이스는 JSON 파일에만 추가

3. **AI 도움 차단 (VSCode 이동)**
   - 문제 환경 생성 후 `code .` 실행
   - VSCode에서 AI 도움 없이 직접 풀이

---

### 4단계: 역할 분리 강화 🎯

**핵심 아이디어**:
> "Solution은 순수 알고리즘만 담당하고, 파싱은 Main과 Test가 담당해야 한다"

**문제점 (3단계)**:
```java
// Solution.java - 파싱 + 알고리즘이 섞여있음
public String solve(String input) {
    String[] lines = input.split("\n");
    int n = Integer.parseInt(lines[0]);
    // ... 파싱 로직
    // ... 알고리즘 로직
}
```

**개선 (4단계)**:
```java
// Main.java - 파싱 담당
int n = Integer.parseInt(br.readLine().trim());
int[] arr = parseArray(br.readLine());
int x = Integer.parseInt(br.readLine().trim());
int result = sol.solve(n, arr, x);  // 파싱된 값 전달

// Solution.java - 순수 알고리즘만
public int solve(int n, int[] arr, int x) {
    // 파싱 로직 없이 알고리즘만 구현
    return 0;
}

// Test.java - parseAndCallSolve()로 JSON 파싱
private static String parseAndCallSolve(Solution sol, String input) {
    String[] lines = input.split("\n");
    int n = Integer.parseInt(lines[0].trim());
    int[] arr = Arrays.stream(lines[1].split(" ")).mapToInt(Integer::parseInt).toArray();
    int x = Integer.parseInt(lines[2].trim());
    return String.valueOf(sol.solve(n, arr, x));
}
```

**장점**:

| 항목 | Before (String input) | After (개별 파라미터) |
|------|----------------------|---------------------|
| 역할 분리 | 파싱+알고리즘 혼재 | 명확한 분리 |
| 가독성 | solve(String) → 뭐가 들어오는지 모름 | solve(int n, int[] arr, int x) → 바로 파악 |
| 테스트 | 문자열로 조합해서 전달 | 값을 직접 전달 |
| 재사용성 | 파싱 로직이 Solution에 종속 | Solution은 어디서든 호출 가능 |

---

### 5단계: 정확한 문제 내용 가져오기 🔍

**문제점**:
- AI가 문제 내용을 기억에 의존해서 작성
- 부정확한 문제 설명이 README에 들어가는 경우 발생

**개선**:
- `.cursorrules`에 명시: **"반드시 웹 검색(web_search)을 통해 실제 백준 문제 내용을 확인한 후 작성"**
- 기억에 의존하지 않고 정확한 문제 설명 보장

```markdown
#### README.md
**중요: 반드시 웹 검색(web_search)을 통해 실제 백준 문제 내용을 확인한 후 작성할 것!**
**기억에 의존하지 말고 정확한 문제 설명을 가져와야 함.**
```

---

### 6단계: 제출 관련 파일 분리 📁

**핵심 아이디어**:
> "제출/리뷰 관련 파일을 별도 폴더로 분리하여 구조를 명확하게"

**변경 (6단계)**:
```
문제폴더/
├── README.md         # 문제 설명
├── Solution.java     # 내 풀이 (알고리즘)
├── Main.java         # 입력 파싱 (로컬용)
├── Test.java         # 테스트 러너 (로컬용)
├── test_cases.json   # 테스트 케이스
├── run.sh, test.sh   # 실행 스크립트
│
└── submit/           # 📁 제출 관련 파일 분리!
    ├── Submit.java   # 백준 제출용 코드
    └── REVIEW.md     # 코드 리뷰
```

**장점**:
- 풀이 파일과 제출 파일의 역할 명확화
- 폴더 구조만 봐도 어떤 파일이 어디에 있는지 직관적
- Git 커밋 시 submit 폴더만 따로 관리 가능

---

### 7단계: 스크립트 개선 🧹

**개선 내용**:
- `run.sh`, `test.sh` 실행 후 항상 `.class` 파일 삭제
- 컴파일 실패 시에도 삭제되어 폴더가 깔끔하게 유지

```bash
#!/bin/bash
javac Main.java Solution.java && java Main
rm -f *.class  # 항상 삭제
```

---

### 8단계: 템플릿 간소화 · run.sh 통합 · Parse 분리 🧩

**핵심 아이디어**:
> "Main/run/test는 제거하고, 테스트는 루트 하나의 run.sh로. 테스트 공통 로직은 template에 두고, 문제별로 Parse만 구현"

**변경 사항**:

| 구분 | Before | After |
|------|--------|--------|
| 문제 폴더 | Main.java, Test.java, run.sh, test.sh 포함 | **Parse.java** + Solution, README, test_cases.json 만 |
| 테스트 실행 | `cd [폴더]` 후 `./test.sh` | **루트에서** `./run.sh [문제번호]` |
| 테스트 로직 | 문제마다 Test.java 전체 복사, parseAndCallSolve만 수정 | **template/Test.java** 공통 사용, **Parse.java**가 ParseAndCallSolve 구현 |

**구조**:
- **template/**: `ParseAndCallSolve.java`(인터페이스), `Test.java`(공통 러너), Solution·test_cases 예시. Main·run·test 제거.
- **루트 run.sh**: `./run.sh 4949` → 해당 문제 폴더로 이동 후 template + Solution + Parse 컴파일·실행.
- **문제 폴더**: `Parse.java`에서 `parseAndCallSolve(Solution sol, String input)` 만 구현.

**장점**:
- 보일러플레이트 감소 (Main·Test·스크립트 복사 없음)
- 테스트 실행 방식 통일 (commit.sh와 같은 문제번호 인자)
- Parse 한 파일만 수정하면 되어 유지보수 용이

---

### 9단계: test/ 폴더 분리 · 테스트도 커밋 📂

**핵심 아이디어**:
> "중심은 Solution.java. 테스트(Parse, test_cases)는 test/로 모아 두고 둘 다 커밋해서, 필요하면 테스트까지 재현 가능하게. submit/을 둔 것처럼(백준에 그대로 붙여넣기용), test/는 '로컬 검증 재현용'."

**변경 사항**:
- 문제 폴더 루트의 `Parse.java`, `test_cases.json` → **test/Parse.java**, **test/test_cases.json** 으로 이동
- **test/** 폴더만 보면 "이 문제의 테스트 설정"이 한눈에 들어옴
- .gitignore·commit.sh에서 **test/** 도 추적·커밋 대상으로 포함 (예: `!*/test/`, `!*/test/Parse.java`, `!*/test/test_cases.json`, commit 시 test/ 추가)
- template/Test.java는 `test/test_cases.json` 경로로 읽도록 수정, run.sh는 `test/Parse.java` 기준으로 컴파일·실행

**정책 (저장소에서 무엇을 추적할지)**:
- **Solution.java** — 풀이의 중심, 반드시 커밋
- **submit/** — 백준에 그대로 붙여넣기용(Submit.java, REVIEW.md), 커밋
- **test/** — 필요 시 테스트까지 재현 가능하도록 Parse.java, test_cases.json 커밋
- **정책·설계 결정** — 별도 POLICY.md 없이, **DEVLOG에 단계별로 기록** (이렇게 하면 "왜 이렇게 바꿨는지"가 이력과 함께 남음)

---

### 10단계: boj CLI — 어디서든 실행 가능한 명령어 🖥️

**고민한 점**: `run.sh`·`commit.sh`를 쓰려면 매번 백준 폴더로 들어가야 해서 불편했다. "어디서든 `boj run 4949`처럼 쓰고 싶다" → 그러려면 **실행 시점에 baekjoon(또는 algorithm) 폴더를 어떻게 찾을지**가 문제였다.

**검토한 방안**:
- **A. 전체 디스크 탐색** (`find`로 run.sh 검색): 설정 없이 어디서든 가능하지만 느리고, clone이 여러 개면 어느 쓸지 불명확.
- **B. 현재 디렉터리에서 위로 올라가며 `baekjoon/run.sh` 포함 디렉터리 찾기**: 설정 없이, algorithm 아래 어디서든 동작·빠름. 다만 `~/Documents` 등 repo 밖에서는 실패.
- **C. algorithm(또는 baekjoon) 안에서만 허용**: 구현은 단순하지만 "어디서든"이 아니므로 요구와 맞지 않음.
- **D. 한 번만 경로 설정** (환경변수 `BOJ_ROOT` 등): 진짜 어디서든 사용 가능하고 빠르며 명확. 대신 최초 1회 설정 필요.

**선택**: **B + D 혼합**.  
우선 현재 디렉터리에서 위로 올라가며 `baekjoon/run.sh`가 있는 디렉터리를 찾고, 없으면 환경변수 `BOJ_ROOT`(algorithm 루트 또는 baekjoon 경로)를 사용. 전체 탐색은 하지 않음.

**구현**:
- **boj** 래퍼 스크립트: 위 방식으로 baekjoon 루트 확정 후, `run.sh` / `commit.sh` 호출.
- **setup-boj-cli.sh**: 한 번 실행 시 `~/bin/boj`에 래퍼 설치, 필요 시 PATH·BOJ_ROOT를 .zshrc에 추가.
- 서브커맨드: `boj run 4949`, `boj commit 4949 [메시지]`, `boj make 4949`, `boj review 4949`.

**boj make / boj review — Cursor Agent CLI 사용**  
- **make**: `agent`가 있으면 `agent chat -f -p "..."` 로 환경 생성. 없으면 baekjoon을 Cursor로 열고 클립보드 안내 → 사용자가 채팅에 붙여넣으면 AI가 폴더 생성 후 **해당 폴더에서 `code .`만 실행** (문제 풀 때 AI 없어야 하므로 VS Code만 사용).  
- **review**: `agent`가 있으면 해당 문제 폴더에서 agent chat. 없으면 **문제 폴더를 VS Code로** 열고 채팅 안내.  
- agent 호출 시 `-f -p`(force, print)로 자동 승인·비대화형 동작.

**문제 폴더는 무조건 code .**  
- 풀 때 AI 없이 풀어야 하므로, 생성된 문제 폴더를 여는 에디터는 **항상 `code .`(VS Code)**. Cursor가 아닌 VS Code로 열어서 AI 도움 없이 구현하도록 함.

---

## 📊 최종 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│  1. 문제 환경 생성                                           │
│     boj make 4949  (또는 Cursor 채팅: "백준 4949번 환경 만들어줘") │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. AI가 자동 생성                                           │
│     📁 4949-균형잡힌-세상/                                    │
│     ├── README.md, Solution.java                             │
│     └── test/ (Parse.java, test_cases.json)                 │
│     → 생성된 폴더에서 code . 실행 (VS Code만, 풀 때 AI 없음)   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. VS Code에서 알고리즘만 구현 (AI 도움 없이)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 테스트 & 제출                                             │
│     boj run 4949  (또는 ./run.sh 4949)                       │
│     "제출해줘" → submit/Submit.java → 백준 제출                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. AI 코드 리뷰                                             │
|     boj review 4949  또는 "리뷰해줘" → submit/REVIEW.md       │
│     📝 내 코드 분석 (시간/공간 복잡도, 장단점)                  │
│     🏆 대표 풀이 비교                                         │
│     🎯 학습 포인트 & 다음 문제 추천                            │
│     📄 REVIEW.md 자동 생성                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  6. GitHub 커밋                                              │
│     boj commit 4949  → GitHub                               |
|        필요한 파일만 자동 커밋 (.gitignore 설정)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 최종 폴더 구조

```
baekjoon/
├── .cursorrules        # AI 가이드라인
├── .gitignore          # 필요한 파일만 업로드
├── commit.sh           # GitHub 커밋 자동화
├── run.sh              # 테스트 실행 (./run.sh [문제번호])
├── boj                 # CLI 래퍼 (설치 후 어디서든 boj run/make/review)
├── setup-boj-cli.sh    # boj CLI 한 번 설치용
├── README.md           # 사용 가이드
├── template/           # 공통 템플릿 (ParseAndCallSolve, Test 등)
│   └── submit/         # 제출 템플릿
│
├── 3273-두-수의-합/     # 문제별 폴더
│   ├── README.md       # ✅ 업로드
│   ├── Solution.java   # ✅ 업로드 (중심)
│   ├── test/           # ✅ 업로드 (테스트 재현용)
│   │   ├── Parse.java
│   │   └── test_cases.json
│   │
│   └── submit/         # ✅ 업로드 (백준 붙여넣기용)
│       ├── Submit.java
│       └── REVIEW.md
│
└── 1475-방-번호/
    └── ...
```

---

## 💡 핵심 학습 포인트

### 1. Agentic Workflow의 힘
단순히 "AI에게 코드 작성 요청"이 아닌, **AI가 스스로 판단하고 적절한 행동을 수행**하도록 설계

### 2. .cursorrules 활용
프로젝트별 컨텍스트와 규칙을 AI에게 전달하여 일관된 결과물 생성

### 3. 인간과 AI의 역할 분리
- **AI**: 반복적/보일러플레이트 작업 (환경 세팅, 파싱, 리뷰)
- **인간**: 핵심 알고리즘 설계 및 구현 (AI 도움 없이)

### 4. 피드백 루프 구축
풀이 → 제출 → 리뷰 → 학습 포인트 도출 → 다음 문제 추천

### 5. 관심사의 분리 (Separation of Concerns)
- **test/Parse.java**: JSON 입력 파싱 (테스트용)
- **Solution.java**: 순수 알고리즘 (비즈니스 로직)
- **template/Test.java**: 테스트 실행 (검증 담당, 공통)

이 원칙은 클린 아키텍처의 핵심이며, 코드의 테스트 용이성과 재사용성을 높임

---

## 📈 효과

| 항목 | Before | After |
|------|--------|-------|
| 환경 세팅 시간 | 5-10분 | 10초 |
| 수정 필요 파일 | 3-4개 | 1개 (Solution.java) |
| Solution 역할 | 파싱 + 알고리즘 | 순수 알고리즘만 |
| solve() 시그니처 | solve(String input) | solve(int n, int[] arr, int x) |
| 테스트 케이스 관리 | 코드에 하드코딩 | JSON 파일 |
| 코드 리뷰 | 없음 | submit/REVIEW.md 자동 생성 |
| 제출 코드 | 수동 병합 | submit/Submit.java 자동 생성 |
| GitHub 업로드 | 수동 | 스크립트 자동화 |
| 문제 설명 | AI 기억 의존 | 웹 검색으로 정확히 |
| 폴더 구조 | 모든 파일 혼재 | submit/ 폴더로 분리 |

---

## 🔮 향후 개선 아이디어

1. **자동 난이도 분류**: 문제 태그/난이도 기반 폴더 정리
2. **통계 대시보드**: 풀이 현황, 취약 유형 분석
3. **스케줄링**: 매일 추천 문제 자동 생성
4. **다른 플랫폼 확장**: LeetCode, 프로그래머스 지원

---

## 🛠️ 사용 기술

- **AI**: Cursor (Claude 기반)
- **언어**: Java, Bash, Python
- **도구**: Git, VSCode

---

*작성일: 2026-02-11*  
*최종 수정: 2026-02-19 (boj CLI 추가, make/review는 컨텍스트·안내만)*
