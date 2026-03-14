class Parse:
    def parse_and_solve(self, sol, input: str) -> str:
        parts = input.strip().split()
        a, b = int(parts[0]), int(parts[1])
        return str(sol.solve(a, b))


# test_runner.py 호환: 모듈 레벨 함수
_parser = Parse()


def parse_and_solve(sol, input: str) -> str:
    return _parser.parse_and_solve(sol, input)
