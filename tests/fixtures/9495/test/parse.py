class Parse:
    def parse_and_solve(self, sol, input: str) -> str:
        lines = input.strip().split('\n')
        n = int(lines[0].strip())
        board = [lines[i + 1].strip() for i in range(n)]
        return str(sol.solve(n, board))
