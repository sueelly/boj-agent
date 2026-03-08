import java.util.*;

public class Solution {
    static final int INF = Integer.MAX_VALUE / 2;

    static class Edge {
        int to, cap, rev;
        Edge(int to, int cap, int rev) { this.to = to; this.cap = cap; this.rev = rev; }
    }

    List<Edge>[] g;
    int[] level, iter;

    @SuppressWarnings("unchecked")
    void initGraph(int n) {
        g = new ArrayList[n];
        for (int i = 0; i < n; i++) g[i] = new ArrayList<>();
        level = new int[n];
        iter = new int[n];
    }

    void addEdge(int from, int to, int cap) {
        g[from].add(new Edge(to, cap, g[to].size()));
        g[to].add(new Edge(from, 0, g[from].size() - 1));
    }

    boolean bfs(int s, int t) {
        Arrays.fill(level, -1);
        Deque<Integer> q = new ArrayDeque<>();
        level[s] = 0;
        q.add(s);
        while (!q.isEmpty()) {
            int v = q.poll();
            for (Edge e : g[v]) {
                if (e.cap > 0 && level[e.to] < 0) {
                    level[e.to] = level[v] + 1;
                    q.add(e.to);
                }
            }
        }
        return level[t] >= 0;
    }

    int dfs(int v, int t, int f) {
        if (v == t) return f;
        for (; iter[v] < g[v].size(); iter[v]++) {
            Edge e = g[v].get(iter[v]);
            if (e.cap > 0 && level[v] < level[e.to]) {
                int d = dfs(e.to, t, Math.min(f, e.cap));
                if (d > 0) {
                    e.cap -= d;
                    g[e.to].get(e.rev).cap += d;
                    return d;
                }
            }
        }
        return 0;
    }

    int maxflow(int s, int t) {
        int flow = 0;
        while (bfs(s, t)) {
            Arrays.fill(iter, 0);
            int d;
            while ((d = dfs(s, t, INF)) > 0) flow += d;
        }
        return flow;
    }

    public int solve(int n, String[] board) {
        int S = 0, T = 1;
        initGraph(2 + n * n);

        int initialEmpty = 0, whiteCount = 0;
        int[] dr = {-1, 1, 0, 0};
        int[] dc = {0, 0, -1, 1};

        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                char ch = board[r].charAt(c);
                int node = 2 + r * n + c;
                if (ch == '.') {
                    initialEmpty++;
                    addEdge(node, T, 1);
                } else if (ch == 'o') {
                    whiteCount++;
                    addEdge(S, node, 1);
                    for (int d = 0; d < 4; d++) {
                        int nr = r + dr[d], nc = c + dc[d];
                        if (nr >= 0 && nr < n && nc >= 0 && nc < n && board[nr].charAt(nc) == '.') {
                            addEdge(node, 2 + nr * n + nc, INF);
                        }
                    }
                }
            }
        }

        return initialEmpty + whiteCount - maxflow(S, T);
    }
}
