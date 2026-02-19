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

## 📊 최종 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│  1. Cursor에서 요청                                          │
│     "백준 1475번 문제 환경 만들어줘"                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. AI가 자동 생성                                           │
│     📁 1475-방-번호/                                         │
│     ├── README.md        (문제 설명 - 웹 검색으로 정확히)      │
│     ├── Solution.java    (빈 solve 메서드, 파라미터 정의)      │
│     ├── Parse.java       (JSON 파싱 → Solution에 전달)        │
│     └── test_cases.json  (예제 테스트 케이스)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. VSCode 자동 실행 (AI 도움 차단)                           │
│     → 순수하게 알고리즘만 구현                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 테스트 & 제출                                            │
│     ./run.sh [문제번호] → 로컬 검증 (백준 루트에서)            │
│     백준 제출 → "제출 완료" 요청                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. AI 코드 리뷰                                             │
│     📝 내 코드 분석 (시간/공간 복잡도, 장단점)                  │
│     🏆 대표 풀이 비교                                         │
│     🎯 학습 포인트 & 다음 문제 추천                            │
│     📄 REVIEW.md 자동 생성                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  6. GitHub 커밋                                              │
│     ./commit.sh 1475                                        │
│     → 필요한 파일만 자동 커밋 (.gitignore 설정)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 최종 폴더 구조

```
baekjoon/
├── .cursorrules        # AI 가이드라인
├── .gitignore          # 필요한 파일만 업로드
├── commit.sh           # GitHub 커밋 자동화
├── README.md           # 사용 가이드
├── run.sh              # 테스트 실행 (./run.sh [문제번호])
├── template/           # 공통 템플릿 (ParseAndCallSolve, Test 등)
│   └── submit/         # 제출 템플릿
│
├── 3273-두-수의-합/     # 문제별 폴더
│   ├── README.md       # ✅ GitHub 업로드
│   ├── Solution.java   # ✅ GitHub 업로드
│   ├── Parse.java      # ❌ 로컬만 (테스트용)
│   ├── test_cases.json # ✅ GitHub 업로드
│   │
│   └── submit/         # 📁 제출 관련
│       ├── Submit.java # ✅ GitHub 업로드
│       └── REVIEW.md   # ✅ GitHub 업로드
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
- **Parse.java**: JSON 입력 파싱 (테스트용)
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
*최종 수정: 2026-02-19 (템플릿 간소화, run.sh 통합, Parse 분리)*
