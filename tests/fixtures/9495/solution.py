from collections import deque


class Solution:
    def solve(self, n: int, board: list) -> int:
        S, T = 0, 1
        N = 2 + n * n
        cap = [[0] * N for _ in range(N)]
        INF = 10 ** 9
        dr = [-1, 1, 0, 0]
        dc = [0, 0, -1, 1]

        initial_empty = 0
        white_count = 0

        for r in range(n):
            for c in range(n):
                ch = board[r][c]
                node = 2 + r * n + c
                if ch == '.':
                    initial_empty += 1
                    cap[node][T] += 1
                elif ch == 'o':
                    white_count += 1
                    cap[S][node] += 1
                    for d in range(4):
                        nr, nc = r + dr[d], c + dc[d]
                        if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == '.':
                            cap[node][2 + nr * n + nc] = INF

        level = [-1] * N
        iter_ = [0] * N

        def bfs() -> bool:
            for i in range(N):
                level[i] = -1
            level[S] = 0
            q = deque([S])
            while q:
                v = q.popleft()
                for u in range(N):
                    if cap[v][u] > 0 and level[u] < 0:
                        level[u] = level[v] + 1
                        q.append(u)
            return level[T] >= 0

        def dfs(v: int, f: int) -> int:
            if v == T:
                return f
            while iter_[v] < N:
                u = iter_[v]
                if cap[v][u] > 0 and level[v] < level[u]:
                    d = dfs(u, min(f, cap[v][u]))
                    if d > 0:
                        cap[v][u] -= d
                        cap[u][v] += d
                        return d
                iter_[v] += 1
            return 0

        flow = 0
        while bfs():
            for i in range(N):
                iter_[i] = 0
            while True:
                d = dfs(S, INF)
                if d == 0:
                    break
                flow += d

        return initial_empty + white_count - flow
