"""
문제별 test/parse.py가 제공해야 하는 계약:
  def parse_and_solve(sol, input: str) -> str

sol: solution.Solution 인스턴스
input: test_cases.json의 한 케이스 "input" 문자열
return: 해당 케이스에 대한 출력 문자열 (공백 정규화 후 비교됨)
"""
# 예시 (문제에 맞게 구현):
# def parse_and_solve(sol, input_str: str) -> str:
#     lines = input_str.strip().split('\n')
#     n = int(lines[0])
#     arr = list(map(int, lines[1].split()))
#     return str(sol.solve(n, arr))
