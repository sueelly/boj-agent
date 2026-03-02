class Parse:
    def parse_and_solve(self, sol, input: str) -> str:
        lines = input.strip().split('\n')
        results = []
        for line in lines:
            n = int(line.strip())
            if n == 0:
                break
            results.append(sol.solve(n))
        return '\n'.join(results)
