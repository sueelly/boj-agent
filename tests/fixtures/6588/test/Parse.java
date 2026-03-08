public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        StringBuilder sb = new StringBuilder();
        String[] lines = input.trim().split("\n");
        boolean first = true;
        for (String line : lines) {
            int n = Integer.parseInt(line.trim());
            if (n == 0) break;
            if (!first) sb.append("\n");
            sb.append(sol.solve(n));
            first = false;
        }
        return sb.toString();
    }
}
