# 백준 (Baekjoon) 알고리즘 문제 풀이

## 🤖 Agentic Workflow

이 폴더는 **AI(Cursor)**를 활용한 자동화된 문제 풀이 환경입니다.
템플릿을 수동으로 수정할 필요 없이, AI가 문제를 분석하여 적합한 코드를 자동 생성합니다.

## 📁 폴더 구조

```
baekjoon/
├── README.md           # 이 파일 (사용 가이드)
├── DEVLOG.md           # 자동화 개발 과정 기록
├── .cursorrules        # AI 가이드 (Cursor가 참조)
├── .gitignore          # GitHub 업로드 파일 설정
├── commit.sh           # GitHub 커밋 자동화
├── run.sh              # 테스트 실행 (./run.sh [문제번호])
├── template/           # 공통 템플릿 (수정 불필요)
│   ├── ParseAndCallSolve.java   # 인터페이스
│   ├── Test.java                # 테스트 러너
│   ├── Solution.java            # 예시
│   ├── test_cases.json          # 예시
│   └── submit/                  # 제출 템플릿
│
└── [문제번호]-[문제제목]/  # 각 문제별 폴더
    ├── README.md         # 문제 설명
    ├── Solution.java     # 알고리즘 (내가 구현)
    ├── Parse.java        # JSON → Solution 파싱 (AI 생성)
    ├── test_cases.json   # 테스트 케이스
    │
    └── submit/           # 📁 제출 관련
        ├── Submit.java   # 백준 제출용 코드
        └── REVIEW.md     # 코드 리뷰
```

## 🚀 사용 방법

### 1. 새 문제 시작하기

Cursor에서 다음과 같이 요청:

```
백준 1000번 문제 풀이 환경 만들어줘
```
또는
```
https://www.acmicpc.net/problem/1000 이 문제 풀이 환경 만들어줘
```

**AI가 자동으로 수행:**
- 📁 폴더 생성 + README.md, Solution.java, Parse.java, test_cases.json 생성
- 🔍 웹 검색으로 정확한 문제 내용 가져오기
- 💻 VSCode 자동 실행 (`code .`)

### 2. 알고리즘 구현

`Solution.java`의 `solve()` 메서드에 알고리즘 구현:
```java
// 파싱된 값을 직접 받음 (파싱 로직 필요 없음!)
public int solve(int n, int[] arr, int x) {
    // TODO: 순수 알고리즘만 구현
    return 0;
}

### 3. 테스트 케이스 추가 (선택)

`test_cases.json`에 테스트 케이스 추가:

```json
{
  "testCases": [
    {
      "id": 1,
      "description": "예제 1",
      "input": "baekjoon",
      "expected": "1 1 0 0 1 0 0 0 0 1 1 0 0 1 2 0 0 0 0 0 0 0 0 0 0 0"
    },
    {
      "id": 2,
      "description": "엣지 케이스",
      "input": "a",
      "expected": "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
    }
  ]
}
```

### 4. 테스트 실행

**백준 폴더 루트에서** 문제 번호만 입력해 테스트:

```bash
./run.sh 4949    # 4949번 문제 테스트
./run.sh 3273    # 3273번 문제 테스트
```
> 실행 후 `.class` 파일은 자동 삭제됩니다.

### 5. 백준 제출

AI에게 "제출해줘" 또는 "백준 제출용 코드 만들어줘"라고 요청하면 `submit/Submit.java` 생성.

```
제출할 수 있게 만들어줘
```
→ AI가 `submit/Submit.java` 생성

```
제출 완료
```
→ AI가 `submit/REVIEW.md` 생성 (코드 분석 + 대표 풀이 비교)

### 6. GitHub 커밋

```bash
./commit.sh 3273                    # 문제 번호만 입력
./commit.sh 3273 "투 포인터 풀이"    # 커밋 메시지 지정
```

## 📄 파일 역할

| 파일 | 역할 | 수정 필요 |
|------|------|----------|
| `Solution.java` | **순수 알고리즘** (파싱 없음) | ✅ 직접 구현 |
| `Parse.java` | JSON input 파싱 → Solution 호출 | ❌ AI 생성 |
| `test_cases.json` | 테스트 입출력 데이터 | ✅ 케이스 추가 가능 |
| `submit/Submit.java` | 백준 제출용 (Solution 로직 + 입출력) | ❌ AI 생성 |
| `submit/REVIEW.md` | 코드 리뷰 | ❌ AI 생성 |

## 💡 워크플로우 요약

```
1. "백준 XXXX번 문제 환경 만들어줘"
       ↓
2. AI가 폴더 + README, Solution, Parse, test_cases.json 생성 → VSCode 실행
       ↓
3. Solution.java에서 알고리즘만 구현 (AI 도움 없이)
       ↓
4. ./run.sh [문제번호] 로 테스트 (백준 루트에서)
       ↓
5. "제출해줘" → submit/Submit.java 생성
       ↓
6. 백준에 제출
       ↓
7. "제출 완료" / "리뷰해줘" → submit/REVIEW.md 생성
       ↓
8. ./commit.sh [문제번호] → GitHub 업로드
```

## 📊 GitHub 업로드 파일

| 파일 | 업로드 |
|------|--------|
| `README.md` | ✅ |
| `Solution.java` | ✅ |
| `test_cases.json` | ✅ |
| `submit/Submit.java` | ✅ |
| `submit/REVIEW.md` | ✅ |
| `Parse.java` | ❌ 로컬만 (테스트용) |

## ⚠️ 주의사항

1. **백준 제출 시**: 클래스명은 반드시 `Main`
2. **패키지 선언 금지**: 백준은 패키지 없이 제출
3. **입출력 최적화**: `BufferedReader`/`BufferedWriter` 사용
