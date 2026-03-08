public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        String[] lines = input.trim().split("\n");
        int n = Integer.parseInt(lines[0].trim());
        String[] board = new String[n];
        for (int i = 0; i < n; i++) board[i] = lines[i + 1].trim();
        return String.valueOf(sol.solve(n, board));
    }
}
