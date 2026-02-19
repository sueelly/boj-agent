import java.util.Arrays;

/**
 * 3273번: 두 수의 합 - JSON input 파싱 후 Solution.solve(n, arr, x) 호출
 */
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        String[] lines = input.split("\n");
        int n = Integer.parseInt(lines[0].trim());
        int[] arr = Arrays.stream(lines[1].split("\\s+")).mapToInt(Integer::parseInt).toArray();
        int x = Integer.parseInt(lines[2].trim());
        return String.valueOf(sol.solve(n, arr, x));
    }
}
