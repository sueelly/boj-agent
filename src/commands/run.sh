#!/usr/bin/env bash
# boj run [문제번호] [옵션]
# 테스트 실행 (test_cases.json 기반)
# 옵션:
#   --lang java|python|cpp|c   언어 override

ROOT="${1:?ROOT}"
PROBLEM_NUM="${2:?문제번호}"
shift 2

# 공통 라이브러리
# shellcheck source=../lib/config.sh
source "$ROOT/src/lib/config.sh"
boj_load_config

# 옵션 파싱
OPT_LANG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang) OPT_LANG="$2"; shift 2 ;;
    --lang=*) OPT_LANG="${1#--lang=}"; shift ;;
    -h|--help)
      echo "사용법: boj run <문제번호> [옵션]"
      echo "  --lang java|python|cpp|c  언어 override (기본: ~/.config/boj/lang)"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

LANG="${OPT_LANG:-$boj_lang}"

# 언어 유효성 검사
boj_validate_lang "$LANG" || exit 1

# 문제 폴더 찾기
PROBLEM_DIR="$(boj_require_problem_dir "$ROOT" "$PROBLEM_NUM")" || exit 1
TEMPLATE="$ROOT/templates/$LANG"

# test_cases.json 확인
if [[ ! -f "$PROBLEM_DIR/test/test_cases.json" ]]; then
  echo -e "${RED}Error: test/test_cases.json이 없습니다. make를 먼저 실행하세요.${NC}" >&2
  exit 1
fi

# test_cases.json id 자동 보완 (id 없는 케이스에 순서대로 id 부여)
# 원본은 수정하지 않고 임시 파일 사용
normalize_test_cases() {
  local json_file="$1"
  local tmp_out
  tmp_out=$(mktemp)
  python3 - "$json_file" > "$tmp_out" 2>/dev/null << 'PYEOF'
import json, sys
path = sys.argv[1]
with open(path) as f:
    raw = f.read()
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    # 파싱 불가 시 원본 그대로
    print(raw)
    sys.exit(0)

cases = data.get("testCases", data.get("test_cases", []))
for i, tc in enumerate(cases, 1):
    if "id" not in tc or tc["id"] is None:
        tc["id"] = i
    if "description" not in tc or not tc.get("description"):
        tc["description"] = f"예제 {i}"
data["testCases"] = cases
print(json.dumps(data, ensure_ascii=False, indent=2))
PYEOF
  echo "$tmp_out"
}

# 언어별 실행
case "$LANG" in
  java)
    # Parse.java 확인
    if [[ ! -f "$PROBLEM_DIR/test/Parse.java" ]]; then
      echo -e "${RED}Error: test/Parse.java를 찾을 수 없습니다.${NC}" >&2
      exit 1
    fi
    # 템플릿 확인
    if [[ ! -f "$TEMPLATE/Test.java" ]]; then
      echo -e "${RED}Error: 테스트 러너 템플릿이 없습니다: $TEMPLATE/Test.java (BOJ_LANG=$LANG)${NC}" >&2
      exit 1
    fi
    if [[ ! -f "$PROBLEM_DIR/Solution.java" ]]; then
      echo -e "${RED}Error: Solution.java를 찾을 수 없습니다.${NC}" >&2
      exit 1
    fi

    # test_cases.json 정규화 (임시 파일, 원본 비파괴)
    normalized="$(normalize_test_cases "$PROBLEM_DIR/test/test_cases.json")"
    # -s: 파일이 존재하고 내용이 있는 경우에만 교체 (빈 파일로 원본 덮어쓰기 방지)
    if [[ -s "$normalized" ]]; then
      # trap 먼저 설정 — 중간 실패 시에도 정규화/백업 파일 정리
      trap 'rm -f "$PROBLEM_DIR/test/test_cases_normalized.json" "$normalized" 2>/dev/null' EXIT
      cp "$normalized" "$PROBLEM_DIR/test/test_cases_normalized.json" || { echo -e "${RED}Error: 정규화 파일 복사 실패${NC}" >&2; exit 1; }
      rm -f "$normalized"
      cp "$PROBLEM_DIR/test/test_cases.json" "$PROBLEM_DIR/test/test_cases_orig.json" || { echo -e "${RED}Error: 원본 백업 실패${NC}" >&2; exit 1; }
      # 백업 생성 후 복원용 trap으로 교체 ($normalized는 이미 삭제됨)
      trap 'cp "$PROBLEM_DIR/test/test_cases_orig.json" "$PROBLEM_DIR/test/test_cases.json" 2>/dev/null; rm -f "$PROBLEM_DIR/test/test_cases_orig.json" "$PROBLEM_DIR/test/test_cases_normalized.json" 2>/dev/null' EXIT
      cp "$PROBLEM_DIR/test/test_cases_normalized.json" "$PROBLEM_DIR/test/test_cases.json" || { echo -e "${RED}Error: 정규화 파일 적용 실패${NC}" >&2; exit 1; }
    else
      rm -f "$normalized"
    fi

    (cd "$PROBLEM_DIR" && javac -cp ".:$TEMPLATE" \
      "$TEMPLATE/ParseAndCallSolve.java" "$TEMPLATE/Test.java" \
      Solution.java test/Parse.java 2>&1) && \
    (cd "$PROBLEM_DIR" && java -cp ".:test:$TEMPLATE" Test)
    ret=$?
    (cd "$PROBLEM_DIR" && rm -f ./*.class test/*.class 2>/dev/null)
    exit $ret
    ;;

  python)
    if [[ ! -f "$PROBLEM_DIR/solution.py" && ! -f "$PROBLEM_DIR/Solution.py" ]]; then
      echo -e "${RED}Error: solution.py 또는 Solution.py를 찾을 수 없습니다.${NC}" >&2
      exit 1
    fi
    if [[ ! -f "$TEMPLATE/test_runner.py" ]]; then
      echo -e "${RED}Error: 테스트 러너 템플릿이 없습니다: $TEMPLATE/test_runner.py${NC}" >&2
      exit 1
    fi

    # test_cases.json 정규화 (원본 비파괴)
    normalized="$(normalize_test_cases "$PROBLEM_DIR/test/test_cases.json")"
    if [[ -s "$normalized" ]]; then
      # trap 먼저 설정 — 중간 실패 시에도 정규화/백업 파일 정리
      trap 'rm -f "$PROBLEM_DIR/test/test_cases_normalized.json" "$normalized" 2>/dev/null' EXIT
      cp "$normalized" "$PROBLEM_DIR/test/test_cases_normalized.json" || { echo -e "${RED}Error: 정규화 파일 복사 실패${NC}" >&2; exit 1; }
      rm -f "$normalized"
      cp "$PROBLEM_DIR/test/test_cases.json" "$PROBLEM_DIR/test/test_cases_orig.json" || { echo -e "${RED}Error: 원본 백업 실패${NC}" >&2; exit 1; }
      # 백업 생성 후 복원용 trap으로 교체 ($normalized는 이미 삭제됨)
      trap 'cp "$PROBLEM_DIR/test/test_cases_orig.json" "$PROBLEM_DIR/test/test_cases.json" 2>/dev/null; rm -f "$PROBLEM_DIR/test/test_cases_orig.json" "$PROBLEM_DIR/test/test_cases_normalized.json" 2>/dev/null' EXIT
      cp "$PROBLEM_DIR/test/test_cases_normalized.json" "$PROBLEM_DIR/test/test_cases.json" || { echo -e "${RED}Error: 정규화 파일 적용 실패${NC}" >&2; exit 1; }
    else
      rm -f "$normalized"
    fi

    (cd "$PROBLEM_DIR" && python3 "$TEMPLATE/test_runner.py")
    exit $?
    ;;

  cpp)
    SOLUTION_FILE="$PROBLEM_DIR/Solution.cpp"
    if [[ ! -f "$SOLUTION_FILE" ]]; then
      echo -e "${RED}Error: Solution.cpp를 찾을 수 없습니다.${NC}" >&2
      exit 1
    fi
    echo -e "${YELLOW}C++ 테스트 러너는 아직 구현 중입니다. Solution.cpp 를 직접 컴파일해 테스트하세요.${NC}" >&2
    exit 1
    ;;

  c)
    SOLUTION_FILE="$PROBLEM_DIR/Solution.c"
    if [[ ! -f "$SOLUTION_FILE" ]]; then
      echo -e "${RED}Error: Solution.c를 찾을 수 없습니다.${NC}" >&2
      exit 1
    fi
    echo -e "${YELLOW}C 테스트 러너는 아직 구현 중입니다. Solution.c 를 직접 컴파일해 테스트하세요.${NC}" >&2
    exit 1
    ;;

  *)
    echo -e "${RED}Error: '$LANG' 언어는 현재 run 명령으로 지원되지 않습니다.${NC}" >&2
    echo "지원 언어: java python" >&2
    exit 1
    ;;
esac
