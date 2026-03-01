#!/usr/bin/env bash
# boj submit [문제번호] [--lang java|python|cpp|c] [--open] [--force]
# Submit.java(또는 언어별 파일) 생성 — BOJ 제출 환경에서 바로 컴파일/실행 가능

ROOT="${1:?ROOT}"
PROBLEM_NUM="${2:?문제번호}"
shift 2

# 공통 라이브러리
# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"
boj_load_config

# 옵션 파싱
OPT_LANG=""
OPT_OPEN=false
OPT_FORCE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang) OPT_LANG="$2"; shift 2 ;;
    --lang=*) OPT_LANG="${1#--lang=}"; shift ;;
    --open) OPT_OPEN=true; shift ;;
    --force|-f) OPT_FORCE=true; shift ;;
    -h|--help)
      echo "사용법: boj submit <문제번호> [옵션]"
      echo "  --lang java|python|cpp|c  언어 override (기본: ~/.config/boj/lang)"
      echo "  --open                    제출 페이지 브라우저 오픈"
      echo "  --force                   기존 Submit 파일 덮어쓰기 확인 없이"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

LANG="${OPT_LANG:-$boj_lang}"

# 문제 폴더 찾기
PROBLEM_DIR="$(boj_require_problem_dir "$ROOT" "$PROBLEM_NUM")" || exit 1
PROBLEM_NAME="$(basename "$PROBLEM_DIR")"

echo -e "${BLUE}📦 Submit 생성: $PROBLEM_NAME ($LANG)${NC}"

# 언어별 파일 확장자
case "$LANG" in
  java)     EXT="java"; SUBMIT_FILE="submit/Submit.java" ;;
  python)   EXT="py";   SUBMIT_FILE="submit/Submit.py" ;;
  cpp)      EXT="cpp";  SUBMIT_FILE="submit/Submit.cpp" ;;
  c)        EXT="c";    SUBMIT_FILE="submit/Submit.c" ;;
  kotlin)   EXT="kt";   SUBMIT_FILE="submit/Submit.kt" ;;
  go)       EXT="go";   SUBMIT_FILE="submit/Submit.go" ;;
  *)
    echo -e "${RED}Error: 'submit' 명령은 현재 java/python/cpp/c/kotlin/go만 지원합니다.${NC}" >&2
    exit 1 ;;
esac

# Python은 템플릿 convention solution.py 우선 (run.sh와 동일)
SOLUTION_FILE="$PROBLEM_DIR/Solution.$EXT"
if [[ "$LANG" == "python" ]]; then
  if [[ -f "$PROBLEM_DIR/solution.py" ]]; then SOLUTION_FILE="$PROBLEM_DIR/solution.py"
  elif [[ -f "$PROBLEM_DIR/Solution.py" ]]; then SOLUTION_FILE="$PROBLEM_DIR/Solution.py"
  fi
fi
PARSE_FILE="$PROBLEM_DIR/test/Parse.$EXT"
SUBMIT_PATH="$PROBLEM_DIR/$SUBMIT_FILE"

# Solution 파일 확인
if [[ ! -f "$SOLUTION_FILE" ]]; then
  echo -e "${RED}Error: Solution 파일이 없습니다 (solution.py 또는 Solution.$EXT). 먼저 풀이를 작성하세요.${NC}" >&2
  exit 1
fi

# submit/ 폴더 생성
mkdir -p "$PROBLEM_DIR/submit"

# 기존 Submit 파일 존재 시
if [[ -f "$SUBMIT_PATH" && "$OPT_FORCE" != "true" ]]; then
  echo -e "${YELLOW}Warning: $SUBMIT_FILE 이 이미 있습니다. 덮어쓰시겠습니까? (y/N)${NC}"
  read -p "  " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "취소됨."
    exit 0
  fi
fi

# ======= 언어별 Submit 생성 =======

generate_java_submit() {
  local solution_content parse_content
  solution_content="$(cat "$SOLUTION_FILE")"

  # Solution 클래스 내용 추출 (class Solution { ... } 블록)
  # 간단한 방식: 파일 전체를 사용하되 public class → class로 변환 + Main 클래스 추가

  # Parse.java 존재 여부
  local has_parse=false
  if [[ -f "$PARSE_FILE" ]]; then
    parse_content="$(cat "$PARSE_FILE")"
    has_parse=true
  fi

  # import 구문 추출 (java.util.*, java.io.* 등)
  local imports
  imports=$(grep "^import " "$SOLUTION_FILE" 2>/dev/null | sort -u)
  if [[ -f "$PARSE_FILE" ]]; then
    local parse_imports
    parse_imports=$(grep "^import " "$PARSE_FILE" 2>/dev/null | sort -u)
    imports=$(echo -e "$imports\n$parse_imports" | sort -u | grep -v "^$")
  fi

  # Main 클래스 생성: stdin 직접 읽기
  # (Solution/Parse 클래스 전체를 아래 섹션에서 sed로 직접 변환하여 붙임)
  # 기본 import + Solution/Parse의 import 합산 (중복 제거)
  {
    echo "import java.util.*;"
    echo "import java.io.*;"
    if [[ -n "$imports" ]]; then
      echo "$imports"
    fi
  } | sort -u > "$SUBMIT_PATH"
  echo "" >> "$SUBMIT_PATH"

  cat >> "$SUBMIT_PATH" << 'SUBMIT_MAIN_END'

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            sb.append(line).append('\n');
        }
        String input = sb.toString().trim();
        Solution sol = new Solution();
SUBMIT_MAIN_END

  # Parse가 있으면 parseAndCallSolve 활용, 없으면 직접 stdin 파싱 예시
  if [[ "$has_parse" == "true" ]]; then
    cat >> "$SUBMIT_PATH" << 'SUBMIT_PARSE_END'
        Parse parser = new Parse();
        String result = parser.parseAndCallSolve(sol, input);
        System.out.println(result);
    }
}
SUBMIT_PARSE_END
  else
    cat >> "$SUBMIT_PATH" << 'SUBMIT_NOPARSE_END'
        // TODO: 입력 파싱 후 sol.solve(...) 호출
        // StringTokenizer st = new StringTokenizer(input);
        // int n = Integer.parseInt(st.nextToken());
        // System.out.println(sol.solve(n));
    }
}
SUBMIT_NOPARSE_END
  fi

  # Solution 클래스 (public 제거)
  echo "" >> "$SUBMIT_PATH"
  echo "// ===== Solution =====" >> "$SUBMIT_PATH"
  sed 's/^public class Solution/class Solution/' "$SOLUTION_FILE" | \
    grep -v "^import " | grep -v "^package " >> "$SUBMIT_PATH"

  # Parse 클래스 (있으면 추가, public 제거, implements ParseAndCallSolve 제거)
  if [[ "$has_parse" == "true" ]]; then
    echo "" >> "$SUBMIT_PATH"
    echo "// ===== Parse =====" >> "$SUBMIT_PATH"
    sed 's/^public class Parse/class Parse/' "$PARSE_FILE" | \
      sed 's/ implements ParseAndCallSolve//' | \
      grep -v "^import " | grep -v "^package " | \
      grep -v "^[[:space:]]*@Override" >> "$SUBMIT_PATH" || true
  fi

  echo -e "${GREEN}✓ Java Submit 생성 완료${NC}"

  # 컴파일 검증
  echo -e "${BLUE}컴파일 검증 중...${NC}"
  local tmp_dir
  tmp_dir=$(mktemp -d)
  cp "$SUBMIT_PATH" "$tmp_dir/Main.java"
  if javac "$tmp_dir/Main.java" 2>/dev/null; then
    echo -e "${GREEN}✓ 컴파일 성공${NC}"
  else
    echo -e "${YELLOW}Warning: Submit.java 컴파일 확인 실패. 수동으로 확인하세요.${NC}" >&2
    # 컴파일 오류는 경고만 (submit 파일은 이미 생성됨)
  fi
  rm -rf "$tmp_dir"
}

generate_python_submit() {
  local solution_content
  solution_content="$(cat "$SOLUTION_FILE")"

  cat > "$SUBMIT_PATH" << 'PYSUBMIT_END'
#!/usr/bin/env python3
import sys
input = sys.stdin.readline

PYSUBMIT_END

  # Solution 내용 추가
  cat "$SOLUTION_FILE" >> "$SUBMIT_PATH"

  # main 블록
  cat >> "$SUBMIT_PATH" << 'PYMAIN_END'


if __name__ == "__main__":
    data = sys.stdin.read().strip()
    sol = Solution()
    # Parse가 있으면 from test.parse import parse_and_solve 활용 가능
    # result = parse_and_solve(sol, data)
    # print(result)
PYMAIN_END

  echo -e "${GREEN}✓ Python Submit 생성 완료${NC}"
}

generate_cpp_submit() {
  cat > "$SUBMIT_PATH" << 'CPPSUBMIT_END'
#include <bits/stdc++.h>
using namespace std;

CPPSUBMIT_END
  # Solution 내용에서 #include 제거 후 추가
  grep -v "^#include" "$SOLUTION_FILE" >> "$SUBMIT_PATH" || true

  cat >> "$SUBMIT_PATH" << 'CPPMAIN_END'

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    // TODO: 입력 파싱 후 solve() 호출
    return 0;
}
CPPMAIN_END

  echo -e "${GREEN}✓ C++ Submit 생성 완료${NC}"
}

generate_c_submit() {
  cat > "$SUBMIT_PATH" << 'CSUBMIT_END'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

CSUBMIT_END
  grep -v "^#include" "$SOLUTION_FILE" >> "$SUBMIT_PATH" || true

  cat >> "$SUBMIT_PATH" << 'CMAIN_END'

int main() {
    // TODO: 입력 파싱 후 solve() 호출
    return 0;
}
CMAIN_END

  echo -e "${GREEN}✓ C Submit 생성 완료${NC}"
}

# 언어별 생성 실행
case "$LANG" in
  java)   generate_java_submit ;;
  python) generate_python_submit ;;
  cpp)    generate_cpp_submit ;;
  c)      generate_c_submit ;;
  kotlin|go)
    # 에이전트 활용 안내
    echo -e "${YELLOW}$LANG Submit 생성은 에이전트를 통해 진행하세요.${NC}"
    echo "에이전트에 전달할 내용이 클립보드에 복사됩니다."
    PROMPT="$PROBLEM_NAME 문제의 Submit.$EXT 를 생성해줘. Solution.$EXT 내용을 BOJ 제출용 단일 파일로 변환."
    if command -v pbcopy &>/dev/null; then
      echo "$PROMPT" | pbcopy
      echo -e "${GREEN}📋 클립보드 복사 완료${NC}"
    fi
    exit 0 ;;
esac

echo ""
echo -e "${BLUE}생성된 파일: $SUBMIT_PATH${NC}"
echo ""

# --open: 제출 페이지 브라우저 오픈
if [[ "$OPT_OPEN" == "true" ]]; then
  SUBMIT_URL="https://www.acmicpc.net/submit/$PROBLEM_NUM"
  echo -e "${BLUE}제출 페이지 오픈: $SUBMIT_URL${NC}"
  if command -v open &>/dev/null; then
    open "$SUBMIT_URL"
  elif command -v xdg-open &>/dev/null; then
    xdg-open "$SUBMIT_URL"
  else
    echo -e "${YELLOW}Warning: 브라우저를 열 수 없습니다. URL: $SUBMIT_URL${NC}"
  fi
fi

echo ""
echo -e "${GREEN}✅ Submit 완료!${NC}"
echo ""
echo "다음 단계:"
echo "  1. $SUBMIT_PATH 내용 확인"
echo "  2. https://www.acmicpc.net/submit/$PROBLEM_NUM 에서 제출"
echo "  또는: boj submit $PROBLEM_NUM --open  (제출 페이지 자동 오픈)"
