/**
 * 10808번: 알파벳 개수 - JSON input 한 줄을 그대로 Solution.solve(s)에 전달
 */
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        return sol.solve(input.trim());
    }
}
