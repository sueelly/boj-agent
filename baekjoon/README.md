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
├── boj                 # CLI 래퍼 (설치 시 어디서든 사용)
├── setup-boj-cli.sh    # boj 한 번 설치용
├── template/           # 공통 템플릿 (수정 불필요)
│   ├── ParseAndCallSolve.java   # 인터페이스
│   ├── Test.java                # 테스트 러너
│   ├── Solution.java            # 예시
│   ├── test_cases.json          # 예시
│   └── submit/                  # 제출 템플릿
│
└── [문제번호]-[문제제목]/  # 각 문제별 폴더
    ├── README.md         # 문제 설명
    ├── Solution.java     # 알고리즘 (내가 구현) ← 중심
    ├── test/             # 테스트 (필요 시 사용, 커밋하여 재현 가능)
    │   ├── Parse.java    # JSON → Solution 파싱
    │   └── test_cases.json
    │
    └── submit/           # 백준에 그대로 붙여넣기용
        ├── Submit.java   # 제출용 코드
        └── REVIEW.md     # 코드 리뷰
```

## 🚀 사용 방법

### 0. (선택) boj CLI — 어디서든 실행

한 번만 설치하면 터미널 어디서든 `boj run 4949`처럼 사용할 수 있습니다.

```bash
cd <algorithm>/baekjoon
./setup-boj-cli.sh
```

설치 후 (새 터미널 또는 `source ~/.zshrc`):

| 명령 | 설명 |
|------|------|
| `boj run 4949` | 테스트 실행 |
| `boj commit 4949 ["메시지"]` | 해당 문제 폴더 커밋 |
| `boj make 4949` | **Cursor Agent CLI**로 환경 생성 요청 (또는 에디터 열기+클립보드 안내) |
| `boj review 4949` | **Cursor Agent CLI**로 리뷰 요청 (또는 에디터 열기+클립보드 안내) |

- **make**: Agent CLI 있으면 `agent chat "..."`로 환경 생성. 없으면 baekjoon 폴더를 Cursor로 열고, 채팅에 붙여넣기 안내 → AI가 폴더 생성 후 **해당 폴더에서 `code .`** 로 VS Code만 연다 (풀 때 AI 없음).
- **review**: Agent CLI 있으면 `agent chat "리뷰해줘"`. 없으면 문제 폴더를 **VS Code**로 열고 채팅 안내.
- **repo 찾기**: 현재 디렉터리에서 위로 올라가며 `baekjoon/run.sh`를 찾고, 없으면 `BOJ_ROOT` 사용. `setup-boj-cli.sh` 실행 시 BOJ_ROOT·PATH 추가 여부를 물어봄.

### 1. 새 문제 시작하기

**방법 A — boj CLI (권장)**  
Cursor Agent CLI가 있으면 한 줄로 환경 생성:

```bash
boj make 4949
```

**방법 B — Cursor 채팅**  
Cursor를 baekjoon 폴더로 연 뒤, 채팅에서 요청:

```
백준 4949번 문제 풀이 환경 만들어줘
```
또는 `https://www.acmicpc.net/problem/4949` 링크와 함께 요청.

**AI가 자동으로 수행:**
- 📁 문제 폴더 생성 + README.md, Solution.java, test/Parse.java, test/test_cases.json 생성
- 🔍 웹 검색으로 정확한 문제 내용 가져오기
- 💻 **해당 문제 폴더에서 `code .` 실행** → VS Code로만 연다 (풀 때 AI 없이 풀기 위해)

### 2. 알고리즘 구현

**VS Code**로 열린 문제 폴더에서 `Solution.java`의 `solve()` 메서드에만 알고리즘 구현 (AI 도움 없이):
```java
// 파싱된 값을 직접 받음 (파싱 로직 필요 없음!)
public int solve(int n, int[] arr, int x) {
    // TODO: 순수 알고리즘만 구현
    return 0;
}
```

### 3. 테스트 케이스 추가 (선택)

`test/test_cases.json`에 테스트 케이스 추가:

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

**boj 설치 후** 어디서든:

```bash
boj run 4949
boj run 3273
```

또는 백준 폴더에서 직접:

```bash
cd <algorithm>/baekjoon
./run.sh 4949
```
> 실행 후 `.class` 파일은 자동 삭제됩니다.

### 5. 백준 제출 & 리뷰

- **제출용 코드**: Cursor에서 "제출해줘" 요청 → `submit/Submit.java` 생성 후 백준에 붙여넣기.
- **코드 리뷰**: Cursor에서 "리뷰해줘" 또는 "제출 완료" 요청 → `submit/REVIEW.md` 생성.  
  또는 터미널에서 `boj review 4949` (Cursor Agent CLI 있으면 자동 실행).

### 6. GitHub 커밋

```bash
boj commit 4949
boj commit 4949 "투 포인터 풀이"
```
또는 `./commit.sh 4949 ["메시지"]` (백준 폴더에서).

## 📄 파일 역할

| 파일 | 역할 | 수정 필요 |
|------|------|----------|
| `Solution.java` | **순수 알고리즘** (파싱 없음) | ✅ 직접 구현 |
| `test/Parse.java` | JSON input 파싱 → Solution 호출 | ❌ AI 생성 |
| `test/test_cases.json` | 테스트 입출력 데이터 | ✅ 케이스 추가 가능 |
| `submit/Submit.java` | 백준 제출용 (Solution 로직 + 입출력) | ❌ AI 생성 |
| `submit/REVIEW.md` | 코드 리뷰 | ❌ AI 생성 |

## 💡 워크플로우 요약

```
1. boj make 4949  (또는 Cursor 채팅에서 "백준 4949번 문제 환경 만들어줘")
       ↓
2. AI가 문제 폴더 + README, Solution, test/ 생성 → 해당 폴더에서 code . (VS Code만)
       ↓
3. VS Code에서 Solution.java만 구현 (AI 없이)
       ↓
4. boj run 4949  (또는 ./run.sh 4949) 로 테스트
       ↓
5. "제출해줘" → submit/Submit.java → 백준 제출
       ↓
6. boj review 4949  또는 "리뷰해줘" → submit/REVIEW.md
       ↓
7. boj commit 4949  → GitHub 업로드
```

## 📊 GitHub 업로드 파일

| 파일 | 업로드 |
|------|--------|
| `README.md` | ✅ |
| `Solution.java` | ✅ |
| `test/test_cases.json` | ✅ |
| `submit/Submit.java` | ✅ |
| `submit/REVIEW.md` | ✅ |
| `test/Parse.java`, `test/test_cases.json` | ✅ (테스트 재현용으로 커밋) |

## ⚠️ 주의사항

1. **백준 제출 시**: 클래스명은 반드시 `Main`
2. **패키지 선언 금지**: 백준은 패키지 없이 제출
3. **입출력 최적화**: `BufferedReader`/`BufferedWriter` 사용
