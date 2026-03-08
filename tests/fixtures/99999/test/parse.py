class Parse:
    def parse_and_solve(self, sol, input: str) -> str:
        parts = input.strip().split()
        a, b = int(parts[0]), int(parts[1])
        return str(sol.solve(a, b))
