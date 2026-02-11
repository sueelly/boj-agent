# 백준 (Baekjoon) 알고리즘 문제 풀이

## 🤖 Agentic Workflow

이 폴더는 **AI(Cursor)**를 활용한 자동화된 문제 풀이 환경입니다.
템플릿을 수동으로 수정할 필요 없이, AI가 문제를 분석하여 적합한 코드를 자동 생성합니다.

## 📁 폴더 구조

```
baekjoon/
├── README.md           # 이 파일 (사용 가이드)
├── .cursorrules        # AI 가이드 (Cursor가 참조)
├── template/           # 기본 템플릿 (AI 참고용)
│   ├── Solution.java   # 알고리즘 로직
│   ├── Main.java       # 백준 제출용
│   ├── Test.java       # 테스트 러너 (수정 불필요)
│   ├── test_cases.json # 테스트 케이스 (JSON)
│   ├── run.sh          # Main 실행
│   └── test.sh         # Test 실행
└── [문제번호]-[문제제목]/  # 각 문제별 폴더
```

## 🚀 사용 방법 (AI 활용 ⭐)

### 1. 새 문제 시작하기

Cursor에서 다음과 같이 요청하세요:

```
백준 1000번 문제 풀이 환경 만들어줘
```
또는
```
https://www.acmicpc.net/problem/1000 이 문제 풀이 환경 만들어줘
```

**AI가 자동으로 수행:**
- 📁 `1000-a+b` 폴더 생성
- 📄 `README.md` - 문제 내용 스크래핑
- 📄 `Solution.java` - 문제에 맞는 메서드 시그니처 생성
- 📄 `Main.java` - 입력 파싱 로직 자동 생성
- 📄 `test_cases.json` - 예제 테스트 케이스 추가
- 📄 `Test.java`, `run.sh`, `test.sh` - 템플릿에서 복사

### 2. 알고리즘 구현

`Solution.java`의 `solve()` 메서드에 알고리즘을 구현하세요.
입력 파싱은 이미 AI가 해놨으니, 순수 로직에만 집중!

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

```bash
cd [문제폴더]
./test.sh    # 테스트 케이스 검증
./run.sh     # 직접 입력 테스트
```

### 5. 백준 제출

`Main.java`와 `Solution.java`를 합쳐서 제출하거나,
AI에게 "백준 제출용 코드 만들어줘"라고 요청하세요.

## 📄 파일 설명

| 파일 | 역할 | 수정 필요 |
|------|------|----------|
| `Solution.java` | 알고리즘 로직 | ✅ 직접 구현 |
| `Main.java` | 입력 파싱 & 출력 | ❌ AI가 생성 |
| `Test.java` | JSON 기반 테스트 러너 | ❌ 수정 불필요 |
| `test_cases.json` | 테스트 입출력 데이터 | ✅ 케이스 추가 가능 |
| `README.md` | 문제 설명 | ❌ AI가 생성 |
| `run.sh` / `test.sh` | 실행 스크립트 | ❌ 수정 불필요 |

## 💡 워크플로우 요약

```
1. "백준 XXXX번 문제 환경 만들어줘" 요청
       ↓
2. AI가 폴더 + 파일 자동 생성
       ↓
3. Solution.java에서 알고리즘만 구현
       ↓
4. ./test.sh로 테스트
       ↓
5. 통과하면 백준 제출
       ↓
6. "제출 완료" 또는 "코드 리뷰해줘" 요청
       ↓
7. AI가 코드 분석 + 대표 풀이 비교 + 학습 포인트 제공
```

---

## 📊 제출 후 코드 리뷰 (AI 활용 ⭐)

### 사용 방법

문제를 풀고 제출한 후, 다음과 같이 요청하세요:

```
제출 완료! 코드 리뷰해줘
```
또는
```
10808번 분석해줘
```

### AI가 제공하는 내용

1. **📝 내 코드 분석**
   - 접근 방식, 시간/공간 복잡도
   - 장점 및 개선 가능한 점

2. **🏆 대표 풀이 소개**
   - 효율적인 다른 풀이 방법
   - 내 코드와의 차이점 비교

3. **🎯 학습 포인트**
   - 이 문제에서 배울 점
   - 보완할 점
   - 관련 문제 추천

4. **📄 REVIEW.md 생성**
   - 분석 내용을 파일로 저장

## 📤 GitHub 커밋

문제 풀이 완료 후 GitHub에 올리기:

```bash
./commit.sh 10808-알파벳-개수
# 또는 커밋 메시지 직접 지정
./commit.sh 10808-알파벳-개수 "알파벳 개수 풀이 완료"
```

### 업로드되는 파일 (.gitignore 설정)
- `README.md` - 문제 설명
- `REVIEW.md` - 코드 리뷰
- `Solution.java` - 내 풀이
- `Submit.java` - 백준 제출용 코드
- `test_cases.json` - 테스트 케이스

## ⚠️ 주의사항

1. **백준 제출 시**: 클래스명은 반드시 `Main`이어야 함
2. **패키지 선언 금지**: 백준은 패키지 없이 제출해야 함
3. **입출력 최적화**: `BufferedReader`/`BufferedWriter` 사용 권장

## 🔧 수동 사용 (선택)

AI 없이 수동으로 사용하려면:

```bash
cp -r template 1000-a+b
cd 1000-a+b
# Main.java, Solution.java, test_cases.json 직접 수정
```
